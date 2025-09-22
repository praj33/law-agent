"""Advanced Reinforcement Learning System with Multi-Dimensional State and Reward."""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from loguru import logger

from ..core.state import LegalDomain, UserType, FeedbackType
from ..core.config import settings


@dataclass
class AdvancedState:
    """Advanced multi-dimensional state representation."""
    # User Context
    user_type: str
    user_satisfaction: float
    user_expertise_level: float
    session_length: int
    
    # Legal Context
    current_domain: str
    domain_confidence: float
    query_complexity: float
    legal_urgency: float
    
    # Historical Context
    recent_domains: List[str]
    feedback_history: List[str]
    success_rate: float
    avg_response_time: float
    
    # Temporal Context
    time_of_day: int  # 0-23
    day_of_week: int  # 0-6
    session_duration: float
    
    def to_vector(self) -> np.ndarray:
        """Convert state to numerical vector for ML algorithms."""
        # Encode categorical variables
        user_type_encoded = {"common_person": 0, "law_firm": 1, "legal_student": 2}.get(self.user_type, 0)
        domain_encoded = {domain.value: i for i, domain in enumerate(LegalDomain)}.get(self.current_domain, 0)
        
        # Create feature vector
        vector = np.array([
            user_type_encoded,
            self.user_satisfaction,
            self.user_expertise_level,
            self.session_length / 100.0,  # Normalize
            domain_encoded,
            self.domain_confidence,
            self.query_complexity,
            self.legal_urgency,
            len(self.recent_domains) / 10.0,  # Normalize
            len(self.feedback_history) / 20.0,  # Normalize
            self.success_rate,
            self.avg_response_time / 60.0,  # Normalize to minutes
            self.time_of_day / 24.0,  # Normalize
            self.day_of_week / 7.0,  # Normalize
            self.session_duration / 3600.0  # Normalize to hours
        ])
        
        return vector
    
    def to_string(self) -> str:
        """Convert to string for hashing/indexing."""
        return f"{self.user_type}_{self.current_domain}_{int(self.user_satisfaction*10)}_{int(self.domain_confidence*10)}"


@dataclass
class AdvancedReward:
    """Multi-dimensional reward structure."""
    user_satisfaction: float = 0.0
    legal_accuracy: float = 0.0
    response_quality: float = 0.0
    time_efficiency: float = 0.0
    domain_expertise: float = 0.0
    user_engagement: float = 0.0
    learning_progress: float = 0.0
    
    def total_reward(self, weights: Dict[str, float] = None) -> float:
        """Calculate weighted total reward."""
        if weights is None:
            weights = {
                "user_satisfaction": 0.25,
                "legal_accuracy": 0.20,
                "response_quality": 0.15,
                "time_efficiency": 0.10,
                "domain_expertise": 0.10,
                "user_engagement": 0.10,
                "learning_progress": 0.10
            }
        
        return sum(getattr(self, key) * weight for key, weight in weights.items())


