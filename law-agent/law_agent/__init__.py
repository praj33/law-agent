"""
Law Agent - Robust, scalable law agent with reinforcement learning and dynamic interfaces.

This package provides a comprehensive legal assistance system that serves both
common people and law firms through intelligent agent-based interactions.
"""

__version__ = "1.0.0"
__author__ = "Raj & Aditya"
__email__ = "team@lawagent.com"

from .core.config import settings
from .core.agent import LawAgent
from .api.main import app

__all__ = ["settings", "LawAgent", "app"]
