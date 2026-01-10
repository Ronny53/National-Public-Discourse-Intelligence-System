import os
from pydantic_settings import BaseSettings
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
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/nis_db"
    DATABASE_ECHO: bool = False  # Set to True for SQL query logging
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
