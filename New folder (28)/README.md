# 🪐 THE-SMART-CHEAT-V2 X SUPRE ELITE 🪐

A powerful **Telegram bot** that delivers **real-time forex trading signals** with **100% accurate result verification** and **Martingale (MTG) system with second candle confirmation**. The system generates 10 signals over 2 hours and automatically verifies trade results with win/loss statistics.

---

## 🚀 Features

### Core Features
- 🔄 **Automatic Signal Generation**: Generates exactly 10 signals spread over 2 hours
- 📊 **11 Major Forex Pairs**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY, NZDCHF
- ⏰ **UTC+6 Timezone**: All signals in UTC+6 (Asia/Dhaka) timezone
- 🎯 **100% Accurate Verification**: Verifies actual trade results by comparing entry vs exit prices

### Advanced MTG System
- 🔥 **Second Candle Confirmation**: If first candle loses, waits for second candle
  - If second candle confirms signal direction → **MTG WIN** ✅{MTG_COUNT}
  - If second candle also loses → **Actual Loss** ❌
- 📈 **Martingale Tracking**: Tracks MTG levels per pair with automatic reset on wins

### Real-Time Updates
- ⚡ **Individual Result Updates**: Sends result immediately when each signal expires
- 📊 **Automatic Final Summary**: Sends complete statistics when all trades close
- 📈 **Win/Loss Statistics**: Shows total trades, wins, losses, and accuracy percentage

### User Interface
- 🎨 **Inline Buttons**: Easy-to-use "Generate Signal" and "Result" buttons
- 📱 **Manual Results**: Click "Result" button anytime to see current results
- 🔔 **Automatic Notifications**: Receives updates without manual checking

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.8+ | Core programming language |
| **Bot Framework** | python-telegram-bot | Telegram bot interface |
| **Data Source** | Binary.com WebSocket API | Real-time forex price data |
| **Technical Analysis** | ta library | RSI, EMA, SMA indicators |
| **Data Processing** | pandas | OHLC data manipulation |
| **Timezone** | pytz | UTC+6 timezone handling |
| **WebSocket** | websocket-client | Real-time data streaming |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Internet connection for WebSocket data

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd <repository-folder>
```

### Step 2: Create Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

Or edit `config.py` directly:
```python
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token_here"
```

---

## ✅ Usage

### Start the Bot
```bash
python bot.py
```

You should see:
```
============================================================
FOREX SIGNAL BOT STARTING...
============================================================
Bot is running! Send /start in Telegram to begin.
============================================================
```

### Using the Bot

1. **Start the Bot**: Send `/start` in Telegram
2. **Generate Signals**: Click "🔄 Generate Signal" button
3. **View Results**: 
   - Click "📊 Result" anytime for manual results
   - Or wait for automatic updates when trades close

### Signal Format
```
⏰ SELECT BROKER TIME UTC: +6:00
♾️ MARTINGALE:-1
1 MINUTES:-
EURUSD-OTC,19:12 M1 CALL
GBPUSD-OTC,19:24 M1 PUT
USDJPY-OTC,19:36 M1 CALL
... (10 signals total)

🪐✧THE-SMART-CHEAT-V2 X SUPRE ELITE✧🪐

MUST FOLLOW TREND 💯
MUST USE SAFETY MARGIN 💯
AVOID GAP UP/DOWN & BIG CANDLE🔻
AVOID DOJI & BIG WICKS🔻
DON'T TRADE BELOW 80% MARKET 📊
```

### Result Format
```
EURUSD-OTC,19:12 M1 CALL ✅
GBPUSD-OTC,19:24 M1 PUT ✅2
USDJPY-OTC,19:36 M1 CALL ❌
... (all signals)

100% ACCURACY SIGNAL DONE..😮‍💨🔥

