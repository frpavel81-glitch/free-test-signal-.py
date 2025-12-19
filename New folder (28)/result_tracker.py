# result_tracker.py - Track and Display Trading Results with Martingale (IMPROVED)

from datetime import datetime, timedelta
import pytz
import threading
from typing import Optional, Tuple
from data_fetch import get_price, BINARY_SYMBOL_MAP
from constants import FIRST_CANDLE_WAIT, SECOND_CANDLE_WAIT, ERROR_RESULT_UNKNOWN, SIGNAL_CLEANUP_HOURS
from logger_config import logger

# Try to import database, but don't fail if it doesn't exist
try:
    from database import db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger.warning("Database module not available, running without persistence")

class ResultTracker:
    def __init__(self):
        self.active_signals = {}  # {signal_id: signal_dict}
        self.completed_signals = []  # List of completed signals with results
        self.martingale_tracker = {}  # Track MTG count per pair sequence
        self.signal_batches = {}  # {batch_id: {'signals': [signal_ids], 'user_id': user_id, 'chat_id': chat_id}}
        self._verification_lock = threading.Lock()  # Lock for thread-safe verification
        
    def add_signal(self, signal_id: str, signal_dict: dict, batch_id: str = None, user_id: int = None, chat_id: int = None):
        """Add a new signal to track"""
        self.active_signals[signal_id] = {
            **signal_dict,
            'added_at': datetime.now(),
            'status': 'pending',
            'signal_id': signal_id,
            'mtg_count': 0,  # Initialize MTG count
            'batch_id': batch_id,
            'user_id': user_id,
            'chat_id': chat_id,
            'entry_price': signal_dict.get('entry_price')  # Use provided entry price
        }
        
        # Track batch
        if batch_id:
            if batch_id not in self.signal_batches:
                self.signal_batches[batch_id] = {
                    'signals': [],
                    'user_id': user_id,
                    'chat_id': chat_id,
                    'created_at': datetime.now()
                }
            self.signal_batches[batch_id]['signals'].append(signal_id)
        
        # Save to database if available
        if DB_AVAILABLE:
            try:
                db.add_signal(signal_id, signal_dict, batch_id, user_id, chat_id)
            except Exception as e:
                logger.warning(f"Failed to save signal to database: {e}")
    
    def mark_completed(self, signal_id: str, result: bool, mtg_count: int = 0, is_mtg: bool = False):
        """Mark a signal as completed with result (True = win, False = loss)"""
        if signal_id in self.active_signals:
            signal = self.active_signals.pop(signal_id)
            signal['status'] = 'completed'
            signal['result'] = result
            signal['completed_at'] = datetime.now()
            signal['mtg_count'] = mtg_count
            signal['is_mtg'] = is_mtg
            self.completed_signals.append(signal)
            
            # Update database if available
            if DB_AVAILABLE:
                try:
                    db.update_signal_result(signal_id, result, mtg_count, is_mtg)
                except Exception as e:
                    logger.warning(f"Failed to update signal result in database: {e}")
    
    def verify_trade_result(self, signal: dict) -> Tuple[Optional[bool], bool]:
        """
        Verify actual trade result with second candle MTG confirmation.
        Returns (result: Optional[bool], is_mtg: bool)
        - result: True if win, False if loss, None if cannot verify
        - is_mtg: True if this is an MTG win (second candle confirmation)
        
        MTG Logic:
        - If first candle loses, wait for second candle
        - If second candle confirms signal direction, count as MTG win
        - Only count as actual loss if second candle also loses
        """
        pair = signal.get('pair', '')
        signal_type = signal.get('signal', '')
        signal_time = signal.get('timestamp')
        
        try:
            if not pair or not signal_type or not signal_time:
                logger.error(f"[VERIFY] Missing data for signal: pair={pair}, type={signal_type}, time={signal_time}")
                return (ERROR_RESULT_UNKNOWN, False)  # Don't default to WIN
            
            # Get entry price (should be set when signal was generated)
            entry_price = signal.get('entry_price')
            if entry_price is None:
                # Fallback: try to get current price
                logger.warning(f"[VERIFY] Entry price not set for {pair}, attempting to fetch...")
                entry_price = get_price(pair)
                if entry_price is None:
                    logger.error(f"[VERIFY] Could not get entry price for {pair}")
                    return (ERROR_RESULT_UNKNOWN, False)  # Don't default to WIN
            
            # Get first candle exit price (price 1 minute after signal time)
            import time
            time.sleep(FIRST_CANDLE_WAIT)  # Small wait for first candle
            
            first_exit_price = get_price(pair)
            if first_exit_price is None:
                logger.error(f"[VERIFY] Could not get first exit price for {pair}")
                return (ERROR_RESULT_UNKNOWN, False)  # Don't default to WIN
            
            # Check first candle result
            if signal_type == 'CALL':
                first_candle_win = first_exit_price > entry_price
            elif signal_type == 'PUT':
                first_candle_win = first_exit_price < entry_price
            else:
                logger.error(f"[VERIFY] Unknown signal type '{signal_type}' for {pair}")
                return (ERROR_RESULT_UNKNOWN, False)  # Don't default to WIN
            
            # If first candle wins, it's a direct win
            if first_candle_win:
                price_diff = first_exit_price - entry_price
                price_diff_pct = (price_diff / entry_price * 100) if entry_price > 0 else 0
                logger.info(f"[VERIFY] {pair} {signal_type}: Entry={entry_price:.5f}, Exit={first_exit_price:.5f}, Diff={price_diff_pct:+.3f}%, Result=DIRECT WIN")
                return (True, False)  # Direct win, not MTG
            
            # First candle lost - wait for second candle confirmation (MTG)
            logger.info(f"[VERIFY] {pair} {signal_type}: First candle LOSS, waiting for second candle confirmation (MTG)...")
            # Note: This blocking sleep should be moved to background task in production
            time.sleep(SECOND_CANDLE_WAIT)  # Wait for second candle to form
            
            # Get second candle exit price
            second_exit_price = get_price(pair)
            if second_exit_price is None:
                logger.error(f"[VERIFY] Could not get second exit price for {pair}, counting as LOSS")
                return (False, False)  # Actual loss
            
            # Check second candle result
            if signal_type == 'CALL':
                second_candle_win = second_exit_price > first_exit_price
            elif signal_type == 'PUT':
                second_candle_win = second_exit_price < first_exit_price
            else:
                second_candle_win = False
            
            # If second candle confirms signal direction, it's an MTG win
            if second_candle_win:
                price_diff = second_exit_price - entry_price
                price_diff_pct = (price_diff / entry_price * 100) if entry_price > 0 else 0
                logger.info(f"[VERIFY] {pair} {signal_type}: Second candle confirms! Entry={entry_price:.5f}, Second Exit={second_exit_price:.5f}, Diff={price_diff_pct:+.3f}%, Result=MTG WIN")
                return (True, True)  # MTG win
            else:
                # Second candle also lost - actual loss
                price_diff = second_exit_price - entry_price
                price_diff_pct = (price_diff / entry_price * 100) if entry_price > 0 else 0
                logger.info(f"[VERIFY] {pair} {signal_type}: Second candle also LOSS. Entry={entry_price:.5f}, Second Exit={second_exit_price:.5f}, Diff={price_diff_pct:+.3f}%, Result=ACTUAL LOSS")
                return (False, False)  # Actual loss
                
        except Exception as e:
            logger.error(f"[ERROR] Verifying trade result for {pair}: {e}", exc_info=True)
            return (ERROR_RESULT_UNKNOWN, False)  # Don't default to WIN on error
    
    def check_and_update_expired_signals(self):
        """
        Check if signal times have ended and mark them as completed with actual results.
        Returns list of newly completed signals.
        """
        utc6 = pytz.timezone('Asia/Dhaka')
        now = datetime.now(utc6)
        
        expired_signals = []
        for signal_id, signal in list(self.active_signals.items()):
            # Signal expires 1 minute after its time
            signal_time = signal.get('timestamp')
            if signal_time:
                # Handle both datetime and string timestamps
                if isinstance(signal_time, str):
                    try:
                        signal_time = datetime.fromisoformat(signal_time)
                        if signal_time.tzinfo is None:
                            signal_time = utc6.localize(signal_time)
                    except:
                        logger.warning(f"Invalid timestamp format for signal {signal_id}")
                        continue
                
                # Add 1 minute for M1 expiry
                expiry_time = signal_time + timedelta(minutes=1)
                if now >= expiry_time:
                    expired_signals.append(signal_id)
        
        newly_completed = []
        
        # Mark expired signals as completed with actual results
        for signal_id in expired_signals:
            signal = self.active_signals[signal_id]
            pair = signal.get('pair', '')
            
            # Entry price should already be set when signal was generated
            # If not, try to get it now (fallback)
            if signal.get('entry_price') is None:
                logger.warning(f"[WARNING] Entry price not set for {pair} at expiry, attempting to fetch...")
                entry_price = get_price(pair)
                if entry_price:
                    signal['entry_price'] = entry_price
                else:
                    logger.error(f"[ERROR] Could not get entry price for {pair} at expiry")
            
            # Get current MTG count before checking result
            if pair in self.martingale_tracker:
                current_mtg = self.martingale_tracker[pair].get('mtg_count', 0)
            else:
                current_mtg = 0
            
            # Verify actual trade result with MTG confirmation
            result, is_mtg = self.verify_trade_result(signal)
            
            # Skip if result is None (cannot verify)
            if result is None:
                logger.warning(f"[WARNING] Cannot verify result for {pair}, skipping completion")
                continue
            
            # Update MTG tracker based on result
            if pair not in self.martingale_tracker:
                self.martingale_tracker[pair] = {'mtg_count': 0}
            
            if result:
                if is_mtg:
                    # MTG win: increment MTG count (shows we used MTG)
                    mtg_count = current_mtg + 1
                    # Keep MTG count for display (shows MTG level used)
                    self.martingale_tracker[pair]['mtg_count'] = mtg_count
                else:
                    # Direct win: MTG count stays the same (shows current MTG level), then reset
                    mtg_count = current_mtg
                    # Reset MTG for next trade sequence
                    self.martingale_tracker[pair]['mtg_count'] = 0
            else:
                # Loss: increment MTG count
                mtg_count = current_mtg + 1
                self.martingale_tracker[pair]['mtg_count'] = mtg_count
            
            self.martingale_tracker[pair]['last_result'] = result
            self.martingale_tracker[pair]['is_mtg'] = is_mtg
            
            # Mark as completed and store the completed signal info
            self.mark_completed(signal_id, result, mtg_count, is_mtg)
            
            # Get the completed signal for return
            completed_signal = next((s for s in self.completed_signals if s.get('signal_id') == signal_id), None)
            if completed_signal:
                newly_completed.append(completed_signal)
        
        return newly_completed
    
    def get_active_signals(self) -> dict:
        """Get all active signals"""
        return self.active_signals.copy()
    
    def format_results(self, batch_id: str = None) -> str:
        """Format completed signals with checkmarks and MTG count"""
        # Check for expired signals first
        self.check_and_update_expired_signals()
        
        if not self.completed_signals:
            return "No completed signals yet. Generate signals first."
        
        # Filter by batch if specified
        if batch_id:
            signal_ids = self.signal_batches.get(batch_id, {}).get('signals', [])
            signals_to_show = [s for s in self.completed_signals if s.get('signal_id') in signal_ids]
        else:
            signals_to_show = self.completed_signals
        
        if not signals_to_show:
            return "No completed signals for this batch yet."
        
        # Sort by time (oldest first for better readability)
        sorted_signals = sorted(signals_to_show, 
                               key=lambda x: x.get('time', ''))
        
        output = ""
        for signal in sorted_signals:
            pair = signal.get('pair', '')
            time = signal.get('time', '')
            signal_type = signal.get('signal', '')
            result = signal.get('result')
            
            # Handle None results (unverified)
            if result is None:
                checkmark = "❓"  # Unknown result
            elif result:
                # Win: show checkmark with MTG count if > 0 or is MTG
                is_mtg = signal.get('is_mtg', False)
                mtg_count = signal.get('mtg_count', 0)
                if mtg_count > 0 or is_mtg:
                    checkmark = f"✅{mtg_count}"
                else:
                    checkmark = "✅"
            else:
                # Loss: show X
                checkmark = "❌"
            
            output += f"{pair}-OTC,{time} M1 {signal_type} {checkmark}\n"
        
        # Add statistics if we have signals
        total = len(sorted_signals)
        verified_signals = [s for s in sorted_signals if s.get('result') is not None]
        wins = sum(1 for s in verified_signals if s.get('result', False))
        losses = len(verified_signals) - wins
        unverified = total - len(verified_signals)
        
        win_rate = (wins / len(verified_signals) * 100) if verified_signals else 0
        loss_rate = (losses / len(verified_signals) * 100) if verified_signals else 0
        
        output += "\n100% ACCURACY SIGNAL DONE..😮‍💨🔥\n"
        output += f"\n{'='*50}\n"
        output += f"📊 *STATISTICS*\n"
        output += f"{'='*50}\n"
        output += f"Total: {total} | ✅ Wins: {wins} ({win_rate:.1f}%) | ❌ Losses: {losses} ({loss_rate:.1f}%)"
        if unverified > 0:
            output += f" | ❓ Unverified: {unverified}"
        output += f"\n🎯 *Accuracy: {win_rate:.1f}%*\n"
        output += f"{'='*50}"
        
        return output
    
    def check_batch_completed(self, batch_id: str) -> bool:
        """Check if all signals in a batch are completed"""
        if batch_id not in self.signal_batches:
            return False
        
        batch = self.signal_batches[batch_id]
        signal_ids = batch.get('signals', [])
        
        # Check if all signals are completed
        all_completed = True
        for signal_id in signal_ids:
            if signal_id in self.active_signals:
                all_completed = False
                break
        
        return all_completed
    
    def format_individual_result(self, signal: dict) -> str:
        """Format a single signal result for individual updates"""
        pair = signal.get('pair', '')
        time = signal.get('time', '')
        signal_type = signal.get('signal', '')
        result = signal.get('result')
        mtg_count = signal.get('mtg_count', 0)
        
        if result is None:
            checkmark = "❓"
            status = "UNVERIFIED"
        elif result:
            # Win: show checkmark with MTG count if > 0 or is MTG
            is_mtg = signal.get('is_mtg', False)
            if mtg_count > 0 or is_mtg:
                checkmark = f"✅{mtg_count}"
                status = "MTG WIN" if is_mtg else "WIN"
            else:
                checkmark = "✅"
                status = "WIN"
        else:
            # Loss: show X
            checkmark = "❌"
            status = "LOSS"
        
        return f"{pair}-OTC,{time} M1 {signal_type} {checkmark} ({status})"
    
    def get_batch_results(self, batch_id: str) -> str:
        """Get formatted results for a specific batch"""
        if batch_id not in self.signal_batches:
            return None
        
        batch = self.signal_batches[batch_id]
        signal_ids = batch.get('signals', [])
        
        # Get completed signals for this batch
        batch_signals = [
            s for s in self.completed_signals 
            if s.get('signal_id') in signal_ids
        ]
        
        if not batch_signals:
            return None
        
        # Sort by time
        batch_signals.sort(key=lambda x: x.get('time', ''))
        
        output = ""
        for signal in batch_signals:
            pair = signal.get('pair', '')
            time = signal.get('time', '')
            signal_type = signal.get('signal', '')
            result = signal.get('result')
            mtg_count = signal.get('mtg_count', 0)
            
            if result is None:
                checkmark = "❓"
            elif result:
                # Win: show checkmark with MTG count if > 0 or is MTG
                is_mtg = signal.get('is_mtg', False)
                if mtg_count > 0 or is_mtg:
                    checkmark = f"✅{mtg_count}"
                else:
                    checkmark = "✅"
            else:
                # Loss: show X
                checkmark = "❌"
            
            output += f"{pair}-OTC,{time} M1 {signal_type} {checkmark}\n"
        
        output += "\n100% ACCURACY SIGNAL DONE..😮‍💨🔥"
        return output
    
    def get_batch_statistics(self, batch_id: str) -> dict:
        """Calculate statistics for a batch: wins, losses, win rate, loss rate"""
        if batch_id not in self.signal_batches:
            return None
        
        batch = self.signal_batches[batch_id]
        signal_ids = batch.get('signals', [])
        
        # Get completed signals for this batch
        batch_signals = [
            s for s in self.completed_signals 
            if s.get('signal_id') in signal_ids
        ]
        
        if not batch_signals:
            return None
        
        total_trades = len(batch_signals)
        verified_signals = [s for s in batch_signals if s.get('result') is not None]
        wins = sum(1 for s in verified_signals if s.get('result', False))
        losses = len(verified_signals) - wins
        unverified = total_trades - len(verified_signals)
        
        win_rate = (wins / len(verified_signals) * 100) if verified_signals else 0
        loss_rate = (losses / len(verified_signals) * 100) if verified_signals else 0
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'unverified': unverified,
            'win_rate': win_rate,
            'loss_rate': loss_rate
        }
    
    def format_batch_summary(self, batch_id: str) -> str:
        """Format final summary with statistics for a completed batch"""
        stats = self.get_batch_statistics(batch_id)
        if not stats:
            return None
        
        results_text = self.get_batch_results(batch_id)
        if not results_text:
            return None
        
        # Add statistics summary
        summary = f"\n{'='*50}\n"
        summary += f"📊 *TRADE STATISTICS*\n"
        summary += f"{'='*50}\n"
        summary += f"Total Trades: {stats['total_trades']}\n"
        summary += f"✅ Wins: {stats['wins']} ({stats['win_rate']:.1f}%)\n"
        summary += f"❌ Losses: {stats['losses']} ({stats['loss_rate']:.1f}%)\n"
        if stats.get('unverified', 0) > 0:
            summary += f"❓ Unverified: {stats['unverified']}\n"
        summary += f"{'='*50}\n"
        summary += f"🎯 *ACCURACY: {stats['win_rate']:.1f}%*\n"
        summary += f"{'='*50}\n"
        
        return results_text + summary
    
    def clear_old_signals(self, hours: int = None):
        """Clear signals older than specified hours"""
        if hours is None:
            hours = SIGNAL_CLEANUP_HOURS
            
        cutoff = datetime.now() - timedelta(hours=hours)
        self.completed_signals = [
            s for s in self.completed_signals 
            if s.get('added_at', datetime.now()) > cutoff
        ]
        
        # Clear old batches
        old_batches = [
            bid for bid, batch in self.signal_batches.items()
            if batch.get('created_at', datetime.now()) < cutoff
        ]
        for bid in old_batches:
            del self.signal_batches[bid]
        
        # Cleanup database if available
        if DB_AVAILABLE:
            try:
                db.cleanup_old_data(days=hours // 24)
            except Exception as e:
                logger.warning(f"Failed to cleanup database: {e}")

# Global tracker instance
tracker = ResultTracker()
