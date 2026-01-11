"""
National Public Discourse Intelligence System (NIS) - API Server

Elite-level FastAPI application with:
- Modern lifespan management
- Structured logging
- Custom exception handling
- Request tracing
- Security middleware
- Dependency injection
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import get_settings
from backend.api.routes import dashboard, alerts
from backend.database.database import init_db

# Core infrastructure
from backend.core.logging import setup_logging, get_logger
from backend.core.exceptions import register_exception_handlers
from backend.core.middleware import (
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from backend.core.dependencies import get_container

# Initialize settings and logging
settings = get_settings()
setup_logging(
    level="DEBUG" if settings.DATABASE_ECHO else "INFO",
    json_format=False,  # Set to True for production
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown events with proper resource management.
    """
    # ==================== STARTUP ====================
    logger.info("🚀 Starting NIS API Server...")
    
    # Initialize database
    try:
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.warning(f"⚠ Database initialization warning: {e}")
        logger.info("  This might be expected if migrations haven't been run yet")
    
    # Warm up service container (lazy initialization)
    try:
        container = get_container()
        logger.info("✓ Service container initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize service container: {e}")
        raise
    
    logger.info(f"✓ NIS API Server started successfully")
    logger.info(f"  → Environment: {'development' if settings.DATABASE_ECHO else 'production'}")
    logger.info(f"  → API Version: {settings.API_V1_STR}")
    
    yield  # Application is running
    
    # ==================== SHUTDOWN ====================
    logger.info("👋 Shutting down NIS API Server...")
    
    # Cleanup resources
    from backend.core.dependencies import reset_container
    reset_container()
    
    logger.info("✓ Cleanup completed. Goodbye!")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    **National Public Discourse Intelligence System (NIS)**
    
    A comprehensive platform for monitoring, analyzing, and understanding 
    public discourse across social media platforms.
    
    ## Features
    
    * **Real-time Sentiment Analysis** - Track public sentiment trends
    * **Emotion Detection** - Identify emotional patterns in discourse
    * **Issue Clustering** - Automatic topic categorization
    * **Integrity Monitoring** - Detect coordinated campaigns
    * **Risk Assessment** - Early warning system for escalation
    * **Policy Briefs** - AI-generated insights for decision makers
    """,
    version="2.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================================
# Middleware Configuration (order matters - last added is first executed)
# ============================================================================

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# Request context and logging
app.add_middleware(RequestContextMiddleware)

# ============================================================================
# Exception Handlers
# ============================================================================

register_exception_handlers(app)

# ============================================================================
# Router Configuration
# ============================================================================

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["Dashboard"],
)

app.include_router(
    alerts.router,
    prefix=f"{settings.API_V1_STR}/alerts",
    tags=["Alerts"],
)

# ============================================================================
# Root Endpoints
# ============================================================================

@app.get(
    "/",
    summary="API Root",
    description="Returns basic API information and status",
    response_class=JSONResponse,
)
async def root():
    """API root endpoint with system information."""
    return {
        "name": "National Public Discourse Intelligence System",
        "acronym": "NIS",
        "status": "operational",
        "version": "2.0.0",
        "api_version": settings.API_V1_STR,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": f"{settings.API_V1_STR}/openapi.json",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Returns the health status of the API and its dependencies",
    tags=["System"],
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns detailed status of all system components.
    """
    from backend.database.database import engine
    from sqlalchemy import text
    
    # Check database connection
    db_healthy = True
    db_message = "connected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_healthy = False
        db_message = str(e)
    
    is_healthy = db_healthy
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "components": {
            "api": {"status": "healthy"},
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": db_message,
            },
        },
    }


@app.get(
    "/ready",
    summary="Readiness Check",
    description="Indicates if the application is ready to receive traffic",
    tags=["System"],
)
async def readiness_check():
    """
    Readiness probe for Kubernetes/container orchestrators.
    
    Returns 200 if the app is ready to handle requests.
    """
    return {"ready": True}


# ============================================================================
# Development Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
