# 🚀 Quick Deploy to Railway + Neon

## TL;DR (5 Minutes)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/Vibe_Alerts.git
git push -u origin main

# 2. Deploy to Railway (via dashboard)
# - Go to https://railway.app
# - New Project → Deploy from GitHub
# - Select Vibe_Alerts repo
# - Add Redis service
# - Add these environment variables:
#   DATABASE_URL = your Neon DB URL
#   TELEGRAM_BOT_TOKEN = your bot token
#   TELEGRAM_CHANNEL_ID = @your_channel
# - Deploy!
```

That's it! Your app will run 24/7 on Railway + Neon. 🎉

---

## Why Railway > Vercel for This App?

| Feature | Railway | Vercel |
|---------|---------|--------|
| Long-running processes | ✅ Yes | ❌ No (60s max) |
| 24/7 monitoring | ✅ Yes | ❌ Cron only |
| 3-second polling | ✅ Yes | ❌ 60s minimum |
| Worker processes | ✅ Native | ❌ Not supported |
| Redis included | ✅ Yes | ⚠️ Paid add-on |
| **Cost (free tier)** | ✅ $5 credit | ❌ Won't work |

**Verdict**: Railway is perfect for this. Vercel is not designed for background workers.

---

## Step-by-Step Railway Deployment

### 1. Push to GitHub

```bash
cd /Users/rohit/Vibe_Alerts

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - Vibe Alerts MVP"

# Create main branch
git branch -M main

# Add your GitHub repo (create it first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/Vibe_Alerts.git

# Push
git push -u origin main
```

### 2. Deploy on Railway Dashboard

**Step 1**: Go to https://railway.app and sign in

**Step 2**: Click "New Project"

**Step 3**: Choose "Deploy from GitHub repo"

**Step 4**: Select `Vibe_Alerts` repository

**Step 5**: Add Redis Service
- Click "+ New"
- Select "Redis"
- Railway will provide `REDIS_URL` automatically

**Step 6**: Configure Environment Variables
Click on your service → Variables → Add:

```
DATABASE_URL = postgresql://user:pass@ep-xxxxx.neon.tech/vibe_alerts?sslmode=require
TELEGRAM_BOT_TOKEN = 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID = @vibe_alerts_yourname
LOG_LEVEL = INFO
ENVIRONMENT = production
```

**Step 7**: Deploy
- Click "Deploy"
- Watch logs to ensure it starts correctly

**Step 8**: Check Logs
- Click on your service
- Go to "Logs" tab
- You should see:
  ```
  🚀 Vibe_Alerts MVP - Quarterly Results Real-Time Monitoring
  ✅ Redis connected
  ✅ Telegram bot connected
  🎯 All systems ready! Starting monitoring...
  ```

**Done!** Your app is now running 24/7 on Railway. 🎉

---

## Cost Estimate

### Railway Free Tier
- **$5 credit per month**
- Your usage:
  - Worker process: ~$3-4/month
  - Redis: $1-2/month
  - **Total: ~$5/month** (covered by free tier!)

### Neon DB Free Tier
- **512 MB storage**
- **Always-on compute**
- **$0/month**

### Telegram
- **Free & unlimited**

**Total Monthly Cost: $0** (within free tiers) 🎉

---

## Alternative: Render (If Railway Doesn't Work)

```bash
# Create render.yaml (already provided)
git push

# Then:
# 1. Go to https://render.com
# 2. New → Worker
# 3. Connect GitHub
# 4. Select Vibe_Alerts
# 5. Add environment variables
# 6. Deploy
```

Render free tier: Worker sleeps after 15 min inactivity (not ideal for monitoring)
Render paid: $7/month for always-on worker

---

## Monitoring Your Deployment

### Railway Logs
```
https://railway.app/project/YOUR_PROJECT/service/YOUR_SERVICE/logs
```

### Check if Running
Your Telegram channel should start receiving alerts!

### View Metrics
Railway dashboard shows:
- CPU usage
- Memory usage
- Network traffic
- Restart count

---

## Updating Your Deployment

```bash
# Make changes to your code
# ...

# Commit and push
git add .
git commit -m "Update: description of changes"
git push

# Railway auto-deploys on push! 🚀
```

---

## Troubleshooting

### "Redis connection failed"
- Check Railway Redis service is running
- Verify REDIS_URL is set correctly

### "Telegram bot connection failed"
- Verify TELEGRAM_BOT_TOKEN in Railway variables
- Check bot is still admin in channel

### "Database connection error"
- Verify DATABASE_URL points to Neon DB
- Check Neon DB is not suspended

### View Detailed Logs
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs
```

---

## 🎯 Summary

**Best Setup for Your Use Case:**
- ✅ **GitHub**: Version control
- ✅ **Railway**: 24/7 hosting ($0 with free tier)
- ✅ **Neon DB**: PostgreSQL ($0 free tier)
- ✅ **Railway Redis**: Caching ($0 included)
- ✅ **Telegram**: Alerts ($0 unlimited)

**Total: $0/month for MVP** 🎉

**Next**: Push to GitHub, then deploy to Railway!

