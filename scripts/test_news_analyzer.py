#!/usr/bin/env python3
"""
Test the news analyzer with real examples
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.news_analyzer import NewsAnalyzer

# Test cases
test_cases = [
    {
        "title": "Solar, EV stock Servotech Power pares intraday loss after this order book update",
        "content": "Servotech Power's stock rebounded 3% to ₹97.95 after securing a ₹73.70 crore rooftop solar project from NREDCAP in Andhra Pradesh. The initiative aims to provide clean energy to 5,886 households.",
        "expected_sentiment": "Bullish",
        "expected_actionability_level": "Medium"
    },
    {
        "title": "SBI Life-owned NBFC stock rebounds 3% from today's low; here's why",
        "content": "Paisalo Digital's stock rebounded over 3% to ₹33.59 after announcing a fund-raising proposal via Non-Convertible Debentures. The company recently reported a 13.5% rise in Q2 net profit to ₹52 crore.",
        "expected_sentiment": "Bullish",
        "expected_actionability_level": "Medium"
    },
    {
        "title": "Tech stock plunges 8% after disappointing quarterly results",
        "content": "Shares of TechCorp fell 8% to ₹245 after the company reported a 15% decline in revenue to ₹180 crore, missing analyst estimates. The management cited weak demand and pricing pressure.",
        "expected_sentiment": "Bearish",
        "expected_actionability_level": "High"
    },
    {
        "title": "Major pharma company announces acquisition of smaller rival for ₹1,200 crore",
        "content": "PharmaCo announced the acquisition of GenericDrugs for ₹1,200 crore in an all-cash deal. The acquisition will expand PharmaCo's product portfolio and manufacturing capacity.",
        "expected_sentiment": "Bullish",
        "expected_actionability_level": "High"
    },
    {
        "title": "Auto stock rises 2% on strong export numbers",
        "content": "AutoMakers Limited rose 2% to ₹580 after reporting a 25% increase in export volumes for October. The company has been focusing on international markets.",
        "expected_sentiment": "Slightly Bullish",
        "expected_actionability_level": "Low"
    }
]

print("\n" + "="*80)
print("🧪 NEWS ANALYZER TEST")
print("="*80 + "\n")

for i, test in enumerate(test_cases, 1):
    insights = NewsAnalyzer.analyze(test["title"], test["content"])
    
    print(f"Test {i}: {test['title'][:60]}...")
    print(f"  {insights['sentiment_emoji']} Sentiment: {insights['sentiment']}")
    
    if insights['price_movement']:
        print(f"  📈 Price: {insights['price_movement']}")
    
    if insights['key_action']:
        print(f"  🎯 Trigger: {insights['key_action']}")
    
    print(f"  📊 Actionability: {insights['actionability']}")
    print(f"  💡 Summary: {insights['summary'][:80]}...")
    print()

print("="*80)
print("✅ All tests completed!")
print("="*80 + "\n")

# Show a formatted alert example
print("\n" + "="*80)
print("📱 EXAMPLE TELEGRAM ALERT FORMAT")
print("="*80 + "\n")

example = test_cases[0]
insights = NewsAnalyzer.analyze(example["title"], example["content"])

alert = f"""📰 **EV - Market News**

{insights['sentiment_emoji']} **Sentiment:** {insights['sentiment']}
📈 **Price:** {insights['price_movement']}
🎯 **Trigger:** {insights['key_action']}

**Summary:**
{insights['summary']}

**{insights['actionability']}**

⏱️ Detected in 0.1s"""

print(alert)
print("\n" + "="*80 + "\n")

