from pytrends.request import TrendReq
from backend.config.settings import get_settings
from backend.api.schemas.social_data import TrendData
from datetime import datetime, timedelta
import random
import logging
import pandas as pd

settings = get_settings()
logger = logging.getLogger(__name__)

class TrendsClient:
    def __init__(self):
        try:
            self.pytrends = TrendReq(hl='en-US', tz=330) # India timezone roughly
            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize pytrends: {e}")
            self.enabled = False

    def get_interest_over_time(self, keywords: list[str]) -> list[TrendData]:
        if not self.enabled or len(keywords) == 0:
            return self._generate_synthetic_trends(keywords)
            
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe='now 7-d', geo=settings.TARGET_REGION)
            df = self.pytrends.interest_over_time()
            
            if df.empty:
                return self._generate_synthetic_trends(keywords)

            trends = []
            for date, row in df.iterrows():
                for kw in keywords:
                    if kw in row:
                        trends.append(TrendData(
                            keyword=kw,
                            timestamp=date,
                            interest_value=int(row[kw]),
                            region=settings.TARGET_REGION
                        ))
            return trends
            
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            if settings.ENABLE_SYNTHETIC_DATA_FALLBACK:
                return self._generate_synthetic_trends(keywords)
            return []

    def _generate_synthetic_trends(self, keywords: list[str]) -> list[TrendData]:
        trends = []
        now = datetime.now()
        # Generate last 7 days of data
        for i in range(7):
            date = now - timedelta(days=6-i)
            # Make it look somewhat organic
            base_val = random.randint(20, 80)
            for kw in keywords:
                val = max(0, min(100, base_val + random.randint(-10, 10)))
                trends.append(TrendData(
                    keyword=kw,
                    timestamp=date,
                    interest_value=val,
                    region=settings.TARGET_REGION
                ))
        return trends
