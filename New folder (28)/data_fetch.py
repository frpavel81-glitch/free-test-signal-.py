# data_fetch.py - Forex Market Data Fetching via Binary.com WebSocket (IMPROVED)

import websocket
import json
import threading
import time
import pandas as pd
from datetime import datetime, timedelta
from config import BINARY_WS_URL
from signal_generator import FOREX_PAIRS, BINARY_SYMBOL_MAP
from constants import (
    WS_CONNECTION_TIMEOUT, WS_STABILIZE_DELAY, WS_REQUEST_DELAY,
    DATA_FETCH_TIMEOUT, DATA_FETCH_WAIT_INTERVAL, OHLC_MAX_CANDLES,
    PRICE_FETCH_TIMEOUT, MAX_RETRY_ATTEMPTS, RETRY_DELAY
)
from logger_config import logger

# Global variables for WebSocket data
_ws = None
_price_data = {}
_ohlc_data = {}
_ohlc_cache = {}  # Cache with timestamps
_cache_duration = 30  # Cache for 30 seconds
_ws_lock = threading.Lock()
_connected = False
_connection_event = threading.Event()
_data_received_event = threading.Event()
_last_connection_attempt = None
_connection_retries = 0

def _on_message(ws, message):
    """Handle incoming WebSocket messages from Binary.com"""
    global _price_data, _ohlc_data, _data_received_event, _ohlc_cache
    
    try:
        data = json.loads(message)
        
        # Handle errors
        if 'error' in data:
            error_msg = data.get('error', {})
            if isinstance(error_msg, dict):
                error_code = error_msg.get('code', '')
                error_message = error_msg.get('message', '')
                logger.error(f"WebSocket error - Code={error_code}, Message={error_message}")
            else:
                logger.error(f"WebSocket error: {error_msg}")
            return
        
        # Handle candles data - Binary.com format: {"candles": [...], "echo_req": {"ticks_history": "frxEURUSD"}}
        if 'candles' in data and isinstance(data.get('candles'), list):
            echo_req = data.get('echo_req', {})
            symbol = echo_req.get('ticks_history', '')
            
            if not symbol:
                symbol = echo_req.get('candles', '')
            
            candles_list = data.get('candles', [])
            
            if symbol and candles_list:
                with _ws_lock:
                    valid_candles = []
                    for candle in candles_list:
                        if isinstance(candle, dict):
                            # Validate candle has required fields
                            if (candle.get('open') is not None and 
                                candle.get('close') is not None and
                                candle.get('epoch') is not None):
                                valid_candles.append(candle)
                    
                    if valid_candles:
                        _ohlc_data[symbol] = valid_candles
                        _ohlc_cache[symbol] = {
                            'data': valid_candles,
                            'timestamp': datetime.now()
                        }
                        logger.debug(f"Received {len(valid_candles)} candles for {symbol}")
                        _data_received_event.set()  # Signal that we got data
        
        # Handle tick data (fallback)
        if 'tick' in data:
            tick = data['tick']
            symbol = tick.get('symbol', '')
            quote = tick.get('quote', 0)
            epoch = tick.get('epoch', 0)
            if symbol and quote:
                with _ws_lock:
                    _price_data[symbol] = quote
                    # Create simple candle from tick
                    if symbol not in _ohlc_data:
                        _ohlc_data[symbol] = []
                    tick_candle = {
                        'epoch': epoch,
                        'open': quote,
                        'high': quote,
                        'low': quote,
                        'close': quote
                    }
                    if not any(c.get('epoch') == epoch for c in _ohlc_data[symbol]):
                        _ohlc_data[symbol].append(tick_candle)
                        if len(_ohlc_data[symbol]) > OHLC_MAX_CANDLES:
                            _ohlc_data[symbol] = _ohlc_data[symbol][-OHLC_MAX_CANDLES:]
    
    except Exception as e:
        print(f"[ERROR] Processing message: {e}")

def _on_error(ws, error):
    """Handle WebSocket errors"""
    logger.error(f"WebSocket error: {error}")

def _on_close(ws, close_status_code, close_msg):
    """Handle WebSocket close"""
    global _connected, _connection_retries
    _connected = False
    _connection_event.clear()
    _connection_retries = 0
    logger.info(f"WebSocket connection closed (code: {close_status_code}, msg: {close_msg})")

