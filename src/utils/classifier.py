"""
Announcement Type Classifier
Determines the type of announcement based on content
"""

import re
from typing import Tuple
from loguru import logger


class AnnouncementClassifier:
    """Classifies announcements into different types"""
    
    # Keywords for different announcement types
    QUARTERLY_RESULT_KEYWORDS = [
        'financial results',
        'unaudited results',
        'audited results',
        'quarterly results',
        'half year results',
        'annual results',
        'outcome of board meeting',
        'q1 results', 'q2 results', 'q3 results', 'q4 results',
        'fy20', 'fy21', 'fy22', 'fy23', 'fy24', 'fy25', 'fy26',
    ]
    
    EARNINGS_CALL_KEYWORDS = [
        'transcript',
        'earnings call',
        'conference call',
        'investor call',
        'concall',
        'earnings group call',
        'analyst meet',
    ]
    
    CORPORATE_ACTION_KEYWORDS = [
        'acquisition',
        'merger',
        'takeover',
        'buyback',
        'rights issue',
        'bonus issue',
        'dividend',
        'disclosure under regulation',
        'substantial acquisition',
        'shareholding',
        'allotment',
        'debenture',
        'preferential',
        'open offer',
    ]
    
    NEWS_KEYWORDS = [
        'rebounds',
        'rebounded',
        'surges',
        'plunges',
        'stock price',
        'shares rise',
        'shares fall',
        'market movement',
        'trading',
        'analysts',
        'upgrade',
        'downgrade',
        'target price',
        'why',
        'here\'s why',
        'tumbles',
        'soars',
        'pares',
        'intraday',
        'today\'s',
        'after',
        'following',
        'on the back of',
        'jumps',
        'drops',
        'falls',
        'rises',
        'gains',
        'losses',
        'stock rebounds',
        'stock surges',
        'stock plunges',
        'order book',
        'secures',
        'wins contract',
        'bags order',
    ]
    
    @staticmethod
    def classify(description: str, attachment_text: str = "", source: str = "") -> Tuple[str, float]:
        """
        Classify announcement type based on description and content
        
        Args:
            description: Announcement description/title
            attachment_text: Full text content (for RSS/news)
            source: Source of announcement (e.g., 'economic_times_rss', 'bse_library')
            
        Returns:
            Tuple of (announcement_type, confidence_score)
        """
        # Combine text for analysis
        text = (description + " " + attachment_text[:1000]).lower()
        
        # Score each category
        scores = {
            'EARNINGS_CALL': 0,
            'CORPORATE_ACTION': 0,
            'NEWS_ARTICLE': 0,
            'QUARTERLY_RESULT': 0,
        }
        
        # PRIORITY RULE 1: If from RSS news source, strongly bias toward NEWS_ARTICLE
        is_rss_news = any(rss in source.lower() for rss in ['economic_times', 'livemint', 'moneycontrol', 'rss'])
        if is_rss_news:
            scores['NEWS_ARTICLE'] += 3  # Strong bias for RSS sources
            logger.debug(f"RSS news source detected: {source}, boosting NEWS_ARTICLE by 3")
        
        # Check for earnings call (highest priority after checking keywords)
        for keyword in AnnouncementClassifier.EARNINGS_CALL_KEYWORDS:
            if keyword in text:
                scores['EARNINGS_CALL'] += 2
        
        # Check for corporate actions
        for keyword in AnnouncementClassifier.CORPORATE_ACTION_KEYWORDS:
            if keyword in text:
                scores['CORPORATE_ACTION'] += 1.5
        
        # Check for news articles
        news_keyword_count = 0
        for keyword in AnnouncementClassifier.NEWS_KEYWORDS:
            if keyword in text:
                scores['NEWS_ARTICLE'] += 2  # Increased from 1.5 to 2
                news_keyword_count += 1
        
        # If multiple news keywords found, it's definitely news
        if news_keyword_count >= 3:
            scores['NEWS_ARTICLE'] += 2
            logger.debug(f"Multiple news keywords found ({news_keyword_count}), boosting NEWS_ARTICLE")
        
        # Check for quarterly results
        for keyword in AnnouncementClassifier.QUARTERLY_RESULT_KEYWORDS:
            if keyword in text:
                scores['QUARTERLY_RESULT'] += 1
        
        # Additional heuristics
        
        # If from news sources in text, likely news article
        if any(word in text for word in ['livemint', 'economic times', 'et markets', 'moneycontrol']):
            scores['NEWS_ARTICLE'] += 2
        
        # PRIORITY RULE 2: If has news language patterns, boost news score
        news_patterns = [
            'stock rebounds', 'stock surges', 'stock plunges', 
            'pares loss', 'pares gain', 'intraday',
            'after securing', 'after announcing', 'following',
            'here\'s why', 'this is why'
        ]
        for pattern in news_patterns:
            if pattern in text:
                scores['NEWS_ARTICLE'] += 1.5
        
        # If has "regulation 29" or "regulation 30", likely corporate action or result
        if 'regulation 29' in text or 'regulation 30' in text:
            # Check if it's a result or action
            if any(word in text for word in ['results', 'financial']):
                scores['QUARTERLY_RESULT'] += 1
            else:
                scores['CORPORATE_ACTION'] += 1
        
        # If attachment_text is very long (>5000 chars), likely transcript or detailed filing
        if len(attachment_text) > 5000:
            if scores['EARNINGS_CALL'] > 0:
                scores['EARNINGS_CALL'] += 1
        
        # If text contains "why" or question marks, likely news analysis
        if '?' in text or 'why' in text or 'here\'s' in text:
            scores['NEWS_ARTICLE'] += 1
        
        # PRIORITY RULE 3: If has stock movement language but also Q1/Q2/Q3/Q4, check context
        has_quarter_mention = any(q in text for q in ['q1', 'q2', 'q3', 'q4', 'quarter'])
        has_movement = any(m in text for m in ['rebounds', 'surges', 'plunges', 'pares', 'rises', 'falls'])
        
        if has_quarter_mention and has_movement and is_rss_news:
            # It's likely a news article ABOUT results, not the results themselves
            scores['NEWS_ARTICLE'] += 2
            scores['QUARTERLY_RESULT'] -= 1  # Reduce quarterly result score
            logger.debug("Quarter mention + movement language in RSS = NEWS_ARTICLE about results")
        
        # Determine winner
        max_score = max(scores.values())
        
        if max_score == 0:
            # No clear category, default to OTHER
            return "OTHER", 0.0
        
        winner = max(scores, key=scores.get)
        confidence = min(max_score / 8.0, 1.0)  # Normalize to 0-1 (adjusted denominator)
        
        logger.debug(f"Classification for '{description[:50]}...' | Source: {source}")
        logger.debug(f"Scores: {scores} -> {winner} (confidence: {confidence:.2f})")
        
        return winner, confidence
    
    @staticmethod
    def should_process(announcement_type: str) -> bool:
        """
        Determine if this announcement type should be processed
        
        Args:
            announcement_type: The classified type
            
        Returns:
            True if should process, False otherwise
        """
        # Process all types for now (can be configured later)
        return announcement_type in [
            'QUARTERLY_RESULT',
            'EARNINGS_CALL',
            'CORPORATE_ACTION',
            'NEWS_ARTICLE',
        ]

