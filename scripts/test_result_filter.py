#!/usr/bin/env python3
"""
Test the quarterly result filter
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def is_quarterly_result(text: str) -> bool:
    """Check if announcement is quarterly result (copied from service.py)"""
    text_lower = text.lower()
    
    # FIRST: Filter out administrative/non-actionable announcements
    exclude_keywords = [
        'newspaper publication',
        'newspaper advertisement',
        'published in newspaper',
        'publication of financial results',
        'newspaper notice',
        'press release publication',
        'advertisement in newspaper',
        'notice published in',
        'copy of newspaper',
        'intimation of newspaper publication',
        'submission of newspaper',
        'compliance certificate',
        'record date',
        'book closure',
        'agm notice',
        'egm notice',
        'intimation of loss of share certificate',
        'duplicate share certificate',
        'postal ballot',
        'e-voting',
    ]
    
    # If it's an administrative notice, reject immediately
    if any(kw in text_lower for kw in exclude_keywords):
        return False
    
    # SECOND: Check if it's an actual result announcement
    keywords = [
        'financial result', 'financial results',
        'quarterly result', 'quarterly results',
        'unaudited financial', 'unaudited results',
        'audited results', 'standalone results',
        'q1', 'q2', 'q3', 'q4',
        'quarter ended', 'half year ended',
        'fy20', 'fy21', 'fy22', 'fy23', 'fy24', 'fy25', 'fy26',
        'outcome of board meeting',
        'submission of financial results',
    ]
    return any(kw in text_lower for kw in keywords)


def test_filter():
    """Test result filtering"""
    
    test_cases = [
        # Should PASS (actual results)
        ("Unaudited Financial Results for quarter ended 30.09.2025", True),
        ("Q2 FY2026 Results - Board Meeting Outcome", True),
        ("Submission of Financial Results for Q3 FY2025", True),
        ("Quarterly and Half Year Results", True),
        ("Approved Unaudited Standalone Results", True),
        
        # Should FAIL (administrative notices)
        ("Newspaper publications: Unaudited Financial Results for quarter ended 30.09.2025", False),
        ("Publication of Financial Results in Newspaper", False),
        ("Copy of newspaper advertisement - Q2 Results", False),
        ("Intimation of newspaper publication", False),
        ("AGM Notice - Annual General Meeting", False),
        ("Book Closure - Record Date Announcement", False),
        ("E-voting facility for shareholders", False),
        ("Loss of Share Certificate - Duplicate Issue", False),
    ]
    
    print("\n" + "="*80)
    print("🧪 QUARTERLY RESULT FILTER TEST")
    print("="*80 + "\n")
    
    passed = 0
    failed = 0
    
    for text, should_pass in test_cases:
        result = is_quarterly_result(text)
        expected = "✅ PASS" if should_pass else "❌ REJECT"
        actual = "PASS" if result else "REJECT"
        status = "✅" if result == should_pass else "⚠️ FAIL"
        
        if result == should_pass:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} Expected: {expected:10} | Got: {actual:6} | {text[:60]}...")
    
    print("\n" + "="*80)
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80 + "\n")
    
    if failed > 0:
        print("⚠️  Some tests failed!")
        return False
    else:
        print("✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = test_filter()
    sys.exit(0 if success else 1)

