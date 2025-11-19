#!/usr/bin/env python3
"""
Test the symbol resolver
"""

import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.symbol_resolver import resolve_symbol


async def test_resolver():
    """Test symbol resolution"""
    
    test_symbols = [
        ("RELIANCE", "NSE symbol"),
        ("507552", "BSE scrip code - HIKAL"),
        ("524735", "BSE scrip code - HIKAL"),
        ("531913", "BSE scrip code - GOPAL IRON"),
        ("HIKAL", "NSE symbol"),
        ("TCS", "NSE symbol"),
        ("500325", "BSE scrip code - RELIANCE"),
    ]
    
    print("\n" + "="*80)
    print("🔍 SYMBOL RESOLVER TEST")
    print("="*80 + "\n")
    
    for symbol, description in test_symbols:
        resolved = await resolve_symbol(symbol)
        status = "✅" if resolved != symbol else "⚠️"
        print(f"{status} {symbol:15} ({description:30}) → {resolved}")
    
    print("\n" + "="*80)
    print("✅ Test completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_resolver())

