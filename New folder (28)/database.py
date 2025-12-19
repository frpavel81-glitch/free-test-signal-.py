# database.py - Database persistence layer using SQLite

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pytz
from logger_config import logger

class Database:
    """SQLite database for persisting signals, results, and statistics"""
    
    def __init__(self, db_path: str = "forex_bot.db"):
        self.db_path = db_path
        self._init_database()
        logger.info(f"Database initialized: {db_path}")
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                batch_id TEXT,
                user_id INTEGER,
                chat_id INTEGER,
                pair TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_time TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                entry_price REAL,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                result TEXT,
                mtg_count INTEGER DEFAULT 0,
                is_mtg INTEGER DEFAULT 0,
                confidence_score REAL,
                FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
            )
        ''')
        
        # Batches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS batches (
                batch_id TEXT PRIMARY KEY,
                user_id INTEGER,
                chat_id INTEGER,
                total_signals INTEGER DEFAULT 0,
                completed_signals INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        ''')
        
        # Statistics table (daily/hourly stats)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                hour INTEGER,
                total_signals INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0,
                mtg_wins INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                UNIQUE(date, hour)
            )
        ''')
        
        # Price history table (for backtesting)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                created_at TEXT NOT NULL,
                UNIQUE(pair, timestamp)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_batch ON signals(batch_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_status ON signals(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_batches_created ON batches(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_statistics_date ON statistics(date, hour)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_pair_time ON price_history(pair, timestamp)')
        
        conn.commit()
        conn.close()
    
    def add_signal(self, signal_id: str, signal_dict: dict, batch_id: str = None, 
                   user_id: int = None, chat_id: int = None):
        """Add a new signal to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp_str = signal_dict.get('timestamp')
            if isinstance(timestamp_str, datetime):
                timestamp_str = timestamp_str.isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO signals 
                (signal_id, batch_id, user_id, chat_id, pair, signal_type, signal_time, 
                 timestamp, entry_price, status, created_at, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal_id,
                batch_id,
                user_id,
                chat_id,
                signal_dict.get('pair'),
                signal_dict.get('signal'),
                signal_dict.get('time'),
                timestamp_str,
                signal_dict.get('entry_price'),
                'pending',
                datetime.now().isoformat(),
                signal_dict.get('confidence_score')
            ))
            
            # Update batch
            if batch_id:
                cursor.execute('''
                    INSERT OR IGNORE INTO batches 
                    (batch_id, user_id, chat_id, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (batch_id, user_id, chat_id, datetime.now().isoformat()))
                
                cursor.execute('''
                    UPDATE batches 
                    SET total_signals = total_signals + 1
                    WHERE batch_id = ?
                ''', (batch_id,))
            
            conn.commit()
            conn.close()
            logger.debug(f"Signal added to database: {signal_id}")
            
        except Exception as e:
            logger.error(f"Error adding signal to database: {e}")
            raise
    
    def update_signal_result(self, signal_id: str, result: bool, mtg_count: int = 0, 
                            is_mtg: bool = False):
        """Update signal with result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE signals 
                SET status = 'completed',
                    result = ?,
                    mtg_count = ?,
                    is_mtg = ?,
                    completed_at = ?
                WHERE signal_id = ?
            ''', (
                'win' if result else 'loss',
                mtg_count,
                1 if is_mtg else 0,
                datetime.now().isoformat(),
                signal_id
            ))
            
            # Get batch_id for statistics update
            cursor.execute('SELECT batch_id FROM signals WHERE signal_id = ?', (signal_id,))
            row = cursor.fetchone()
            if row and row[0]:
                batch_id = row[0]
                if result:
                    cursor.execute('''
                        UPDATE batches 
                        SET wins = wins + 1, completed_signals = completed_signals + 1
                        WHERE batch_id = ?
                    ''', (batch_id,))
                else:
                    cursor.execute('''
                        UPDATE batches 
                        SET losses = losses + 1, completed_signals = completed_signals + 1
                        WHERE batch_id = ?
                    ''', (batch_id,))
                
                # Update win rate
                cursor.execute('''
                    UPDATE batches 
                    SET win_rate = CAST(wins AS REAL) / NULLIF(completed_signals, 0) * 100
                    WHERE batch_id = ?
                ''', (batch_id,))
            
            conn.commit()
            conn.close()
            logger.debug(f"Signal result updated: {signal_id} = {'WIN' if result else 'LOSS'}")
            
        except Exception as e:
            logger.error(f"Error updating signal result: {e}")
            raise
    
    def get_pending_signals(self) -> List[Dict]:
        """Get all pending signals"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM signals 
                WHERE status = 'pending'
                ORDER BY timestamp ASC
            ''')
            
            rows = cursor.fetchall()
            signals = [dict(row) for row in rows]
            
            conn.close()
            return signals
            
        except Exception as e:
            logger.error(f"Error getting pending signals: {e}")
            return []
    
    def get_batch_signals(self, batch_id: str) -> List[Dict]:
        """Get all signals for a batch"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM signals 
                WHERE batch_id = ?
                ORDER BY timestamp ASC
            ''', (batch_id,))
            
            rows = cursor.fetchall()
            signals = [dict(row) for row in rows]
            
            conn.close()
            return signals
            
        except Exception as e:
            logger.error(f"Error getting batch signals: {e}")
            return []
    
    def get_batch_statistics(self, batch_id: str) -> Optional[Dict]:
        """Get statistics for a batch"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM batches WHERE batch_id = ?
            ''', (batch_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting batch statistics: {e}")
            return None
    
    def cleanup_old_data(self, days: int = 7):
        """Clean up data older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Delete old signals
            cursor.execute('DELETE FROM signals WHERE created_at < ?', (cutoff_date,))
            deleted_signals = cursor.rowcount
            
            # Delete old batches
            cursor.execute('DELETE FROM batches WHERE created_at < ?', (cutoff_date,))
            deleted_batches = cursor.rowcount
            
            # Delete old price history (keep last 30 days)
            price_cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute('DELETE FROM price_history WHERE created_at < ?', (price_cutoff,))
            deleted_prices = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up: {deleted_signals} signals, {deleted_batches} batches, {deleted_prices} price records")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# Global database instance
db = Database()

