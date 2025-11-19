"""
Stock Symbol Resolver
Resolves stock codes/symbols to company names
"""

import aiohttp
import asyncio
from typing import Optional, Dict
from loguru import logger
from bse import BSE


class SymbolResolver:
    """Resolves stock codes to company names"""
    
    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.bse_client = None
        
    def _init_bse_client(self):
        """Lazy initialize BSE client"""
        if self.bse_client is None:
            try:
                import tempfile
                self.bse_client = BSE(download_folder=tempfile.gettempdir())
            except Exception as e:
                logger.warning(f"Failed to initialize BSE client: {e}")
                self.bse_client = False  # Mark as failed
    
    async def resolve(self, symbol: str) -> str:
        """
        Resolve symbol/code to company name
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE', '507552', 'HIKAL')
            
        Returns:
            Company name or original symbol if not found
        """
        # Check cache first
        if symbol in self.cache:
            return self.cache[symbol]
        
        # If it's already a readable name (alphabetic), return as-is
        if symbol.isalpha() and len(symbol) >= 3:
            self.cache[symbol] = symbol
            return symbol
        
        # Try to resolve numeric codes
        if symbol.isdigit():
            name = await self._resolve_bse_code(symbol)
            if name:
                self.cache[symbol] = name
                return name
        
        # Try NSE symbol lookup
        name = await self._resolve_nse_symbol(symbol)
        if name:
            self.cache[symbol] = name
            return name
        
        # Fallback: return original symbol
        self.cache[symbol] = symbol
        return symbol
    
    async def _resolve_bse_code(self, code: str) -> Optional[str]:
        """Resolve BSE scrip code to company name"""
        try:
            # Method 1: Try BSE library
            self._init_bse_client()
            if self.bse_client and self.bse_client is not False:
                try:
                    name = self.bse_client.getScripName(code)
                    if name and name != code:
                        logger.debug(f"Resolved BSE code {code} -> {name}")
                        return name
                except Exception as e:
                    logger.debug(f"BSE library failed for {code}: {e}")
            
            # Method 2: Try BSE API endpoint
            url = f"https://api.bseindia.com/BseIndiaAPI/api/ComHeader/w?quotetype=EQ&scripcode={code}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if 'ScrFullNm' in data:
                            name = data['ScrFullNm'].strip()
                            logger.debug(f"Resolved BSE code {code} -> {name} (API)")
                            return name
        
        except Exception as e:
            logger.debug(f"Failed to resolve BSE code {code}: {e}")
        
        return None
    
    async def _resolve_nse_symbol(self, symbol: str) -> Optional[str]:
        """Resolve NSE symbol to company name"""
        try:
            url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if 'info' in data and 'companyName' in data['info']:
                            name = data['info']['companyName']
                            logger.debug(f"Resolved NSE symbol {symbol} -> {name}")
                            return name
        
        except Exception as e:
            logger.debug(f"Failed to resolve NSE symbol {symbol}: {e}")
        
        return None
    
    def get_cache_size(self) -> int:
        """Get number of cached symbols"""
        return len(self.cache)
    
    def clear_cache(self):
        """Clear the symbol cache"""
        self.cache.clear()
        logger.info("Symbol cache cleared")


# Global instance
_resolver = SymbolResolver()


async def resolve_symbol(symbol: str) -> str:
    """
    Convenience function to resolve a symbol
    
    Args:
        symbol: Stock symbol/code
        
    Returns:
        Company name or original symbol
    """
    return await _resolver.resolve(symbol)


def get_cache_size() -> int:
    """Get symbol cache size"""
    return _resolver.get_cache_size()

