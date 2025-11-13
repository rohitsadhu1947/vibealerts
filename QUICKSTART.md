# ⚡ Vibe Alerts - Quick Start (5 Steps, 15 Minutes)

**100% Free MVP Setup** - No credit card required for any service!

---

## 🎯 Step 1: Install Redis (2 minutes)

### macOS (Homebrew):
```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify it's running
redis-cli ping
# Should return: PONG
```

### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
redis-cli ping
```

### Windows:
Download from https://github.com/microsoftarchive/redis/releases
Or use **Upstash** (cloud, free): https://upstash.com

---

## 🗄️ Step 2: Set Up Neon DB (3 minutes)

1. Go to **https://neon.tech**
2. Sign up (free, no credit card)
3. Create project → Name: `vibe_alerts`
4. **Copy the connection string** - looks like:
   ```
   postgresql://user:password@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require
   ```
5. Keep this handy - you'll paste it in Step 4

---

## 📱 Step 3: Create Telegram Bot & Channel (5 minutes)

### Part A: Create Bot

1. Open **Telegram** app
2. Search for **@BotFather**
3. Send: `/newbot`
4. Bot name: `Vibe Alerts Bot`
5. Bot username: `vibe_alerts_yourname_bot` (must end with 'bot')
6. **Copy the token** - looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### Part B: Create Channel

1. In Telegram → **New Channel**
2. Name: `Vibe Alerts Test`
3. Make it **PUBLIC**
4. Username: `vibe_alerts_yourname`
5. Go to channel → **Settings → Administrators → Add Administrator**
6. Search for your bot username and **add it**
7. Grant **"Post Messages"** permission
8. **Save the channel username**: `@vibe_alerts_yourname`

---

## ⚙️ Step 4: Configure .env File (2 minutes)

```bash
# Navigate to project
cd /Users/rohit/Vibe_Alerts

# Copy example file
cp .env.example .env

# Edit with your favorite editor
nano .env
# or: code .env, vim .env, etc.
```

### Fill in these 4 values:

```bash
# Paste your Neon DB connection string
DATABASE_URL=postgresql://user:password@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require

# Keep this if using local Redis
REDIS_URL=redis://localhost:6379/0

# Paste your bot token from @BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Paste your channel username (include @)
TELEGRAM_CHANNEL_ID=@vibe_alerts_yourname
```

**Save and exit** (Ctrl+X, then Y, then Enter in nano)

---

## 🚀 Step 5: Install & Run (3 minutes)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
./scripts/init_db.sh

# Test your setup
python scripts/test_setup.py

# If all tests pass, start the app!
python main.py
```

---

## ✅ Success! You Should See:

```
======================================================================
🚀 Vibe_Alerts MVP - Quarterly Results Real-Time Monitoring
======================================================================
📢 Channel: @vibe_alerts_yourname
⏱️  Poll interval: 3s
🔍 Monitoring sources: 2
======================================================================
Testing connections...
✅ Redis connected
✅ Telegram bot connected: @vibe_alerts_yourname_bot
======================================================================
🎯 All systems ready! Starting monitoring...
======================================================================
```

Check your **Telegram channel** - the bot should be posting there!

---

## 🐛 Troubleshooting

### "Redis connection failed"
```bash
# Make sure Redis is running
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### "Telegram bot connection failed"
- Double-check token in `.env` (no extra spaces)
- Verify bot is added as **admin** to channel
- Test: https://api.telegram.org/bot[YOUR_TOKEN]/getMe

### "Database connection error"
- Verify `DATABASE_URL` in `.env`
- Must end with `?sslmode=require`
- Check Neon dashboard

### Run the test script:
```bash
python scripts/test_setup.py
```

This will check **all** your configuration!

---

## 📊 What Happens Now?

Vibe Alerts will:
1. Monitor **NSE/BSE every 3 seconds** for quarterly results
2. **Download PDFs** and extract financial metrics
3. **Analyze** results vs estimates
4. Send **formatted alerts** to your Telegram channel in **< 10 seconds**

**Note:** During non-result season you won't see many alerts. Best time to test:
- **Q3 FY2025**: January 2025  
- **Q4 FY2025**: April-May 2025

---

## 🎯 Next Steps

### Keep It Running 24/7:
```bash
# Use screen or tmux
screen -S vibe
python main.py
# Press Ctrl+A then D to detach
# Reattach: screen -r vibe
```

### View Logs:
```bash
tail -f logs/vibe_alerts_$(date +%Y-%m-%d).log
```

### Check Redis:
```bash
redis-cli
KEYS processed:*  # See processed results
KEYS estimates:*  # See cached estimates
exit
```

---

## 📚 More Help

- **Detailed Guide**: See `SETUP_GUIDE.md`
- **Architecture**: See main `README.md`
- **Test Setup**: Run `python scripts/test_setup.py`

---

**Happy Monitoring! 🚀📈**

Built with ❤️ for Indian stock traders

