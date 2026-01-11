"""
Simple in-memory alert history tracker for cooldown logic.
For production, this should be moved to database.
"""
from datetime import datetime, timedelta
from typing import Optional

class AlertHistory:
    """Tracks alert history for cooldown management."""
    
    def __init__(self):
        self._last_alert_time: Optional[datetime] = None
        self._cooldown_minutes: int = 15
    
    def set_cooldown(self, minutes: int):
        """Set cooldown period in minutes."""
        self._cooldown_minutes = minutes
    
    def can_send_alert(self) -> bool:
        """Check if enough time has passed since last alert."""
        if self._last_alert_time is None:
            return True
        
        elapsed = datetime.utcnow() - self._last_alert_time
        return elapsed >= timedelta(minutes=self._cooldown_minutes)
    
    def record_alert(self):
        """Record that an alert was sent."""
        self._last_alert_time = datetime.utcnow()
    
    def get_last_alert_time(self) -> Optional[datetime]:
        """Get the timestamp of the last alert."""
        return self._last_alert_time
    
    def get_time_until_next_alert(self) -> Optional[timedelta]:
        """Get time remaining until next alert can be sent."""
        if self._last_alert_time is None:
            return None
        
        elapsed = datetime.utcnow() - self._last_alert_time
        cooldown = timedelta(minutes=self._cooldown_minutes)
        
        if elapsed >= cooldown:
            return None
        
        return cooldown - elapsed


# Global instance
alert_history = AlertHistory()
