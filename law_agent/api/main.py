"""Main FastAPI application for the Law Agent system."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from ..core.config import settings
from .routes import router
from .middleware import setup_logging, setup_metrics


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Law Agent API",
        description="Robust, scalable law agent with reinforcement learning and dynamic interfaces",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Setup middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup logging and metrics
    setup_logging(app)
    if settings.enable_metrics:
        setup_metrics(app)
    
    # Include routers
    app.include_router(router, prefix="/api/v1")

    # Include perfect RL feedback router
    try:
        from law_agent.api.perfect_feedback_api import router as perfect_feedback_router
        app.include_router(perfect_feedback_router, prefix="/api/v1")
        logger.info("✅ Perfect RL Feedback API included")
    except Exception as e:
        logger.warning(f"Perfect RL Feedback API not available: {e}")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.0.0"}
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    logger.info("Law Agent API initialized successfully")
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "law_agent.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
