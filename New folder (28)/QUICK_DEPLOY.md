# ⚡ Quick Deploy Guide - Railway (5 Minutes)

## 🎯 **Recommended: Railway.app**

**Best for hobbyists - Free tier with always-on!**

---

## 📋 **Prerequisites (2 minutes)**

1. ✅ GitHub account (free) - https://github.com
2. ✅ Telegram bot token from @BotFather
3. ✅ Your code ready

---

## 🚀 **Deployment Steps (5 minutes)**

### **Step 1: Push to GitHub** (2 min)

```bash
# In your project folder
git init
git add .
git commit -m "Deploy to Railway"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

**Or use GitHub Desktop:**
- File → Add Local Repository
- Publish to GitHub

---

### **Step 2: Sign Up Railway** (1 min)

1. Go to **https://railway.app**
2. Click **"Start a New Project"**
3. Click **"Login with GitHub"**
4. Authorize Railway

✅ Done!

---

### **Step 3: Deploy** (1 min)

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Click **"Deploy Now"**

⏳ Wait 2-3 minutes...

---

### **Step 4: Add Bot Token** (1 min)

1. Click your **service** (deployed app)
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add:
   ```
   Name: TELEGRAM_BOT_TOKEN
   Value: your_bot_token_here
   ```
5. Click **"Add"**

**Get token from @BotFather on Telegram**

---

### **Step 5: Set Start Command** (30 sec)

1. Go to **"Settings"** tab
2. Find **"Start Command"**
3. Set to: `python bot.py`
4. Click **"Save"**

---

### **Step 6: Verify** (30 sec)

1. Go to **"Deployments"** → **"View Logs"**
2. Look for: `Bot is running! Send /start in Telegram to begin.`
3. Test in Telegram: Send `/start` to your bot

✅ **Done! Your bot is live!**

---

## 🎉 **That's It!**

**Total Time:** ~5 minutes
**Cost:** FREE (usually stays under $5/month credit)
**Status:** Always-on, 24/7

---

## 🔍 **Quick Troubleshooting**

### Bot not responding?
- ✅ Check logs in Railway
- ✅ Verify `TELEGRAM_BOT_TOKEN` is set
- ✅ Ensure token is valid

### Deployment failed?
- ✅ Check `requirements.txt` exists
- ✅ Verify `bot.py` is in root
- ✅ Check logs for errors

---

## 📊 **Monitor Your Bot**

- **Logs:** Deployments → View Logs
- **Usage:** Usage tab (see credit usage)
- **Metrics:** Performance metrics

---

**🪐 Deploy in 5 minutes with Railway! 🪐**

