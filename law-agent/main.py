"""Main entry point for the Law Agent application."""

import uvicorn
from law_agent.core.config import settings


def main():
    """Run the Law Agent application."""
    uvicorn.run(
        "law_agent.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
