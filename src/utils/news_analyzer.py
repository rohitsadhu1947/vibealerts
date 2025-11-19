"""
News Article Analyzer
Extracts actionable insights from market news
"""

import re
from typing import Dict, Optional, Tuple
from loguru import logger


class NewsAnalyzer:
    """Analyzes news articles for actionable insights"""
    
    # Bullish signals
    BULLISH_KEYWORDS = [
        'rebounds', 'rebounded', 'surges', 'soars', 'jumps', 'rallies',
        'gains', 'rises', 'climbs', 'secured', 'wins', 'bags', 'signs',
        'approval', 'approved', 'upgrade', 'upbeat', 'positive',
        'breakthrough', 'record', 'highest', 'strong', 'beats',
        'expansion', 'growth', 'profitable', 'dividend increase'
    ]
    
    # Bearish signals
    BEARISH_KEYWORDS = [
        'plunges', 'tumbles', 'drops', 'falls', 'crashes', 'slumps',
        'declines', 'losses', 'downgrade', 'downgrades', 'miss', 'missed',
        'disappointing', 'weak', 'worst', 'lowest', 'concern', 'warning',
        'loss', 'debt', 'lawsuit', 'investigation', 'scandal',
        'regulatory action', 'penalty', 'fine'
    ]
    
    # High priority actions (definitely look at)
    HIGH_PRIORITY_ACTIONS = [
        'acquisition', 'merger', 'takeover', 'buyback', 'demerger',
        'ipo', 'qip', 'rights issue', 'bonus issue', 'stock split',
        'management change', 'ceo', 'promoter stake', 'insider buying',
        'major contract', 'government order', 'regulatory approval',
        'breakthrough', 'patent', 'license'
    ]
    
    # Medium priority (worth a quick look)
    MEDIUM_PRIORITY_ACTIONS = [
        'earnings', 'profit', 'revenue', 'results', 'quarterly',
        'order', 'contract', 'deal', 'partnership', 'collaboration',
        'expansion', 'plant', 'capacity', 'investment'
    ]
    
    @staticmethod
    def analyze(title: str, content: str = "") -> Dict:
        """
        Analyze news article and extract actionable insights
        
        Args:
            title: News headline
            content: Full article content
            
        Returns:
            Dict with sentiment, signals, summary, and actionability
        """
        text = (title + " " + content[:500]).lower()
        
        # 1. Extract price movement if mentioned
        price_move = NewsAnalyzer._extract_price_movement(text)
        
        # 2. Determine sentiment
        sentiment, sentiment_emoji = NewsAnalyzer._analyze_sentiment(text)
        
        # 3. Extract key action/trigger
        action, action_category = NewsAnalyzer._extract_key_action(text, title)
        
        # 4. Calculate actionability score
        actionability = NewsAnalyzer._calculate_actionability(
            text, action_category, price_move
        )
        
        # 5. Generate quick summary
        summary = NewsAnalyzer._generate_summary(
            title, action, price_move, sentiment
        )
        
        return {
            'sentiment': sentiment,
            'sentiment_emoji': sentiment_emoji,
            'price_movement': price_move,
            'key_action': action,
            'action_category': action_category,
            'actionability': actionability,
            'summary': summary
        }
    
    @staticmethod
    def _extract_price_movement(text: str) -> Optional[str]:
        """Extract percentage or price change from text"""
        
        # Pattern 1: X% or X percent
        pattern1 = r'(\d+\.?\d*)\s*%'
        match = re.search(pattern1, text)
        if match:
            pct = float(match.group(1))
            direction = "↗️" if any(word in text for word in ['rise', 'gain', 'surge', 'rebound', 'jump']) else "↘️"
            return f"{direction} {pct}%"
        
        # Pattern 2: to ₹X or at ₹X
        pattern2 = r'to\s*₹?(\d+\.?\d*)'
        match = re.search(pattern2, text)
        if match:
            price = match.group(1)
            return f"→ ₹{price}"
        
        return None
    
    @staticmethod
    def _analyze_sentiment(text: str) -> Tuple[str, str]:
        """Determine sentiment from text"""
        
        bullish_count = sum(1 for word in NewsAnalyzer.BULLISH_KEYWORDS if word in text)
        bearish_count = sum(1 for word in NewsAnalyzer.BEARISH_KEYWORDS if word in text)
        
        # Strong bullish indicators
        strong_bullish = ['secured', 'securing', 'wins', 'winning', 'bags', 'bagging', 'acquisition', 'approval', 'breakthrough']
        has_strong_bullish = any(word in text for word in strong_bullish)
        
        if has_strong_bullish or (bullish_count > bearish_count and bullish_count >= 2):
            return "Bullish", "🟢"
        elif bearish_count > bullish_count and bearish_count >= 2:
            return "Bearish", "🔴"
        elif bullish_count > bearish_count:
            return "Slightly Bullish", "🟢"
        elif bearish_count > bullish_count:
            return "Slightly Bearish", "🔴"
        else:
            return "Neutral", "⚪"
    
    @staticmethod
    def _extract_key_action(text: str, title: str) -> Tuple[Optional[str], str]:
        """Extract the main action/trigger from the news"""
        
        # Check for contract/order wins with value
        contract_keywords = ['secured', 'securing', 'wins', 'winning', 'bags', 'bagging', 'signs', 'signing', 'wins contract']
        if any(word in text for word in contract_keywords):
            value_match = re.search(r'₹\s*(\d+\.?\d*)\s*(crore|cr|lakh)', text)
            if value_match:
                value = value_match.group(1)
                unit = value_match.group(2)
                return f"Secured ₹{value} {unit} contract", "HIGH"
        
        # Check for other high priority actions
        for action in NewsAnalyzer.HIGH_PRIORITY_ACTIONS:
            if action in text:
                return action.title(), "HIGH"
        
        # Check for medium priority actions
        for action in NewsAnalyzer.MEDIUM_PRIORITY_ACTIONS:
            if action in text:
                return action.title(), "MEDIUM"
        
        # Fallback: extract first few words of title
        words = title.split()[:5]
        return " ".join(words) + "...", "LOW"
    
    @staticmethod
    def _calculate_actionability(text: str, action_category: str, price_move: Optional[str]) -> str:
        """Calculate how actionable this news is"""
        
        score = 0
        
        # Category scoring
        if action_category == "HIGH":
            score += 3
        elif action_category == "MEDIUM":
            score += 2
        else:
            score += 1
        
        # Price movement scoring
        if price_move:
            if "%" in price_move:
                pct = float(re.search(r'(\d+\.?\d*)', price_move).group(1))
                if pct >= 5:
                    score += 2
                elif pct >= 3:
                    score += 1
        
        # High volume keywords
        high_volume_keywords = ['acquisition', 'merger', 'ipo', 'results beat', 'major contract']
        if any(kw in text for kw in high_volume_keywords):
            score += 1
        
        # Determine actionability
        if score >= 5:
            return "🔥 High - Worth immediate review"
        elif score >= 3:
            return "⚠️ Medium - Quick look recommended"
        else:
            return "ℹ️ Low - FYI only"
    
    @staticmethod
    def _generate_summary(title: str, action: Optional[str], price_move: Optional[str], sentiment: str) -> str:
        """Generate a one-line summary"""
        
        parts = []
        
        if action:
            parts.append(action)
        
        if price_move:
            parts.append(f"Stock moved {price_move}")
        
        if sentiment and sentiment != "Neutral":
            parts.append(f"({sentiment} signal)")
        
        if parts:
            return " • ".join(parts)
        else:
            # Fallback: just return cleaned title
            return title[:80] + "..." if len(title) > 80 else title

