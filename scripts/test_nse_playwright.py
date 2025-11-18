#!/usr/bin/env python3
"""
NSE Corporate Announcements Scraper using Playwright
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging import setup_logging

logger = setup_logging()


async def scrape_nse_announcements():
    """Scrape NSE corporate announcements using Playwright"""
    
    print("\n" + "="*80)
    print("🎭 NSE PLAYWRIGHT SCRAPER TEST")
    print("="*80)
    
    async with async_playwright() as p:
        print("\n1️⃣  Launching headless browser (with stealth mode)...")
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='Asia/Kolkata',
            extra_http_headers={
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Add script to mask automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
        """)
        
        page = await context.new_page()
        
        try:
            # Visit NSE homepage first to get cookies
            print("2️⃣  Visiting NSE homepage...")
            await page.goto('https://www.nseindia.com/', wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)
            
            # Now visit the corporate announcements page
            print("3️⃣  Navigating to Corporate Announcements...")
            await page.goto(
                'https://www.nseindia.com/companies-listing/corporate-filings-financial-results',
                wait_until='networkidle',
                timeout=30000
            )
            await asyncio.sleep(3)
            
            print("4️⃣  Waiting for data to load...")
            
            # Take a screenshot for debugging
            await page.screenshot(path='logs/nse_page.png')
            print("   📸 Screenshot saved to logs/nse_page.png")
            
            # Get page content
            content = await page.content()
            print(f"   📄 Page content size: {len(content)} bytes")
            
            # Try to find the announcements table/section
            print("\n5️⃣  Looking for announcements...")
            
            # Method 1: Look for common table selectors
            table_selectors = [
                'table',
                '[role="grid"]',
                '[role="table"]',
                '.table',
                '#cr-table',
                '.dataTable'
            ]
            
            for selector in table_selectors:
                tables = await page.query_selector_all(selector)
                if tables:
                    print(f"   ✅ Found {len(tables)} elements with selector: {selector}")
                    
                    # Try to extract text from first table
                    if tables:
                        first_table = tables[0]
                        text = await first_table.inner_text()
                        print(f"   📊 First table content ({len(text)} chars):")
                        print(f"   {text[:500]}")
            
            # Method 2: Look for API calls made by the page
            print("\n6️⃣  Intercepting network requests...")
            
            # Reload page with request interception
            requests = []
            
            def handle_request(request):
                if 'api' in request.url.lower() or 'announcement' in request.url.lower():
                    requests.append(request.url)
                    print(f"   📡 API Call: {request.url}")
            
            page.on('request', handle_request)
            
            await page.reload(wait_until='networkidle')
            await asyncio.sleep(3)
            
            if requests:
                print(f"\n   Found {len(requests)} API requests!")
                print("   Most promising endpoints:")
                for req in requests[:5]:
                    print(f"   - {req}")
            
            # Method 3: Try to execute JavaScript to get data
            print("\n7️⃣  Trying to extract data via JavaScript...")
            
            try:
                # Try to find React/Angular data store
                data = await page.evaluate('''() => {
                    // Try common data storage locations
                    if (window.__INITIAL_STATE__) return window.__INITIAL_STATE__;
                    if (window.__DATA__) return window.__DATA__;
                    if (window.tableData) return window.tableData;
                    
                    // Try to find table rows
                    const rows = document.querySelectorAll('tr');
                    if (rows.length > 0) {
                        return Array.from(rows).slice(0, 10).map(row => row.innerText);
                    }
                    
                    return null;
                }''')
                
                if data:
                    print(f"   ✅ Extracted data:")
                    print(f"   {data}")
                else:
                    print(f"   ⚠️  No data found via JavaScript")
                    
            except Exception as e:
                print(f"   ❌ JavaScript error: {e}")
            
            # Save full HTML for analysis
            with open('logs/nse_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("\n   💾 Full HTML saved to logs/nse_page.html")
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            print(f"\n❌ Error: {e}")
        
        finally:
            await browser.close()
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80 + "\n")


async def main():
    await scrape_nse_announcements()


if __name__ == "__main__":
    asyncio.run(main())

