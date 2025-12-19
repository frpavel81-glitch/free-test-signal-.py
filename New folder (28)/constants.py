# constants.py - System-wide constants

# Signal Generation Constants
SIGNAL_MIN_SCORE = 15  # Minimum score required for 90%+ accuracy
SIGNAL_MIN_DIFF = 6    # Minimum difference between call/put scores
SIGNAL_MIN_STRONG_INDICATORS = 5  # Minimum strong indicators required

# RSI Thresholds
RSI_VERY_OVERSOLD = 25
RSI_OVERSOLD = 30
RSI_VERY_OVERBOUGHT = 75
RSI_OVERBOUGHT = 70

# EMA Thresholds
EMA_DIFF_VERY_STRONG = 0.15
EMA_DIFF_STRONG = 0.08

# SMA Thresholds
SMA_DIFF_EXTREMELY_STRONG = 0.2
SMA_DIFF_VERY_STRONG = 0.15

# MACD Thresholds
MACD_STRENGTH_VERY_STRONG = 0.0005
MACD_STRENGTH_STRONG = 0.0003
MACD_STRENGTH_MODERATE = 0.0002

# Stochastic Thresholds
STOCH_EXTREMELY_OVERSOLD = 10
STOCH_VERY_OVERSOLD = 15
STOCH_EXTREMELY_OVERBOUGHT = 90
STOCH_VERY_OVERBOUGHT = 85

# ADX Thresholds
ADX_EXTREMELY_STRONG = 40
ADX_VERY_STRONG = 35
ADX_WEAK = 25
ADX_MODERATE = 30

# Price Momentum Thresholds
MOMENTUM_EXTREMELY_STRONG = 0.1
MOMENTUM_VERY_STRONG = 0.07
MOMENTUM_STRONG = 0.05

# Bollinger Bands Thresholds
BB_WIDTH_HIGH = 0.3
BB_WIDTH_GOOD = 0.25

# VWAP Thresholds
VWAP_DIFF_VERY_SIGNIFICANT = 0.1
VWAP_DIFF_SIGNIFICANT = 0.07

# ATR (Volatility) Thresholds
ATR_EXTREMELY_HIGH = 1.5
ATR_TOO_HIGH = 1.0
ATR_TOO_LOW = 0.15
ATR_LOW = 0.2

# Trend Confirmation Thresholds
TREND_5_EXTREMELY_STRONG = 0.15
TREND_3_VERY_STRONG = 0.1
TREND_3_STRONG = 0.15

# Signal Generation Settings
TARGET_SIGNALS = 30
SIGNAL_INTERVAL_MINUTES = 8
DATA_FETCH_TIMEOUT = 20  # seconds
DATA_FETCH_WAIT_INTERVAL = 0.5  # seconds

# WebSocket Settings
WS_CONNECTION_TIMEOUT = 15  # seconds
WS_STABILIZE_DELAY = 2  # seconds
WS_REQUEST_DELAY = 0.1  # seconds between requests

# Result Verification Settings
FIRST_CANDLE_WAIT = 0.5  # seconds
SECOND_CANDLE_WAIT = 65  # seconds (1 minute + 5 seconds buffer)
VERIFICATION_TIMEOUT = 120  # seconds

# News Filter Settings
NEWS_BUFFER_MINUTES = 15
NEWS_FILTER_MAX_ATTEMPTS = 5

# Data Settings
OHLC_DEFAULT_SIZE = 50
OHLC_MAX_CANDLES = 200
PRICE_FETCH_TIMEOUT = 0.8  # seconds

# Memory Management
SIGNAL_CLEANUP_HOURS = 24
BATCH_CLEANUP_HOURS = 24

# Error Handling
ERROR_RESULT_UNKNOWN = None  # Don't default to WIN on errors
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

