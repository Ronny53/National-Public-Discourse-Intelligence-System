from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SocialPost(BaseModel):
    id: str
    source: str # e.g., "reddit"
    author_id: Optional[str] = None # Hashed or redacted in production
    subreddit: Optional[str] = None
    title: str
    text: str
    created_at: datetime
    url: str
    score: int
    upvote_ratio: Optional[float] = None
    num_comments: int
    is_synthetic: bool = False

class SocialComment(BaseModel):
    id: str
    post_id: str
    source: str
    text: str
    created_at: datetime
    score: int
    is_synthetic: bool = False

class TrendData(BaseModel):
    keyword: str
    timestamp: datetime
    interest_value: int
    region: str
