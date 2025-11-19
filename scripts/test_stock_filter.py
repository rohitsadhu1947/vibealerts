#!/usr/bin/env python3
"""
Test the stock filter
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.stock_filter import StockFilter


def test_stock_filter():
    """Test stock filtering logic"""
    
    # Mock config
    config = {
        'stock_filter': {
            'enabled': True,
            'bse_500_only': True,
            'nse_500_only': True,
            'allow_custom_watchlist': True,
            'custom_watchlist': ['534309', 'CUSTOM123', 'MYTCS']  # NBCC + custom stocks
        }
    }
    
    stock_filter = StockFilter(config)
    
    print("\n" + "="*80)
    print("🧪 STOCK FILTER TEST")
    print("="*80 + "\n")
    
    test_cases = [
        # BSE 500 stocks (should pass)
        ('534309', 'bse_library', True, 'NBCC - BSE 500 stock'),
        ('524735', 'bse_library', True, 'HIKAL - BSE 500 stock'),
        ('500325', 'bse_library', True, 'Reliance - BSE 500 stock'),
        
        # Custom watchlist (should pass)
        ('CUSTOM123', 'bse_library', True, 'Custom stock in watchlist'),
        ('MYTCS', 'nse_api', True, 'Custom NSE stock in watchlist'),
        
        # Not in BSE 500 or watchlist (should fail)
        ('999999', 'bse_library', False, 'Random penny stock - NOT in BSE 500'),
        ('123456', 'bse_library', False, 'Another penny stock'),
        
        # NSE 500 stocks (should pass)
        ('RELIANCE', 'nse_api', True, 'Reliance - NSE 500'),
        ('TCS', 'nse_api', True, 'TCS - NSE 500'),
        ('HIKAL', 'nse_api', True, 'HIKAL - NSE 500'),
        
        # RSS feeds (should always pass)
        ('ANYRANDOM', 'economic_times_rss', True, 'RSS feeds - always accepted'),
        ('WHATEVER', 'livemint_rss', True, 'RSS feeds - always accepted'),
    ]
    
    passed = 0
    failed = 0
    
    for symbol, source, should_pass, desc in test_cases:
        result = stock_filter.should_process(symbol, source)
        status = "✅" if result == should_pass else "❌ FAIL"
        actual = "PASS" if result else "REJECT"
        
        if result == should_pass:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {actual:6} | {symbol:12} ({source:20}) | {desc}")
    
    print("\n" + "="*80)
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80 + "\n")
    
    # Show filter stats
    print("Filter Statistics:")
    stats = stock_filter.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return failed == 0


if __name__ == "__main__":
    success = test_stock_filter()
    sys.exit(0 if success else 1)

