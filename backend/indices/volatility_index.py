from typing import List
import numpy as np

class VolatilityIndex:
    def __init__(self):
        pass

    def calculate(self, sentiments: List[dict]) -> float:
        """
        Calculates 0-100 Volatility Score.
        High score means rapid swings in public opinion.
        """
        if not sentiments or len(sentiments) < 2:
            return 0.0

        compounds = [s['compound'] for s in sentiments]
        std_dev = np.std(compounds)
        
        # Max std dev for range -1 to 1 is 1.0 (e.g. half -1, half 1)
        # Scale to 0-100
        volatility = (std_dev / 1.0) * 100
        
        return round(min(volatility, 100.0), 1)
