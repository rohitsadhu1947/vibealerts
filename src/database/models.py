"""
Vibe_Alerts - Data Models
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum


class Sentiment(Enum):
    """Result sentiment categories"""
    STRONG_BEAT = "STRONG_BEAT"
    BEAT = "BEAT"
    INLINE = "INLINE"
    MISS = "MISS"
    MAJOR_MISS = "MAJOR_MISS"


class AnnouncementType(Enum):
    """Types of market announcements"""
    QUARTERLY_RESULT = "QUARTERLY_RESULT"  # Actual financial results
    EARNINGS_CALL = "EARNINGS_CALL"  # Earnings call transcript
    CORPORATE_ACTION = "CORPORATE_ACTION"  # M&A, buyback, takeover, rights issue
    NEWS_ARTICLE = "NEWS_ARTICLE"  # News about stock/market movement
    ANALYST_REPORT = "ANALYST_REPORT"  # Analyst ratings/reports
    OTHER = "OTHER"  # Other announcements


@dataclass
class Announcement:
    """Announcement from monitoring sources"""
    source: str  # nse, bse, etc.
    symbol: str
    date: str
    description: str
    attachment_url: str
    attachment_text: str = ""
    announcement_type: Optional[str] = None  # Will be classified
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_json(self) -> dict:
        return {
            'source': self.source,
            'symbol': self.symbol,
            'date': self.date,
            'description': self.description,
            'attachment_url': self.attachment_url,
            'attachment_text': self.attachment_text,
            'announcement_type': self.announcement_type,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_json(cls, data: dict):
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ExtractedMetrics:
    """Extracted financial metrics from PDFs"""
    symbol: str
    quarter: int  # 1-4
    fiscal_year: int
    
    # Core metrics (in Crores)
    revenue: Optional[Decimal] = None
    profit_after_tax: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    
    # Previous period comparisons
    revenue_prev_quarter: Optional[Decimal] = None
    profit_prev_quarter: Optional[Decimal] = None
    revenue_prev_year: Optional[Decimal] = None
    profit_prev_year: Optional[Decimal] = None
    
    # Additional metrics
    ebitda: Optional[Decimal] = None
    operating_profit: Optional[Decimal] = None
    total_income: Optional[Decimal] = None
    
    # Metadata
    extraction_method: str = ""
    confidence_score: float = 0.0
    extraction_time_ms: int = 0
    
    def to_dict(self) -> dict:
        return {k: str(v) if isinstance(v, Decimal) else v 
                for k, v in self.__dict__.items()}


@dataclass
class AnalystEstimates:
    """Pre-loaded analyst estimates"""
    symbol: str
    quarter: int
    fiscal_year: int
    
    revenue_est: Optional[Decimal] = None
    profit_est: Optional[Decimal] = None
    eps_est: Optional[Decimal] = None
    
    source: str = ""
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        result = {k: str(v) if isinstance(v, Decimal) else v 
                  for k, v in self.__dict__.items()}
        if self.updated_at:
            result['updated_at'] = self.updated_at.isoformat()
        return result


@dataclass
class AnalysisResult:
    """Analysis output with beat/miss calculations"""
    symbol: str
    quarter: int
    fiscal_year: int
    
    # Beat/miss percentages
    revenue_beat_pct: Optional[float] = None
    profit_beat_pct: Optional[float] = None
    eps_beat_pct: Optional[float] = None
    
    # Growth rates
    yoy_revenue_growth: Optional[float] = None
    yoy_profit_growth: Optional[float] = None
    qoq_revenue_growth: Optional[float] = None
    qoq_profit_growth: Optional[float] = None
    
    # Overall sentiment
    sentiment: Sentiment = Sentiment.INLINE
    sentiment_score: float = 0.0
    
    # Action recommendation
    action_text: str = ""
    action_emoji: str = "➡️"
    
    def to_dict(self) -> dict:
        result = self.__dict__.copy()
        result['sentiment'] = self.sentiment.value
        return result


@dataclass
class AlertMessage:
    """Formatted alert message for delivery"""
    symbol: str
    metrics: ExtractedMetrics
    analysis: AnalysisResult
    detection_time_sec: float
    pdf_url: str
    announcement_type: str = "QUARTERLY_RESULT"  # Default to quarterly result
    
    def format_telegram(self) -> str:
        """Format message for Telegram with Markdown"""
        emoji = self.analysis.action_emoji
        
        # Different formats based on announcement type
        if self.announcement_type == "NEWS_ARTICLE":
            return self._format_news_alert()
        elif self.announcement_type == "CORPORATE_ACTION":
            return self._format_corporate_action_alert()
        elif self.announcement_type == "EARNINGS_CALL":
            return self._format_earnings_call_alert()
        else:
            return self._format_result_alert()
    
    def _format_result_alert(self) -> str:
        """Format quarterly result alert"""
        emoji = self.analysis.action_emoji
        
        # Format numbers
        revenue = f"₹{float(self.metrics.revenue):,.0f}Cr" if self.metrics.revenue else "N/A"
        profit = f"₹{float(self.metrics.profit_after_tax):,.0f}Cr" if self.metrics.profit_after_tax else "N/A"
        eps = f"₹{float(self.metrics.eps):.2f}" if self.metrics.eps else "N/A"
        
        # YoY growth indicators
        yoy_rev = f"({self.analysis.yoy_revenue_growth:+.1f}%)" if self.analysis.yoy_revenue_growth else ""
        yoy_profit = f"({self.analysis.yoy_profit_growth:+.1f}%)" if self.analysis.yoy_profit_growth else ""
        
        message = f"""📊 **{self.symbol} Q{self.metrics.quarter} FY{self.metrics.fiscal_year} Results**

