# ⚡ Render Quick Start - 10 Minutes

## 🎯 **Quick Deployment Steps**

### **1. Push to GitHub** (2 min)
```bash
git init
git add .
git commit -m "Deploy to Render"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main
```

### **2. Sign Up Render** (1 min)
- Go to https://render.com
- Click "Get Started for Free"
- Sign up with GitHub

### **3. Create Web Service** (2 min)
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Select your repository

### **4. Configure** (3 min)
```
Name: forex-signal-bot
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot.py
Plan: Starter ($7/month) ⚠️ REQUIRED for always-on
```

### **5. Add Environment Variables** (1 min)
```
TELEGRAM_BOT_TOKEN = your_bot_token_here
```
Get token from @BotFather on Telegram

### **6. Deploy** (1 min)
- Click "Create Web Service"
- Wait 3-5 minutes
- Check logs for "Bot is running!"

### **7. Test** (30 sec)
- Send `/start` to your bot in Telegram
- Click "🔄 Generate Signal"
- Verify signals appear

✅ **Done!**

---

## ⚠️ **IMPORTANT: Plan Selection**

- **Free Plan:** Sleeps after 15 min ❌ (Not for bots)
- **Starter Plan ($7/month):** Always-on ✅ (Required!)

**For Telegram bots, you MUST use Starter Plan ($7/month)**

---

## 📋 **Checklist**

- [ ] Code on GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Plan: Starter ($7/month)
- [ ] `TELEGRAM_BOT_TOKEN` added
- [ ] Service deployed
- [ ] Bot responds in Telegram

---

## 🔍 **Troubleshooting**

**Bot not responding?**
- Check logs in Render
- Verify token is set
- Ensure Starter plan is selected

**Deployment failed?**
- Check `requirements.txt` exists
- Verify `bot.py` in root
- Check build logs

---

## 📖 **Full Guide**

See `RENDER_DEPLOY.md` for complete instructions.

---

**🪐 Deploy to Render in 10 minutes! 🪐**

