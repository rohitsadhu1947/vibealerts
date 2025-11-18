#!/usr/bin/env python3
"""
Simple Telegram test - just sends a message to verify bot works
This can run on Railway where credentials are configured
"""

import asyncio
import os
from telegram import Bot

async def test_telegram():
    print("\n" + "="*70)
    print("📱 Testing Telegram Bot")
    print("="*70 + "\n")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        return
    
    if not channel_id:
        print("❌ TELEGRAM_CHANNEL_ID not set")
        return
    
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Channel ID: {channel_id}\n")
    
    try:
        bot = Bot(token=bot_token)
        
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username}\n")
        
        # Send test message
        print(f"📤 Sending test message to {channel_id}...")
        
        test_message = """🧪 **Vibe Alerts Test Message**

This is a test to verify your bot is working correctly!

✅ If you see this message in your Telegram channel, 
everything is configured properly and ready for live alerts!

🚀 **Next:** Wait for quarterly result season (January 2025) 
to see real alerts!

_This is an automated test message._"""
        
        message = await bot.send_message(
            chat_id=channel_id,
            text=test_message,
            parse_mode='Markdown'
        )
        
        print(f"✅ SUCCESS! Message sent (ID: {message.message_id})\n")
        print("="*70)
        print(f"👉 Check your Telegram channel: {channel_id}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram())

