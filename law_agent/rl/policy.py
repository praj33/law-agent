"""Reinforcement Learning policy for the Law Agent system."""

import json
import pickle
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import os
from loguru import logger

from ..core.config import settings
from ..core.state import LegalDomain, UserType

# Use the factory function as the default RLPolicy
RLPolicy = lambda: create_rl_policy("qtable")


class RLPolicy(ABC):
    """Abstract base class for RL policies."""
    
    @abstractmethod
    async def get_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get action recommendation for given state."""
        pass
    
    @abstractmethod
    async def update_policy(self, state: Dict[str, Any], reward: float) -> None:
        """Update policy based on reward feedback."""
        pass
    
    @abstractmethod
    def save_policy(self, path: str) -> None:
        """Save policy to disk."""
        pass
    
    @abstractmethod
    def load_policy(self, path: str) -> None:
        """Load policy from disk."""
        pass


class QTablePolicy(RLPolicy):
    """Q-Table based reinforcement learning policy."""
    
    def __init__(self, learning_rate: float = None, exploration_rate: float = None):
        """Initialize Q-Table policy."""
        self.learning_rate = learning_rate or settings.rl_learning_rate
        self.exploration_rate = exploration_rate or settings.rl_exploration_rate
        self.discount_factor = 0.95
        
        # Q-table: state -> action -> Q-value
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Action space definition
        self.actions = self._define_action_space()
        
        # State discretization parameters
        self.satisfaction_bins = [-1.0, -0.5, 0.0, 0.5, 1.0]
        self.confidence_bins = [0.0, 0.3, 0.6, 0.8, 1.0]
        
        logger.info("Q-Table RL Policy initialized")
    
    def _define_action_space(self) -> List[str]:
        """Define possible actions the agent can take."""
        actions = []
        
        # Route selection actions
        route_actions = [
            "recommend_simple_route",
            "recommend_detailed_route",
            "recommend_professional_route",
            "recommend_self_help_route"
        ]
        
        # Glossary emphasis actions
        glossary_actions = [
            "emphasize_basic_terms",
            "emphasize_advanced_terms",
            "provide_examples",
            "provide_cross_references"
        ]
        
        # Response style actions
        style_actions = [
            "formal_response",
            "casual_response",
            "detailed_response",
            "concise_response"
        ]
        
        # Confidence adjustment actions
        confidence_actions = [
            "high_confidence_response",
            "moderate_confidence_response",
            "low_confidence_response",
            "request_clarification"
        ]
        
        actions.extend(route_actions)
        actions.extend(glossary_actions)
        actions.extend(style_actions)
        actions.extend(confidence_actions)
        
        return actions
    
    def _discretize_state(self, state: Dict[str, Any]) -> str:
        """Convert continuous state to discrete state string."""
        # Extract key features
        user_type = state.get("user_type", "common_person")
        current_domain = state.get("current_domain", "unknown")
        satisfaction_score = state.get("satisfaction_score", 0.0)
        interaction_count = state.get("interaction_count", 0)
        average_confidence = state.get("average_confidence", 0.5)
        
        # Discretize continuous values
        satisfaction_bin = self._get_bin_index(satisfaction_score, self.satisfaction_bins)
        confidence_bin = self._get_bin_index(average_confidence, self.confidence_bins)
        
        # Create interaction count bins
        if interaction_count == 0:
            interaction_bin = "new"
        elif interaction_count <= 5:
            interaction_bin = "few"
        elif interaction_count <= 20:
            interaction_bin = "moderate"
        else:
            interaction_bin = "many"
        
        # Get recent feedback pattern
        recent_feedback = state.get("recent_feedback", [])
        if not recent_feedback:
            feedback_pattern = "none"
        elif recent_feedback.count("upvote") > recent_feedback.count("downvote"):
            feedback_pattern = "positive"
        elif recent_feedback.count("downvote") > recent_feedback.count("upvote"):
            feedback_pattern = "negative"
        else:
            feedback_pattern = "mixed"
        
        # Create state string
        state_str = f"{user_type}_{current_domain}_{satisfaction_bin}_{confidence_bin}_{interaction_bin}_{feedback_pattern}"
        
        return state_str
    
    def _get_bin_index(self, value: float, bins: List[float]) -> int:
        """Get bin index for a continuous value."""
        for i, bin_edge in enumerate(bins[1:], 1):
            if value <= bin_edge:
                return i - 1
        return len(bins) - 2
    
    async def get_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get action using epsilon-greedy policy."""
        state_str = self._discretize_state(state)
        
        # Initialize state in Q-table if not exists
        if state_str not in self.q_table:
            self.q_table[state_str] = {action: 0.0 for action in self.actions}
        
        # Epsilon-greedy action selection
        if np.random.random() < self.exploration_rate:
            # Explore: random action
            action = np.random.choice(self.actions)
            logger.debug(f"Exploring with action: {action}")
        else:
            # Exploit: best action
            q_values = self.q_table[state_str]
            action = max(q_values.items(), key=lambda x: x[1])[0]
            logger.debug(f"Exploiting with action: {action}")
        
        # Convert action to recommendation
        recommendation = self._action_to_recommendation(action, state)
        
        # Store last state-action for learning
        self.last_state = state_str
        self.last_action = action
        
        return recommendation
    
    def _action_to_recommendation(self, action: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Convert action to concrete recommendation."""
        recommendation = {
            "action": action,
            "route_preference": [],
            "glossary_emphasis": "balanced",
            "response_style": "adaptive",
            "confidence_adjustment": 0.0
        }
        
        # Route recommendations
        if "simple" in action:
            recommendation["route_preference"] = ["basic", "self-help"]
        elif "detailed" in action:
            recommendation["route_preference"] = ["comprehensive", "step-by-step"]
        elif "professional" in action:
            recommendation["route_preference"] = ["expert", "complex"]
        
        # Glossary emphasis
        if "basic_terms" in action:
            recommendation["glossary_emphasis"] = "basic"
        elif "advanced_terms" in action:
            recommendation["glossary_emphasis"] = "advanced"
        elif "examples" in action:
            recommendation["glossary_emphasis"] = "examples"
        elif "cross_references" in action:
            recommendation["glossary_emphasis"] = "references"
        
        # Response style
        if "formal" in action:
            recommendation["response_style"] = "formal"
        elif "casual" in action:
            recommendation["response_style"] = "casual"
        elif "detailed" in action:
            recommendation["response_style"] = "detailed"
        elif "concise" in action:
            recommendation["response_style"] = "concise"
        
        # Confidence adjustment
        if "high_confidence" in action:
            recommendation["confidence_adjustment"] = 0.1
        elif "low_confidence" in action:
            recommendation["confidence_adjustment"] = -0.1
        elif "request_clarification" in action:
            recommendation["confidence_adjustment"] = -0.2
            recommendation["request_clarification"] = True
        
        return recommendation
    
    async def update_policy(self, state: Dict[str, Any], reward: float) -> None:
        """Update Q-table using Q-learning algorithm."""
        if not hasattr(self, 'last_state') or not hasattr(self, 'last_action'):
            logger.warning("No previous state-action to update")
            return
        
        current_state_str = self._discretize_state(state)
        
        # Initialize current state if not exists
        if current_state_str not in self.q_table:
            self.q_table[current_state_str] = {action: 0.0 for action in self.actions}
        
        # Q-learning update
        old_q_value = self.q_table[self.last_state][self.last_action]
        max_future_q = max(self.q_table[current_state_str].values())
        
        new_q_value = old_q_value + self.learning_rate * (
            reward + self.discount_factor * max_future_q - old_q_value
        )
        
        self.q_table[self.last_state][self.last_action] = new_q_value
        
        logger.debug(f"Updated Q-value for {self.last_state}:{self.last_action} "
                    f"from {old_q_value:.3f} to {new_q_value:.3f} (reward: {reward:.3f})")
        
        # Decay exploration rate
        self.exploration_rate = max(0.01, self.exploration_rate * 0.995)
    
    def save_policy(self, path: str = None) -> None:
        """Save Q-table to disk."""
        if path is None:
            path = settings.rl_model_path
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        policy_data = {
            "q_table": self.q_table,
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "discount_factor": self.discount_factor,
            "actions": self.actions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        with open(f"{path}_qtable.json", "w") as f:
            json.dump(policy_data, f, indent=2)
        
        logger.info(f"Saved Q-table policy to {path}_qtable.json")
    
    def load_policy(self, path: str = None) -> None:
        """Load Q-table from disk."""
        if path is None:
            path = settings.rl_model_path
        
        try:
            with open(f"{path}_qtable.json", "r") as f:
                policy_data = json.load(f)
            
            self.q_table = policy_data["q_table"]
            self.learning_rate = policy_data["learning_rate"]
            self.exploration_rate = policy_data["exploration_rate"]
            self.discount_factor = policy_data["discount_factor"]
            self.actions = policy_data["actions"]
            
            logger.info(f"Loaded Q-table policy from {path}_qtable.json")
            
        except FileNotFoundError:
            logger.info("No existing Q-table found, starting with empty policy")
        except Exception as e:
            logger.error(f"Error loading Q-table: {e}")
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get statistics about the current policy."""
        if not self.q_table:
            return {"states": 0, "total_q_values": 0, "exploration_rate": self.exploration_rate}
        
        total_q_values = sum(len(actions) for actions in self.q_table.values())
        avg_q_value = np.mean([
            q_val for actions in self.q_table.values() 
            for q_val in actions.values()
        ])
        
        return {
            "states": len(self.q_table),
            "total_q_values": total_q_values,
            "average_q_value": avg_q_value,
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate
        }


class MemoryBasedPolicy(RLPolicy):
    """Memory-based policy using reward history."""
    
    def __init__(self):
        """Initialize memory-based policy."""
        self.reward_memory: Dict[str, List[float]] = {}
        self.action_counts: Dict[str, Dict[str, int]] = {}
        self.window_size = 100  # Remember last 100 rewards per state-action
        
        logger.info("Memory-based RL Policy initialized")
    
    async def get_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get action based on historical reward memory."""
        state_str = self._state_to_string(state)
        
        if state_str not in self.reward_memory:
            # Random action for new states
            action = np.random.choice(["balanced", "simple", "detailed", "professional"])
        else:
            # Choose action with highest average reward
            action_rewards = {}
            for action, rewards in self.reward_memory[state_str].items():
                if rewards:
                    action_rewards[action] = np.mean(rewards)
                else:
                    action_rewards[action] = 0.0
            
            action = max(action_rewards.items(), key=lambda x: x[1])[0]
        
        self.last_state = state_str
        self.last_action = action
        
        return {"action": action, "policy_type": "memory_based"}
    
    async def update_policy(self, state: Dict[str, Any], reward: float) -> None:
        """Update reward memory."""
        if not hasattr(self, 'last_state') or not hasattr(self, 'last_action'):
            return
        
        if self.last_state not in self.reward_memory:
            self.reward_memory[self.last_state] = {}
        
        if self.last_action not in self.reward_memory[self.last_state]:
            self.reward_memory[self.last_state][self.last_action] = []
        
        # Add reward and maintain window size
        rewards = self.reward_memory[self.last_state][self.last_action]
        rewards.append(reward)
        if len(rewards) > self.window_size:
            rewards.pop(0)
    
    def _state_to_string(self, state: Dict[str, Any]) -> str:
        """Convert state to string representation."""
        return f"{state.get('user_type', 'unknown')}_{state.get('current_domain', 'unknown')}"
    
    def save_policy(self, path: str = None) -> None:
        """Save memory to disk."""
        if path is None:
            path = settings.rl_model_path
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        with open(f"{path}_memory.pickle", "wb") as f:
            pickle.dump({
                "reward_memory": self.reward_memory,
                "action_counts": self.action_counts
            }, f)
    
    def load_policy(self, path: str = None) -> None:
        """Load memory from disk."""
        if path is None:
            path = settings.rl_model_path
        
        try:
            with open(f"{path}_memory.pickle", "rb") as f:
                data = pickle.load(f)
                self.reward_memory = data["reward_memory"]
                self.action_counts = data["action_counts"]
        except FileNotFoundError:
            logger.info("No existing memory found, starting fresh")


# Factory function to create appropriate policy
def create_rl_policy(policy_type: str = "qtable") -> RLPolicy:
    """Create RL policy based on type."""
    if policy_type == "qtable":
        policy = QTablePolicy()
    elif policy_type == "memory":
        policy = MemoryBasedPolicy()
    else:
        raise ValueError(f"Unknown policy type: {policy_type}")
    
    # Try to load existing policy
    policy.load_policy()
    
    return policy
