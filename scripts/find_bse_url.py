#!/usr/bin/env python3
"""
Find the correct BSE announcements URL
"""
import asyncio
import aiohttp


BSE_URLS = [
    "https://www.bseindia.com/corporates/ann.aspx",
    "https://www.bseindia.com/corporates/corporate_announcements.html",
    "https://www.bseindia.com/stock-share-price/",
    "https://www.bseindia.com/markets/PublicIssues/corporate_announcements.aspx",
    "https://www.bseindia.com/corporates/Announcements.aspx",
    "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w",
    "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w",
]


async def test_url(url):
    """Test if URL is accessible"""
    print(f"\n🔗 Testing: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                status = resp.status
                content_type = resp.headers.get('Content-Type', 'unknown')
                
                if status == 200:
                    text = await resp.text()
                    print(f"  ✅ Status: {status} | Type: {content_type} | Size: {len(text)} bytes")
                    
                    # Quick content check
                    if 'error' in text.lower()[:500] or '404' in text[:500]:
                        print(f"  ⚠️  Content suggests error page")
                    else:
                        print(f"  🎯 LOOKS GOOD!")
                        print(f"  Snippet: {text[:200]}")
                    return True
                else:
                    print(f"  ❌ Status: {status}")
                    return False
                    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


async def main():
    print("="*80)
    print("🔍 FINDING CORRECT BSE ANNOUNCEMENTS URL")
    print("="*80)
    
    for url in BSE_URLS:
        await test_url(url)
        await asyncio.sleep(1)
    
    print("\n" + "="*80)
    print("✅ Search Complete")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())

