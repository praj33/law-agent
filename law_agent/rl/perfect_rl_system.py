"""
Perfect RL System Implementation - Exactly matching your specifications
State: user domain + feedback history
Action: legal domain → legal route → glossary  
Reward: user upvote/downvote or time spent
"""

import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from loguru import logger
import pickle
import os


@dataclass
class FeedbackHistoryEntry:
    """Single feedback entry in history"""
    timestamp: str
    domain: str
    action_taken: str
    reward: float
    upvote: Optional[bool]
    time_spent: float
    user_satisfaction: float


@dataclass
class PerfectRLState:
    """Perfect RL State: user domain + feedback history"""
    user_domain: str  # Current legal domain user is asking about
    feedback_history: List[FeedbackHistoryEntry]  # Complete feedback history
    user_type: str
    session_length: int
    recent_satisfaction: float  # Average satisfaction from recent feedback
    domain_expertise: Dict[str, float]  # User's expertise in each domain based on history
    
    def to_key(self) -> str:
        """Convert state to string key for Q-table"""
        # Summarize feedback history for state key
        recent_feedback = self.feedback_history[-5:] if self.feedback_history else []
        history_summary = {
            "avg_reward": np.mean([f.reward for f in recent_feedback]) if recent_feedback else 0.0,
            "upvote_ratio": sum(1 for f in recent_feedback if f.upvote) / len(recent_feedback) if recent_feedback else 0.5,
            "avg_time_spent": np.mean([f.time_spent for f in recent_feedback]) if recent_feedback else 30.0
        }
        
        return f"{self.user_domain}_{self.user_type}_{history_summary['avg_reward']:.2f}_{history_summary['upvote_ratio']:.2f}"


@dataclass 
class PerfectRLAction:
    """Perfect RL Action: legal domain → legal route → glossary"""
    legal_domain: str  # Predicted/confirmed legal domain
    legal_route: str   # Recommended legal route/process
    glossary_terms: List[str]  # Relevant glossary terms to include
    response_style: str  # How to present the information
    
    def to_key(self) -> str:
        """Convert action to string key"""
        return f"{self.legal_domain}_{self.legal_route}_{self.response_style}"


