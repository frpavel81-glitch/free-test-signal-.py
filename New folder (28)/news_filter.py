# news_filter.py - Economic News Filter to Avoid Trading During High Impact News

from datetime import datetime, timedelta
import pytz
import requests
import json

class NewsFilter:
    def __init__(self):
        self.high_impact_events = []
        self.news_cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
    def get_economic_calendar(self):
        """
        Get economic calendar events for today.
        Uses free API or fallback to hardcoded high-impact times.
        """
        try:
            # Try to fetch from free economic calendar API
            # Using ForexFactory-style approach (free tier)
            today = datetime.now(pytz.UTC)
            url = f"https://www.forexfactory.com/calendar.php?day={today.strftime('%b%d.%Y')}"
            
            # For now, use hardcoded high-impact news times
            # In production, integrate with economic calendar API
            return self.get_high_impact_times()
            
        except Exception as e:
            print(f"[NEWS FILTER] Error fetching calendar: {e}")
            return self.get_high_impact_times()
    
    def get_high_impact_times(self):
        """
        Return high-impact news times (UTC).
        These are common times when major economic news is released.
        """
        utc6 = pytz.timezone('Asia/Dhaka')
        now = datetime.now(utc6)
        today = now.date()
        
        # High-impact news times (UTC+6 timezone)
        # Major news usually at: 2:00 PM, 3:00 PM, 4:00 PM, 5:00 PM, 6:00 PM, 8:00 PM, 9:00 PM
        high_impact_times = [
            datetime.combine(today, datetime.strptime("14:00", "%H:%M").time()).replace(tzinfo=utc6),  # 2:00 PM
            datetime.combine(today, datetime.strptime("15:00", "%H:%M").time()).replace(tzinfo=utc6),  # 3:00 PM
            datetime.combine(today, datetime.strptime("16:00", "%H:%M").time()).replace(tzinfo=utc6),  # 4:00 PM
            datetime.combine(today, datetime.strptime("17:00", "%H:%M").time()).replace(tzinfo=utc6),  # 5:00 PM
            datetime.combine(today, datetime.strptime("18:00", "%H:%M").time()).replace(tzinfo=utc6),  # 6:00 PM
            datetime.combine(today, datetime.strptime("20:00", "%H:%M").time()).replace(tzinfo=utc6),  # 8:00 PM
            datetime.combine(today, datetime.strptime("21:00", "%H:%M").time()).replace(tzinfo=utc6),  # 9:00 PM
        ]
        
        # Add next day's early morning news (1:00 AM, 2:00 AM)
        tomorrow = today + timedelta(days=1)
        high_impact_times.extend([
            datetime.combine(tomorrow, datetime.strptime("01:00", "%H:%M").time()).replace(tzinfo=utc6),
            datetime.combine(tomorrow, datetime.strptime("02:00", "%H:%M").time()).replace(tzinfo=utc6),
        ])
        
        return high_impact_times
    
    def is_news_time(self, signal_time: datetime, buffer_minutes: int = 15) -> bool:
        """
        Check if signal time is too close to high-impact news.
        Returns True if we should skip trading (news time), False if safe to trade.
        
        Args:
            signal_time: The time when signal will execute
            buffer_minutes: Minutes before/after news to avoid trading (default 15)
        """
        try:
            high_impact_times = self.get_high_impact_times()
            utc6 = pytz.timezone('Asia/Dhaka')
            
            if signal_time.tzinfo is None:
                signal_time = utc6.localize(signal_time)
            
            for news_time in high_impact_times:
                time_diff = abs((signal_time - news_time).total_seconds() / 60)
                
                # Skip if within buffer period
                if time_diff <= buffer_minutes:
                    print(f"[NEWS FILTER] ⚠️ Signal at {signal_time.strftime('%H:%M')} too close to news at {news_time.strftime('%H:%M')} (diff: {time_diff:.1f} min)")
                    return True  # Skip this signal
            
            return False  # Safe to trade
            
        except Exception as e:
            print(f"[NEWS FILTER] Error checking news time: {e}")
            return False  # If error, allow trading
    
    def filter_signals(self, signals: list) -> list:
        """
        Filter out signals that are too close to news events.
        Returns filtered list of signals.
        """
        filtered_signals = []
        skipped_count = 0
        
        for signal in signals:
            signal_time = signal.get('timestamp')
            if signal_time and self.is_news_time(signal_time):
                skipped_count += 1
                print(f"[NEWS FILTER] Skipping {signal.get('pair')} at {signal.get('time')} - too close to news")
                continue
            
            filtered_signals.append(signal)
        
        if skipped_count > 0:
            print(f"[NEWS FILTER] Filtered out {skipped_count} signals due to news events")
        
        return filtered_signals

# Global instance
news_filter = NewsFilter()

