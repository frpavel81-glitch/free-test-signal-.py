# Setup Guide - Improved Forex Signal Bot

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

**Important:** Get your bot token from [@BotFather](https://t.me/BotFather) on Telegram.

### 3. Run the Bot
```bash
python bot.py
```

## What's New

### ✅ All Critical Improvements Implemented

1. **Fixed Critical Bugs**
   - Signal generation now works correctly
   - All signals are properly stored
   - No more unreachable code

2. **Better Error Handling**
   - No more false wins on errors
   - Unverifiable signals marked as "❓"
   - Proper error logging

3. **Database Persistence**
   - All signals saved to SQLite database
   - Historical data available
   - Automatic cleanup

4. **Professional Logging**
   - Color-coded console output
   - File logging to `logs/forex_bot.log`
   - Configurable log levels

5. **Security**
   - No hardcoded credentials
   - Environment variable validation
   - Secure configuration

6. **Performance**
   - Data caching (30 seconds)
   - Connection retry logic
   - Memory management

7. **Code Quality**
   - Constants file for all magic numbers
   - Better code organization
   - Improved maintainability

## Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|-----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | - | Telegram bot token |
| `DATABASE_PATH` | No | `forex_bot.db` | Database file path |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | No | `logs/forex_bot.log` | Log file path |
| `BINARY_WS_URL` | No | `wss://ws.binaryws.com/...` | WebSocket URL |

### Example `.env` File
```env
# Required
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Optional
DATABASE_PATH=forex_bot.db
LOG_LEVEL=INFO
LOG_FILE=logs/forex_bot.log
```

## File Structure

```
.
├── bot.py                 # Main bot application
├── result_tracker.py      # Result tracking (IMPROVED)
├── signal_generator.py    # Signal generation (FIXED)
├── data_fetch.py          # Data fetching (IMPROVED)
├── config.py              # Configuration (IMPROVED)
├── constants.py           # Constants (NEW)
├── logger_config.py       # Logging (NEW)
├── database.py            # Database (NEW)
├── news_filter.py         # News filtering
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (CREATE THIS)
├── forex_bot.db           # Database (auto-created)
└── logs/                  # Log files (auto-created)
    └── forex_bot.log
```

## Troubleshooting

### Bot Won't Start
1. Check that `TELEGRAM_BOT_TOKEN` is set in `.env`
2. Verify token is valid (get new one from @BotFather if needed)
3. Check logs in `logs/forex_bot.log`

### No Signals Generated
1. Check WebSocket connection in logs
2. Verify internet connection
3. Check Binary.com API status

### Database Errors
- Database is optional - bot works without it
- If database fails, check file permissions
- Delete `forex_bot.db` to reset database

### Connection Issues
- Bot automatically retries connections
- Check firewall settings
- Verify WebSocket URL is accessible

## Logging

### View Logs
```bash
# Real-time logs
tail -f logs/forex_bot.log

# Last 100 lines
tail -n 100 logs/forex_bot.log
```

### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

Set in `.env`:
```env
LOG_LEVEL=DEBUG
```

## Database

### Location
- Default: `forex_bot.db` in project root
- Change via `DATABASE_PATH` in `.env`

### Tables
- `signals`: All generated signals
- `batches`: Signal batches
- `statistics`: Performance statistics
- `price_history`: Historical price data

### Query Example
```python
import sqlite3
conn = sqlite3.connect('forex_bot.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM signals WHERE status='completed'")
results = cursor.fetchall()
```

## Performance Tips

1. **Caching**: Price data cached for 30 seconds
2. **Cleanup**: Old data automatically cleaned after 24 hours
3. **Connection**: WebSocket connection reused
4. **Retry**: Automatic retry with exponential backoff

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git
- Keep bot token secret
- Use environment variables in production
- Regularly rotate tokens

## Support

For issues:
1. Check `logs/forex_bot.log` for errors
2. Review `IMPROVEMENTS_SUMMARY.md` for changes
3. Verify configuration in `.env`

---

**Version:** 2.0 (Improved)
**Last Updated:** 2025-01-XX