class AdvancedAgentMemory:
    """Advanced agent memory system with pattern recognition."""
    
    def __init__(self, max_memory_size: int = 10000):
        self.max_memory_size = max_memory_size
        
        # Multi-level memory storage
        self.episodic_memory = deque(maxlen=max_memory_size)  # Recent experiences
        self.semantic_memory = defaultdict(list)  # Domain-specific knowledge
        self.procedural_memory = defaultdict(float)  # Learned skills/patterns
        
        # Pattern recognition
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.user_preferences = defaultdict(dict)
        
        # Performance tracking
        self.domain_performance = defaultdict(lambda: {"successes": 0, "total": 0, "avg_reward": 0.0})
        self.temporal_patterns = defaultdict(list)
        
        logger.info("Advanced Agent Memory initialized")
    
    def store_experience(
        self,
        state: AdvancedState,
        action: Dict[str, Any],
        reward: AdvancedReward,
        next_state: Optional[AdvancedState] = None
    ):
        """Store experience in multi-level memory."""
        
        experience = {
            "timestamp": datetime.now(),
            "state": asdict(state),
            "action": action,
            "reward": asdict(reward),
            "next_state": asdict(next_state) if next_state else None,
            "total_reward": reward.total_reward()
        }
        
        # Store in episodic memory
        self.episodic_memory.append(experience)
        
        # Update semantic memory (domain-specific)
        domain = state.current_domain
        self.semantic_memory[domain].append({
            "state_vector": state.to_vector(),
            "action": action,
            "reward": reward.total_reward(),
            "timestamp": datetime.now()
        })
        
        # Update procedural memory (learned patterns)
        state_key = state.to_string()
        action_key = f"{action.get('action', 'unknown')}_{action.get('response_style', 'default')}"
        procedure_key = f"{state_key}_{action_key}"
        
        # Exponential moving average for procedural memory
        alpha = 0.1
        current_value = self.procedural_memory[procedure_key]
        self.procedural_memory[procedure_key] = (1 - alpha) * current_value + alpha * reward.total_reward()
        
        # Pattern recognition
        if reward.total_reward() > 0.5:
            self.success_patterns[domain].append({
                "state": state.to_vector(),
                "action": action,
                "reward": reward.total_reward()
            })
        elif reward.total_reward() < -0.5:
            self.failure_patterns[domain].append({
                "state": state.to_vector(),
                "action": action,
                "reward": reward.total_reward()
            })
        
        # Update performance tracking
        self.domain_performance[domain]["total"] += 1
        if reward.total_reward() > 0:
            self.domain_performance[domain]["successes"] += 1
        
        # Update average reward
        perf = self.domain_performance[domain]
        perf["avg_reward"] = (perf["avg_reward"] * (perf["total"] - 1) + reward.total_reward()) / perf["total"]
        
        # Store temporal patterns
        hour = datetime.now().hour
        self.temporal_patterns[hour].append(reward.total_reward())
        
        logger.debug(f"Stored experience: domain={domain}, reward={reward.total_reward():.3f}")
    
    def retrieve_similar_experiences(
        self,
        current_state: AdvancedState,
        similarity_threshold: float = 0.8,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve similar experiences for learning."""
        
        current_vector = current_state.to_vector()
        similar_experiences = []
        
        # Search through semantic memory for the current domain
        domain_memories = self.semantic_memory[current_state.current_domain]
        
        for memory in domain_memories[-100:]:  # Check recent memories
            memory_vector = memory["state_vector"]
            
            # Calculate cosine similarity
            similarity = np.dot(current_vector, memory_vector) / (
                np.linalg.norm(current_vector) * np.linalg.norm(memory_vector) + 1e-8
            )
            
            if similarity >= similarity_threshold:
                similar_experiences.append({
                    "similarity": similarity,
                    "action": memory["action"],
                    "reward": memory["reward"],
                    "timestamp": memory["timestamp"]
                })
        
        # Sort by similarity and return top results
        similar_experiences.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_experiences[:max_results]
    
    def get_best_action_for_state(self, state: AdvancedState) -> Optional[Dict[str, Any]]:
        """Get best action based on procedural memory."""
        
        state_key = state.to_string()
        best_action = None
        best_reward = float('-inf')
        
        # Search procedural memory for best action
        for procedure_key, reward in self.procedural_memory.items():
            if procedure_key.startswith(state_key):
                if reward > best_reward:
                    best_reward = reward
                    # Extract action from procedure key
                    action_part = procedure_key.replace(f"{state_key}_", "")
                    action_components = action_part.split("_")
                    best_action = {
                        "action": action_components[0] if action_components else "balanced",
                        "response_style": action_components[1] if len(action_components) > 1 else "adaptive"
                    }
        
        return best_action if best_reward > 0 else None
    
    def get_domain_expertise(self, domain: str) -> float:
        """Get expertise level for a specific domain."""
        perf = self.domain_performance[domain]
        if perf["total"] == 0:
            return 0.5  # Default neutral expertise
        
        # Combine success rate and average reward
        success_rate = perf["successes"] / perf["total"]
        avg_reward = max(-1.0, min(1.0, perf["avg_reward"]))  # Clamp to [-1, 1]
        
        # Weighted combination
        expertise = 0.6 * success_rate + 0.4 * (avg_reward + 1) / 2
        return max(0.0, min(1.0, expertise))
    
    def get_temporal_insights(self) -> Dict[str, Any]:
        """Get insights about temporal patterns."""
        
        insights = {
            "best_hours": [],
            "worst_hours": [],
            "peak_performance_time": None,
            "avg_performance_by_hour": {}
        }
        
        hour_averages = {}
        for hour, rewards in self.temporal_patterns.items():
            if rewards:
                avg_reward = np.mean(rewards)
                hour_averages[hour] = avg_reward
                insights["avg_performance_by_hour"][hour] = avg_reward
        
        if hour_averages:
            # Find best and worst performing hours
            sorted_hours = sorted(hour_averages.items(), key=lambda x: x[1], reverse=True)
            insights["best_hours"] = [hour for hour, _ in sorted_hours[:3]]
            insights["worst_hours"] = [hour for hour, _ in sorted_hours[-3:]]
            insights["peak_performance_time"] = sorted_hours[0][0]
        
        return insights
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        
        return {
            "episodic_memory_size": len(self.episodic_memory),
            "semantic_memory_domains": len(self.semantic_memory),
            "procedural_memory_size": len(self.procedural_memory),
            "success_patterns": {domain: len(patterns) for domain, patterns in self.success_patterns.items()},
            "failure_patterns": {domain: len(patterns) for domain, patterns in self.failure_patterns.items()},
            "domain_performance": dict(self.domain_performance),
            "temporal_insights": self.get_temporal_insights()
        }
