"""
Core Dependencies for FastAPI Dependency Injection
Provides shared instances and dependency injection for the law agent API
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from loguru import logger

from law_agent.core.agent import LawAgent

# Global agent instance
_law_agent_instance: Optional[LawAgent] = None


def get_law_agent() -> LawAgent:
    """
    Dependency injection for LawAgent instance
    Returns the singleton LawAgent instance
    """
    global _law_agent_instance
    
    if _law_agent_instance is None:
        try:
            logger.info("🚀 Initializing LawAgent instance for dependency injection")
            _law_agent_instance = LawAgent()
            logger.info("✅ LawAgent instance created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create LawAgent instance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize law agent: {str(e)}"
            )
    
    return _law_agent_instance


def get_current_agent() -> Generator[LawAgent, None, None]:
    """
    Generator-based dependency for LawAgent
    Useful for cleanup operations if needed
    """
    agent = get_law_agent()
    try:
        yield agent
    finally:
        # Cleanup operations if needed
        pass


def reset_agent_instance():
    """
    Reset the global agent instance (useful for testing)
    """
    global _law_agent_instance
    _law_agent_instance = None
    logger.info("🔄 LawAgent instance reset")


# Health check dependency
def health_check() -> dict:
    """
    Health check dependency
    """
    try:
        agent = get_law_agent()
        return {
            "status": "healthy",
            "agent_initialized": agent is not None,
            "perfect_rl_available": hasattr(agent, 'perfect_rl_policy') and agent.perfect_rl_policy is not None,
            "ml_classifier_available": hasattr(agent, 'domain_classifier') and agent.domain_classifier is not None,
            "memory_available": hasattr(agent, 'memory') and agent.memory is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Authentication dependency (placeholder for future use)
def get_current_user():
    """
    Placeholder for user authentication
    Currently returns anonymous user
    """
    return {
        "user_id": "anonymous",
        "user_type": "common_person",
        "authenticated": False
    }


# Rate limiting dependency (placeholder for future use)
def rate_limit_check():
    """
    Placeholder for rate limiting
    Currently allows all requests
    """
    return True
