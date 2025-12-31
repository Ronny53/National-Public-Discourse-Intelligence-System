from typing import List, Dict, Any
from backend.api.schemas.social_data import SocialPost
import pandas as pd

class CoordinationDetector:
    def __init__(self):
        pass

    def detect_bursts(self, posts: List[SocialPost], window_minutes: int = 60) -> Dict[str, Any]:
        """
        Identifies if there are unusual bursts of activity.
        """
        if not posts:
            return {"burst_score": 0.0, "is_burst": False}

        # Convert to DataFrame for time series analysis
        df = pd.DataFrame([vars(p) for p in posts])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at')

        # Resample to count posts per window
        resampled = df.set_index('created_at').resample(f'{window_minutes}min').count()['id']
        
        if resampled.empty:
             return {"burst_score": 0.0, "is_burst": False}

        mean_rate = resampled.mean()
        max_rate = resampled.max()
        std_dev = resampled.std() if len(resampled) > 1 else 0

        # Burst Score: How many standard deviations above mean is the peak?
        # Z-score approach
        if std_dev > 0:
            burst_z_score = (max_rate - mean_rate) / std_dev
        else:
            burst_z_score = 0.0

        # Normalize score roughly 0-1 (Z-score 3+ is high)
        normalized_score = min(max(burst_z_score / 4.0, 0), 1.0)

        return {
            "burst_score": round(normalized_score, 2),
            "max_rate_per_window": int(max_rate),
            "mean_rate": round(mean_rate, 2),
            "is_burst": burst_z_score > 2.5
        }
