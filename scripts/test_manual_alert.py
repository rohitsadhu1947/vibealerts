#!/usr/bin/env python3
"""
Manual test script to verify the complete pipeline
Simulates a quarterly result and sends a test alert to Telegram
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from redis import Redis
from config import load_config
from src.database.models import ExtractedMetrics, AnalysisResult, AlertMessage, Sentiment
from src.notification.telegram import TelegramNotifier

# Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'


async def test_complete_pipeline():
    """Test the complete alert pipeline with dummy data"""
    
    print(f"\n{BLUE}{'=' * 70}")
    print(f"🧪 Vibe Alerts - Manual Pipeline Test".center(70))
    print(f"{'=' * 70}{RESET}\n")
    
    # Load config
    config = load_config()
    
    # Initialize services
    telegram_notifier = TelegramNotifier(config)
    
    print(f"{YELLOW}📊 Creating test data for RELIANCE Q3 FY2025...{RESET}\n")
    
    # 1. Create test metrics (simulating extraction)
    test_metrics = ExtractedMetrics(
        symbol="RELIANCE",
        quarter=3,
        fiscal_year=2025,
        
        # Current period
        revenue=Decimal("245000"),  # ₹2,45,000 Cr
        profit_after_tax=Decimal("18900"),  # ₹18,900 Cr
        eps=Decimal("28.20"),
        
        # Previous year (for YoY)
        revenue_prev_year=Decimal("210000"),  # ₹2,10,000 Cr
        profit_prev_year=Decimal("16800"),  # ₹16,800 Cr
        
        # Metadata
        extraction_method="test",
        confidence_score=1.0,
        extraction_time_ms=100
    )
    
    print(f"{GREEN}✅ Test metrics created:{RESET}")
    print(f"   Revenue: ₹{test_metrics.revenue:,} Cr")
    print(f"   Profit: ₹{test_metrics.profit_after_tax:,} Cr")
    print(f"   EPS: ₹{test_metrics.eps}\n")
    
    # 2. Create test analysis (simulating analysis engine)
    test_analysis = AnalysisResult(
        symbol="RELIANCE",
        quarter=3,
        fiscal_year=2025,
        
        # Beat/miss (simulating vs estimates)
        revenue_beat_pct=2.5,  # +2.5% beat
        profit_beat_pct=8.3,   # +8.3% beat
        eps_beat_pct=5.1,      # +5.1% beat
        
        # Growth
        yoy_revenue_growth=16.7,  # +16.7% YoY
        yoy_profit_growth=12.5,   # +12.5% YoY
        
        # Sentiment
        sentiment=Sentiment.STRONG_BEAT,
        sentiment_score=12.5,
        
        # Action
        action_text="🚀 STRONG performance - Major beat across metrics!",
        action_emoji="🚀"
    )
    
    print(f"{GREEN}✅ Test analysis created:{RESET}")
    print(f"   Sentiment: {test_analysis.sentiment.value}")
    print(f"   YoY Revenue Growth: +{test_analysis.yoy_revenue_growth}%")
    print(f"   YoY Profit Growth: +{test_analysis.yoy_profit_growth}%\n")
    
    # 3. Create alert message
    test_alert = AlertMessage(
        symbol="RELIANCE",
        metrics=test_metrics,
        analysis=test_analysis,
        detection_time_sec=6.2,
        pdf_url="https://www.nseindia.com/test/reliance_q3fy25.pdf"
    )
    
    print(f"{YELLOW}📱 Formatted Telegram message:{RESET}")
    print(f"{BLUE}{'─' * 70}{RESET}")
    print(test_alert.format_telegram())
    print(f"{BLUE}{'─' * 70}{RESET}\n")
    
    # 4. Send to Telegram
    print(f"{YELLOW}📤 Sending test alert to Telegram...{RESET}\n")
    
    try:
        success = await telegram_notifier.send_alert(test_alert)
        
        if success:
            print(f"{GREEN}{'=' * 70}")
            print(f"✅ SUCCESS! Test alert sent to your Telegram channel!".center(70))
            print(f"{'=' * 70}{RESET}\n")
            print(f"{YELLOW}👉 Check your Telegram channel now:{RESET}")
            print(f"   {config['telegram']['channel_id']}\n")
            print(f"{GREEN}If you see the RELIANCE test message, everything is working! 🎉{RESET}\n")
            return 0
        else:
            print(f"{YELLOW}⚠️  Alert sending returned False{RESET}")
            print(f"Check the error messages above.\n")
            return 1
            
    except Exception as e:
        print(f"{YELLOW}❌ Failed to send alert: {e}{RESET}\n")
        print(f"Common issues:")
        print(f"  1. Bot is not admin in the channel")
        print(f"  2. Channel ID is incorrect (should be @username)")
        print(f"  3. Bot token is invalid\n")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_complete_pipeline())
        exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user{RESET}\n")
        exit(1)
    except Exception as e:
        print(f"\n{YELLOW}❌ Test failed with error: {e}{RESET}\n")
        import traceback
        traceback.print_exc()
        exit(1)

