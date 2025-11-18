#!/usr/bin/env python3
"""
Find ACTUAL corporate quarterly result announcement sources
"""
import asyncio
import aiohttp
import feedparser
from datetime import datetime


SOURCES = {
    "BSE Announcements": "https://www.bseindia.com/corporates/ann.aspx",
    "NSE Corporate Actions": "https://www.nseindia.com/companies-listing/corporate-filings-financial-results",
    "MoneyControl Results RSS": "https://www.moneycontrol.com/rss/results.xml",
    "MoneyControl Latest News": "https://www.moneycontrol.com/rss/latestnews.xml", 
    "Screener Latest Results": "https://www.screener.in/api/company/latest-results/",
    "BSE Corp Announcements XML": "https://www.bseindia.com/xml-data/corpfiling/announcement/NewTicker_announce.xml",
}


async def test_source(name: str, url: str):
    """Test a single source"""
    print(f"\n{'='*80}")
    print(f"📡 Testing: {name}")
    print(f"🔗 URL: {url}")
    print(f"{'='*80}")
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                status = resp.status
                content_type = resp.headers.get('Content-Type', 'unknown')
                
                print(f"✅ Status: {status}")
                print(f"📄 Content-Type: {content_type}")
                
                if status == 200:
                    text = await resp.text()
                    print(f"📊 Content Length: {len(text)} bytes")
                    
                    # Try to parse as RSS/XML
                    if 'xml' in content_type.lower() or 'rss' in url.lower():
                        feed = feedparser.parse(text)
                        if feed.entries:
                            print(f"📰 RSS Feed Entries: {len(feed.entries)}")
                            print(f"\n🔍 First 3 entries:")
                            for i, entry in enumerate(feed.entries[:3], 1):
                                print(f"\n  --- Entry {i} ---")
                                print(f"  Title: {entry.get('title', 'N/A')[:100]}")
                                print(f"  Published: {entry.get('published', 'N/A')}")
                                title_lower = entry.get('title', '').lower()
                                if any(kw in title_lower for kw in ['q1', 'q2', 'q3', 'q4', 'quarter', 'result', 'fy']):
                                    print(f"  🎯 RESULT KEYWORDS FOUND!")
                    
                    # Show snippet
                    print(f"\n📝 Content Snippet (first 500 chars):")
                    print(text[:500])
                else:
                    print(f"❌ Failed with status {status}")
                    
    except asyncio.TimeoutError:
        print(f"⏰ TIMEOUT after 30s")
    except Exception as e:
        print(f"❌ ERROR: {e}")


async def main():
    """Test all sources"""
    print("\n" + "="*80)
    print("🚀 FINDING ACTUAL CORPORATE RESULT ANNOUNCEMENT SOURCES")
    print("="*80)
    
    for name, url in SOURCES.items():
        await test_source(name, url)
        await asyncio.sleep(2)  # Be nice to servers
    
    print("\n" + "="*80)
    print("✅ All tests complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

