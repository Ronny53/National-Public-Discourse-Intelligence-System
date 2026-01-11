"""
Elite-level dependency injection container for NIS backend.

Features:
- Lazy initialization of services
- Singleton pattern for expensive resources
- Easy testing through dependency override
- Lifecycle management
- Type-safe dependency resolution
"""

from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Generic, Callable, Optional, Any
from functools import lru_cache
from dataclasses import dataclass, field
from contextlib import contextmanager
import threading

from backend.core.logging import get_logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
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
    from backend.prediction.forecaster import SentimentForecaster
    from backend.database.services import DatabaseService

logger = get_logger(__name__)

T = TypeVar("T")


class ServiceProvider(Generic[T]):
    """
    Lazy service provider with optional singleton behavior.
    
    Provides thread-safe lazy initialization of services.
    """
    
    def __init__(
        self,
        factory: Callable[[], T],
        singleton: bool = True,
    ) -> None:
        self._factory = factory
        self._singleton = singleton
        self._instance: Optional[T] = None
        self._lock = threading.Lock()
    
    def get(self) -> T:
        """Get or create the service instance."""
        if not self._singleton:
            return self._factory()
        
        if self._instance is None:
            with self._lock:
                # Double-check locking
                if self._instance is None:
                    self._instance = self._factory()
        
        return self._instance
    
    def reset(self) -> None:
        """Reset the singleton instance (useful for testing)."""
        with self._lock:
            self._instance = None
    
    def override(self, instance: T) -> None:
        """Override with a specific instance (useful for testing)."""
        with self._lock:
            self._instance = instance


