"""
Elite-level exception handling for NIS backend.

Features:
- Hierarchical exception classes
- Structured error responses
- Automatic HTTP status code mapping
- Exception context preservation
- FastAPI exception handler integration
"""

from typing import Any, Optional
from enum import Enum
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone


class ErrorCode(str, Enum):
    """Standardized error codes for API responses."""
    
    # General errors (1xxx)
    INTERNAL_ERROR = "NIS-1000"
    VALIDATION_ERROR = "NIS-1001"
    NOT_FOUND = "NIS-1002"
    RATE_LIMITED = "NIS-1003"
    UNAUTHORIZED = "NIS-1004"
    FORBIDDEN = "NIS-1005"
    
    # Data ingestion errors (2xxx)
    REDDIT_API_ERROR = "NIS-2001"
    TRENDS_API_ERROR = "NIS-2002"
    DATA_FETCH_ERROR = "NIS-2003"
    DATA_PARSE_ERROR = "NIS-2004"
    
    # Database errors (3xxx)
    DATABASE_ERROR = "NIS-3001"
    CONNECTION_ERROR = "NIS-3002"
    QUERY_ERROR = "NIS-3003"
    INTEGRITY_ERROR = "NIS-3004"
    
    # Analysis errors (4xxx)
    ANALYSIS_ERROR = "NIS-4001"
    NLP_ERROR = "NIS-4002"
    CLUSTERING_ERROR = "NIS-4003"
    PREDICTION_ERROR = "NIS-4004"
    
    # Email/Alert errors (5xxx)
    EMAIL_ERROR = "NIS-5001"
    ALERT_COOLDOWN = "NIS-5002"
    NOTIFICATION_ERROR = "NIS-5003"


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    
    success: bool = False
    error_code: str
    message: str
    detail: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None
    path: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error_code": "NIS-1000",
                "message": "An unexpected error occurred",
                "detail": "Database connection timeout",
                "timestamp": "2026-01-11T10:30:00Z",
                "request_id": "abc-123-def",
                "path": "/api/v1/dashboard/summary"
            }
        }


