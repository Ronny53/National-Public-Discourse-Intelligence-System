import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "National Public Discourse Intelligence System"
    API_V1_STR: str = "/api/v1"
    
    # Reddit API Credentials
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "python:nis.hackathon:v1.0.0 (by /u/nis_bot)"
    
    # Data Sources
    TARGET_SUBREDDITS: list[str] = ["india", "indianews", "indiaspeaks", "bangalore", "delhi", "mumbai"]
    TARGET_REGION: str = "IN"
    
    # Analysis Config
    ENABLE_SYNTHETIC_DATA_FALLBACK: bool = True
    
    # Database Configuration
    # Use SQLite for development (no server needed), PostgreSQL for production
    # Set DATABASE_URL environment variable to use PostgreSQL
    DATABASE_URL: str = "sqlite:///./nis_dev.db"  # SQLite for development
    DATABASE_ECHO: bool = False  # Set to True for SQL query logging
    
    # Email Alert Configuration
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_APP_PASSWORD: str = ""
    EMAIL_RECIPIENTS: list[str] = []
    ALERT_THRESHOLD: float = 70.0
    ALERT_COOLDOWN_MINUTES: int = 15  # Prevent duplicate alerts within this time
    
    @field_validator('EMAIL_RECIPIENTS', mode='before')
    @classmethod
    def parse_recipients(cls, v):
        """Parse EMAIL_RECIPIENTS from JSON string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fallback: treat as comma-separated string
                return [email.strip() for email in v.split(',') if email.strip()]
        return v or []
    
    class Config:
        # Try backend/.env first, then root .env
        backend_env = Path(__file__).parent.parent / ".env"
        root_env = Path(__file__).parent.parent.parent / ".env"
        env_file = str(backend_env) if backend_env.exists() else (str(root_env) if root_env.exists() else ".env")

@lru_cache()
def get_settings():
    return Settings()
