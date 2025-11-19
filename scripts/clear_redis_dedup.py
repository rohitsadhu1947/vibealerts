#!/usr/bin/env python3
"""
Clear Redis deduplication keys to allow re-processing
"""
import redis
import os

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
r = redis.from_url(redis_url, decode_responses=True)

print("🔍 Checking Redis keys...")
keys = r.keys('processed:*')
print(f"Found {len(keys)} processed announcements")

if keys:
    print("\nClearing all deduplication keys...")
    count = r.delete(*keys)
    print(f"✅ Cleared {count} keys")
    print("\n🎯 Next monitoring cycle will re-process all announcements!")
else:
    print("No keys to clear")

