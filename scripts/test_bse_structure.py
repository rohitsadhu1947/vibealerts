#!/usr/bin/env python3
"""
Test BSE announcements page to understand structure
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re


async def test_bse_page():
    """Fetch and analyze BSE announcements page"""
    url = "https://www.bseindia.com/corporates/ann.aspx"
    
    print("\n" + "="*80)
    print("🔍 ANALYZING BSE ANNOUNCEMENTS PAGE")
    print("="*80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            html = await resp.text()
            
    print(f"✅ Fetched {len(html)} bytes")
    
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    print("\n📊 Page Structure Analysis:")
    print(f"  Title: {soup.title.string if soup.title else 'N/A'}")
    
    # Look for common patterns
    print("\n🔍 Looking for announcement patterns...")
    
    # Find tables
    tables = soup.find_all('table')
    print(f"\n  Found {len(tables)} tables")
    
    # Find forms (might need to submit to get data)
    forms = soup.find_all('form')
    print(f"  Found {len(forms)} forms")
    
    # Check for JavaScript that loads data
    scripts = soup.find_all('script')
    print(f"  Found {len(scripts)} script tags")
    
    # Look for specific keywords in the HTML
    result_keywords = ['announcement', 'result', 'quarter', 'financial']
    for keyword in result_keywords:
        count = html.lower().count(keyword)
        if count > 0:
            print(f"  Keyword '{keyword}': {count} occurrences")
    
    # Try to find announcement-related elements
    print("\n🎯 Searching for announcement elements...")
    
    # Common class/id patterns
    patterns = [
        'announcement', 'ann', 'corporate', 'result', 
        'table', 'grid', 'data', 'content'
    ]
    
    for pattern in patterns:
        # Search by class
        elements = soup.find_all(class_=re.compile(pattern, re.I))
        if elements:
            print(f"  Found {len(elements)} elements with class containing '{pattern}'")
            
        # Search by id
        elements = soup.find_all(id=re.compile(pattern, re.I))
        if elements:
            print(f"  Found {len(elements)} elements with id containing '{pattern}'")
    
    # Check if page is dynamically loaded (AJAX)
    if 'ajax' in html.lower() or 'api' in html.lower():
        print("\n⚠️  Page appears to use AJAX/API for loading data")
        
    # Look for API endpoints in scripts
    print("\n🔌 Looking for API endpoints in JavaScript...")
    api_patterns = [
        r'api[/\w\-]*',
        r'/xml-data/[\w\-/]+',
        r'\.ashx[\w\-?=&]*',
        r'\.aspx[\w\-?=&]*'
    ]
    
    for script in scripts:
        if script.string:
            for pattern in api_patterns:
                matches = re.findall(pattern, script.string, re.I)
                if matches:
                    unique_matches = set(matches)
                    for match in list(unique_matches)[:5]:  # Show max 5
                        print(f"  Found: {match}")
    
    # Save sample HTML for inspection
    print("\n💾 Saving sample HTML...")
    with open('/Users/rohit/Vibe_Alerts/logs/bse_sample.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("  Saved to: logs/bse_sample.html")
    
    # Show a snippet of the body
    print("\n📝 Body Content Snippet (first 1000 chars):")
    body = soup.body
    if body:
        print(body.get_text()[:1000])
    
    print("\n" + "="*80)
    print("✅ Analysis Complete!")
    print("="*80)


async def main():
    await test_bse_page()


if __name__ == "__main__":
    asyncio.run(main())

