from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Create database engine
# SQLite doesn't support pool_pre_ping, pool_size, max_overflow
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )
    logger.info("Using SQLite database (development mode)")
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=10,
        max_overflow=20
    )
    logger.info("Using PostgreSQL database (production mode)")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    This should be called once when setting up the application.
    """
    Base.metadata.create_all(bind=engine)