def _on_open(ws):
    """Handle WebSocket open"""
    global _connected, _connection_retries
    _connected = True
    _connection_retries = 0
    _connection_event.set()
    logger.info("WebSocket connected to Binary.com")

def _ensure_connection(retry=True):
    """Ensure WebSocket connection is established with retry logic"""
    global _ws, _connected, _last_connection_attempt, _connection_retries
    
    # Check if connection is still valid
    if _ws is not None and _connected:
        try:
            if hasattr(_ws, 'sock') and _ws.sock:
                # Check if socket is still alive
                try:
                    _ws.sock.getpeername()
                    return True
                except:
                    logger.warning("Socket appears disconnected, reconnecting...")
                    _connected = False
        except:
            pass
    
    # Rate limiting: don't retry too frequently
    if _last_connection_attempt:
        time_since_last = (datetime.now() - _last_connection_attempt).total_seconds()
        if time_since_last < RETRY_DELAY:
            time.sleep(RETRY_DELAY - time_since_last)
    
    _last_connection_attempt = datetime.now()
    
    for attempt in range(MAX_RETRY_ATTEMPTS if retry else 1):
        try:
            logger.info(f"Establishing WebSocket connection (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS})...")
            _connected = False
            _connection_event.clear()
            
            _ws = websocket.WebSocketApp(
                BINARY_WS_URL,
                on_message=_on_message,
                on_error=_on_error,
                on_close=_on_close,
                on_open=_on_open
            )
            
            wst = threading.Thread(target=_ws.run_forever)
            wst.daemon = True
            wst.start()
            
            if not _connection_event.wait(timeout=WS_CONNECTION_TIMEOUT):
                raise Exception(f"Connection timeout after {WS_CONNECTION_TIMEOUT}s")
            
            time.sleep(WS_STABILIZE_DELAY)  # Wait for connection to stabilize
            logger.info("WebSocket ready")
            _connection_retries = 0
            return True
            
        except Exception as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            _connected = False
            _ws = None
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
    
    # All retries failed
    logger.error("Failed to establish WebSocket connection after all retries")
    raise Exception("WebSocket connection failed after retries")

