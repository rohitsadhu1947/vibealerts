#!/usr/bin/env python3
"""
Test multiple RSS feeds to find working ones
"""

import asyncio
import aiohttp
from xml.etree import ElementTree as ET
from datetime import datetime

FEEDS_TO_TEST = [
    {
        'name': 'MoneyControl Results',
        'url': 'https://www.moneycontrol.com/rss/results.xml'
    },
    {
        'name': 'Economic Times Markets',
        'url': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms'
    },
    {
        'name': 'Economic Times Earnings',
        'url': 'https://economictimes.indiatimes.com/markets/earnings/rssfeeds/58147724.cms'
    },
    {
        'name': 'Business Standard Results',
        'url': 'https://www.business-standard.com/rss/results-117.rss'
    },
    {
        'name': 'Livemint Markets',
        'url': 'https://www.livemint.com/rss/markets'
    },
    {
        'name': 'NDTV Profit Markets',
        'url': 'https://www.ndtvprofit.com/rss/markets'
    }
]

async def test_feed(feed_info):
    """Test a single RSS feed"""
    
    name = feed_info['name']
    url = feed_info['url']
    
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('-'*70)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    print(f"❌ HTTP {resp.status}")
                    return {'name': name, 'status': 'failed', 'reason': f'HTTP {resp.status}'}
                
                text = await resp.text()
                
                # Try to parse as XML
                try:
                    root = ET.fromstring(text)
                except:
                    print(f"❌ Not valid XML")
                    return {'name': name, 'status': 'failed', 'reason': 'Invalid XML'}
                
                # Find items
                items = root.findall('.//item')
                
                if not items:
                    print(f"⚠️  No items found")
                    return {'name': name, 'status': 'empty', 'items': 0}
                
                print(f"✅ Found {len(items)} items")
                
                # Check dates of recent items
                recent_dates = []
                for item in items[:5]:
                    pub_date = item.find('pubDate')
                    if pub_date is not None and pub_date.text:
                        recent_dates.append(pub_date.text)
                        title = item.find('title')
                        title_text = title.text if title is not None else 'No title'
                        print(f"   - {title_text[:60]}...")
                        print(f"     Date: {pub_date.text}")
                
                if recent_dates:
                    print(f"\n✅ WORKING - Has recent items!")
                    return {'name': name, 'status': 'working', 'items': len(items), 'dates': recent_dates[:3]}
                else:
                    print(f"⚠️  No dates found")
                    return {'name': name, 'status': 'no_dates', 'items': len(items)}
                
    except asyncio.TimeoutError:
        print(f"❌ Timeout")
        return {'name': name, 'status': 'timeout'}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {'name': name, 'status': 'error', 'reason': str(e)}

async def main():
    """Test all feeds"""
    
    print("\n" + "="*70)
    print("🔍 Testing RSS Feeds for Indian Stock Market Results")
    print(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    print("="*70)
    
    results = []
    for feed in FEEDS_TO_TEST:
        result = await test_feed(feed)
        results.append(result)
        await asyncio.sleep(1)  # Be nice to servers
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70 + "\n")
    
    working = [r for r in results if r.get('status') == 'working']
    failed = [r for r in results if r.get('status') in ['failed', 'timeout', 'error']]
    empty = [r for r in results if r.get('status') in ['empty', 'no_dates']]
    
    if working:
        print("✅ WORKING FEEDS:")
        for r in working:
            print(f"   • {r['name']} ({r.get('items', 0)} items)")
    else:
        print("❌ No working feeds found!")
    
    if empty:
        print("\n⚠️  EMPTY/STALE FEEDS:")
        for r in empty:
            print(f"   • {r['name']}")
    
    if failed:
        print("\n❌ FAILED FEEDS:")
        for r in failed:
            print(f"   • {r['name']}")
    
    print("\n" + "="*70)
    
    if working:
        print(f"\n🎯 Recommendation: Use {len(working)} working feed(s) for your app")
    else:
        print("\n⚠️  CRITICAL: No RSS feeds are working!")
        print("    Recommendation: Implement web scraping for NSE/BSE")

if __name__ == "__main__":
    asyncio.run(main())