class PerfectQLearningPolicy:
    """Perfect Q-Learning implementation matching your specifications"""
    
    def __init__(self, learning_rate: float = 0.1, exploration_rate: float = 0.1, discount_factor: float = 0.95):
        """Initialize perfect Q-learning policy"""
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        self.discount_factor = discount_factor
        
        # Q-table: state_key -> action_key -> Q-value
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Feedback history storage
        self.feedback_history: Dict[str, List[FeedbackHistoryEntry]] = {}  # user_id -> feedback history
        
        # Domain expertise tracking
        self.domain_expertise: Dict[str, Dict[str, float]] = {}  # user_id -> domain -> expertise
        
        # Available actions (legal domain → legal route → glossary combinations)
        self.available_actions = self._initialize_action_space()
        
        # State-action memory for updates
        self.last_state: Optional[PerfectRLState] = None
        self.last_action: Optional[PerfectRLAction] = None
        
        logger.info("Perfect Q-Learning Policy initialized")
    
    def _initialize_action_space(self) -> List[PerfectRLAction]:
        """Initialize action space: legal domain → legal route → glossary"""
        
        # Define legal domains and their routes
        domain_routes = {
            "family_law": [
                ("divorce_process", ["divorce", "custody", "alimony", "mediation"]),
                ("child_custody", ["custody", "visitation", "child_support", "guardian"]),
                ("domestic_violence", ["restraining_order", "protection", "abuse", "safety"])
            ],
            "criminal_law": [
                ("arrest_procedure", ["arrest", "warrant", "miranda_rights", "bail"]),
                ("court_defense", ["defense", "attorney", "plea", "trial"]),
                ("sentencing", ["sentence", "probation", "fine", "jail"])
            ],
            "employment_law": [
                ("discrimination_claim", ["discrimination", "eeoc", "harassment", "wrongful_termination"]),
                ("wage_dispute", ["wages", "overtime", "minimum_wage", "labor_board"]),
                ("workplace_rights", ["rights", "safety", "accommodation", "leave"])
            ],
            "property_law": [
                ("tenant_rights", ["eviction", "rent", "lease", "landlord", "tenant_rights"]),
                ("property_dispute", ["boundary", "easement", "title", "deed"]),
                ("real_estate", ["purchase", "sale", "contract", "closing"])
            ],
            "consumer_law": [
                ("product_defect", ["warranty", "defect", "refund", "lemon_law"]),
                ("debt_collection", ["debt", "collection", "harassment", "validation"]),
                ("fraud_protection", ["fraud", "scam", "identity_theft", "ftc"])
            ]
        }
        
        actions = []
        response_styles = ["simple", "balanced", "detailed", "professional"]
        
        for domain, routes in domain_routes.items():
            for route, glossary in routes:
                for style in response_styles:
                    actions.append(PerfectRLAction(
                        legal_domain=domain,
                        legal_route=route,
                        glossary_terms=glossary,
                        response_style=style
                    ))
        
        logger.info(f"Initialized {len(actions)} perfect RL actions")
        return actions
    
    def get_user_state(self, user_id: str, current_domain: str, user_type: str, session_length: int) -> PerfectRLState:
        """Get perfect RL state: user domain + feedback history"""
        
        # Get user's feedback history
        user_feedback = self.feedback_history.get(user_id, [])
        
        # Calculate recent satisfaction
        recent_feedback = user_feedback[-10:] if user_feedback else []
        recent_satisfaction = np.mean([f.user_satisfaction for f in recent_feedback]) if recent_feedback else 0.5
        
        # Get domain expertise
        user_expertise = self.domain_expertise.get(user_id, {})
        
        return PerfectRLState(
            user_domain=current_domain,
            feedback_history=user_feedback,
            user_type=user_type,
            session_length=session_length,
            recent_satisfaction=recent_satisfaction,
            domain_expertise=user_expertise
        )
    
    def select_action(self, state: PerfectRLState) -> PerfectRLAction:
        """Select action using epsilon-greedy policy"""
        
        state_key = state.to_key()
        
        # Initialize state in Q-table if not exists
        if state_key not in self.q_table:
            self.q_table[state_key] = {}
            for action in self.available_actions:
                self.q_table[state_key][action.to_key()] = 0.0
        
        # Epsilon-greedy selection
        if np.random.random() < self.exploration_rate:
            # Explore: random action
            action = np.random.choice(self.available_actions)
            logger.debug(f"🎲 Exploring with action: {action.legal_domain} → {action.legal_route}")
        else:
            # Exploit: best action based on Q-values
            q_values = self.q_table[state_key]
            best_action_key = max(q_values.items(), key=lambda x: x[1])[0]
            
            # Find action object by key
            action = next(a for a in self.available_actions if a.to_key() == best_action_key)
            logger.debug(f"Exploiting with action: {action.legal_domain} → {action.legal_route}")
        
        # Store for later update
        self.last_state = state
        self.last_action = action
        
        return action
    
    def update_policy(self, user_id: str, reward: float, upvote: Optional[bool], time_spent: float, new_state: PerfectRLState):
        """Update Q-table with perfect reward: upvote/downvote or time spent"""
        
        if not self.last_state or not self.last_action:
            logger.warning("No previous state-action to update")
            return
        
        # Calculate perfect reward based on your specifications
        perfect_reward = self._calculate_perfect_reward(reward, upvote, time_spent)
        
        # Store feedback in history
        feedback_entry = FeedbackHistoryEntry(
            timestamp=datetime.now().isoformat(),
            domain=self.last_action.legal_domain,
            action_taken=self.last_action.to_key(),
            reward=perfect_reward,
            upvote=upvote,
            time_spent=time_spent,
            user_satisfaction=reward
        )
        
        if user_id not in self.feedback_history:
            self.feedback_history[user_id] = []
        self.feedback_history[user_id].append(feedback_entry)
        
        # Update domain expertise
        self._update_domain_expertise(user_id, self.last_action.legal_domain, perfect_reward)
        
        # Q-learning update
        old_state_key = self.last_state.to_key()
        new_state_key = new_state.to_key()
        action_key = self.last_action.to_key()
        
        # Initialize new state if needed
        if new_state_key not in self.q_table:
            self.q_table[new_state_key] = {}
            for action in self.available_actions:
                self.q_table[new_state_key][action.to_key()] = 0.0
        
        # Q-learning formula: Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
        old_q_value = self.q_table[old_state_key][action_key]
        max_future_q = max(self.q_table[new_state_key].values())
        
        new_q_value = old_q_value + self.learning_rate * (
            perfect_reward + self.discount_factor * max_future_q - old_q_value
        )
        
        self.q_table[old_state_key][action_key] = new_q_value
        
        logger.info(f"Updated Q-value: {old_q_value:.3f} → {new_q_value:.3f} (reward: {perfect_reward:.3f})")
    
    def _calculate_perfect_reward(self, base_reward: float, upvote: Optional[bool], time_spent: float) -> float:
        """Calculate perfect reward: upvote/downvote or time spent"""
        
        reward = base_reward
        
        # Upvote/downvote component (primary signal)
        if upvote is True:
            reward += 0.5  # Strong positive signal
        elif upvote is False:
            reward -= 0.5  # Strong negative signal
        
        # Time spent component (engagement signal)
        # Normalize time spent: 30s = neutral, >60s = positive, <10s = negative
        if time_spent > 60:
            reward += 0.2  # Good engagement
        elif time_spent > 30:
            reward += 0.1  # Decent engagement
        elif time_spent < 10:
            reward -= 0.2  # Poor engagement
        
        # Clamp reward to [-1, 1]
        return max(-1.0, min(1.0, reward))
    
    def _update_domain_expertise(self, user_id: str, domain: str, reward: float):
        """Update user's domain expertise based on feedback"""
        
        if user_id not in self.domain_expertise:
            self.domain_expertise[user_id] = {}
        
        if domain not in self.domain_expertise[user_id]:
            self.domain_expertise[user_id][domain] = 0.5  # Start neutral
        
        # Update expertise with learning rate
        current_expertise = self.domain_expertise[user_id][domain]
        expertise_update = 0.1 * reward  # Small learning rate for expertise
        
        self.domain_expertise[user_id][domain] = max(0.0, min(1.0, current_expertise + expertise_update))
    
    def save_policy(self, filepath: str = "law_agent/models/perfect_rl_policy.pkl"):
        """Save perfect RL policy"""
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        policy_data = {
            "q_table": self.q_table,
            "feedback_history": {k: [asdict(f) for f in v] for k, v in self.feedback_history.items()},
            "domain_expertise": self.domain_expertise,
            "learning_rate": self.learning_rate,
            "exploration_rate": self.exploration_rate,
            "discount_factor": self.discount_factor
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(policy_data, f)
        
        logger.info(f"Saved perfect RL policy to {filepath}")
    
    def load_policy(self, filepath: str = "law_agent/models/perfect_rl_policy.pkl"):
        """Load perfect RL policy"""
        
        if not os.path.exists(filepath):
            logger.info("No existing perfect RL policy found, starting fresh")
            return
        
        try:
            with open(filepath, 'rb') as f:
                policy_data = pickle.load(f)
            
            self.q_table = policy_data["q_table"]
            self.domain_expertise = policy_data["domain_expertise"]
            
            # Reconstruct feedback history
            self.feedback_history = {}
            for user_id, feedback_list in policy_data["feedback_history"].items():
                self.feedback_history[user_id] = [
                    FeedbackHistoryEntry(**f) for f in feedback_list
                ]
            
            logger.info(f"Loaded perfect RL policy from {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to load perfect RL policy: {e}")
    
    def get_policy_stats(self) -> Dict[str, Any]:
        """Get comprehensive policy statistics"""
        
        total_feedback = sum(len(history) for history in self.feedback_history.values())
        total_users = len(self.feedback_history)
        total_states = len(self.q_table)
        
        # Calculate average rewards by domain
        domain_rewards = {}
        for user_history in self.feedback_history.values():
            for feedback in user_history:
                domain = feedback.domain
                if domain not in domain_rewards:
                    domain_rewards[domain] = []
                domain_rewards[domain].append(feedback.reward)
        
        avg_domain_rewards = {
            domain: np.mean(rewards) for domain, rewards in domain_rewards.items()
        }
        
        return {
            "total_feedback_entries": total_feedback,
            "total_users": total_users,
            "total_states_learned": total_states,
            "average_rewards_by_domain": avg_domain_rewards,
            "exploration_rate": self.exploration_rate,
            "learning_rate": self.learning_rate
        }