==================================================
📊 TRADE STATISTICS
==================================================
Total Trades: 10
✅ Wins: 9 (90.0%)
❌ Losses: 1 (10.0%)
==================================================
🎯 ACCURACY: 90.0%
==================================================
```

---

## 🧠 How It Works

### Signal Generation
1. **Data Fetching**: Connects to Binary.com WebSocket API
2. **Technical Analysis**: Calculates RSI, EMA, SMA for each pair
3. **Signal Logic**: Generates CALL/PUT signals based on indicators
4. **Guaranteed Output**: Always generates exactly 10 signals

### Result Verification
1. **Entry Price**: Captured when signal is generated
2. **First Candle**: Checked 1 minute after signal time
   - If win → Direct win ✅
   - If loss → Wait for second candle
3. **Second Candle (MTG)**: Checked 2 minutes after signal time
   - If confirms signal → MTG win ✅{MTG_COUNT}
   - If also loses → Actual loss ❌

### Automatic Updates
- **Individual Results**: Sent immediately when each signal expires
- **Final Summary**: Sent automatically when all 10 signals complete
- **Statistics**: Calculates win rate, loss rate, and accuracy

---

## 📊 MTG System Explained

### Direct Win
- First candle confirms signal direction
- Result: `✅` (no MTG count)

### MTG Win
- First candle loses
- Second candle confirms signal direction
- Result: `✅1`, `✅2`, etc. (shows MTG level used)

### Actual Loss
- Both first and second candles lose
- Result: `❌`

### Example Flow
```
Signal: GBPJPY-OTC,18:36 M1 PUT

[First Candle - 18:36 to 18:37]
Entry: 150.500
Exit: 150.550 (price went UP - LOSS)
→ Waiting for second candle...

[Second Candle - 18:37 to 18:38]
Entry: 150.550
Exit: 150.480 (price went DOWN - confirms PUT)
→ MTG WIN! ✅1
```

---

## 🚀 Deployment

### Local Deployment
```bash
python bot.py
```

### Cloud Deployment (Pella.app)
See [PELLA_DEPLOY.md](PELLA_DEPLOY.md) for detailed deployment instructions.

---

## 📁 Project Structure

```
.
├── bot.py                 # Main Telegram bot application
├── result_tracker.py      # Result tracking and MTG system
├── signal_generator.py    # Signal generation logic
├── data_fetch.py          # WebSocket data fetching
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── PELLA_DEPLOY.md       # Deployment guide
└── .gitignore           # Git ignore file
```

---

## 🔧 Configuration

### Supported Forex Pairs
- EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD
- USDCAD, NZDUSD, EURGBP, EURJPY, GBPJPY, NZDCHF

### Signal Settings
- **Timeframe**: 1 minute (M1)
- **Signal Count**: 10 signals per batch
- **Time Span**: 2 hours (12-minute intervals)
- **Timezone**: UTC+6 (Asia/Dhaka)

---

## 🐛 Troubleshooting

### Bot Not Starting
- Check if `TELEGRAM_BOT_TOKEN` is set correctly
- Ensure no other bot instance is running
- Check internet connection

### No Signals Generated
- Verify WebSocket connection in logs
- Check Binary.com API status
- Review error messages in terminal

### Results Not Showing
- Wait for signal expiry time (1 minute after signal time)
- Check if background task is running
- Verify result verification logs

---

## 📈 Features in Detail

### Real-Time Individual Updates
- Each signal result sent immediately when it expires
- Shows: `PAIR-OTC,TIME M1 SIGNAL ✅/❌ (WIN/LOSS/MTG WIN)`

### Automatic Final Summary
- Sent when all 10 signals complete
- Includes all results and statistics
- Shows win rate and accuracy percentage

### Manual Result Button
- Click "📊 Result" anytime
- Shows all completed signals
- Displays current statistics

---

## 🔐 Security

- **Environment Variables**: Store sensitive tokens in `.env` file
- **Git Ignore**: `.env` file is excluded from version control
- **Token Security**: Never commit bot tokens to repository

---

## 📝 License

MIT License © 2025

---

## 🆘 Support

For issues or questions:
1. Check the logs in terminal
2. Review error messages
3. Verify configuration settings

---

## 🎯 Credits

**🪐 THE-SMART-CHEAT-V2 X SUPRE ELITE 🪐**

- Built with advanced MTG system
- 100% accurate result verification
- Real-time signal generation
- Automatic statistics calculation

---

## 📊 System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 512MB (1GB recommended)
- **Internet**: Stable connection for WebSocket
- **Platform**: Windows, Linux, macOS, or cloud (Pella.app)

---

**Ready to generate accurate forex signals with MTG confirmation! 🚀**