def get_all_ohlc_data(outputsize=50) -> dict:
    """
    Get OHLC data for all forex pairs.
    Returns dictionary with binary symbols as keys and DataFrames as values.
    """
    global _data_received_event
    
    try:
        logger.info(f"Starting data fetch for {len(FOREX_PAIRS)} pairs...")
        _ensure_connection()
        
        if not _ws or not _connected:
            raise Exception("WebSocket not connected")
        
        # Clear the data received event
        _data_received_event.clear()
        
        # Request candles for all pairs
        print(f"[INFO] Sending requests for {len(FOREX_PAIRS)} pairs...")
        request_count = 0
        
        for pair in FOREX_PAIRS:
            binary_symbol = BINARY_SYMBOL_MAP.get(pair)
            if binary_symbol:
                try:
                    request = {
                        "ticks_history": binary_symbol,
                        "end": "latest",
                        "count": outputsize,
                        "granularity": 60,
                        "style": "candles"
                    }
                    _ws.send(json.dumps(request))
                    request_count += 1
                    time.sleep(WS_REQUEST_DELAY)  # Small delay between requests
                except Exception as e:
                    logger.error(f"Failed to send request for {pair}: {e}")
        
        logger.info(f"Sent {request_count} requests, waiting for data...")
        
        # Wait for at least some data to arrive
        max_wait = DATA_FETCH_TIMEOUT
        wait_interval = DATA_FETCH_WAIT_INTERVAL
        waited = 0
        result = {}
        
        while waited < max_wait:
            time.sleep(wait_interval)
            waited += wait_interval
            
            with _ws_lock:
                # Process all available data
                for pair in FOREX_PAIRS:
                    binary_symbol = BINARY_SYMBOL_MAP.get(pair)
                    if binary_symbol and binary_symbol not in result:
                        candles = _ohlc_data.get(binary_symbol, [])
                        
                        if candles and len(candles) > 0:
                            # Convert to DataFrame
                            df_data = []
                            for candle in candles[-outputsize:]:
                                if isinstance(candle, dict):
                                    epoch = candle.get('epoch', 0)
                                    if epoch == 0:
                                        continue
                                    
                                    open_val = candle.get('open', 0)
                                    high_val = candle.get('high', 0)
                                    low_val = candle.get('low', 0)
                                    close_val = candle.get('close', 0)
                                    
                                    # Skip invalid data
                                    if open_val == 0 and high_val == 0 and low_val == 0 and close_val == 0:
                                        continue
                                    
                                    df_data.append({
                                        'timestamp': epoch,
                                        'open': float(open_val),
                                        'high': float(high_val),
                                        'low': float(low_val),
                                        'close': float(close_val)
                                    })
                            
                            if df_data:
                                df = pd.DataFrame(df_data)
                                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', errors='coerce')
                                
                                # Ensure numeric columns
                                for col in ['open', 'high', 'low', 'close']:
                                    if col in df.columns:
                                        df[col] = pd.to_numeric(df[col], errors='coerce')
                                
                                df = df.dropna(subset=['open', 'high', 'low', 'close'])
                                
                                if not df.empty:
                                    df = df.sort_values(by='timestamp')
                                    df.reset_index(drop=True, inplace=True)
                                    result[binary_symbol] = df
                                    logger.debug(f"Processed {len(df)} candles for {binary_symbol}")
            
            # If we have data for at least some pairs, we can proceed
            if len(result) > 0:
                logger.info(f"Got data for {len(result)}/{len(FOREX_PAIRS)} pairs")
                break
            
            # Check if we received any data at all
            with _ws_lock:
                if len(_ohlc_data) > 0:
                    logger.debug(f"Waiting... ({waited:.1f}s/{max_wait}s) - Found {len(_ohlc_data)} symbols with data")
        
        if not result:
            with _ws_lock:
                available = list(_ohlc_data.keys())
                logger.warning(f"No processed data. Available symbols: {available}")
                if available:
                    logger.info("Data received but couldn't process. Check candle format.")
            raise Exception(f"No OHLC data received. Available: {available}")
        
        logger.info(f"Returning data for {len(result)} pairs")
        return result
    
    except Exception as e:
        logger.error(f"get_all_ohlc_data failed: {e}", exc_info=True)
        return {}

def get_price(pair: str, use_cache: bool = True) -> float:
    """Get current price for a specific forex pair with caching"""
    try:
        binary_symbol = BINARY_SYMBOL_MAP.get(pair)
        if not binary_symbol:
            logger.warning(f"Unknown pair: {pair}")
            return None
        
        # Check cache first
        if use_cache:
            with _ws_lock:
                cached = _ohlc_cache.get(binary_symbol)
                if cached:
                    cache_age = (datetime.now() - cached['timestamp']).total_seconds()
                    if cache_age < _cache_duration:
                        candles = cached['data']
                        if candles:
                            latest = candles[-1]
                            if isinstance(latest, dict):
                                price = latest.get('close', 0)
                                if price > 0:
                                    logger.debug(f"Using cached price for {pair}: {price}")
                                    return float(price)
        
        # Fetch fresh price
        _ensure_connection()
        
        if _ws and _connected:
            request = {"ticks": binary_symbol}
            _ws.send(json.dumps(request))
            time.sleep(PRICE_FETCH_TIMEOUT)
        
        with _ws_lock:
            price = _price_data.get(binary_symbol, 0)
            if price == 0:
                candles = _ohlc_data.get(binary_symbol, [])
                if candles:
                    latest = candles[-1]
                    if isinstance(latest, dict):
                        price = latest.get('close', 0)
        
        result = float(price) if price > 0 else None
        if result:
            logger.debug(f"Fetched price for {pair}: {result}")
        else:
            logger.warning(f"Could not get price for {pair}")
        return result
    
    except Exception as e:
        logger.error(f"get_price failed for {pair}: {e}", exc_info=True)
        return None

# Legacy functions
def get_chfjpy_price():
    return get_price("CHFJPY")

def get_ohlc_data(interval='1min', outputsize=50):
    all_data = get_all_ohlc_data(outputsize)
    return all_data.get("frxCHFJPY", None)
