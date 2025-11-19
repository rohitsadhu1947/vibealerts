#!/usr/bin/env python3
"""
Quick test to send a Telegram alert
"""
import asyncio
import os
from telegram import Bot

async def test_telegram():
    """Test sending a message to Telegram channel"""
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8217021625:AAH0tkFn6B1Lt-W8N4gA08gWsZ77MQYH1p8')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID', '@vibetradingalerts')
    
    print(f"🤖 Bot Token: {bot_token[:20]}...")
    print(f"📢 Channel: {channel_id}")
    
    bot = Bot(token=bot_token)
    
    try:
        # Test message
        message = """
🚀 *Vibe Alerts Test Message*

✅ System is online and working!
📊 This is a test alert from your monitoring system.

_If you see this, Telegram integration is successful!_
"""
        
        print("\n📤 Sending test message...")
        result = await bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode='Markdown'
        )
        
        print(f"✅ SUCCESS! Message sent to {channel_id}")
        print(f"   Message ID: {result.message_id}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print(f"\n💡 Possible issues:")
        print(f"   1. Bot not added as admin to channel")
        print(f"   2. Wrong channel ID")
        print(f"   3. Bot doesn't have 'Post Messages' permission")
        return False

if __name__ == "__main__":
    asyncio.run(test_telegram())

