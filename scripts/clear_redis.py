#!/usr/bin/env python3
"""
Clear Redis deduplication - Run on Railway
"""
import os
import sys

def clear_redis():
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL not set")
        return False
    
    try:
        from redis import Redis
        
        print("=" * 70)
        print("🗑️  CLEARING REDIS DEDUPLICATION KEYS")
        print("=" * 70)
        
        r = Redis.from_url(redis_url, decode_responses=True)
        
        print("🔍 Connecting to Redis...")
        r.ping()
        print("✅ Redis connected")
        
        print("🔍 Checking for processed keys...")
        keys = r.keys('processed:*')
        print(f"   Found {len(keys)} processed announcements")
        
        if keys:
            print("\n🗑️  Clearing all deduplication keys...")
            count = r.delete(*keys)
            print(f"✅ Successfully cleared {count} keys!")
            print("\n🎯 All announcements will be re-processed in next cycle!")
            print("=" * 70)
            return True
        else:
            print("⚠️  No keys to clear (already empty)")
            print("=" * 70)
            return True
            
    except Exception as e:
        print(f"❌ Error clearing Redis: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        return False

if __name__ == "__main__":
    print("\n🚀 Starting Redis clear script...")
    success = clear_redis()
    if success:
        print("✅ Script completed successfully\n")
    else:
        print("❌ Script failed\n")
    sys.exit(0 if success else 1)

