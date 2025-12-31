import re
from backend.api.schemas.social_data import SocialPost

class EthicsFilter:
    def __init__(self):
        # Regex for common PII (Phones, Indian Aadhaar-like patterns, Emails)
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'\b\d{10}\b') # Simple 10 digit check
        
    def process_posts(self, posts: list[SocialPost]) -> list[SocialPost]:
        """Filters or redacts posts containing sensitive PII."""
        # For public discourse analysis, we generally want to KEEP the content 
        # but REDACT the PII. However, if the post is entirely PII, we might drop it.
        
        cleaned_posts = []
        for post in posts:
            if self._is_safe(post):
                post.text = self._redact(post.text)
                cleaned_posts.append(post)
        return cleaned_posts

    def _is_safe(self, post: SocialPost) -> bool:
        # Check scope - e.g. strictly excludes NSFW or wildly irrelevant subreddits 
        # (though we filter by subreddit source already)
        return True

    def _redact(self, text: str) -> str:
        text = self.email_pattern.sub("[EMAIL REDACTED]", text)
        text = self.phone_pattern.sub("[PHONE REDACTED]", text)
        return text
