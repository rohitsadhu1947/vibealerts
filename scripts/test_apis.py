#!/usr/bin/env python3
"""
Test script to verify NSE/BSE API integration
Run this to check if the monitoring sources are working
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from pprint import pprint

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text):
    print(f"   {text}")


async def test_nse_api():
    """Test NSE corporate announcements API"""
    print_header("Testing NSE API")
    
    # NSE API endpoint
    url = "https://www.nseindia.com/api/corporate-announcements"
    
    # NSE requires specific headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.nseindia.com/',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    print_info(f"URL: {url}")
    print_info("Sending request...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # First, visit homepage to get cookies
            print_info("Getting session cookies from homepage...")
            async with session.get(
                "https://www.nseindia.com",
                headers={'User-Agent': headers['User-Agent']},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                print_info(f"Homepage response: {resp.status}")
            
            # Now try the API
            print_info("Fetching announcements...")
            async with session.get(
                url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                print_info(f"Response status: {resp.status}")
                
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        
                        if isinstance(data, list):
                            print_success(f"Successfully fetched {len(data)} announcements")
                            
                            # Look for quarterly results
                            result_keywords = ['financial result', 'quarterly result', 'unaudited financial']
                            results = []
                            
                            for item in data[:20]:  # Check first 20
                                desc = item.get('desc', '').lower()
                                if any(kw in desc for kw in result_keywords):
                                    results.append(item)
                            
                            if results:
                                print_success(f"Found {len(results)} potential quarterly results")
                                print_info("\nSample announcements:")
                                for i, item in enumerate(results[:3], 1):
                                    print(f"\n   {i}. {item.get('symbol', 'N/A')}")
                                    print(f"      Date: {item.get('an_dt', 'N/A')}")
                                    print(f"      Desc: {item.get('desc', 'N/A')[:80]}...")
                                    if item.get('attchmntFile'):
                                        print(f"      PDF: {item.get('attchmntFile', 'N/A')[:60]}...")
                            else:
                                print_warning("No quarterly results found in recent announcements")
                                print_info("This is normal if not during result season")
                            
                            return True
                        else:
                            print_warning(f"Unexpected response format: {type(data)}")
                            print_info(f"Response: {str(data)[:200]}")
                            return False
                            
                    except json.JSONDecodeError as e:
                        print_error(f"Failed to parse JSON: {e}")
                        text = await resp.text()
                        print_info(f"Response text: {text[:200]}")
                        return False
                        
                elif resp.status == 403:
                    print_error("Access forbidden (403)")
                    print_warning("NSE may be blocking automated requests")
                    print_info("Possible solutions:")
                    print_info("  1. Add more realistic headers")
                    print_info("  2. Use proxy/VPN")
                    print_info("  3. Increase delay between requests")
                    return False
                    
                else:
                    print_error(f"Failed with status: {resp.status}")
                    text = await resp.text()
                    print_info(f"Response: {text[:200]}")
                    return False
                    
    except asyncio.TimeoutError:
        print_error("Request timeout")
        print_info("NSE API may be slow or unreachable")
        return False
        
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


async def test_bse_api():
    """Test BSE announcements"""
    print_header("Testing BSE API")
    
    # BSE doesn't have a simple public API like NSE
    # We need to scrape or use alternative sources
    
    print_warning("BSE API integration is not fully implemented")
    print_info("BSE doesn't provide a simple public JSON API")
    print_info("\nAlternative approaches:")
    print_info("  1. Scrape BSE website: https://www.bseindia.com/corporates/ann.html")
    print_info("  2. Use RSS feeds if available")
    print_info("  3. Focus on NSE only for MVP (covers most major stocks)")
    
    return None


async def test_screener_rss():
    """Test Screener.in RSS feed as alternative source"""
    print_header("Testing Screener.in RSS Feed (Alternative)")
    
    url = "https://www.screener.in/api/results/rss/"
    
    print_info(f"URL: {url}")
    print_info("Checking if RSS feed is available...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                print_info(f"Response status: {resp.status}")
                
                if resp.status == 200:
                    text = await resp.text()
                    
                    if '<rss' in text.lower() or '<feed' in text.lower():
                        print_success("RSS feed is accessible")
                        print_info(f"Response size: {len(text)} bytes")
                        
                        # Count items
                        item_count = text.count('<item>') or text.count('<entry>')
                        print_success(f"Found {item_count} items in feed")
                        
                        return True
                    else:
                        print_warning("Response doesn't look like RSS/Atom feed")
                        print_info(f"Response: {text[:200]}")
                        return False
                else:
                    print_error(f"Failed with status: {resp.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


async def test_moneycontrol_rss():
    """Test MoneyControl RSS as alternative"""
    print_header("Testing MoneyControl Results (Alternative)")
    
    url = "https://www.moneycontrol.com/rss/results.xml"
    
    print_info(f"URL: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                print_info(f"Response status: {resp.status}")
                
                if resp.status == 200:
                    text = await resp.text()
                    
                    if '<rss' in text.lower():
                        print_success("RSS feed is accessible")
                        item_count = text.count('<item>')
                        print_success(f"Found {item_count} items")
                        return True
                    else:
                        print_warning("Not an RSS feed")
                        return False
                else:
                    print_error(f"Failed with status: {resp.status}")
                    return False
                    
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


async def main():
    """Run all API tests"""
    print(f"\n{BLUE}{'=' * 70}")
    print(f"🔍 Vibe Alerts - API Integration Test".center(70))
    print(f"{'=' * 70}{RESET}\n")
    
    results = {}
    
    # Test NSE (primary source)
    results['nse'] = await test_nse_api()
    
    # Test BSE (secondary source)
    results['bse'] = await test_bse_api()
    
    # Test alternative sources
    results['screener'] = await test_screener_rss()
    results['moneycontrol'] = await test_moneycontrol_rss()
    
    # Summary
    print_header("API Integration Summary")
    
    if results['nse']:
        print_success("NSE API: Working ✓")
    elif results['nse'] is False:
        print_error("NSE API: Failed ✗")
    
    if results['bse']:
        print_success("BSE API: Working ✓")
    elif results['bse'] is None:
        print_warning("BSE API: Not implemented (optional)")
    
    if results['screener']:
        print_success("Screener RSS: Working ✓ (good alternative)")
    else:
        print_warning("Screener RSS: Not accessible")
    
    if results['moneycontrol']:
        print_success("MoneyControl RSS: Working ✓ (good alternative)")
    else:
        print_warning("MoneyControl RSS: Not accessible")
    
    print(f"\n{BLUE}{'─' * 70}{RESET}\n")
    
    if results['nse']:
        print(f"{GREEN}✅ Primary source (NSE) is working!{RESET}")
        print(f"{GREEN}   You can proceed with the MVP.{RESET}\n")
        return 0
    elif any([results.get('screener'), results.get('moneycontrol')]):
        print(f"{YELLOW}⚠️  NSE API is not working, but alternative sources are available.{RESET}")
        print(f"{YELLOW}   Consider using RSS feeds as backup.{RESET}\n")
        return 0
    else:
        print(f"{RED}❌ No working data sources found.{RESET}")
        print(f"{RED}   NSE API integration needs debugging.{RESET}")
        print(f"\n{BLUE}Recommended actions:{RESET}")
        print(f"   1. Try again (NSE API can be temporarily down)")
        print(f"   2. Check if you're behind a firewall/proxy")
        print(f"   3. Consider implementing RSS feed parsers")
        print(f"   4. Focus on PDF extraction with manual URLs for testing\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}\n")
        exit(1)

