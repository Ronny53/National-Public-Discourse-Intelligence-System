"""
Elite-level logging configuration for NIS backend.

Features:
- Structured JSON logging for production
- Pretty console logging for development
- Request correlation IDs
- Performance tracking
- Log rotation support
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from contextvars import ContextVar
from functools import wraps
import time

# Context variable for request correlation ID
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON structured log formatter for production environments.
    Outputs logs in a format suitable for log aggregation systems.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request ID if available
        request_id = request_id_ctx.get()
        if request_id:
            log_entry["request_id"] = request_id
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        extra_data = getattr(record, "extra_data", None)
        if extra_data is not None:
            log_entry["data"] = extra_data
        
        return json.dumps(log_entry, default=str)


class PrettyFormatter(logging.Formatter):
    """
    Human-readable colored log formatter for development.
    """
    
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Build prefix with request ID if available
        request_id = request_id_ctx.get()
        request_prefix = f"[{request_id[:8]}] " if request_id else ""
        
        # Format timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build the log message
        formatted = (
            f"{color}{timestamp} | {record.levelname:8} | "
            f"{request_prefix}{record.name} | "
            f"{record.getMessage()}{self.RESET}"
        )
        
        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        
        return formatted


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that supports structured extra data.
    """
    
    extra: dict  # type: ignore
    
    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        # Merge extra data
        extra = kwargs.get("extra", {})
        if self.extra:
            extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs
    
    def with_context(self, **context: Any) -> "LoggerAdapter":
        """Create a new adapter with additional context."""
        current_extra = dict(self.extra) if self.extra else {}
        current_extra.update(context)
        return LoggerAdapter(self.logger, current_extra)


def get_logger(name: str, **default_context) -> LoggerAdapter:
    """
    Get a logger instance with optional default context.
    
    Args:
        name: Logger name (usually __name__)
        **default_context: Default context to include in all logs
    
    Returns:
        LoggerAdapter with structured logging support
    
    Example:
        logger = get_logger(__name__, service="reddit_client")
        logger.info("Fetching posts", extra={"subreddit": "india"})
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, default_context)


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[Path] = None,
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting (for production)
        log_file: Optional file path for log output
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Set formatter based on environment
    if json_format:
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(PrettyFormatter())
    
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
        )
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def log_execution_time(logger: Optional[LoggerAdapter] = None, level: int = logging.DEBUG):
    """
    Decorator to log function execution time.
    
    Example:
        @log_execution_time()
        def slow_function():
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            start_time = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start_time) * 1000
                _logger.log(
                    level,
                    f"{func.__name__} completed in {elapsed:.2f}ms"
                )
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start_time) * 1000
                _logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}ms: {e}"
                )
                raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            start_time = time.perf_counter()
            
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.perf_counter() - start_time) * 1000
                _logger.log(
                    level,
                    f"{func.__name__} completed in {elapsed:.2f}ms"
                )
                return result
            except Exception as e:
                elapsed = (time.perf_counter() - start_time) * 1000
                _logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}ms: {e}"
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator
