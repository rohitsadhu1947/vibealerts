# Vibe_Alerts MVP - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Get Your Credentials

#### 1.1 Neon DB (PostgreSQL)
1. Go to [neon.tech](https://neon.tech)
2. Sign up for free account
3. Create new project: "vibe_alerts"
4. Copy connection string (looks like: `postgresql://user:pass@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require`)

#### 1.2 Telegram Bot
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose name: "Vibe Alerts Bot"
4. Choose username: "vibe_alerts_bot" (must be unique)
5. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### 1.3 Telegram Channel
1. Create a new public channel in Telegram
2. Add your bot as admin with "Post Messages" permission
3. Note the channel username (e.g., `@vibe_alerts_test`)

#### 1.4 Redis (Local)
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Docker (easiest)
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### Step 2: Install

```bash
# Navigate to project
cd Vibe_Alerts

# Run setup script
bash scripts/setup.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Configure

Edit `.env` file:

```bash
# Open .env
nano .env

# Add your credentials:
DATABASE_URL=postgresql://user:pass@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@vibe_alerts_test
```

### Step 4: Initialize Database

```bash
# The app will create tables automatically on first run
# Or manually:
psql $DATABASE_URL < src/database/schema.sql
```

### Step 5: Run!

```bash
# Activate virtual environment (if not already)
source venv/bin/activate

# Run the application
python main.py
```

You should see:
```
🚀 Vibe_Alerts MVP - Quarterly Results Real-Time Monitoring
📢 Channel: @vibe_alerts_test
⏱️  Poll interval: 3s
✅ Redis connected
✅ Telegram bot connected: @vibe_alerts_bot
🎯 All systems ready! Starting monitoring...
```

## 🧪 Testing

### Test 1: Check Connections

```bash
# Test Redis
redis-cli ping
# Should return: PONG

# Test Telegram bot
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
# Should return bot info

# Test Neon DB
psql $DATABASE_URL -c "SELECT 1"
# Should return: 1
```

### Test 2: Manual Result Processing

For testing, you can add a mock announcement to Redis:

```python
python3
>>> import redis
>>> import json
>>> r = redis.Redis(host='localhost', port=6379, decode_responses=True)
>>> 
>>> # Mock announcement
>>> ann = {
...     'source': 'nse',
...     'symbol': 'RELIANCE',
...     'date': '13-11-2024',
...     'description': 'Q3 FY2025 Financial Results',
...     'attachment_url': 'https://www.nseindia.com/corporate/RELIANCE_Q3FY25.pdf',
...     'timestamp': '2024-11-13T10:00:00'
... }
>>> 
>>> r.lpush('extraction_queue', json.dumps(ann))
>>> exit()
```

## 📊 Monitoring

### View Logs
```bash
# Live logs
tail -f logs/vibe_alerts_$(date +%Y-%m-%d).log

# Search for errors
grep ERROR logs/vibe_alerts_*.log
```

### Check Redis
```bash
redis-cli

# See processed announcements
KEYS processed:*

# Check queue
LLEN extraction_queue

# See cached estimates
KEYS estimates:*
```

### Monitor Application
```bash
# Check if running
ps aux | grep python

# Resource usage
top -p $(pgrep -f "python main.py")
```

## 🚨 Troubleshooting

### Issue: "DATABASE_URL not set"
**Solution**: Make sure `.env` file exists and contains `DATABASE_URL`
```bash
cat .env | grep DATABASE_URL
```

### Issue: "Telegram bot connection failed"
**Solution**: 
1. Check bot token is correct
2. Make sure bot exists (test with curl)
3. Try creating a new bot

### Issue: "Redis connection refused"
**Solution**:
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
docker start redis  # Docker
```

### Issue: "PDF extraction failed"
**Solution**: Install system dependencies
```bash
# macOS
brew install tesseract poppler

# Ubuntu
sudo apt-get install tesseract-ocr poppler-utils python3-dev
```

### Issue: "No results detected"
**Solution**: 
- Check NSE API is accessible
- Try during market hours (9:15 AM - 3:30 PM IST)
- Results are typically announced after market hours (4 PM onwards)

## 🎯 What's Next?

### Phase 1 Complete ✅
- Real-time monitoring
- PDF extraction
- Basic analysis
- Telegram alerts

### Phase 2 (Coming Soon)
- [ ] BSE monitoring
- [ ] Analyst estimates pre-loading
- [ ] User watchlists
- [ ] Bot commands (/watch, /list)
- [ ] Database persistence
- [ ] Admin dashboard

### Testing During Result Season

The best time to test is during quarterly result season:
- **Q3 FY2025**: January 2025
- **Q4 FY2025**: April-May 2025

Major companies announce around:
- Banks: First week
- IT companies: Second week
- Pharma/FMCG: Throughout the month

## 🆘 Support

- Documentation: `README.md`
- Architecture: `docs/architecture.md`
- Issues: Create GitHub issue
- Contact: @vibe_alerts

## 🎉 Success!

If you see alerts coming through on your Telegram channel, you're all set!

Example successful flow:
1. NSE publishes result → Detected in 3-5 seconds
2. PDF downloaded → Text extracted in 1-2 seconds
3. Metrics parsed → Analysis in < 1 second
4. Alert sent to Telegram → Total time: 6-8 seconds

**Happy monitoring! 🚀📊**

