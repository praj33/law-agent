"""Middleware for the Law Agent API."""

import time
from typing import Callable
from fastapi import FastAPI, Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sys

from ..core.config import settings


# Prometheus metrics
REQUEST_COUNT = Counter(
    'law_agent_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'law_agent_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

QUERY_COUNT = Counter(
    'law_agent_queries_total',
    'Total number of legal queries processed',
    ['domain', 'user_type']
)

FEEDBACK_COUNT = Counter(
    'law_agent_feedback_total',
    'Total feedback received',
    ['feedback_type']
)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} "
            f"Duration: {duration:.3f}s "
            f"Path: {request.url.path}"
        )
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for Prometheus metrics collection."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Collect metrics for requests."""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Extract endpoint info
        method = request.method
        path = request.url.path
        status_code = str(response.status_code)
        
        # Update metrics
        REQUEST_COUNT.labels(
            method=method,
            endpoint=path,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=path
        ).observe(duration)
        
        return response


def setup_logging(app: FastAPI) -> None:
    """Setup logging configuration."""
    
    # Configure loguru
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True
    )
    
    # Add file handler if log file is specified
    if settings.log_file:
        logger.add(
            settings.log_file,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    logger.info("Logging middleware configured")


def setup_metrics(app: FastAPI) -> None:
    """Setup Prometheus metrics."""
    
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware)
    
    # Add metrics endpoint
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint."""
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    logger.info("Metrics middleware configured")


def track_query_metrics(domain: str, user_type: str) -> None:
    """Track query-specific metrics."""
    QUERY_COUNT.labels(
        domain=domain,
        user_type=user_type
    ).inc()


def track_feedback_metrics(feedback_type: str) -> None:
    """Track feedback-specific metrics."""
    FEEDBACK_COUNT.labels(
        feedback_type=feedback_type
    ).inc()
