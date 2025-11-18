#!/usr/bin/env python3
"""
Test BSE Python library for corporate announcements
"""
from bse import BSE
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging import setup_logging

logger = setup_logging()


def test_bse_library():
    """Test BSE library functions"""
    
    print("\n" + "="*80)
    print("🏢 TESTING BSE PYTHON LIBRARY")
    print("="*80)
    
    try:
        print("\n1️⃣  Initializing BSE...")
        with BSE(download_folder='./logs') as bse:
            
            # Test 1: Get scrip code
            print("\n2️⃣  Testing getScripCode()...")
            try:
                scrip = bse.getScripCode('Reliance')
                print(f"   ✅ Reliance scrip code: {scrip}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Test 2: Get company actions
            print("\n3️⃣  Testing actions()...")
            try:
                actions = bse.actions(scripcode='500325')  # Reliance
                print(f"   ✅ Got actions data:")
                print(f"   {actions}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Test 3: Get corporate announcements (if available)
            print("\n4️⃣  Exploring BSE object methods...")
            methods = [m for m in dir(bse) if not m.startswith('_')]
            print(f"   Available methods: {methods}")
            
            # Try some other methods
            interesting_methods = ['announcements', 'results', 'corp', 'financial']
            for method_name in interesting_methods:
                if hasattr(bse, method_name):
                    print(f"\n5️⃣  Found method: {method_name}!")
                    try:
                        method = getattr(bse, method_name)
                        print(f"   Trying to call {method_name}()...")
                        result = method()
                        print(f"   ✅ Result: {result}")
                    except Exception as e:
                        print(f"   ❌ Error calling {method_name}: {e}")
            
    except Exception as e:
        logger.error(f"BSE library test error: {e}")
        print(f"\n❌ Error: {e}")
    
    print("\n" + "="*80)
    print("✅ Test Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_bse_library()

