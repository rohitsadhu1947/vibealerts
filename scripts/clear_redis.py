#!/usr/bin/env python3
"""
Clear Redis deduplication - Run on Railway
"""
import redis
import os
import sys

def clear_redis():
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL not set")
        return False
    
    try:
        r = redis.from_url(redis_url, decode_responses=True)
        
        print("🔍 Checking Redis keys...")
        keys = r.keys('processed:*')
        print(f"Found {len(keys)} processed announcements")
        
        if keys:
            print("\n🗑️  Clearing all deduplication keys...")
            count = r.delete(*keys)
            print(f"✅ Cleared {count} keys")
            print("\n🎯 Next monitoring cycle will re-process all announcements!")
            return True
        else:
            print("No keys to clear")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = clear_redis()
    sys.exit(0 if success else 1)