class NISException(Exception):
    """
    Base exception for all NIS application errors.
    
    Provides structured error information and automatic HTTP response mapping.
    """
    
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR
    status_code: int = 500
    message: str = "An unexpected error occurred"
    
    def __init__(
        self,
        message: Optional[str] = None,
        detail: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.detail = detail
        self.context = context or {}
        super().__init__(self.message)
    
    def to_response(self, request_id: Optional[str] = None, path: Optional[str] = None) -> ErrorResponse:
        """Convert exception to standardized error response."""
        return ErrorResponse(
            error_code=self.error_code.value,
            message=self.message,
            detail=self.detail,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=request_id,
            path=path,
        )


# ============================================================================
# Data Ingestion Exceptions
# ============================================================================

class DataIngestionError(NISException):
    """Base exception for data ingestion errors."""
    error_code = ErrorCode.DATA_FETCH_ERROR
    status_code = 502
    message = "Failed to fetch data from external source"


class RedditAPIError(DataIngestionError):
    """Reddit API specific errors."""
    error_code = ErrorCode.REDDIT_API_ERROR
    message = "Failed to communicate with Reddit API"


class TrendsAPIError(DataIngestionError):
    """Google Trends API specific errors."""
    error_code = ErrorCode.TRENDS_API_ERROR
    message = "Failed to fetch Google Trends data"


class DataParseError(DataIngestionError):
    """Data parsing/transformation errors."""
    error_code = ErrorCode.DATA_PARSE_ERROR
    status_code = 500
    message = "Failed to parse external data"


# ============================================================================
# Database Exceptions
# ============================================================================

class DatabaseError(NISException):
    """Base exception for database errors."""
    error_code = ErrorCode.DATABASE_ERROR
    status_code = 500
    message = "A database error occurred"


class ConnectionError(DatabaseError):
    """Database connection errors."""
    error_code = ErrorCode.CONNECTION_ERROR
    status_code = 503
    message = "Failed to connect to database"


class QueryError(DatabaseError):
    """Query execution errors."""
    error_code = ErrorCode.QUERY_ERROR
    message = "Failed to execute database query"


class IntegrityError(DatabaseError):
    """Data integrity constraint violations."""
    error_code = ErrorCode.INTEGRITY_ERROR
    status_code = 409
    message = "Data integrity constraint violated"


# ============================================================================
# Analysis Exceptions
# ============================================================================

class AnalysisError(NISException):
    """Base exception for analysis errors."""
    error_code = ErrorCode.ANALYSIS_ERROR
    status_code = 500
    message = "Analysis operation failed"


class NLPError(AnalysisError):
    """NLP processing errors."""
    error_code = ErrorCode.NLP_ERROR
    message = "Natural language processing failed"


class ClusteringError(AnalysisError):
    """Clustering operation errors."""
    error_code = ErrorCode.CLUSTERING_ERROR
    message = "Issue clustering failed"


class PredictionError(AnalysisError):
    """Prediction/forecasting errors."""
    error_code = ErrorCode.PREDICTION_ERROR
    message = "Prediction model failed"


# ============================================================================
# Notification Exceptions
# ============================================================================

class NotificationError(NISException):
    """Base exception for notification errors."""
    error_code = ErrorCode.NOTIFICATION_ERROR
    status_code = 500
    message = "Failed to send notification"


class EmailError(NotificationError):
    """Email sending errors."""
    error_code = ErrorCode.EMAIL_ERROR
    message = "Failed to send email"


class AlertCooldownError(NotificationError):
    """Alert rate limiting errors."""
    error_code = ErrorCode.ALERT_COOLDOWN
    status_code = 429
    message = "Alert cooldown is active"


# ============================================================================
# HTTP Exceptions (Client Errors)
# ============================================================================

class NotFoundError(NISException):
    """Resource not found."""
    error_code = ErrorCode.NOT_FOUND
    status_code = 404
    message = "Resource not found"


class ValidationError(NISException):
    """Request validation error."""
    error_code = ErrorCode.VALIDATION_ERROR
    status_code = 422
    message = "Request validation failed"


class RateLimitError(NISException):
    """Rate limit exceeded."""
    error_code = ErrorCode.RATE_LIMITED
    status_code = 429
    message = "Rate limit exceeded"


class UnauthorizedError(NISException):
    """Authentication required."""
    error_code = ErrorCode.UNAUTHORIZED
    status_code = 401
    message = "Authentication required"


class ForbiddenError(NISException):
    """Access denied."""
    error_code = ErrorCode.FORBIDDEN
    status_code = 403
    message = "Access denied"


# ============================================================================
# Exception Handlers for FastAPI
# ============================================================================

async def nis_exception_handler(request: Request, exc: NISException) -> JSONResponse:
    """Handle NIS custom exceptions."""
    from backend.core.logging import request_id_ctx
    
    request_id = request_id_ctx.get()
    error_response = exc.to_response(request_id=request_id, path=str(request.url.path))
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPExceptions with consistent format."""
    from backend.core.logging import request_id_ctx
    
    request_id = request_id_ctx.get()
    
    error_response = ErrorResponse(
        error_code=f"HTTP-{exc.status_code}",
        message=str(exc.detail),
        timestamp=datetime.now(timezone.utc).isoformat(),
        request_id=request_id,
        path=str(request.url.path),
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    from backend.core.logging import request_id_ctx, get_logger
    
    logger = get_logger(__name__)
    request_id = request_id_ctx.get()
    
    # Log the full exception
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"request_id": request_id, "path": str(request.url.path)}
    )
    
    error_response = ErrorResponse(
        error_code=ErrorCode.INTERNAL_ERROR.value,
        message="An unexpected error occurred",
        detail=str(exc) if __debug__ else None,  # Only show detail in debug mode
        timestamp=datetime.now(timezone.utc).isoformat(),
        request_id=request_id,
        path=str(request.url.path),
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with FastAPI app."""
    app.add_exception_handler(NISException, nis_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
