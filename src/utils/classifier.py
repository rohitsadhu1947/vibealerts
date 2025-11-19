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
    ]
    
    @staticmethod
    def classify(description: str, attachment_text: str = "") -> Tuple[str, float]:
        """
        Classify announcement type based on description and content
        
        Args:
            description: Announcement description/title
            attachment_text: Full text content (for RSS/news)
            
        Returns:
            Tuple of (announcement_type, confidence_score)
        """
        # Combine text for analysis
        text = (description + " " + attachment_text[:500]).lower()
        
        # Score each category
        scores = {
            'EARNINGS_CALL': 0,
            'CORPORATE_ACTION': 0,
            'NEWS_ARTICLE': 0,
            'QUARTERLY_RESULT': 0,
        }
        
        # Check for earnings call (highest priority after checking keywords)
        for keyword in AnnouncementClassifier.EARNINGS_CALL_KEYWORDS:
            if keyword in text:
                scores['EARNINGS_CALL'] += 2
        
        # Check for corporate actions
        for keyword in AnnouncementClassifier.CORPORATE_ACTION_KEYWORDS:
            if keyword in text:
                scores['CORPORATE_ACTION'] += 1.5
        
        # Check for news articles
        for keyword in AnnouncementClassifier.NEWS_KEYWORDS:
            if keyword in text:
                scores['NEWS_ARTICLE'] += 1.5
        
        # Check for quarterly results
        for keyword in AnnouncementClassifier.QUARTERLY_RESULT_KEYWORDS:
            if keyword in text:
                scores['QUARTERLY_RESULT'] += 1
        
        # Additional heuristics
        
        # If from news sources, likely news article
        if any(word in text for word in ['livemint', 'economic times', 'et markets', 'moneycontrol']):
            scores['NEWS_ARTICLE'] += 2
        
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
        
        # Determine winner
        max_score = max(scores.values())
        
        if max_score == 0:
            # No clear category, default to OTHER
            return "OTHER", 0.0
        
        winner = max(scores, key=scores.get)
        confidence = min(max_score / 5.0, 1.0)  # Normalize to 0-1
        
        logger.debug(f"Classification scores: {scores} -> {winner} ({confidence:.2f})")
        
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

