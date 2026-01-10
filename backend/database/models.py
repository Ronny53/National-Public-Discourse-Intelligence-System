from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from backend.database.database import Base


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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keyword = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    interest_value = Column(Integer, nullable=False)  # 0-100
    region = Column(String, nullable=False, default="IN")
    
    # Composite index for efficient queries
    __table_args__ = (
        {'postgresql_indexes': [
            {'name': 'idx_keyword_timestamp', 'columns': ['keyword', 'timestamp']}
        ]}
    )


class DashboardSummary(Base):
    """
    Model for storing aggregated dashboard summary data
    """
    __tablename__ = "dashboard_summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
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
