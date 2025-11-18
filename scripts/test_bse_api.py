#!/usr/bin/env python3
"""
Test BSE page with actual browser simulation to see real data
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def test_bse_with_params():
    """Test BSE with various parameters"""
    
    # BSE Corporate Announcements page
    base_url = "https://www.bseindia.com/corporates/ann.aspx"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print("="*80)
    print("🔍 TESTING BSE ANNOUNCEMENTS ACCESS")
    print("="*80)
    
    async with aiohttp.ClientSession() as session:
        # First, visit homepage to get cookies
        print("\n1️⃣  Visiting BSE homepage...")
        async with session.get('https://www.bseindia.com/', headers=headers) as resp:
            print(f"   Status: {resp.status}")
        
        await asyncio.sleep(1)
        
        # Now try announcements page
        print("\n2️⃣  Visiting announcements page...")
        async with session.get(base_url, headers=headers) as resp:
            html = await resp.text()
            print(f"   Status: {resp.status}")
            print(f"   Size: {len(html)} bytes")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for the actual data table or AJAX endpoint
            print("\n3️⃣  Analyzing page structure...")
            
            # Find all script tags that might load data
            scripts = soup.find_all('script')
            print(f"   Found {len(scripts)} script tags")
            
            # Look for AJAX URLs
            ajax_urls = []
            for script in scripts:
                if script.string:
                    # Look for common AJAX patterns
                    if 'GetData' in script.string or 'ajax' in script.string.lower():
                        print(f"\n   📡 Found AJAX-related script:")
                        print(f"   {script.string[:500]}")
                        ajax_urls.append(script.string)
            
            # Check if there's a form we need to submit
            forms = soup.find_all('form')
            if forms:
                print(f"\n   📝 Found {len(forms)} forms")
                for i, form in enumerate(forms[:2]):
                    print(f"   Form {i+1}:")
                    print(f"     Action: {form.get('action', 'N/A')}")
                    print(f"     Method: {form.get('method', 'GET')}")
                    print(f"     ID: {form.get('id', 'N/A')}")
    
    # Try direct API endpoints
    print("\n4️⃣  Testing BSE API endpoints...")
    
    api_endpoints = [
        "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=-1&strPrevDate=20251117&strScrip=&strSearch=P&strToDate=20251118&strType=C",
        "https://api.bseindia.com/BseIndiaAPI/api/DefaultData/w",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in api_endpoints:
            print(f"\n   Testing: {endpoint}")
            try:
                async with session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    print(f"   Status: {resp.status}")
                    if resp.status == 200:
                        text = await resp.text()
                        print(f"   Size: {len(text)} bytes")
                        
                        # Try to parse as JSON
                        try:
                            import json
                            data = json.loads(text)
                            print(f"   ✅ Valid JSON!")
                            print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                            if isinstance(data, dict) and 'Table' in data:
                                print(f"   📊 Found {len(data['Table'])} records in Table")
                                if data['Table']:
                                    print(f"   Sample record: {data['Table'][0]}")
                        except:
                            print(f"   Not JSON, HTML/Text response")
                            print(f"   Snippet: {text[:300]}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80)


async def main():
    await test_bse_with_params()


if __name__ == "__main__":
    asyncio.run(main())

