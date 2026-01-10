from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session

# Import Services
from backend.config.settings import get_settings
from backend.ingestion.reddit_client import RedditClient
from backend.ingestion.trends_client import TrendsClient
from backend.ingestion.ethics_filter import EthicsFilter
from backend.preprocessing.cleaner import TextCleaner
from backend.preprocessing.deduplicator import Deduplicator
from backend.nlp.sentiment import SentimentAnalyzer
from backend.nlp.emotion import EmotionAnalyzer
from backend.integrity.amplification import AmplificationDetector
from backend.integrity.coordination import CoordinationDetector
from backend.clustering.issue_clustering import IssueClusterer
from backend.indices.trust_index import TrustIndex
from backend.indices.volatility_index import VolatilityIndex
from backend.indices.escalation_risk import EscalationRisk
from backend.policy.policy_brief import PolicyBriefGenerator

# Database imports
from backend.database.database import get_db
from backend.database.services import DatabaseService

router = APIRouter()
settings = get_settings()

# Initialize Services (Singleton pattern for this scale)
reddit_client = RedditClient()
trends_client = TrendsClient()
ethics_filter = EthicsFilter()
cleaner = TextCleaner()
deduplicator = Deduplicator()
sentiment_analyzer = SentimentAnalyzer()
emotion_analyzer = EmotionAnalyzer()
amp_detector = AmplificationDetector()
coord_detector = CoordinationDetector()
issue_clusterer = IssueClusterer()
trust_index = TrustIndex()
volatility_index = VolatilityIndex()
escalation_risk = EscalationRisk()
policy_brief_gen = PolicyBriefGenerator()

async def refresh_pipeline(db: Session = None):
    """
    Runs the full analysis pipeline and saves results to database.
    Can be called with a session (for background tasks) or will create one.
    """
    print("Refreshing pipeline...")
    
    # If no session provided, create one
    if db is None:
        from backend.database.database import SessionLocal
        db = SessionLocal()
        should_close = True
    else:
        should_close = False
    
    try:
        db_service = DatabaseService(db)
        # 1. Ingest
        posts = []
        for sub in settings.TARGET_SUBREDDITS:
            posts.extend(reddit_client.fetch_recent_posts(sub, limit=30))
        
        # 2. Ethics & Preprocessing
        posts = ethics_filter.process_posts(posts)
        for p in posts:
            p.text = cleaner.clean(p.text)
        
        posts = deduplicator.deduplicate(posts)
        
        # Save posts to database
        if posts:
            db_service.save_posts_batch(posts)
        
        # 3. Analysis
        sentiments = []
        emotions_agg = {}  # Aggregate emotions
        
        for p in posts:
            # Sentiment
            s_res = sentiment_analyzer.analyze(p.text)
            sentiments.append(s_res)
            
            # Emotion
            e_res = emotion_analyzer.analyze(p.text)
            for emo, score in e_res.items():
                if emo not in emotions_agg:
                    emotions_agg[emo] = 0.0
                emotions_agg[emo] += score
            
            # Save analysis to database
            sentiment_label = "positive" if s_res > 0.1 else "negative" if s_res < -0.1 else "neutral"
            db_service.save_post_analysis(
                post_id=p.id,
                sentiment_score=s_res,
                sentiment_label=sentiment_label,
                emotion_scores=e_res
            )
                
        # Normalize emotions
        total_emotion_score = sum(emotions_agg.values())
        if total_emotion_score > 0:
            for k in emotions_agg:
                emotions_agg[k] /= len(posts)  # Average density per post

        # 4. Integrity
        amp_res = amp_detector.detect_campaigns(posts)
        coord_res = coord_detector.detect_bursts(posts)
        
        # 5. Clustering
        clusters = issue_clusterer.cluster_issues(posts)
        
        # Save clusters to database
        if clusters:
            db_service.save_clusters(clusters)
        
        # 6. Indices
        t_score = trust_index.calculate(posts, amp_res['amplification_score'], sentiments)
        v_score = volatility_index.calculate(sentiments)
        risk_res = escalation_risk.calculate(
            sentiments, 
            emotions_agg, 
            coord_res['burst_score'], 
            len(posts)
        )

        # 7. Save Summary to Database
        summary_data = {
            "trust_index": t_score,
            "volatility_index": v_score,
            "escalation_risk": risk_res,
            "integrity_metrics": {
                "amplification": amp_res,
                "coordination": coord_res
            },
            "total_posts_analyzed": len(posts),
            "total_clusters": len(clusters)
        }
        db_service.save_dashboard_summary(summary_data)
        
        # 8. Save Trends to Database
        keywords = [c['top_keywords'][0] for c in clusters[:3]] if clusters else ["India", "Policy", "Economy"]
        trends_data = trends_client.get_interest_over_time(keywords)
        if trends_data:
            db_service.save_trends(trends_data)
        
        print("Pipeline refresh complete.")
        return summary_data
        
    except Exception as e:
        print(f"Error in pipeline refresh: {e}")
        if should_close:
            db.rollback()
        raise
    finally:
        if should_close:
            db.close()

