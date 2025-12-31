from typing import List, Dict, Any
from backend.api.schemas.social_data import SocialPost
from collections import Counter

class AmplificationDetector:
    def __init__(self):
        pass

    def detect_campaigns(self, posts: List[SocialPost]) -> Dict[str, Any]:
        """
        Analyzes a batch of posts for signs of amplification.
        Returns metrics on repetition and inorganic spread.
        """
        if not posts:
            return {"amplification_score": 0.0, "flagged_posts": 0}

        # Check for exact textual repetition (Copy-Pasta)
        text_counts = Counter(p.text for p in posts)
        repeated_texts = {text: count for text, count in text_counts.items() if count > 1}
        
        # Calculate Repetition Ratio
        total_posts = len(posts)
        total_repeats = sum(count - 1 for count in repeated_texts.values())
        repetition_ratio = total_repeats / total_posts if total_posts > 0 else 0

        # Heuristic: If > 20% of posts are repeats, high amplification
        amplification_score = min(repetition_ratio * 5, 1.0) # Scale 0-1 (0.2 -> 1.0)

        return {
            "amplification_score": round(amplification_score, 2),
            "repeated_message_count": len(repeated_texts),
            "total_repeats": total_repeats
        }
