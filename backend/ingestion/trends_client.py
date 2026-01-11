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

    def get_interest_over_time(self, keywords: list[str], days: int = 7) -> list[TrendData]:
        """
        Fetches real Google Trends data for given keywords.
        Prioritizes real data, falls back to synthetic only if necessary.
        """
        if not self.enabled or len(keywords) == 0:
            logger.info("Google Trends not enabled or no keywords provided. Using synthetic data.")
            return self._generate_synthetic_trends(keywords)
            
        try:
            # Build timeframe string based on days parameter
            if days <= 7:
                timeframe = 'now 7-d'
            elif days <= 30:
                timeframe = 'today 1-m'
            elif days <= 90:
                timeframe = 'today 3-m'
            else:
                timeframe = 'today 1-y'
            
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=settings.TARGET_REGION)
            df = self.pytrends.interest_over_time()
            
            if df.empty or len(df) == 0:
                logger.warning(f"Google Trends returned empty data for keywords: {keywords}")
                if settings.ENABLE_SYNTHETIC_DATA_FALLBACK:
                    return self._generate_synthetic_trends(keywords)
                return []

            trends = []
            for date, row in df.iterrows():
                for kw in keywords:
                    if kw in row and pd.notna(row[kw]):
                        trends.append(TrendData(
                            keyword=kw,
                            timestamp=date,
                            interest_value=int(row[kw]),
                            region=settings.TARGET_REGION
                        ))
            
            if trends:
                logger.info(f"Successfully fetched {len(trends)} real trend data points for {len(keywords)} keywords")
                return trends
            else:
                logger.warning("No valid trend data extracted. Using synthetic data.")
                if settings.ENABLE_SYNTHETIC_DATA_FALLBACK:
                    return self._generate_synthetic_trends(keywords)
                return []
            
        except Exception as e:
            logger.error(f"Error fetching Google Trends: {e}")
            logger.info("Falling back to synthetic data")
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
