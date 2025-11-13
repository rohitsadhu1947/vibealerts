# 🚀 Vibe Alerts - Quick Setup Guide (100% FREE)

This guide will help you set up Vibe Alerts MVP using only free-tier services.

**Total Setup Time:** ~15 minutes  
**Cost:** $0/month (all free tiers)

---

## 📋 Prerequisites

- Python 3.11+ installed
- Terminal/Command line access
- Telegram account (for receiving alerts)

---

## Step 1: Install Redis (5 minutes)

Redis is used for caching and deduplication.

### macOS (using Homebrew):
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Redis
brew install redis

# Start Redis
brew services start redis

# Test Redis is running
redis-cli ping
# Should return: PONG
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# Test
redis-cli ping
```

### Alternative: Upstash Redis (Cloud - FREE)
If you don't want to install locally:
1. Go to https://upstash.com
2. Sign up (free, no credit card needed)
3. Create a Redis database
4. Copy the connection URL
5. Use this URL in your `.env` file

---

## Step 2: Set Up Neon DB (5 minutes)

Neon is a serverless PostgreSQL database with a generous free tier.

1. **Sign up:**
   - Go to https://neon.tech
   - Click "Sign up" (GitHub/Google login available)
   - No credit card required

2. **Create Project:**
   - Click "Create Project"
   - Name: `vibe_alerts`
   - Region: Choose closest to you (Mumbai for India)
   - Click "Create Project"

3. **Get Connection String:**
   - After creation, you'll see a connection string
   - Format: `postgresql://user:password@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require`
   - **Copy this - you'll need it in Step 4**

4. **Initialize Database:**
   ```bash
   # We'll do this after setting up .env
   ```

---

## Step 3: Create Telegram Bot & Channel (5 minutes)

### 3.1 Create Telegram Bot

1. **Open Telegram** (mobile or desktop app)

2. **Find BotFather:**
   - Search for `@BotFather` in Telegram
   - Start a conversation

3. **Create Bot:**
   - Send: `/newbot`
   - BotFather will ask for a name
   - Enter: `Vibe Alerts Bot` (or any name you like)
   - BotFather will ask for a username
   - Enter: `vibe_alerts_rohit_bot` (must end with 'bot' and be unique)
   - If taken, try: `vibe_alerts_[yourname]_bot`

4. **Copy Token:**
   - BotFather will give you a token like:
     ```
     1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
     ```
   - **Save this token - you'll need it in Step 4**

### 3.2 Create Telegram Channel

1. **Create Channel:**
   - In Telegram, tap menu → New Channel
   - Name: `Vibe Alerts Test` (or any name)
   - Description: (optional)
   - Choose **Public** channel
   - Username: `vibe_alerts_rohit` (must be unique)
   - If taken, try: `vibe_alerts_[yourname]`

2. **Add Bot as Admin:**
   - Go to your channel
   - Tap channel name → Administrators
   - Tap "Add Administrator"
   - Search for your bot username (`vibe_alerts_rohit_bot`)
   - Add it and grant **"Post Messages"** permission
   - Save

3. **Note Channel Username:**
   - Your channel username is: `@vibe_alerts_rohit`
   - **Save this - you'll need it in Step 4**

---

## Step 4: Configure Environment Variables

1. **Copy the example file:**
   ```bash
   cd /Users/rohit/Vibe_Alerts
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   nano .env
   # or use your preferred editor: code .env, vim .env, etc.
   ```

3. **Fill in your values:**
   ```bash
   # Paste your Neon DB connection string
   DATABASE_URL=postgresql://user:password@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require

   # Keep this if using local Redis
   REDIS_URL=redis://localhost:6379/0

   # Paste your bot token from BotFather
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

   # Paste your channel username (include @)
   TELEGRAM_CHANNEL_ID=@vibe_alerts_rohit
   ```

