#!/usr/bin/env python3
"""
Test MoneyControl RSS feed directly
"""

import asyncio
import aiohttp
from xml.etree import ElementTree as ET

async def test_moneycontrol_rss():
    """Test if MoneyControl RSS is accessible and has data"""
    
    url = "https://www.moneycontrol.com/rss/results.xml"
    
    print("\n" + "="*70)
    print("🔍 Testing MoneyControl RSS Feed")
    print("="*70 + "\n")
    
    print(f"URL: {url}\n")
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📡 Fetching RSS feed...")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                print(f"Status: {resp.status}")
                
                if resp.status == 200:
                    text = await resp.text()
                    print(f"✅ Response received: {len(text)} bytes\n")
                    
                    # Parse XML
                    root = ET.fromstring(text)
                    
                    # Find all items
                    items = root.findall('.//item')
                    print(f"📊 Found {len(items)} items in feed\n")
                    
                    if items:
                        print("Recent items:")
                        print("-" * 70)
                        for i, item in enumerate(items[:5], 1):
                            title = item.find('title').text if item.find('title') is not None else 'No title'
                            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else 'No date'
                            
                            print(f"\n{i}. {title}")
                            print(f"   Date: {pub_date}")
                            
                            # Check if it's a quarterly result
                            if any(kw in title.lower() for kw in ['result', 'quarter', 'q1', 'q2', 'q3', 'q4']):
                                print(f"   ✅ Looks like a quarterly result!")
                        
                        print("\n" + "-" * 70)
                        print(f"\n✅ MoneyControl RSS is working and has data!")
                        
                    else:
                        print("⚠️  RSS feed has no items")
                        
                else:
                    print(f"❌ HTTP {resp.status}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_moneycontrol_rss())

