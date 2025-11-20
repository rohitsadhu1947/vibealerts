"""
Stock Universe Filter
Filters stocks by index membership (BSE 500, NSE 500) and custom watchlists
"""

from typing import Set, Optional
from loguru import logger


class StockFilter:
    """Filters stocks based on index membership and custom watchlists"""
    
    # BSE 500 scrip codes (top 500 stocks by market cap)
    # Auto-generated from BSE API on Nov 20, 2025
    # Source: BSE listSecurities() sorted by market cap
    BSE_500_SCRIP_CODES = {
        '500325', '500180', '532454', '532540', '532174', '500112', '500034', '500209', '543526', '500696',
        '500510', '500875', '532500', '500520', '532281', '524715', '500247', '532215', '532538', '500114',
        '532978', '532921', '532555', '512599', '541154', '500312', '500049', '543320', '533096', '500228',
        '500820', '540376', '507685', '532898', '532977', '500790', '530965', '533278', '539448', '500470',
        '540719', '500188', '500295', '543940', '505200', '544274', '500300', '532868', '500440', '540005',
        '532488', '541450', '532343', '540777', '500547', '543257', '500251', '511218', '540180', '500331',
        '532134', '533398', '511243', '532461', '532755', '500825', '500425', '544574', '532483', '500570',
        '500490', '532725', '500420', '500400', '500087', '532810', '500480', '532155', '500182', '543287',
        '539254', '532814', '517334', '532477', '500800', '541729', '532424', '542652', '500550', '543237',
        '543220', '500093', '500116', '532822', '500530', '500002', '532286', '532754', '508869', '534816',
        '500850', '500124', '532432', '500104', '540716', '533179', '543187', '500103', '500387', '531642',
        '532955', '532321', '500096', '500257', '540699', '543904', '544162', '517354', '540133', '544252',
        '532777', '533148', '500477', '540691', '543390', '503806', '543066', '543396', '533098', '522275',
        '532667', '543384', '532388', '532539', '533274', '533519', '532466', '533106', '532648', '532843',
        '524804', '509480', '540611', '500493', '539523', '540755', '542066', '532149', '506395', '542649',
        '512455', '532779', '526371', '532187', '500290', '539437', '533150', '890157', '512070', '505790',
        '500368', '532508', '500488', '533273', '532541', '503100', '500469', '500830', '500271', '540762',
        '543994', '532892', '541143', '500113', '540767', '542830', '500483', '540222', '532523', '532296',
        '523642', '523457', '526299', '543278', '534091', '532720', '533758', '540530', '532234', '500575',
        '542772', '539177', '540115', '532478', '532525', '500163', '509930', '540678', '544238', '532497',
        '502355', '532644', '532827', '500660', '500459', '539551', '544026', '532522', '523395', '543664',
        '500495', '517569', '532830', '531344', '533155', '532505', '540153', '501301', '542812', '524000',
        '542216', '532889', '532259', '500067', '524494', '543458', '532683', '504973', '500411', '500164',
        '532885', '500410', '540975', '513683', '500092', '542011', '500408', '500877', '542651', '544179',
        '543654', '543498', '500086', '533206', '543529', '543300', '513599', '534309', '532331', '543426',
        '517174', '500253', '500109', '532504', '543245', '543412', '520056', '523610', '540769', '532514',
        '539336', '544028', '507815', '506943', '500003', '543308', '532947', '543988', '539524', '544210',
        '517271', '539006', '543235', '540902', '539268', '515030', '543635', '532809', '533023', '541153',
        '542752', '531213', '539083', '543415', '531531', '500840', '540173', '500260', '543299', '532144',
        '506401', '522113', '532636', '532805', '500680', '506820', '500033', '531162', '542920', '540596',
        '532929', '544081', '500084', '543064', '515055', '500184', '532927', '543374', '532300', '524558',
        '541770', '532733', '522287', '544176', '500770', '506285', '500403', '543232', '500040', '532210',
        '532642', '542399', '543945', '500165', '540065', '531768', '500042', '500870', '531595', '532714',
        '543720', '500085', '523367', '544203', '500125', '500645', '543330', '544174', '543653', '534139',
        '500027', '504614', '500008', '533573', '543663', '543428', '539876', '500233', '533655', '533293',
        '530019', '500266', '532548', '532702', '506076', '524200', '543573', '544226', '532734', '533581',
        '532784', '500252', '520111', '500048', '504067', '532939', '531358', '532181', '543276', '522074',
        '500620', '500110', '513375', '532756', '543990', '500878', '524816', '541956', '543981', '500710',
        '544045', '513023', '538835', '505714', '532953', '500238', '543960', '543463', '532627', '503310',
        '543333', '532605', '543238', '524742', '521064', '531335', '538962', '500106', '542726', '532783',
        '543349', '541557', '543335', '526612', '524208', '542141', '509496', '523405', '500241', '543524',
        '519600', '502986', '543275', '501425', '517146', '514162', '532482', '540073', '544012', '533339',
        '540900', '543530', '500043', '535789', '541988', '543334', '540750', '543413', '533272', '532175',
        '506590', '533282', '530005', '500249', '544172', '530007', '543259', '543768', '500210', '539957',
        '541233', '501423', '505700', '543959', '541556', '500405', '543534', '532209', '533553', '511196',
        '500144', '532966', '523598', '534618', '512573', '532762', '543271', '532926', '532439', '500294',
        '543265', '532832', '523025', '544061', '543322', '500940', '532178', '500039', '543482', '509488',
        '540743', '544250', '532400', '532922', '532689', '500378', '500183', '539787', '500674', '543317',
        '544046', '542904', '543350', '530517', '532221', '530343', '541578', '532856', '543398', '543527',
        '542650', '500380', '532371', '543358', '532218', '509631', '543318', '533158', '500472', '532527',
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

