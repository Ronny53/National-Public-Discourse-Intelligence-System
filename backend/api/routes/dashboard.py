from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from datetime import datetime

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

# In-memory cache for demo purposes
DATA_CACHE = {
    "last_updated": None,
    "summary": None,
    "issues": None,
    "trends": None,
    "raw_posts": []
}

async def refresh_pipeline():
    """Runs the full analysis pipeline."""
    print("Refreshing pipeline...")
    
    # 1. Ingest
    posts = []
    for sub in settings.TARGET_SUBREDDITS:
        posts.extend(reddit_client.fetch_recent_posts(sub, limit=30))
    
    # 2. Ethics & Preprocessing
    posts = ethics_filter.process_posts(posts)
    for p in posts:
        p.text = cleaner.clean(p.text)
    
    posts = deduplicator.deduplicate(posts)
    
    # 3. Analysis
    sentiments = []
    emotions_agg = {} # Aggregate emotions
    
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
            
    # Normalize emotions
    total_emotion_score = sum(emotions_agg.values())
    if total_emotion_score > 0:
        for k in emotions_agg:
            emotions_agg[k] /= len(posts) # Average density per post

    # 4. Integrity
    amp_res = amp_detector.detect_campaigns(posts)
    coord_res = coord_detector.detect_bursts(posts)
    
    # 5. Clustering
    clusters = issue_clusterer.cluster_issues(posts)
    
    # 6. Indices
    t_score = trust_index.calculate(posts, amp_res['amplification_score'], sentiments)
    v_score = volatility_index.calculate(sentiments)
    risk_res = escalation_risk.calculate(
        sentiments, 
        emotions_agg, 
        coord_res['burst_score'], 
        len(posts)
    )

    # 7. Update Cache
    DATA_CACHE["summary"] = {
        "trust_index": t_score,
        "volatility_index": v_score,
        "escalation_risk": risk_res,
        "integrity_metrics": {
            "amplification": amp_res,
            "coordination": coord_res
        },
        "total_posts_analyzed": len(posts)
    }
    
    DATA_CACHE["issues"] = clusters
    DATA_CACHE["raw_posts"] = posts # In real app, store in DB
    
    # Trends
    keywords = [c['top_keywords'][0] for c in clusters[:3]] if clusters else ["India", "Policy", "Economy"]
    trends_data = trends_client.get_interest_over_time(keywords)
    DATA_CACHE["trends"] = trends_data
    
    DATA_CACHE["last_updated"] = datetime.now()
    print("Pipeline refresh complete.")

@router.get("/summary")
async def get_dashboard_summary(background_tasks: BackgroundTasks):
    if not DATA_CACHE["last_updated"]:
        await refresh_pipeline()
    else:
        # Trigger background refresh if old (> 5 mins) - omitted for demo simplicity, just use cache
        pass
        
    return DATA_CACHE["summary"]

@router.get("/issues")
async def get_top_issues():
    if not DATA_CACHE["last_updated"]:
        await refresh_pipeline()
    return DATA_CACHE["issues"]

@router.get("/trends")
async def get_trends():
    if not DATA_CACHE["last_updated"]:
        await refresh_pipeline()
    return DATA_CACHE["trends"]

@router.get("/brief")
async def get_policy_brief():
    if not DATA_CACHE["last_updated"]:
        await refresh_pipeline()
        
    return policy_brief_gen.generate_brief(
        DATA_CACHE["summary"],
        DATA_CACHE["issues"]
    )

@router.post("/refresh")
async def force_refresh():
    await refresh_pipeline()
    return {"status": "refreshed", "timestamp": DATA_CACHE["last_updated"]}
