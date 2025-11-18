#!/usr/bin/env python3
"""
Test script to see detailed RSS feed data and understand what's being fetched
"""
import asyncio
import aiohttp
import feedparser
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging import setup_logging

logger = setup_logging()


async def test_economic_times():
    """Test Economic Times RSS feed in detail"""
    url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    
    print("\n" + "="*80)
    print("📰 ECONOMIC TIMES MARKETS RSS FEED")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            content = await response.text()
            
    feed = feedparser.parse(content)
    
    print(f"\n✅ Feed Status: {feed.get('status', 'unknown')}")
    print(f"📊 Total Entries: {len(feed.entries)}")
    
    if feed.entries:
        print(f"\n🔍 First 10 entries:\n")
        for i, entry in enumerate(feed.entries[:10], 1):
            print(f"\n--- Entry {i} ---")
            print(f"Title: {entry.get('title', 'N/A')}")
            print(f"Link: {entry.get('link', 'N/A')}")
            print(f"Published: {entry.get('published', 'N/A')}")
            
            # Check if it contains result keywords
            title_lower = entry.get('title', '').lower()
            keywords = ['result', 'quarter', 'q1', 'q2', 'q3', 'q4', 'fy', 
                       'profit', 'revenue', 'earnings', 'financial']
            matches = [kw for kw in keywords if kw in title_lower]
            
            if matches:
                print(f"🎯 RESULT KEYWORDS FOUND: {', '.join(matches)}")
            else:
                print(f"⚠️  No result keywords found")
            
            print(f"Description: {entry.get('description', 'N/A')[:200]}...")


async def test_livemint():
    """Test Livemint RSS feed in detail"""
    url = "https://www.livemint.com/rss/markets"
    
    print("\n" + "="*80)
    print("📰 LIVEMINT MARKETS RSS FEED")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            content = await response.text()
            
    feed = feedparser.parse(content)
    
    print(f"\n✅ Feed Status: {feed.get('status', 'unknown')}")
    print(f"📊 Total Entries: {len(feed.entries)}")
    
    if feed.entries:
        print(f"\n🔍 First 10 entries:\n")
        for i, entry in enumerate(feed.entries[:10], 1):
            print(f"\n--- Entry {i} ---")
            print(f"Title: {entry.get('title', 'N/A')}")
            print(f"Link: {entry.get('link', 'N/A')}")
            print(f"Published: {entry.get('published', 'N/A')}")
            
            # Check if it contains result keywords
            title_lower = entry.get('title', '').lower()
            keywords = ['result', 'quarter', 'q1', 'q2', 'q3', 'q4', 'fy', 
                       'profit', 'revenue', 'earnings', 'financial']
            matches = [kw for kw in keywords if kw in title_lower]
            
            if matches:
                print(f"🎯 RESULT KEYWORDS FOUND: {', '.join(matches)}")
            else:
                print(f"⚠️  No result keywords found")
            
            print(f"Description: {entry.get('description', 'N/A')[:200]}...")


async def main():
    """Main test function"""
    print("\n🚀 Testing RSS Feeds for Result Announcements\n")
    
    await test_economic_times()
    await test_livemint()
    
    print("\n" + "="*80)
    print("✅ Test Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

