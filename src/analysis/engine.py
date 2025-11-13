"""
Vibe_Alerts - Analysis Engine
Compare results vs estimates, calculate beat/miss, generate sentiment
"""

import json
from typing import Optional
from decimal import Decimal
from loguru import logger
from redis import Redis

from src.database.models import ExtractedMetrics, AnalystEstimates, AnalysisResult, Sentiment


class EstimatesManager:
    """Manage analyst estimates with caching"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.cache_ttl = 86400  # 24 hours
    
    async def get_estimates(
        self,
        symbol: str,
        quarter: int,
        fiscal_year: int
    ) -> Optional[AnalystEstimates]:
        """Get estimates from cache (for MVP, estimates are optional)"""
        
        cache_key = f"estimates:{symbol}:Q{quarter}:FY{fiscal_year}"
        
        try:
            cached = self.redis.get(cache_key)
            
            if cached:
                data = json.loads(cached)
                logger.debug(f"Found cached estimates for {symbol}")
                return AnalystEstimates(**data)
        except Exception as e:
            logger.warning(f"Error fetching estimates for {symbol}: {e}")
        
        # For MVP, return None if no estimates found
        logger.debug(f"No estimates found for {symbol} Q{quarter} FY{fiscal_year}")
        return None


class AnalysisEngine:
    """Core analysis logic"""
    
    def __init__(self, redis_client: Redis):
        self.estimates_manager = EstimatesManager(redis_client)
        
        # Sentiment thresholds
        self.thresholds = {
            'strong_beat': 10.0,
            'beat': 5.0,
            'inline_upper': 5.0,
            'inline_lower': -5.0,
            'miss': -10.0,
        }
        
        # Metric weights for overall score
        self.weights = {
            'profit': 0.5,
            'revenue': 0.3,
            'eps': 0.2,
        }
    
    async def analyze(self, metrics: ExtractedMetrics) -> AnalysisResult:
        """Analyze extracted metrics vs estimates"""
        
        result = AnalysisResult(
            symbol=metrics.symbol,
            quarter=metrics.quarter,
            fiscal_year=metrics.fiscal_year
        )
        
        # 1. Fetch estimates (optional for MVP)
        estimates = await self.estimates_manager.get_estimates(
            metrics.symbol,
            metrics.quarter,
            metrics.fiscal_year
        )
        
        # 2. Calculate beat/miss percentages if estimates available
        if estimates:
            result.revenue_beat_pct = self._calculate_beat_pct(
                metrics.revenue,
                estimates.revenue_est
            )
            result.profit_beat_pct = self._calculate_beat_pct(
                metrics.profit_after_tax,
                estimates.profit_est
            )
            result.eps_beat_pct = self._calculate_beat_pct(
                metrics.eps,
                estimates.eps_est
            )
        
        # 3. Calculate growth rates
        result.yoy_revenue_growth = self._calculate_growth(
            metrics.revenue,
            metrics.revenue_prev_year
        )
        result.yoy_profit_growth = self._calculate_growth(
            metrics.profit_after_tax,
            metrics.profit_prev_year
        )
        result.qoq_revenue_growth = self._calculate_growth(
            metrics.revenue,
            metrics.revenue_prev_quarter
        )
        result.qoq_profit_growth = self._calculate_growth(
            metrics.profit_after_tax,
            metrics.profit_prev_quarter
        )
        
        # 4. Calculate overall sentiment
        result.sentiment_score = self._calculate_sentiment_score(result)
        result.sentiment = self._determine_sentiment(result.sentiment_score)
        
        # 5. Generate action text
        result.action_text = self._generate_action_text(result)
        result.action_emoji = self._get_sentiment_emoji(result.sentiment)
        
        logger.info(
            f"Analysis for {metrics.symbol}: "
            f"Sentiment={result.sentiment.value}, Score={result.sentiment_score:.1f}, "
            f"YoY Growth={result.yoy_profit_growth:.1f}%" if result.yoy_profit_growth else ""
        )
        
        return result
    
    def _calculate_beat_pct(
        self,
        actual: Optional[Decimal],
        estimate: Optional[Decimal]
    ) -> Optional[float]:
        """Calculate beat/miss percentage"""
        
        if actual is None or estimate is None or estimate == 0:
            return None
        
        beat_pct = ((actual - estimate) / estimate) * 100
        return float(beat_pct)
    
    def _calculate_growth(
        self,
        current: Optional[Decimal],
        previous: Optional[Decimal]
    ) -> Optional[float]:
        """Calculate growth percentage"""
        
        if current is None or previous is None or previous == 0:
            return None
        
        growth = ((current - previous) / previous) * 100
        return float(growth)
    
    def _calculate_sentiment_score(self, result: AnalysisResult) -> float:
        """Calculate weighted sentiment score"""
        
        score = 0.0
        total_weight = 0.0
        
        # Use beat/miss if available
        if result.profit_beat_pct is not None:
            score += result.profit_beat_pct * self.weights['profit']
            total_weight += self.weights['profit']
        
        if result.revenue_beat_pct is not None:
            score += result.revenue_beat_pct * self.weights['revenue']
            total_weight += self.weights['revenue']
        
        if result.eps_beat_pct is not None:
            score += result.eps_beat_pct * self.weights['eps']
            total_weight += self.weights['eps']
        
        if total_weight > 0:
            return score / total_weight
        
        # Fallback to YoY growth if no estimates
        if result.yoy_profit_growth is not None:
            return result.yoy_profit_growth
        
        # No data for scoring
        return 0.0
    
    def _determine_sentiment(self, score: float) -> Sentiment:
        """Map score to sentiment category"""
        
        if score > self.thresholds['strong_beat']:
            return Sentiment.STRONG_BEAT
        elif score > self.thresholds['beat']:
            return Sentiment.BEAT
        elif score > self.thresholds['inline_lower']:
            return Sentiment.INLINE
        elif score > self.thresholds['miss']:
            return Sentiment.MISS
        else:
            return Sentiment.MAJOR_MISS
    
    def _generate_action_text(self, result: AnalysisResult) -> str:
        """Generate actionable text for traders"""
        
        base_texts = {
            Sentiment.STRONG_BEAT: "🚀 STRONG performance - Major beat across metrics!",
            Sentiment.BEAT: "✅ Positive results - Above expectations",
            Sentiment.INLINE: "➡️ Mixed results - In-line with expectations",
            Sentiment.MISS: "⚠️ Weak results - Below expectations",
            Sentiment.MAJOR_MISS: "🔴 Poor performance - Significant miss",
        }
        
        base_text = base_texts[result.sentiment]
        
        # Add growth context if available
        if result.yoy_profit_growth:
            if result.yoy_profit_growth > 20:
                base_text += f" | Strong YoY growth: {result.yoy_profit_growth:+.1f}%"
            elif result.yoy_profit_growth < -10:
                base_text += f" | YoY decline: {result.yoy_profit_growth:+.1f}%"
        
        return base_text
    
    def _get_sentiment_emoji(self, sentiment: Sentiment) -> str:
        """Get emoji for sentiment"""
        
        emojis = {
            Sentiment.STRONG_BEAT: "🚀",
            Sentiment.BEAT: "✅",
            Sentiment.INLINE: "➡️",
            Sentiment.MISS: "⚠️",
            Sentiment.MAJOR_MISS: "🔴",
        }
        
        return emojis[sentiment]

