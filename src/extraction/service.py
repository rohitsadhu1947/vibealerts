"""
Vibe_Alerts - PDF Extraction Service
Multi-strategy PDF extraction: PyPDF2 → pdfplumber → OCR
"""

import os
import re
import time
import aiohttp
import asyncio
from typing import Optional, Dict
from decimal import Decimal
from datetime import datetime
from loguru import logger

import PyPDF2
import pdfplumber
from src.database.models import Announcement, ExtractedMetrics
from src.utils.classifier import AnnouncementClassifier


class PDFExtractor:
    """Multi-strategy PDF text extraction"""
    
    def __init__(self, config: dict):
        self.config = config
        self.strategies = [
            ('pypdf2', self._extract_with_pypdf2),
            ('pdfplumber', self._extract_with_pdfplumber),
        ]
    
    async def extract(self, pdf_path: str, symbol: str) -> Optional[str]:
        """Extract text from PDF using multiple strategies"""
        
        for strategy_name, strategy_func in self.strategies:
            try:
                logger.debug(f"Trying {strategy_name} for {symbol}")
                text = await strategy_func(pdf_path)
                
                if text and len(text) > 100:  # Minimum text threshold
                    logger.info(f"Successfully extracted with {strategy_name}: {len(text)} chars")
                    return text
                else:
                    logger.debug(f"{strategy_name} returned insufficient text")
                    
            except Exception as e:
                logger.warning(f"{strategy_name} failed for {symbol}: {e}")
                continue
        
        logger.error(f"All extraction strategies failed for {symbol}")
        return None
    
    async def _extract_with_pypdf2(self, pdf_path: str) -> Optional[str]:
        """Fast extraction with PyPDF2"""
        text_parts = []
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n".join(text_parts) if text_parts else None
    
    async def _extract_with_pdfplumber(self, pdf_path: str) -> Optional[str]:
        """Better table extraction with pdfplumber"""
        text_parts = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                
                # Extract tables
                tables = page.extract_tables()
                for table in tables:
                    table_text = self._format_table(table)
                    text_parts.append(table_text)
        
        return "\n".join(text_parts) if text_parts else None
    
    def _format_table(self, table: list) -> str:
        """Format table for text processing"""
        formatted = []
        for row in table:
            if row:
                row_text = " | ".join(str(cell) if cell else "" for cell in row)
                formatted.append(row_text)
        return "\n".join(formatted)


