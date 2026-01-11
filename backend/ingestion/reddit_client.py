import praw
from praw.models import Submission
from typing import List, Optional
from datetime import datetime
import random
import logging
from backend.config.settings import get_settings
from backend.api.schemas.social_data import SocialPost

settings = get_settings()
logger = logging.getLogger(__name__)

class RedditClient:
    def __init__(self):
        # Check if keys are present and not default placeholders
        has_id = settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET
        is_placeholder = "your_client_id" in str(settings.REDDIT_CLIENT_ID).lower()
        
        self.enabled = has_id and not is_placeholder
        
        if self.enabled:
            try:
                self.reddit = praw.Reddit(
                    client_id=settings.REDDIT_CLIENT_ID,
                    client_secret=settings.REDDIT_CLIENT_SECRET,
                    user_agent=settings.REDDIT_USER_AGENT
                )
                # Test connection by making a simple request
                try:
                    _ = self.reddit.subreddit("test").display_name
                    logger.info("Reddit API connection successful. Real data mode enabled.")
                except Exception as test_e:
                    logger.warning(f"Reddit API test failed: {test_e}. Will attempt real fetch but may fallback.")
            except Exception as e:
                logger.error(f"Failed to init Reddit client: {e}")
                self.enabled = False
        else:
            logger.warning("Reddit credentials missing or invalid. Using synthetic data mode.")
            logger.info("To enable real Reddit data, set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env file")
            self.reddit = None

    def fetch_recent_posts(self, subreddit_name: str, limit: int = 50) -> List[SocialPost]:
        """
        Fetches recent posts from a specific subreddit.
        Prioritizes real data, falls back to synthetic only if necessary.
        """
        if not self.enabled:
            logger.info(f"Reddit API not enabled. Using synthetic data for r/{subreddit_name}")
            return self._generate_synthetic_posts(subreddit_name, limit)

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            fetched_count = 0
            
            # Try to fetch real posts
            for submission in subreddit.new(limit=limit * 2):  # Fetch more to account for stickied posts
                if submission.stickied:
                    continue
                
                # Skip if post has no text content (link-only posts)
                if not submission.selftext and not submission.title:
                    continue
                
                posts.append(self._map_submission_to_schema(submission))
                fetched_count += 1
                
                if fetched_count >= limit:
                    break
            
            if posts:
                logger.info(f"Successfully fetched {len(posts)} real posts from r/{subreddit_name}")
                return posts
            else:
                logger.warning(f"No posts retrieved from r/{subreddit_name}. Using synthetic data.")
                if settings.ENABLE_SYNTHETIC_DATA_FALLBACK:
                    return self._generate_synthetic_posts(subreddit_name, limit)
                return []
                
        except Exception as e:
            logger.error(f"Error fetching from Reddit r/{subreddit_name}: {e}")
            logger.info("Falling back to synthetic data")
            if settings.ENABLE_SYNTHETIC_DATA_FALLBACK:
                return self._generate_synthetic_posts(subreddit_name, limit)
            return []

    def _map_submission_to_schema(self, submission: Submission) -> SocialPost:
        return SocialPost(
            id=submission.id,
            source="reddit",
            subreddit=submission.subreddit.display_name,
            title=submission.title,
            text=submission.selftext,
            created_at=datetime.fromtimestamp(submission.created_utc),
            url=submission.url,
            score=submission.score,
            upvote_ratio=submission.upvote_ratio,
            num_comments=submission.num_comments,
            is_synthetic=False
        )

    def _generate_synthetic_posts(self, subreddit_name: str, limit: int) -> List[SocialPost]:
        """Generates realistic synthetic data for demo/fallback."""
        topics = [
            "Infrastructure development in Tier 2 cities",
            "New policy on digital payments",
            "Environmental concerns in the Himalayas",
            "Educational reform and NEP implementation",
            "Startups ecosystem growth",
            "Public transport challenges",
            "Traffic regulations in metro cities",
            "Water conservation initiatives"
        ]
        
        posts = []
        for i in range(limit):
            topic = random.choice(topics)
            posts.append(SocialPost(
                id=f"synth_{i}",
                source="reddit_mock",
                subreddit=subreddit_name,
                title=f"Update on {topic}",
                text=f"Discussion regarding {topic} and its impact on the general public. What are your thoughts? #India",
                created_at=datetime.now(),
                url=f"http://mock.reddit.com/{i}",
                score=random.randint(5, 500),
                upvote_ratio=random.uniform(0.6, 0.99),
                num_comments=random.randint(0, 100),
                is_synthetic=True
            ))
        return posts
