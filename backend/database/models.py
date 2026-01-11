from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from backend.database.database import Base

# Use String for UUID in SQLite, UUID type for PostgreSQL
from backend.config.settings import get_settings
settings = get_settings()

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support UUID type, use String
    UUID_TYPE = String(36)
    # For SQLite, we need to convert UUID to string
    def uuid_default():
        return str(uuid.uuid4())
else:
    # PostgreSQL supports UUID type
    try:
        from sqlalchemy.dialects.postgresql import UUID as PG_UUID
        UUID_TYPE = PG_UUID(as_uuid=True)
        uuid_default = uuid.uuid4
    except ImportError:
        # Fallback if psycopg2-binary is not installed or not PostgreSQL
        UUID_TYPE = String(36)
        def uuid_default():
            return str(uuid.uuid4())


class SocialPost(Base):
    """
    Model for storing social media posts (Reddit, etc.)
    """
    __tablename__ = "social_posts"
    
    id = Column(String, primary_key=True, index=True)  # Original post ID from source
    source = Column(String, nullable=False, index=True)  # e.g., "reddit"
    author_id = Column(String, nullable=True)  # Hashed or redacted
    subreddit = Column(String, nullable=True, index=True)
    title = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, index=True)
    url = Column(String, nullable=False)
    score = Column(Integer, default=0)
    upvote_ratio = Column(Float, nullable=True)
    num_comments = Column(Integer, default=0)
    is_synthetic = Column(Boolean, default=False)
    
    # Timestamps
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    analyses = relationship("PostAnalysis", back_populates="post", cascade="all, delete-orphan")


class PostAnalysis(Base):
    """
    Model for storing NLP analysis results for each post
    """
    __tablename__ = "post_analyses"
    
    id = Column(UUID_TYPE, primary_key=True, default=uuid_default)
    post_id = Column(String, ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Sentiment Analysis
    sentiment_score = Column(Float, nullable=False)  # -1 to 1
    sentiment_label = Column(String, nullable=False)  # "positive", "negative", "neutral"
    
    # Emotion Analysis
    emotion_scores = Column(JSON, nullable=False)  # {"anger": 0.5, "fear": 0.3, ...}
    
    # Timestamps
    analyzed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    post = relationship("SocialPost", back_populates="analyses")


class IssueCluster(Base):
    """
    Model for storing clustered issues/topics
    """
    __tablename__ = "issue_clusters"
    
    id = Column(UUID_TYPE, primary_key=True, default=uuid_default)
    cluster_id = Column(Integer, nullable=False, index=True)  # K-means cluster ID
    label = Column(String, nullable=False, index=True)
    top_keywords = Column(JSON, nullable=False)  # List of keywords
    size = Column(Integer, nullable=False)  # Number of posts in cluster
    avg_sentiment = Column(Float, nullable=True)
    trend = Column(String, nullable=True)  # "rising", "falling", "stable"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class TrendData(Base):
    """
    Model for storing Google Trends data
    """
    __tablename__ = "trend_data"
    
    id = Column(UUID_TYPE, primary_key=True, default=uuid_default)
    keyword = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    interest_value = Column(Integer, nullable=False)  # 0-100
    region = Column(String, nullable=False, default="IN")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_keyword_timestamp', 'keyword', 'timestamp'),
    )


class DashboardSummary(Base):
    """
    Model for storing aggregated dashboard summary data
    """
    __tablename__ = "dashboard_summaries"
    
    id = Column(UUID_TYPE, primary_key=True, default=uuid_default)
    
    # Indices
    trust_index = Column(Float, nullable=False)
    volatility_index = Column(Float, nullable=False)
    escalation_risk_score = Column(Float, nullable=False)
    escalation_risk_level = Column(String, nullable=False)  # "low", "medium", "high"
    
    # Integrity Metrics
    amplification_score = Column(Float, nullable=False)
    coordination_score = Column(Float, nullable=False)
    
    # Aggregate Data
    total_posts_analyzed = Column(Integer, nullable=False)
    total_clusters = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    valid_until = Column(DateTime, nullable=True)  # For cache expiration