@dataclass
class ServiceContainer:
    """
    Central dependency injection container.
    
    Manages all service instances with lazy initialization.
    Thread-safe and supports testing overrides.
    """
    
    _providers: dict[str, ServiceProvider] = field(default_factory=dict)
    _overrides: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        self._register_services()
    
    def _register_services(self) -> None:
        """Register all application services."""
        
        # Data Ingestion Services
        self._providers["reddit_client"] = ServiceProvider(
            lambda: self._create_reddit_client()
        )
        self._providers["trends_client"] = ServiceProvider(
            lambda: self._create_trends_client()
        )
        self._providers["ethics_filter"] = ServiceProvider(
            lambda: self._create_ethics_filter()
        )
        
        # Preprocessing Services
        self._providers["text_cleaner"] = ServiceProvider(
            lambda: self._create_text_cleaner()
        )
        self._providers["deduplicator"] = ServiceProvider(
            lambda: self._create_deduplicator()
        )
        
        # NLP Services
        self._providers["sentiment_analyzer"] = ServiceProvider(
            lambda: self._create_sentiment_analyzer()
        )
        self._providers["emotion_analyzer"] = ServiceProvider(
            lambda: self._create_emotion_analyzer()
        )
        
        # Integrity Services
        self._providers["amplification_detector"] = ServiceProvider(
            lambda: self._create_amplification_detector()
        )
        self._providers["coordination_detector"] = ServiceProvider(
            lambda: self._create_coordination_detector()
        )
        
        # Clustering Services
        self._providers["issue_clusterer"] = ServiceProvider(
            lambda: self._create_issue_clusterer()
        )
        
        # Index Services
        self._providers["trust_index"] = ServiceProvider(
            lambda: self._create_trust_index()
        )
        self._providers["volatility_index"] = ServiceProvider(
            lambda: self._create_volatility_index()
        )
        self._providers["escalation_risk"] = ServiceProvider(
            lambda: self._create_escalation_risk()
        )
        
        # Policy Services
        self._providers["policy_brief_generator"] = ServiceProvider(
            lambda: self._create_policy_brief_generator()
        )
        
        # Prediction Services
        self._providers["sentiment_forecaster"] = ServiceProvider(
            lambda: self._create_sentiment_forecaster()
        )
    
    # ========================================================================
    # Service Factory Methods
    # ========================================================================
    
    def _create_reddit_client(self) -> "RedditClient":
        from backend.ingestion.reddit_client import RedditClient
        logger.debug("Initializing RedditClient")
        return RedditClient()
    
    def _create_trends_client(self) -> "TrendsClient":
        from backend.ingestion.trends_client import TrendsClient
        logger.debug("Initializing TrendsClient")
        return TrendsClient()
    
    def _create_ethics_filter(self) -> "EthicsFilter":
        from backend.ingestion.ethics_filter import EthicsFilter
        logger.debug("Initializing EthicsFilter")
        return EthicsFilter()
    
    def _create_text_cleaner(self) -> "TextCleaner":
        from backend.preprocessing.cleaner import TextCleaner
        logger.debug("Initializing TextCleaner")
        return TextCleaner()
    
    def _create_deduplicator(self) -> "Deduplicator":
        from backend.preprocessing.deduplicator import Deduplicator
        logger.debug("Initializing Deduplicator")
        return Deduplicator()
    
    def _create_sentiment_analyzer(self) -> "SentimentAnalyzer":
        from backend.nlp.sentiment import SentimentAnalyzer
        logger.debug("Initializing SentimentAnalyzer")
        return SentimentAnalyzer()
    
    def _create_emotion_analyzer(self) -> "EmotionAnalyzer":
        from backend.nlp.emotion import EmotionAnalyzer
        logger.debug("Initializing EmotionAnalyzer")
        return EmotionAnalyzer()
    
    def _create_amplification_detector(self) -> "AmplificationDetector":
        from backend.integrity.amplification import AmplificationDetector
        logger.debug("Initializing AmplificationDetector")
        return AmplificationDetector()
    
    def _create_coordination_detector(self) -> "CoordinationDetector":
        from backend.integrity.coordination import CoordinationDetector
        logger.debug("Initializing CoordinationDetector")
        return CoordinationDetector()
    
    def _create_issue_clusterer(self) -> "IssueClusterer":
        from backend.clustering.issue_clustering import IssueClusterer
        logger.debug("Initializing IssueClusterer")
        return IssueClusterer()
    
    def _create_trust_index(self) -> "TrustIndex":
        from backend.indices.trust_index import TrustIndex
        logger.debug("Initializing TrustIndex")
        return TrustIndex()
    
    def _create_volatility_index(self) -> "VolatilityIndex":
        from backend.indices.volatility_index import VolatilityIndex
        logger.debug("Initializing VolatilityIndex")
        return VolatilityIndex()
    
    def _create_escalation_risk(self) -> "EscalationRisk":
        from backend.indices.escalation_risk import EscalationRisk
        logger.debug("Initializing EscalationRisk")
        return EscalationRisk()
    
    def _create_policy_brief_generator(self) -> "PolicyBriefGenerator":
        from backend.policy.policy_brief import PolicyBriefGenerator
        logger.debug("Initializing PolicyBriefGenerator")
        return PolicyBriefGenerator()
    
    def _create_sentiment_forecaster(self) -> "SentimentForecaster":
        from backend.prediction.forecaster import SentimentForecaster
        logger.debug("Initializing SentimentForecaster")
        return SentimentForecaster()
    
    # ========================================================================
    # Service Accessors
    # ========================================================================
    
    def get(self, name: str) -> Any:
        """Get a service by name."""
        if name in self._overrides:
            return self._overrides[name]
        
        if name not in self._providers:
            raise KeyError(f"Unknown service: {name}")
        
        return self._providers[name].get()
    
    @property
    def reddit_client(self) -> "RedditClient":
        return self.get("reddit_client")
    
    @property
    def trends_client(self) -> "TrendsClient":
        return self.get("trends_client")
    
    @property
    def ethics_filter(self) -> "EthicsFilter":
        return self.get("ethics_filter")
    
    @property
    def text_cleaner(self) -> "TextCleaner":
        return self.get("text_cleaner")
    
    @property
    def deduplicator(self) -> "Deduplicator":
        return self.get("deduplicator")
    
    @property
    def sentiment_analyzer(self) -> "SentimentAnalyzer":
        return self.get("sentiment_analyzer")
    
    @property
    def emotion_analyzer(self) -> "EmotionAnalyzer":
        return self.get("emotion_analyzer")
    
    @property
    def amplification_detector(self) -> "AmplificationDetector":
        return self.get("amplification_detector")
    
    @property
    def coordination_detector(self) -> "CoordinationDetector":
        return self.get("coordination_detector")
    
    @property
    def issue_clusterer(self) -> "IssueClusterer":
        return self.get("issue_clusterer")
    
    @property
    def trust_index(self) -> "TrustIndex":
        return self.get("trust_index")
    
    @property
    def volatility_index(self) -> "VolatilityIndex":
        return self.get("volatility_index")
    
    @property
    def escalation_risk(self) -> "EscalationRisk":
        return self.get("escalation_risk")
    
    @property
    def policy_brief_generator(self) -> "PolicyBriefGenerator":
        return self.get("policy_brief_generator")
    
    @property
    def sentiment_forecaster(self) -> "SentimentForecaster":
        return self.get("sentiment_forecaster")
    
    # ========================================================================
    # Testing Utilities
    # ========================================================================
    
    @contextmanager
    def override(self, **overrides: Any):
        """
        Context manager for temporarily overriding services.
        
        Useful for testing:
            with container.override(reddit_client=mock_client):
                # Test code here
        """
        original = self._overrides.copy()
        self._overrides.update(overrides)
        try:
            yield
        finally:
            self._overrides = original
    
    def reset_all(self) -> None:
        """Reset all singleton instances."""
        for provider in self._providers.values():
            provider.reset()
        self._overrides.clear()


