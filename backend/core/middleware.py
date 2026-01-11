"""
Elite-level middleware for NIS backend.

Features:
- Request ID generation and propagation
- Request/Response logging
- Performance timing
- Security headers
- Rate limiting support
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.core.logging import get_logger, request_id_ctx

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds request context for logging and tracing.
    
    - Generates unique request ID
    - Logs request/response details
    - Measures request duration
    - Adds security headers
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Set request ID in context for logging
        token = request_id_ctx.set(request_id)
        
        # Start timing
        start_time = time.perf_counter()
        
        # Log incoming request
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client": request.client.host if request.client else "unknown",
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log response
            log_level = "info" if response.status_code < 400 else "warning"
            getattr(logger, log_level)(
                f"← {request.method} {request.url.path} → {response.status_code} ({duration_ms:.2f}ms)",
                extra={
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )
            
            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            
            return response
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"✗ {request.method} {request.url.path} → Error ({duration_ms:.2f}ms): {e}",
                exc_info=True
            )
            raise
        
        finally:
            # Reset context
            request_id_ctx.reset(token)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Cache control for API responses
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        
        return response


class RateLimitState:
    """Simple in-memory rate limit state."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = {}
    
    def is_allowed(self, client_id: str) -> tuple[bool, int]:
        """
        Check if request is allowed.
        
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get or create request history for client
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Clean old requests
        self.requests[client_id] = [
            ts for ts in self.requests[client_id]
            if ts > window_start
        ]
        
        # Check limit
        current_count = len(self.requests[client_id])
        if current_count >= self.max_requests:
            return False, 0
        
        # Record this request
        self.requests[client_id].append(now)
        
        return True, self.max_requests - current_count - 1


# Global rate limiter instance
_rate_limiter = RateLimitState()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    
    Uses client IP for identification.
    Can be extended to use API keys or user IDs.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 100,
        window_seconds: int = 60,
        exclude_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.rate_limiter = RateLimitState(max_requests, window_seconds)
        self.exclude_paths = exclude_paths or ["/health", "/"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        is_allowed, remaining = self.rate_limiter.is_allowed(client_id)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {client_id}",
                extra={"client": client_id, "path": request.url.path}
            )
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(self.rate_limiter.window_seconds),
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
