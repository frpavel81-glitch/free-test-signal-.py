# config.py - Configuration settings (IMPROVED)

from dotenv import load_dotenv
import os
from logger_config import logger

load_dotenv()  # load from .env

# Telegram Bot API Token (REQUIRED)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
    logger.error("Please create a .env file with: TELEGRAM_BOT_TOKEN=your_token_here")
    raise ValueError("TELEGRAM_BOT_TOKEN is required. Set it in .env file or environment variables.")

# Telegram Client API credentials (optional - for future features)
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")

# Binary.com WebSocket URL
BINARY_WS_URL = os.getenv("BINARY_WS_URL", "wss://ws.binaryws.com/websockets/v3?app_id=1089")

# Database settings
DATABASE_PATH = os.getenv("DATABASE_PATH", "forex_bot.db")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/forex_bot.log")

def validate_config():
    """Validate that all required configuration is present"""
    errors = []
    
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN is required")
    
    if errors:
        error_msg = "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Configuration validated successfully")
    return True

# Validate on import
try:
    validate_config()
except ValueError:
    # Don't fail on import, but log the error
    pass