**Revenue:** {revenue} {yoy_rev}
**Profit:** {profit} {yoy_profit}
**EPS:** {eps}
"""
        
        # Add beat/miss section if estimates available
        if (self.analysis.revenue_beat_pct is not None or 
            self.analysis.profit_beat_pct is not None or 
            self.analysis.eps_beat_pct is not None):
            
            message += "\n📈 **vs Estimates:**"
            
            if self.analysis.revenue_beat_pct is not None:
                icon = "🟢" if self.analysis.revenue_beat_pct > 0 else "🔴"
                message += f"\n• Revenue: {self.analysis.revenue_beat_pct:+.1f}% {icon}"
            
            if self.analysis.profit_beat_pct is not None:
                icon = "🟢" if self.analysis.profit_beat_pct > 0 else "🔴"
                message += f"\n• Profit: {self.analysis.profit_beat_pct:+.1f}% {icon}"
            
            if self.analysis.eps_beat_pct is not None:
                icon = "🟢" if self.analysis.eps_beat_pct > 0 else "🔴"
                message += f"\n• EPS: {self.analysis.eps_beat_pct:+.1f}% {icon}"
        
        message += f"""

⚡ **Action:** {self.analysis.action_text}
⏱️ Detected in {self.detection_time_sec:.1f}s"""
        
        return message
    
    def _format_news_alert(self) -> str:
        """Format news article alert"""
        # Extract key metrics if available
        revenue = f"₹{float(self.metrics.revenue):,.0f}Cr" if self.metrics.revenue else None
        profit = f"₹{float(self.metrics.profit_after_tax):,.0f}Cr" if self.metrics.profit_after_tax else None
        
        message = f"""📰 **{self.symbol} - Market News**

"""
        
        # Add metrics if found in news
        if revenue or profit:
            message += "**Key Figures:**\n"
            if revenue:
                message += f"• Revenue: {revenue}\n"
            if profit:
                message += f"• Profit: {profit}\n"
            message += "\n"
        
        message += f"""💡 **Source:** News Article
⏱️ Detected in {self.detection_time_sec:.1f}s"""
        
        return message
    
    def _format_corporate_action_alert(self) -> str:
        """Format corporate action alert (M&A, buyback, etc.)"""
        message = f"""🔔 **{self.symbol} - Corporate Action**

**Type:** Disclosure/Corporate Filing

"""
        
        # Add any extracted metrics
        if self.metrics.revenue or self.metrics.profit_after_tax:
            message += "**Mentioned Figures:**\n"
            if self.metrics.revenue:
                message += f"• Revenue: ₹{float(self.metrics.revenue):,.0f}Cr\n"
            if self.metrics.profit_after_tax:
                message += f"• Profit: ₹{float(self.metrics.profit_after_tax):,.0f}Cr\n"
            message += "\n"
        
        message += f"""⏱️ Detected in {self.detection_time_sec:.1f}s"""
        
        return message
    
    def _format_earnings_call_alert(self) -> str:
        """Format earnings call transcript alert"""
        # Format numbers
        revenue = f"₹{float(self.metrics.revenue):,.0f}Cr" if self.metrics.revenue else "N/A"
        profit = f"₹{float(self.metrics.profit_after_tax):,.0f}Cr" if self.metrics.profit_after_tax else "N/A"
        
        message = f"""🎤 **{self.symbol} Q{self.metrics.quarter} FY{self.metrics.fiscal_year} Earnings Call**

**Type:** Transcript/Conference Call

**Revenue:** {revenue}
**Profit:** {profit}

⏱️ Detected in {self.detection_time_sec:.1f}s"""
        
        return message