4. **Save and exit:**
   - In nano: `Ctrl+X`, then `Y`, then `Enter`
   - In vim: `:wq`

---

## Step 5: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 6: Initialize Database

```bash
# Load your DATABASE_URL from .env
source .env

# Run the schema
psql $DATABASE_URL -f src/database/schema.sql

# You should see: CREATE TABLE messages (one for each table)
```

---

## Step 7: Run Vibe Alerts! 🎉

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start the application
python main.py
```

**Expected Output:**
```
======================================================================
🚀 Vibe_Alerts MVP - Quarterly Results Real-Time Monitoring
======================================================================
📢 Channel: @vibe_alerts_rohit
⏱️  Poll interval: 3s
🔍 Monitoring sources: 2
======================================================================
Testing connections...
✅ Redis connected
✅ Telegram bot connected: @vibe_alerts_rohit_bot
======================================================================
🎯 All systems ready! Starting monitoring...
======================================================================
```

---

## ✅ Verification Steps

### 1. Test Telegram Bot
Send a test message to your channel:
```bash
# In a new terminal (keep main.py running)
python3 -c "
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'))
import asyncio
asyncio.run(bot.send_message(
    chat_id=os.getenv('TELEGRAM_CHANNEL_ID'),
    text='✅ Vibe Alerts is live!'
))
"
```

Check your Telegram channel - you should see the message!

### 2. Check Redis
```bash
redis-cli ping
# Should return: PONG

redis-cli KEYS "*"
# Should show any keys created by the app
```

### 3. Check Database
```bash
psql $DATABASE_URL -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
# Should list all tables: stock_symbols, analyst_estimates, etc.
```

---

## 🎯 What Happens Next?

Once running, Vibe Alerts will:

1. **Monitor NSE/BSE every 3 seconds** for new quarterly results
2. **Download and extract** financial metrics from PDFs
3. **Analyze** results vs estimates (if available)
4. **Send formatted alerts** to your Telegram channel within 10 seconds

**Note:** During non-result season, you might not see alerts immediately. The best time to test is during quarterly result seasons:
- **Q3 FY2025**: January 2025
- **Q4 FY2025**: April-May 2025

---

## 🐛 Troubleshooting

### "Redis connection failed"
```bash
# Check if Redis is running
redis-cli ping

# If not, start it
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### "Telegram bot connection failed"
- Double-check your bot token in `.env`
- Make sure there are no extra spaces
- Test your token: https://api.telegram.org/bot[YOUR_TOKEN]/getMe

### "Database connection error"
- Verify your DATABASE_URL in `.env`
- Make sure it ends with `?sslmode=require`
- Check Neon dashboard to ensure database is running

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📊 Monitoring Your App

### View Logs
```bash
# Live logs
tail -f logs/vibe_alerts_$(date +%Y-%m-%d).log

# Search for errors
grep ERROR logs/vibe_alerts_*.log
```

### Check Redis Cache
```bash
redis-cli

# See processed announcements
KEYS processed:*

# See cached estimates
KEYS estimates:*

# Exit
exit
```

---

## 🚀 Next Steps

Once your MVP is running:

1. **Add Test Estimates** to Redis for testing beat/miss calculations
2. **Monitor during result season** (January/April)
3. **Add Phase 2 features:**
   - User watchlists
   - Bot commands (/watch, /list)
   - Admin dashboard

---

## 💡 Tips

- **Keep it running 24/7** during result season for best coverage
- **Use `screen` or `tmux`** to keep it running after closing terminal:
  ```bash
  screen -S vibe_alerts
  python main.py
  # Press Ctrl+A, then D to detach
  # Reattach later: screen -r vibe_alerts
  ```
- **Set up on a cloud VM** (DigitalOcean, AWS free tier) for always-on monitoring

---

## 📞 Need Help?

- Check logs in `logs/` directory
- Review the main README.md for architecture details
- Check your .env file for correct values

**Happy Monitoring! 📈🚀**

