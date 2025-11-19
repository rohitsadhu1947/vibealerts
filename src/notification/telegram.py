"""
Vibe_Alerts - Telegram Notification Service
Send formatted alerts to Telegram channel and users
"""

from typing import Optional
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from loguru import logger

from src.database.models import AlertMessage


class TelegramNotifier:
    """Telegram notification service"""
    
    def __init__(self, config: dict):
        self.config = config
        self.bot_token = config['telegram']['bot_token']
        self.channel_id = config['telegram']['channel_id']
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not configured")
        
        self.bot = Bot(token=self.bot_token)
        
        logger.info(f"Telegram notifier initialized (channel: {self.channel_id})")
    
    async def send_alert(self, alert: AlertMessage) -> bool:
        """Send alert to channel"""
        
        message_text = await alert.format_telegram()  # Now async!
        reply_markup = self._get_buttons(alert)
        
        try:
            # Send to public channel
            message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=message_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
            
            # Use company name if available for logging
            display_name = alert.company_name if alert.company_name else alert.symbol
            logger.info(f"📤 Sent alert to channel: {display_name} (msg_id: {message.message_id})")
            
            # Pin if strong beat or major miss
            from src.database.models import Sentiment
            if alert.analysis.sentiment in [Sentiment.STRONG_BEAT, Sentiment.MAJOR_MISS]:
                try:
                    await self.bot.pin_chat_message(
                        chat_id=self.channel_id,
                        message_id=message.message_id
                    )
                    logger.info(f"📌 Pinned message for {display_name}")
                except Exception as e:
                    logger.warning(f"Failed to pin message: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert for {alert.symbol}: {e}")
            return False
    
    def _get_buttons(self, alert: AlertMessage) -> InlineKeyboardMarkup:
        """Generate interactive buttons"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "📈 Chart",
                    url=f"https://www.tradingview.com/chart/?symbol=NSE:{alert.symbol}"
                ),
                InlineKeyboardButton(
                    "📄 PDF",
                    url=alert.pdf_url if alert.pdf_url.startswith('http') else f"https://www.nseindia.com{alert.pdf_url}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "🔍 Screener",
                    url=f"https://www.screener.in/company/{alert.symbol}"
                ),
                InlineKeyboardButton(
                    "💹 Kite",
                    url=f"https://kite.zerodha.com/chart/NSE/{alert.symbol}"
                ),
            ],
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    async def test_connection(self) -> bool:
        """Test Telegram bot connection"""
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Telegram bot connected: @{bot_info.username}")
            return True
        except Exception as e:
            logger.error(f"❌ Telegram bot connection failed: {e}")
            return False

