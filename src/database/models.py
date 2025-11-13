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


@dataclass
class Announcement:
    """Announcement from monitoring sources"""
    source: str  # nse, bse, etc.
    symbol: str
    date: str
    description: str
    attachment_url: str
    attachment_text: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_json(self) -> dict:
        return {
            'source': self.source,
            'symbol': self.symbol,
            'date': self.date,
            'description': self.description,
            'attachment_url': self.attachment_url,
            'attachment_text': self.attachment_text,
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
    
    def format_telegram(self) -> str:
        """Format message for Telegram with Markdown"""
        emoji = self.analysis.action_emoji
        
        # Format numbers
        revenue = f"₹{float(self.metrics.revenue):,.0f}Cr" if self.metrics.revenue else "N/A"
        profit = f"₹{float(self.metrics.profit_after_tax):,.0f}Cr" if self.metrics.profit_after_tax else "N/A"
        eps = f"₹{float(self.metrics.eps):.2f}" if self.metrics.eps else "N/A"
        
        # YoY growth indicators
        yoy_rev = f"({self.analysis.yoy_revenue_growth:+.1f}%)" if self.analysis.yoy_revenue_growth else ""
        yoy_profit = f"({self.analysis.yoy_profit_growth:+.1f}%)" if self.analysis.yoy_profit_growth else ""
        
        message = f"""{emoji} **{self.symbol} Q{self.metrics.quarter} FY{self.metrics.fiscal_year} Results**

**Revenue:** {revenue} {yoy_rev}
**Profit:** {profit} {yoy_profit}
**EPS:** {eps}
"""
        
        # Add beat/miss section if estimates available
        if (self.analysis.revenue_beat_pct is not None or 
            self.analysis.profit_beat_pct is not None or 
            self.analysis.eps_beat_pct is not None):
            
            message += "\n📊 **vs Estimates:**"
            
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

