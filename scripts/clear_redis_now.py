"""
Clear Redis deduplication keys - EMERGENCY
"""
import os
import sys
from redis import Redis

# Load environment
from dotenv import load_dotenv
load_dotenv()

def clear_redis():
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        redis = Redis.from_url(redis_url, decode_responses=True)
        
        # Clear all processed keys
        keys = redis.keys("processed:*")
        
        if keys:
            print(f"Found {len(keys)} dedup keys")
            deleted = redis.delete(*keys)
            print(f"✅ Cleared {deleted} Redis deduplication keys")
        else:
            print("No dedup keys found")
        
        redis.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    clear_redis()