class MetricsParser:
    """Parse financial metrics from extracted text"""
    
    def __init__(self):
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for metric extraction"""
        
        # Indian number format: 1,234.56 or 1234.56
        number = r'([-]?\d{1,3}(?:,\d{2,3})*(?:\.\d{1,2})?|[-]?\d+(?:\.\d{1,2})?)'
        
        patterns = {
            'revenue': re.compile(
                rf'(?:total\s+)?(?:income|revenue)(?:\s+from\s+operations)?.*?{number}\s*(?:cr|crore)',
                re.IGNORECASE
            ),
            'profit_after_tax': re.compile(
                rf'(?:profit\s+(?:after\s+tax|attributable)|net\s+profit|pat).*?{number}\s*(?:cr|crore)',
                re.IGNORECASE
            ),
            'eps': re.compile(
                rf'(?:basic\s+)?(?:earnings|eps)(?:\s+per\s+share)?.*?{number}',
                re.IGNORECASE
            ),
            'ebitda': re.compile(
                rf'ebitda.*?{number}\s*(?:cr|crore)',
                re.IGNORECASE
            ),
            'quarter': re.compile(
                r'(?:q\s*([1-4])|quarter\s+([1-4])|([1-4])(?:st|nd|rd|th)\s+quarter)',
                re.IGNORECASE
            ),
            'fiscal_year': re.compile(
                r'(?:fy|f\.?y\.?|fiscal\s+year)[\s\-]*(\d{2,4})',
                re.IGNORECASE
            ),
        }
        
        return patterns
    
    def parse(self, text: str, symbol: str) -> ExtractedMetrics:
        """Parse metrics from text"""
        
        start_time = time.time()
        
        # Extract temporal context first
        quarter = self._extract_quarter(text)
        fiscal_year = self._extract_fiscal_year(text)
        
        metrics = ExtractedMetrics(
            symbol=symbol,
            quarter=quarter,
            fiscal_year=fiscal_year
        )
        
        # Extract each metric
        metrics.revenue = self._extract_metric(text, self.patterns['revenue'], 'revenue')
        metrics.profit_after_tax = self._extract_metric(text, self.patterns['profit_after_tax'], 'profit')
        metrics.eps = self._extract_metric(text, self.patterns['eps'], 'eps')
        metrics.ebitda = self._extract_metric(text, self.patterns['ebitda'], 'ebitda')
        
        # Try to extract YoY comparisons
        self._extract_comparisons(text, metrics)
        
        # Calculate confidence
        metrics.confidence_score = self._calculate_confidence(metrics)
        
        # Record extraction time
        metrics.extraction_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Parsed {symbol}: Rev={metrics.revenue}, PAT={metrics.profit_after_tax}, "
            f"EPS={metrics.eps}, confidence={metrics.confidence_score:.2f}"
        )
        
        return metrics
    
    def _extract_metric(self, text: str, pattern: re.Pattern, metric_name: str) -> Optional[Decimal]:
        """Extract single metric using pattern"""
        
        match = pattern.search(text)
        if not match:
            return None
        
        # Get the number (first capturing group)
        number_str = match.group(1).replace(',', '').strip()
        
        try:
            value = Decimal(number_str)
            
            # Convert lakhs to crores if needed
            if 'lakh' in match.group(0).lower():
                value = value / Decimal('100')
            
            return value
        except Exception as e:
            logger.warning(f"Failed to parse {metric_name} from '{number_str}': {e}")
            return None
    
    def _extract_quarter(self, text: str) -> int:
        """Extract quarter number (1-4)"""
        match = self.patterns['quarter'].search(text)
        if match:
            # Check all groups
            for group in match.groups():
                if group:
                    return int(group)
        
        # Default to Q3 (most results are Q3)
        logger.warning("Could not determine quarter, defaulting to Q3")
        return 3
    
    def _extract_fiscal_year(self, text: str) -> int:
        """Extract fiscal year"""
        match = self.patterns['fiscal_year'].search(text)
        if match:
            year_str = match.group(1)
            year = int(year_str)
            
            # Convert 2-digit to 4-digit
            if year < 100:
                year = 2000 + year if year < 50 else 1900 + year
            
            return year
        
        # Default to current fiscal year
        now = datetime.now()
        fiscal_year = now.year if now.month >= 4 else now.year - 1
        logger.warning(f"Could not determine fiscal year, defaulting to FY{fiscal_year}")
        return fiscal_year
    
    def _extract_comparisons(self, text: str, metrics: ExtractedMetrics):
        """Extract YoY/QoQ comparison values"""
        
        # Look for "previous year" or "corresponding period" sections
        yoy_patterns = [
            r'(?:previous\s+year|corresponding\s+period|year\s+ago)(.*?)(?:\n\n|$)',
            r'(?:fy\s*\d{2})(.*?)(?:\n\n|$)',
        ]
        
        for pattern in yoy_patterns:
            yoy_match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if yoy_match:
                section_text = yoy_match.group(1)[:500]  # Limit search area
                
                # Try to extract revenue from this section
                prev_rev = self._extract_metric(
                    section_text,
                    self.patterns['revenue'],
                    'revenue_prev_year'
                )
                if prev_rev:
                    metrics.revenue_prev_year = prev_rev
                
                # Try to extract profit
                prev_profit = self._extract_metric(
                    section_text,
                    self.patterns['profit_after_tax'],
                    'profit_prev_year'
                )
                if prev_profit:
                    metrics.profit_prev_year = prev_profit
                
                break
    
    def _calculate_confidence(self, metrics: ExtractedMetrics) -> float:
        """Calculate confidence score based on extracted metrics"""
        
        score = 0.0
        
        # Core metrics present
        if metrics.revenue: score += 0.4
        if metrics.profit_after_tax: score += 0.4
        if metrics.eps: score += 0.2
        
        return score


class ExtractionService:
    """Main extraction orchestrator"""
    
    def __init__(self, config: dict):
        self.config = config
        self.pdf_extractor = PDFExtractor(config)
        self.metrics_parser = MetricsParser()
        self.pdf_timeout = config['extraction'].get('pdf_timeout', 10)
    
    async def process_announcement(self, announcement: Announcement) -> Optional[ExtractedMetrics]:
        """Full extraction pipeline: classify → download → extract → parse OR use text directly"""
        
        start_time = time.time()
        
        try:
            # 1. Classify announcement type first
            logger.info(f"[1/4] Classifying announcement type for {announcement.symbol}...")
            announcement_type, confidence = AnnouncementClassifier.classify(
                announcement.description,
                announcement.attachment_text,
                announcement.source  # Pass source for better classification
            )
            announcement.announcement_type = announcement_type
            
            logger.info(
                f"✅ Classified as {announcement_type} (confidence: {confidence:.2f}) "
                f"for {announcement.symbol}"
            )
            
            # 2. Check if announcement already has extracted text (from RSS feeds)
            if announcement.attachment_text and len(announcement.attachment_text) > 200:
                logger.info(f"[2/4] Using pre-extracted text from {announcement.source} for {announcement.symbol}")
                text = announcement.attachment_text
            else:
                # Download PDF (for exchange sources like BSE/NSE)
                logger.info(f"[2/4] Downloading PDF for {announcement.symbol}...")
                pdf_path = await self._download_pdf(announcement)
                if not pdf_path:
                    logger.error(f"PDF download failed for {announcement.symbol}")
                    return None
                
                # 3. Extract text from PDF
                logger.info(f"[3/4] Extracting text from PDF for {announcement.symbol}...")
                text = await self.pdf_extractor.extract(pdf_path, announcement.symbol)
                
                # Cleanup PDF
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                
                if not text:
                    logger.error(f"Text extraction failed for {announcement.symbol}")
                    return None
            
            # 4. Parse metrics from text
            logger.info(f"[4/4] Parsing metrics for {announcement.symbol}...")
            metrics = self.metrics_parser.parse(text, announcement.symbol)
            
            # 5. Set extraction method
            if announcement.attachment_text and len(announcement.attachment_text) > 200:
                metrics.extraction_method = "rss_text"
            else:
                metrics.extraction_method = "multi_strategy"
            
            elapsed = time.time() - start_time
            logger.info(
                f"✅ Extracted {announcement.symbol} in {elapsed:.2f}s "
                f"(type: {announcement_type}, confidence: {metrics.confidence_score:.2f}, method: {metrics.extraction_method})"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Extraction failed for {announcement.symbol}: {e}")
            return None
    
    async def _download_pdf(self, announcement: Announcement) -> Optional[str]:
        """Download PDF from URL"""
        
        url = announcement.attachment_url
        
        # Make absolute URL if needed
        if not url.startswith('http'):
            if announcement.source == 'nse':
                url = f"https://www.nseindia.com{url}"
            elif announcement.source == 'bse':
                url = f"https://www.bseindia.com{url}"
        
        # Create temp file path
        pdf_path = f"/tmp/{announcement.symbol}_{announcement.date.replace('/', '_')}.pdf"
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                }
                
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.pdf_timeout)
                ) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        
                        with open(pdf_path, 'wb') as f:
                            f.write(content)
                        
                        logger.debug(f"Downloaded PDF: {pdf_path} ({len(content)} bytes)")
                        return pdf_path
                    else:
                        logger.error(f"PDF download failed: HTTP {resp.status} for {url}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"PDF download timeout after {self.pdf_timeout}s")
            return None
        except Exception as e:
            logger.error(f"PDF download error: {e}")
            return None