@router.get("/summary")
async def get_dashboard_summary(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Get the latest dashboard summary from database.
    If no summary exists or it's older than 5 minutes, triggers a refresh.
    """
    db_service = DatabaseService(db)
    
    # Get latest summary from database
    latest_summary = db_service.get_latest_dashboard_summary()
    
    # Check if summary exists and is still valid (less than 5 minutes old)
    should_refresh = False
    if not latest_summary:
        should_refresh = True
    elif latest_summary.valid_until and latest_summary.valid_until < datetime.utcnow():
        should_refresh = True
    
    if should_refresh:
        # Trigger refresh (in background for better UX)
        background_tasks.add_task(refresh_pipeline, db)
        # Return the latest summary we have, or empty if none
        if latest_summary:
            return {
                "trust_index": latest_summary.trust_index,
                "volatility_index": latest_summary.volatility_index,
                "escalation_risk": {
                    "score": latest_summary.escalation_risk_score,
                    "level": latest_summary.escalation_risk_level
                },
                "integrity_metrics": {
                    "amplification": {"amplification_score": latest_summary.amplification_score},
                    "coordination": {"burst_score": latest_summary.coordination_score}
                },
                "total_posts_analyzed": latest_summary.total_posts_analyzed
            }
        else:
            # Return default empty summary if no data exists yet
            return {
                "trust_index": 0.0,
                "volatility_index": 0.0,
                "escalation_risk": {"score": 0.0, "level": "low"},
                "integrity_metrics": {
                    "amplification": {"amplification_score": 0.0},
                    "coordination": {"burst_score": 0.0}
                },
                "total_posts_analyzed": 0
            }
    
    # Return latest summary from database
    return {
        "trust_index": latest_summary.trust_index,
        "volatility_index": latest_summary.volatility_index,
        "escalation_risk": {
            "score": latest_summary.escalation_risk_score,
            "level": latest_summary.escalation_risk_level
        },
        "integrity_metrics": {
            "amplification": {"amplification_score": latest_summary.amplification_score},
            "coordination": {"burst_score": latest_summary.coordination_score}
        },
        "total_posts_analyzed": latest_summary.total_posts_analyzed
    }

@router.get("/issues")
async def get_top_issues(db: Session = Depends(get_db)):
    """
    Get top issues/clusters from database.
    """
    db_service = DatabaseService(db)
    
    # Get latest clusters from database
    clusters = db_service.get_latest_clusters(limit=10)
    
    # Transform database format to frontend format
    transformed = []
    for cluster in clusters:
        transformed.append({
            "label": cluster.label,
            "top_keywords": cluster.top_keywords,
            "post_count": cluster.size,
            "avg_sentiment": cluster.avg_sentiment if cluster.avg_sentiment is not None else 0.0,
            "trend": cluster.trend if cluster.trend else "stable"
        })
    
    return transformed

@router.get("/trends")
async def get_trends(
    keywords: str = None,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get trends data from database.
    Optional query parameters:
    - keywords: comma-separated list of keywords to filter by
    - days: number of days of history to retrieve (default: 7)
    """
    db_service = DatabaseService(db)
    
    # Parse keywords if provided
    keyword_list = None
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(",")]
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get trends from database
    trends = db_service.get_trends(
        keywords=keyword_list,
        start_date=start_date,
        end_date=end_date,
        limit=1000
    )
    
    if not trends:
        return []
    
    # Group by keyword
    grouped = defaultdict(list)
    for trend in trends:
        try:
            keyword = trend.keyword
            timestamp = trend.timestamp
            value = trend.interest_value
            
            # Convert timestamp to ISO format string
            if hasattr(timestamp, 'isoformat'):
                date_str = timestamp.isoformat()
            elif isinstance(timestamp, str):
                date_str = timestamp
            else:
                date_str = str(timestamp)
            
            grouped[keyword].append({
                "date": date_str,
                "value": int(value)
            })
        except Exception as e:
            # Skip malformed entries
            print(f"Error processing trend entry: {e}")
            continue
    
    # Transform to frontend format
    transformed = [
        {
            "keyword": keyword,
            "data": sorted(points, key=lambda p: p["date"])  # Sort by date
        }
        for keyword, points in grouped.items()
    ]
    
    return transformed

@router.get("/brief")
async def get_policy_brief(db: Session = Depends(get_db)):
    """
    Get policy brief generated from latest database data.
    """
    db_service = DatabaseService(db)
    
    # Get latest summary and clusters from database
    latest_summary = db_service.get_latest_dashboard_summary()
    clusters = db_service.get_latest_clusters(limit=10)
    
    if not latest_summary:
        raise HTTPException(status_code=404, detail="No dashboard summary available. Please refresh data first.")
    
    # Convert database models to dict format expected by policy brief generator
    summary_dict = {
        "trust_index": latest_summary.trust_index,
        "volatility_index": latest_summary.volatility_index,
        "escalation_risk": {
            "score": latest_summary.escalation_risk_score,
            "level": latest_summary.escalation_risk_level
        },
        "integrity_metrics": {
            "amplification": {"amplification_score": latest_summary.amplification_score},
            "coordination": {"burst_score": latest_summary.coordination_score}
        },
        "total_posts_analyzed": latest_summary.total_posts_analyzed
    }
    
    issues_list = [
        {
            "label": cluster.label,
            "top_keywords": cluster.top_keywords,
            "size": cluster.size,
            "avg_sentiment": cluster.avg_sentiment if cluster.avg_sentiment is not None else 0.0,
            "trend": cluster.trend if cluster.trend else "stable"
        }
        for cluster in clusters
    ]
        
    return policy_brief_gen.generate_brief(summary_dict, issues_list)

@router.post("/refresh")
async def force_refresh(db: Session = Depends(get_db)):
    """
    Force refresh of the analysis pipeline.
    """
    await refresh_pipeline(db)
    return {
        "status": "refreshed",
        "timestamp": datetime.utcnow().isoformat()
    }
