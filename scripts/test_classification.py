#!/usr/bin/env python3
"""
Test the announcement classifier with real examples
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.classifier import AnnouncementClassifier

# Test cases
test_cases = [
    {
        "description": "EV Q3 FY2025 Results",
        "text": "Solar, EV stock Servotech Power pares intraday loss after this order book update. Servotech Power's stock rebounded 3% to ₹97.95 after securing a ₹73.70 crore rooftop solar project",
        "source": "economic_times_rss",
        "expected": "NEWS_ARTICLE"
    },
    {
        "description": "Transcript of Earnings group call for quarter and the half year ended September 30, 2025",
        "text": "Dear Sir/Madam, In continuation to our letters dated November 10, 2025 and November 13, 2025...",
        "source": "bse_library",
        "expected": "EARNINGS_CALL"
    },
    {
        "description": "Disclosure under Regulation 29(2) of SEBI for M/S GOPAL IRON & STEELS COMPANY",
        "text": "With Reference to captioned subject, Please Find attached herewith a copy of disclosure as required under Regulation 29(2) of SEBI (Substantial Acquisition of Shares and Takeovers)",
        "source": "bse_library",
        "expected": "CORPORATE_ACTION"
    },
    {
        "description": "Unaudited Financial Results for Q2 FY2026",
        "text": "The Board of Directors at their meeting held today have approved the Unaudited Financial Results for the quarter ended September 30, 2025. Revenue: 319 Cr, PAT: 52 Cr",
        "source": "bse_library",
        "expected": "QUARTERLY_RESULT"
    },
    {
        "description": "SBI Life-owned NBFC stock rebounds 3% from today's low; here's why",
        "text": "Paisalo Digital's stock rebounded over 3% to ₹33.59 after announcing a fund-raising proposal via Non-Convertible Debentures. The company recently reported a 13.5% rise in Q2 net profit to ₹52 crore",
        "source": "livemint_rss",
        "expected": "NEWS_ARTICLE"
    }
]

print("\n" + "="*80)
print("🧪 ANNOUNCEMENT CLASSIFIER TEST")
print("="*80 + "\n")

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    result, confidence = AnnouncementClassifier.classify(
        test["description"],
        test["text"],
        test["source"]
    )
    
    is_correct = result == test["expected"]
    status = "✅ PASS" if is_correct else "❌ FAIL"
    
    if is_correct:
        passed += 1
    else:
        failed += 1
    
    print(f"Test {i}: {status}")
    print(f"  Description: {test['description'][:60]}...")
    print(f"  Source: {test['source']}")
    print(f"  Expected: {test['expected']}")
    print(f"  Got: {result} (confidence: {confidence:.2f})")
    print()

print("="*80)
print(f"📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print("="*80 + "\n")

