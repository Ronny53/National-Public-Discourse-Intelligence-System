"""
Database service layer for handling database operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid

from backend.database.models import (
    SocialPost,
    PostAnalysis,
    IssueCluster,
    TrendData,
    DashboardSummary
)
from backend.api.schemas.social_data import SocialPost as SocialPostSchema, TrendData as TrendDataSchema


class DatabaseService:
    """Service class for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Post Operations
    def save_post(self, post: SocialPostSchema) -> SocialPost:
        """Save or update a social media post"""
        db_post = self.db.query(SocialPost).filter(SocialPost.id == post.id).first()
        
        if db_post:
            # Update existing post
            db_post.title = post.title
            db_post.text = post.text
            db_post.score = post.score
            db_post.upvote_ratio = post.upvote_ratio
            db_post.num_comments = post.num_comments
        else:
            # Create new post
            db_post = SocialPost(
                id=post.id,
                source=post.source,
                author_id=post.author_id,
                subreddit=post.subreddit,
                title=post.title,
                text=post.text,
                created_at=post.created_at,
                url=post.url,
                score=post.score,
                upvote_ratio=post.upvote_ratio,
                num_comments=post.num_comments,
                is_synthetic=post.is_synthetic
            )
            self.db.add(db_post)
        
        return db_post
    
    def save_posts_batch(self, posts: List[SocialPostSchema]) -> List[SocialPost]:
        """Save multiple posts efficiently"""
        saved_posts = []
        for post in posts:
            saved_posts.append(self.save_post(post))
        self.db.commit()
        return saved_posts
    
    def get_recent_posts(self, limit: int = 100) -> List[SocialPost]:
        """Get recent posts ordered by creation date"""
        return self.db.query(SocialPost).order_by(desc(SocialPost.created_at)).limit(limit).all()
    
    # Analysis Operations
    def save_post_analysis(
        self,
        post_id: str,
        sentiment_score: float,
        sentiment_label: str,
        emotion_scores: Dict[str, float]
    ) -> PostAnalysis:
        """Save NLP analysis results for a post"""
        # Delete existing analysis if any
        self.db.query(PostAnalysis).filter(PostAnalysis.post_id == post_id).delete()
        
        analysis = PostAnalysis(
            post_id=post_id,
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            emotion_scores=emotion_scores
        )
        self.db.add(analysis)
        self.db.commit()
        return analysis
    
    def get_post_analyses(self, post_ids: Optional[List[str]] = None) -> List[PostAnalysis]:
        """Get post analyses, optionally filtered by post IDs"""
        query = self.db.query(PostAnalysis)
        if post_ids:
            query = query.filter(PostAnalysis.post_id.in_(post_ids))
        return query.all()
    
    # Cluster Operations
    def save_clusters(self, clusters: List[Dict[str, Any]]) -> List[IssueCluster]:
        """Save issue clusters"""
        # Delete old clusters (optional: keep for history, but for now we replace)
        self.db.query(IssueCluster).delete()
        
        db_clusters = []
        for cluster in clusters:
            db_cluster = IssueCluster(
                cluster_id=cluster.get('cluster_id', 0),
                label=cluster.get('label', 'Unknown'),
                top_keywords=cluster.get('top_keywords', []),
                size=cluster.get('size', cluster.get('post_count', 0)),
                avg_sentiment=cluster.get('avg_sentiment'),
                trend=cluster.get('trend', 'stable')
            )
            db_clusters.append(db_cluster)
            self.db.add(db_cluster)
        
        self.db.commit()
        return db_clusters
    
    def get_latest_clusters(self, limit: int = 10) -> List[IssueCluster]:
        """Get latest clusters ordered by size"""
        return self.db.query(IssueCluster).order_by(desc(IssueCluster.size)).limit(limit).all()
    
    # Trend Operations
    def save_trends(self, trends: List[TrendDataSchema]) -> List[TrendData]:
        """Save trend data"""
        db_trends = []
        for trend in trends:
            db_trend = TrendData(
                keyword=trend.keyword,
                timestamp=trend.timestamp,
                interest_value=trend.interest_value,
                region=trend.region
            )
            db_trends.append(db_trend)
            self.db.add(db_trend)
        
        self.db.commit()
        return db_trends
    
    def get_trends(
        self,
        keywords: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[TrendData]:
        """Get trend data with optional filters"""
        query = self.db.query(TrendData)
        
        if keywords:
            query = query.filter(TrendData.keyword.in_(keywords))
        if start_date:
            query = query.filter(TrendData.timestamp >= start_date)
        if end_date:
            query = query.filter(TrendData.timestamp <= end_date)
        
        return query.order_by(TrendData.timestamp).limit(limit).all()
    
    # Dashboard Summary Operations
    def save_dashboard_summary(self, summary_data: Dict[str, Any]) -> DashboardSummary:
        """Save dashboard summary data"""
        escalation_risk = summary_data.get('escalation_risk', {})
        integrity_metrics = summary_data.get('integrity_metrics', {})
        
        summary = DashboardSummary(
            trust_index=summary_data.get('trust_index', 0.0),
            volatility_index=summary_data.get('volatility_index', 0.0),
            escalation_risk_score=escalation_risk.get('score', 0.0),
            escalation_risk_level=escalation_risk.get('level', 'low'),
            amplification_score=integrity_metrics.get('amplification', {}).get('amplification_score', 0.0),
            coordination_score=integrity_metrics.get('coordination', {}).get('burst_score', 0.0),
            total_posts_analyzed=summary_data.get('total_posts_analyzed', 0),
            total_clusters=summary_data.get('total_clusters', 0),
            valid_until=datetime.utcnow() + timedelta(minutes=5)  # Cache for 5 minutes
        )
        self.db.add(summary)
        self.db.commit()
        return summary
    
    def get_latest_dashboard_summary(self) -> Optional[DashboardSummary]:
        """Get the most recent dashboard summary"""
        return self.db.query(DashboardSummary).order_by(desc(DashboardSummary.created_at)).first()
    
    def get_dashboard_summary_in_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[DashboardSummary]:
        """Get dashboard summaries within a date range (for historical analysis)"""
        return self.db.query(DashboardSummary).filter(
            DashboardSummary.created_at >= start_date,
            DashboardSummary.created_at <= end_date
        ).order_by(DashboardSummary.created_at).all()
