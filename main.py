"""
Vibe_Alerts - Main Application
MVP: Real-time quarterly results monitoring and alerting
"""

import asyncio
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from redis import Redis
from loguru import logger

from config import load_config
from src.utils.logging import setup_logging
from src.utils.stock_filter import init_stock_filter
from src.monitoring.service import MonitoringService
from src.extraction.service import ExtractionService
from src.analysis.engine import AnalysisEngine
from src.notification.telegram import TelegramNotifier
from src.database.models import AlertMessage


class VibeAlerts:
    """Main application orchestrator"""
    
    def __init__(self):
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logging(self.config['app']['log_level'])
        
        # Initialize stock filter
        init_stock_filter(self.config)
        logger.info("Stock filter initialized")
        
        # Initialize Redis
        self.redis = Redis.from_url(
            self.config['redis_url'],
            decode_responses=True
        )
        
        # Initialize services
        self.monitoring_service = MonitoringService(self.config, self.redis)
        self.extraction_service = ExtractionService(self.config)
        self.analysis_engine = AnalysisEngine(self.redis)
        self.telegram_notifier = TelegramNotifier(self.config)
        
        logger.info("Vibe_Alerts initialized")
    
    async def start(self):
        """Start the application"""
        
        logger.info("=" * 70)
        logger.info("🚀 Vibe_Alerts MVP - Quarterly Results Real-Time Monitoring")
        logger.info("=" * 70)
        logger.info(f"📢 Channel: {self.config['telegram']['channel_id']}")
        logger.info(f"⏱️  Poll interval: {self.config['monitoring']['poll_interval']}s")
        logger.info(f"🔍 Monitoring sources: {len(self.config['monitoring']['sources'])}")
        logger.info("=" * 70)
        
        # Test connections
        logger.info("Testing connections...")
        
        try:
            self.redis.ping()
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            return
        
        telegram_ok = await self.telegram_notifier.test_connection()
        if not telegram_ok:
            logger.error("❌ Telegram bot connection failed")
            return
        
        logger.info("=" * 70)
        logger.info("🎯 All systems ready! Starting monitoring...")
        logger.info("=" * 70)
        
        # Start monitoring and processing loop
        announcement_count = 0
        
        async for announcement in self.monitoring_service.monitor():
            try:
                announcement_count += 1
                start_time = time.time()
                
                logger.info(f"\n{'=' * 70}")
                logger.info(f"📋 Processing announcement #{announcement_count}: {announcement.symbol}")
                logger.info(f"{'=' * 70}")
                
                # Extract metrics
                logger.info(f"[1/3] Extracting metrics from PDF...")
                metrics = await self.extraction_service.process_announcement(announcement)
                
                if not metrics:
                    logger.warning(f"❌ Extraction failed for {announcement.symbol}")
                    continue
                
                # Analyze
                logger.info(f"[2/3] Analyzing results...")
                analysis = await self.analysis_engine.analyze(metrics)
                
                # Create alert
                detection_time = time.time() - start_time
                alert = AlertMessage(
                    symbol=metrics.symbol,
                    metrics=metrics,
                    analysis=analysis,
                    detection_time_sec=detection_time,
                    pdf_url=announcement.attachment_url,
                    announcement_type=announcement.announcement_type or "QUARTERLY_RESULT",
                    news_title=announcement.description,  # Pass news title
                    news_content=announcement.attachment_text  # Pass news content
                )
                
                # Send notification
                logger.info(f"[3/3] Sending alert to Telegram...")
                success = await self.telegram_notifier.send_alert(alert)
                
                if success:
                    logger.info(f"{'=' * 70}")
                    logger.info(
                        f"✅ {metrics.symbol} processed successfully!"
                    )
                    logger.info(
                        f"   Sentiment: {analysis.sentiment.value} | "
                        f"Time: {detection_time:.1f}s | "
                        f"Confidence: {metrics.confidence_score:.0%}"
                    )
                    logger.info(f"{'=' * 70}\n")
                else:
                    logger.error(f"❌ Failed to send alert for {announcement.symbol}")
                
            except KeyboardInterrupt:
                logger.info("\n\n⚠️  Shutting down gracefully...")
                break
            except Exception as e:
                logger.error(f"❌ Error processing {announcement.symbol}: {e}")
                logger.exception(e)
                continue


async def main():
    """Application entry point"""
    
    try:
        app = VibeAlerts()
        await app.start()
    except KeyboardInterrupt:
        logger.info("\n\n👋 Vibe_Alerts stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    # Run the application
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