# Global container instance
_container: Optional[ServiceContainer] = None
_container_lock = threading.Lock()


def get_container() -> ServiceContainer:
    """Get the global service container instance."""
    global _container
    
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = ServiceContainer()
    
    return _container


def reset_container() -> None:
    """Reset the global container (for testing)."""
    global _container
    with _container_lock:
        if _container:
            _container.reset_all()
        _container = None


# ============================================================================
# FastAPI Dependencies
# ============================================================================

def get_reddit_client() -> "RedditClient":
    """FastAPI dependency for RedditClient."""
    return get_container().reddit_client


def get_trends_client() -> "TrendsClient":
    """FastAPI dependency for TrendsClient."""
    return get_container().trends_client


def get_ethics_filter() -> "EthicsFilter":
    """FastAPI dependency for EthicsFilter."""
    return get_container().ethics_filter


def get_text_cleaner() -> "TextCleaner":
    """FastAPI dependency for TextCleaner."""
    return get_container().text_cleaner


def get_deduplicator() -> "Deduplicator":
    """FastAPI dependency for Deduplicator."""
    return get_container().deduplicator


def get_sentiment_analyzer() -> "SentimentAnalyzer":
    """FastAPI dependency for SentimentAnalyzer."""
    return get_container().sentiment_analyzer


def get_emotion_analyzer() -> "EmotionAnalyzer":
    """FastAPI dependency for EmotionAnalyzer."""
    return get_container().emotion_analyzer


def get_amplification_detector() -> "AmplificationDetector":
    """FastAPI dependency for AmplificationDetector."""
    return get_container().amplification_detector


def get_coordination_detector() -> "CoordinationDetector":
    """FastAPI dependency for CoordinationDetector."""
    return get_container().coordination_detector


def get_issue_clusterer() -> "IssueClusterer":
    """FastAPI dependency for IssueClusterer."""
    return get_container().issue_clusterer


def get_trust_index() -> "TrustIndex":
    """FastAPI dependency for TrustIndex."""
    return get_container().trust_index


def get_volatility_index() -> "VolatilityIndex":
    """FastAPI dependency for VolatilityIndex."""
    return get_container().volatility_index


def get_escalation_risk() -> "EscalationRisk":
    """FastAPI dependency for EscalationRisk."""
    return get_container().escalation_risk


def get_policy_brief_generator() -> "PolicyBriefGenerator":
    """FastAPI dependency for PolicyBriefGenerator."""
    return get_container().policy_brief_generator


def get_sentiment_forecaster() -> "SentimentForecaster":
    """FastAPI dependency for SentimentForecaster."""
    return get_container().sentiment_forecaster
