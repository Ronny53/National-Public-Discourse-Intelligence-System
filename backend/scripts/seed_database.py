"""
Script to populate the database with synthetic data for development/demo purposes.
This generates realistic dummy data similar to what the app would process from real sources.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from backend.database.database import SessionLocal, init_db
from backend.database.services import DatabaseService
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
from backend.config.settings import get_settings

settings = get_settings()

def seed_database():
    """Populate database with synthetic data."""
    print("=" * 60)
    print("Starting database seeding with synthetic data...")
    print("=" * 60)
    
    # Initialize database
    print("\n1. Initializing database...")
    try:
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"[WARNING] Database initialization: {e}")
    
    db: Session = SessionLocal()
    db_service = DatabaseService(db)
    
    try:
        # Initialize services
        print("\n2. Initializing services...")
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
        print("[OK] Services initialized")
        
        # Generate synthetic posts
        print("\n3. Generating synthetic posts...")
        posts = []
        subreddits = settings.TARGET_SUBREDDITS if hasattr(settings, 'TARGET_SUBREDDITS') else ['india', 'IndianPolitics', 'developersIndia']
        
        for subreddit in subreddits:
            # Force synthetic data generation
            synthetic_posts = reddit_client._generate_synthetic_posts(subreddit, limit=30)
            posts.extend(synthetic_posts)
        
        print(f"[OK] Generated {len(posts)} synthetic posts")
        
        # Process posts
        print("\n4. Processing posts (ethics, cleaning, deduplication)...")
        posts = ethics_filter.process_posts(posts)
        for p in posts:
            p.text = cleaner.clean(p.text)
        posts = deduplicator.deduplicate(posts)
        print(f"[OK] Processed {len(posts)} posts")
        
        # Save posts to database
        print("\n5. Saving posts to database...")
        if posts:
            db_service.save_posts_batch(posts)
            print(f"[OK] Saved {len(posts)} posts to database")
        
        # Analyze posts
        print("\n6. Analyzing posts (sentiment, emotion)...")
        sentiments = []
        emotions_agg = {}
        
        for p in posts:
            # Sentiment
            s_res = sentiment_analyzer.analyze(p.text)
            sentiments.append(s_res)  # Keep full dict for trust_index
            compound_score = s_res.get('compound', 0.0)
            
            # Emotion
            e_res = emotion_analyzer.analyze(p.text)
            for emo, score in e_res.items():
                if emo not in emotions_agg:
                    emotions_agg[emo] = 0.0
                emotions_agg[emo] += score
            
            # Save analysis to database
            sentiment_label = s_res.get('label', 'neutral')
            db_service.save_post_analysis(
                post_id=p.id,
                sentiment_score=compound_score,
                sentiment_label=sentiment_label,
                emotion_scores=e_res
            )
        
        # Normalize emotions
        total_emotion_score = sum(emotions_agg.values())
        if total_emotion_score > 0:
            for k in emotions_agg:
                emotions_agg[k] /= len(posts)
        
        print(f"[OK] Analyzed {len(posts)} posts")
        
        # Integrity detection
        print("\n7. Running integrity checks...")
        amp_res = amp_detector.detect_campaigns(posts)
        coord_res = coord_detector.detect_bursts(posts)
        print("[OK] Integrity checks complete")
        
        # Clustering
        print("\n8. Clustering issues...")
        clusters = issue_clusterer.cluster_issues(posts)
        if clusters:
            db_service.save_clusters(clusters)
            print(f"[OK] Created {len(clusters)} issue clusters")
        else:
            print("[WARNING] No clusters generated")
        
        # Calculate indices
        print("\n9. Calculating indices...")
        t_score = trust_index.calculate(posts, amp_res['amplification_score'], sentiments)
        v_score = volatility_index.calculate(sentiments)
        risk_res = escalation_risk.calculate(
            sentiments,
            emotions_agg,
            coord_res['burst_score'],
            len(posts)
        )
        print(f"[OK] Trust Index: {t_score:.2f}")
        print(f"[OK] Volatility Index: {v_score:.2f}")
        print(f"[OK] Escalation Risk: {risk_res['score']:.2f} ({risk_res['level']})")
        
        # Save dashboard summary
        print("\n10. Saving dashboard summary...")
        summary_data = {
            "trust_index": t_score,
            "volatility_index": v_score,
            "escalation_risk": risk_res,
            "integrity_metrics": {
                "amplification": amp_res,
                "coordination": coord_res
            },
            "total_posts_analyzed": len(posts),
            "total_clusters": len(clusters) if clusters else 0
        }
        db_service.save_dashboard_summary(summary_data)
        print("[OK] Dashboard summary saved")
        
        # Generate and save trends
        print("\n11. Generating trend data...")
        keywords = [c['top_keywords'][0] for c in clusters[:3]] if clusters else ["India", "Policy", "Economy"]
        trends_data = trends_client._generate_synthetic_trends(keywords)
        if trends_data:
            db_service.save_trends(trends_data)
            print(f"[OK] Saved trend data for {len(keywords)} keywords")
        
        print("\n" + "=" * 60)
        print("[OK] Database seeding completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Posts: {len(posts)}")
        print(f"  - Analyses: {len(posts)}")
        print(f"  - Clusters: {len(clusters) if clusters else 0}")
        print(f"  - Trends: {len(trends_data) if trends_data else 0}")
        print(f"  - Trust Index: {t_score:.2f}")
        print(f"  - Volatility Index: {v_score:.2f}")
        print(f"  - Risk Level: {risk_res['level']}")
        
    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
