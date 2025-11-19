"""
Stock Universe Filter
Filters stocks by index membership (BSE 500, NSE 500) and custom watchlists
"""

from typing import Set, Optional
from loguru import logger


class StockFilter:
    """Filters stocks based on index membership and custom watchlists"""
    
    # BSE 500 scrip codes (top 500 stocks by market cap)
    # This is a representative sample - full list should be updated periodically
    BSE_500_SCRIP_CODES = {
        # Large caps (top 100)
        '500325', '500209', '500180', '532174', '500112', '532215', '500103',
        '500034', '532540', '532454', '532555', '500087', '532977', '500010',
        '532187', '500696', '532712', '500875', '532281', '532286',
        
        # Mid caps (101-250)
        '533155', '532478', '500440', '532234', '532755', '533278', '532313',
        '532921', '532438', '532869', '532129', '532689', '532898', '532622',
        
        # Small caps (251-500)
        '533274', '532926', '534309',  # NBCC - your example
        '524735',  # HIKAL
        '531913',  # GOPAL IRON
        '507552',  # FOODSIN
        
        # Add more as needed - this should be regularly updated
    }
    
    # NSE symbols for NSE 500
    NSE_500_SYMBOLS = {
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ICICIBANK',
        'KOTAKBANK', 'LT', 'SBIN', 'BHARTIARTL', 'ASIANPAINT', 'ITC',
        'AXISBANK', 'BAJFINANCE', 'MARUTI', 'TITAN', 'WIPRO', 'ULTRACEMCO',
        'SUNPHARMA', 'NESTLEIND', 'POWERGRID', 'NTPC', 'ONGC', 'JSWSTEEL',
        'TATASTEEL', 'TATAMOTORS', 'COALINDIA', 'ADANIPORTS', 'M&M', 'GRASIM',
        'HIKAL', 'NBCC',  # Add more
    }
    
    def __init__(self, config: dict):
        """
        Initialize stock filter
        
        Args:
            config: Configuration dict with filtering settings
        """
        self.config = config
        self.custom_watchlist: Set[str] = set()
        self.load_custom_watchlist()
        
        # Filter settings
        self.filter_enabled = config.get('stock_filter', {}).get('enabled', True)
        self.bse_500_only = config.get('stock_filter', {}).get('bse_500_only', True)
        self.nse_500_only = config.get('stock_filter', {}).get('nse_500_only', True)
        self.allow_custom = config.get('stock_filter', {}).get('allow_custom_watchlist', True)
        
        logger.info(
            f"Stock filter initialized: "
            f"Enabled={self.filter_enabled}, "
            f"BSE500={self.bse_500_only}, "
            f"NSE500={self.nse_500_only}, "
            f"Custom={len(self.custom_watchlist)} stocks"
        )
    
    def load_custom_watchlist(self):
        """Load custom watchlist from config"""
        watchlist = self.config.get('stock_filter', {}).get('custom_watchlist', [])
        self.custom_watchlist = set(str(s).strip().upper() for s in watchlist if s)
        
        if self.custom_watchlist:
            logger.info(f"Loaded custom watchlist: {sorted(self.custom_watchlist)}")
    
    def should_process(self, symbol: str, source: str) -> bool:
        """
        Check if stock should be processed based on filters
        
        Args:
            symbol: Stock symbol/scrip code
            source: Source of announcement (e.g., 'bse_library', 'nse_api')
            
        Returns:
            True if stock should be processed, False otherwise
        """
        # If filtering is disabled, process everything
        if not self.filter_enabled:
            return True
        
        symbol_upper = symbol.strip().upper()
        
        # Check custom watchlist first (highest priority)
        if self.allow_custom and symbol_upper in self.custom_watchlist:
            logger.debug(f"✅ {symbol} in custom watchlist")
            return True
        
        # Check BSE 500 for BSE sources
        if source in ['bse_library', 'bse_api', 'bse']:
            if self.bse_500_only:
                if symbol in self.BSE_500_SCRIP_CODES:
                    logger.debug(f"✅ {symbol} in BSE 500")
                    return True
                else:
                    logger.debug(f"❌ {symbol} NOT in BSE 500 (filtered out)")
                    return False
            else:
                return True  # BSE 500 filter disabled, accept all BSE
        
        # Check NSE 500 for NSE sources
        if source in ['nse_api', 'nse']:
            if self.nse_500_only:
                if symbol_upper in self.NSE_500_SYMBOLS:
                    logger.debug(f"✅ {symbol} in NSE 500")
                    return True
                else:
                    logger.debug(f"❌ {symbol} NOT in NSE 500 (filtered out)")
                    return False
            else:
                return True  # NSE 500 filter disabled, accept all NSE
        
        # For RSS feeds, accept everything (news is curated)
        if 'rss' in source.lower():
            return True
        
        # Default: accept (for unknown sources)
        return True
    
    def add_to_watchlist(self, symbol: str):
        """Add stock to custom watchlist"""
        symbol_upper = symbol.strip().upper()
        self.custom_watchlist.add(symbol_upper)
        logger.info(f"Added {symbol_upper} to custom watchlist")
    
    def remove_from_watchlist(self, symbol: str):
        """Remove stock from custom watchlist"""
        symbol_upper = symbol.strip().upper()
        if symbol_upper in self.custom_watchlist:
            self.custom_watchlist.remove(symbol_upper)
            logger.info(f"Removed {symbol_upper} from custom watchlist")
    
    def get_watchlist(self) -> Set[str]:
        """Get current custom watchlist"""
        return self.custom_watchlist.copy()
    
    def get_stats(self) -> dict:
        """Get filter statistics"""
        return {
            'filter_enabled': self.filter_enabled,
            'bse_500_only': self.bse_500_only,
            'nse_500_only': self.nse_500_only,
            'custom_watchlist_size': len(self.custom_watchlist),
            'custom_watchlist': sorted(self.custom_watchlist),
        }


# Global filter instance
_stock_filter: Optional[StockFilter] = None


def init_stock_filter(config: dict):
    """Initialize global stock filter"""
    global _stock_filter
    _stock_filter = StockFilter(config)


def get_stock_filter() -> StockFilter:
    """Get global stock filter instance"""
    if _stock_filter is None:
        raise RuntimeError("Stock filter not initialized. Call init_stock_filter() first.")
    return _stock_filter

