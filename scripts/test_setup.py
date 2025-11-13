#!/usr/bin/env python3
"""
Test script to verify Vibe Alerts setup
Run this after completing setup to verify all services are working
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from redis import Redis
from telegram import Bot
import psycopg2

# Load environment variables
load_dotenv()

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text):
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text):
    print(f"   {text}")


def test_env_variables():
    """Test if all required environment variables are set"""
    print_header("Testing Environment Variables")
    
    required_vars = {
        'DATABASE_URL': 'Neon DB connection string',
        'REDIS_URL': 'Redis connection URL',
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'TELEGRAM_CHANNEL_ID': 'Telegram channel ID',
    }
    
    all_present = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != '' and not value.startswith('postgresql://user:password') and value != '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz':
            print_success(f"{var}: {description}")
            print_info(f"Value: {value[:30]}..." if len(value) > 30 else f"Value: {value}")
        else:
            print_error(f"{var}: Not set or using example value")
            print_info(f"Please set this in your .env file")
            all_present = False
    
    return all_present


def test_redis():
    """Test Redis connection"""
    print_header("Testing Redis Connection")
    
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    print_info(f"Connecting to: {redis_url}")
    
    try:
        redis_client = Redis.from_url(redis_url, decode_responses=True)
        
        # Test ping
        response = redis_client.ping()
        if response:
            print_success("Redis connection successful")
            
            # Test write/read
            test_key = "vibe_alerts_test"
            redis_client.set(test_key, "Hello from Vibe Alerts!")
            value = redis_client.get(test_key)
            
            if value == "Hello from Vibe Alerts!":
                print_success("Redis read/write test passed")
                redis_client.delete(test_key)
            else:
                print_error("Redis read/write test failed")
                return False
            
            # Show Redis info
            info = redis_client.info()
            print_info(f"Redis version: {info.get('redis_version', 'unknown')}")
            print_info(f"Connected clients: {info.get('connected_clients', 'unknown')}")
            print_info(f"Used memory: {info.get('used_memory_human', 'unknown')}")
            
            return True
        else:
            print_error("Redis ping failed")
            return False
            
    except Exception as e:
        print_error(f"Redis connection failed: {e}")
        print_warning("Make sure Redis is running:")
        print_info("  macOS: brew services start redis")
        print_info("  Linux: sudo systemctl start redis")
        print_info("  Or use Upstash Redis (https://upstash.com)")
        return False


def test_database():
    """Test PostgreSQL database connection"""
    print_header("Testing Database Connection (Neon DB)")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url or db_url.startswith('postgresql://user:password'):
        print_error("DATABASE_URL not set properly")
        print_info("Get your connection string from: https://console.neon.tech")
        return False
    
    print_info(f"Connecting to: {db_url.split('@')[1] if '@' in db_url else 'unknown'}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        print_success("Database connection successful")
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print_info(f"PostgreSQL version: {version.split(',')[0]}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname='public' 
            ORDER BY tablename;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print_success(f"Found {len(tables)} tables")
            for table in tables:
                print_info(f"  - {table[0]}")
        else:
            print_warning("No tables found. Run schema initialization:")
            print_info("  psql $DATABASE_URL -f src/database/schema.sql")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        print_warning("Check your DATABASE_URL in .env file")
        print_info("Format: postgresql://user:pass@host:5432/db?sslmode=require")
        return False


async def test_telegram():
    """Test Telegram bot connection"""
    print_header("Testing Telegram Bot")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    if not bot_token or bot_token == '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz':
        print_error("TELEGRAM_BOT_TOKEN not set")
        print_info("Get token from @BotFather in Telegram")
        return False
    
    if not channel_id or channel_id == '@vibe_alerts_test':
        print_error("TELEGRAM_CHANNEL_ID not set")
        print_info("Create a channel and set its username")
        return False
    
    try:
        bot = Bot(token=bot_token)
        
        # Test bot connection
        bot_info = await bot.get_me()
        print_success(f"Bot connected: @{bot_info.username}")
        print_info(f"Bot name: {bot_info.first_name}")
        print_info(f"Bot ID: {bot_info.id}")
        
        # Test sending message to channel
        print_info(f"Testing message send to channel: {channel_id}")
        
        try:
            message = await bot.send_message(
                chat_id=channel_id,
                text="✅ **Vibe Alerts Setup Test**\n\nIf you see this message, your bot is configured correctly!",
                parse_mode='Markdown'
            )
            print_success(f"Test message sent successfully (message_id: {message.message_id})")
            print_info(f"Check your channel: {channel_id}")
            
            # Try to delete the test message
            try:
                await bot.delete_message(chat_id=channel_id, message_id=message.message_id)
                print_info("Test message deleted")
            except:
                print_warning("Could not delete test message (needs delete permission)")
            
            return True
            
        except Exception as e:
            print_error(f"Failed to send message to channel: {e}")
            print_warning("Make sure:")
            print_info("  1. Bot is added as admin to the channel")
            print_info("  2. Bot has 'Post Messages' permission")
            print_info("  3. Channel username is correct (include @)")
            return False
        
    except Exception as e:
        print_error(f"Telegram bot connection failed: {e}")
        print_warning("Check your TELEGRAM_BOT_TOKEN in .env file")
        return False


def test_file_structure():
    """Test if all required files exist"""
    print_header("Testing File Structure")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'config/config.yaml',
        'src/monitoring/service.py',
        'src/extraction/service.py',
        'src/analysis/engine.py',
        'src/notification/telegram.py',
        'src/database/models.py',
        'src/database/schema.sql',
    ]
    
    all_present = True
    project_root = Path(__file__).parent.parent
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} - Missing!")
            all_present = False
    
    return all_present


async def main():
    """Run all tests"""
    print(f"\n{BLUE}{'=' * 70}")
    print(f"🧪 Vibe Alerts Setup Verification".center(70))
    print(f"{'=' * 70}{RESET}\n")
    
    results = {}
    
    # Test 1: Environment variables
    results['env'] = test_env_variables()
    
    # Test 2: File structure
    results['files'] = test_file_structure()
    
    # Test 3: Redis
    results['redis'] = test_redis()
    
    # Test 4: Database
    results['database'] = test_database()
    
    # Test 5: Telegram
    results['telegram'] = await test_telegram()
    
    # Summary
    print_header("Setup Verification Summary")
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed_test in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if passed_test else f"{RED}❌ FAIL{RESET}"
        print(f"  {test_name.upper().ljust(15)} {status}")
    
    print(f"\n{BLUE}{'─' * 70}{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 All tests passed! Vibe Alerts is ready to run.{RESET}")
        print(f"\n{BLUE}Start the application:{RESET}")
        print(f"  {YELLOW}python main.py{RESET}\n")
        return 0
    else:
        print(f"\n{YELLOW}⚠️  {passed}/{total} tests passed. Please fix the issues above.{RESET}\n")
        print(f"{BLUE}See SETUP_GUIDE.md for detailed setup instructions.{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

