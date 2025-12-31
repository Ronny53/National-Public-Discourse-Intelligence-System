from typing import List
from backend.api.schemas.social_data import SocialPost

class TrustIndex:
    def __init__(self):
        pass

    def calculate(self, posts: List[SocialPost], amplification_score: float, sentiments: List[dict]) -> float:
        """
        Calculates a 0-100 Trust Score.
        """
        if not posts or not sentiments:
            return 50.0

        # Component 1: Sentiment Balance (-1 to 1) -> normalized 0 to 1
        avg_compound = sum(s['compound'] for s in sentiments) / len(sentiments)
        sentiment_score = (avg_compound + 1) / 2 # 0.0 to 1.0

        # Component 2: Organic Integrity (1 - amplification)
        integrity_score = 1.0 - amplification_score
        
        # Component 3: Civil Discourse (ratio of neutral/positive to total)
        # Penalize highly negative toxicity
        non_negative_count = sum(1 for s in sentiments if s['label'] != 'negative')
        civility_score = non_negative_count / len(sentiments)

        # Weighted Sum
        # Sentiment: 30%, Integrity: 40%, Civility: 30%
        raw_trust = (sentiment_score * 0.3) + (integrity_score * 0.4) + (civility_score * 0.3)
        
        return round(raw_trust * 100, 1)
