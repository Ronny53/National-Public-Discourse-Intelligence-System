from typing import List
from backend.api.schemas.social_data import SocialPost

class Deduplicator:
    def __init__(self, threshold: float = 0.85):
        self.threshold = threshold

    def deduplicate(self, posts: List[SocialPost]) -> List[SocialPost]:
        """Removes near-duplicate posts based on content similarity."""
        unique_posts = []
        seen_contents = []

        for post in posts:
            is_dup = False
            post_tokens = self._tokenize(post.text)
            
            if not post_tokens:
                # If empty text, check title
                post_tokens = self._tokenize(post.title)

            for seen_tokens in seen_contents:
                similarity = self._jaccard_similarity(post_tokens, seen_tokens)
                if similarity > self.threshold:
                    is_dup = True
                    break
            
            if not is_dup:
                unique_posts.append(post)
                seen_contents.append(post_tokens)
        
        return unique_posts

    def _tokenize(self, text: str) -> set:
        return set(text.lower().split())

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
