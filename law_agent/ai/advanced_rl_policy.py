"""Advanced Reinforcement Learning Policy with Deep Learning and Pattern Recognition."""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")

from ..rl.policy import RLPolicy
from .advanced_rl_system import AdvancedState, AdvancedReward, AdvancedAgentMemory
from ..core.state import LegalDomain, UserType, FeedbackType


class AdvancedLegalRLPolicy(RLPolicy):
    """Advanced RL policy with deep learning, pattern recognition, and multi-dimensional rewards."""
    
    def __init__(self):
        """Initialize advanced legal RL policy."""
        super().__init__()
        
        # Advanced memory system
        self.memory = AdvancedAgentMemory(max_memory_size=50000)
        
        # ML models for prediction
        self.reward_predictor = None
        self.action_selector = None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        
        # Advanced learning parameters
        self.learning_rate = 0.001
        self.exploration_rate = 0.1
        self.exploration_decay = 0.995
        self.min_exploration = 0.01
        
        # Multi-armed bandit for action selection
        self.action_rewards = {}
        self.action_counts = {}
        self.confidence_threshold = 0.7
        
        # Pattern recognition
        self.success_patterns = []
        self.failure_patterns = []
        
        # Performance tracking
        self.session_performance = {}
        self.domain_expertise = {}
        self.user_adaptation = {}
        
        # Initialize ML models if available
        if SKLEARN_AVAILABLE:
            self._initialize_ml_models()
        
        logger.info("Advanced Legal RL Policy initialized with ML capabilities")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models with pre-trained models if available."""
        if not SKLEARN_AVAILABLE:
            return

        try:
            # Try to load pre-trained models
            import os
            import pickle
            model_dir = "law_agent/models"
            reward_model_path = os.path.join(model_dir, "reward_predictor.pkl")

            if os.path.exists(reward_model_path):
                # Load pre-trained reward predictor
                with open(reward_model_path, 'rb') as f:
                    self.reward_predictor = pickle.load(f)
                logger.info("Loaded pre-trained reward predictor")
            else:
                # Train models if not available
                logger.info("🔄 Training RL models (first time setup)...")
                from law_agent.ai.rl_model_trainer import train_rl_models
                training_result = train_rl_models()

                # Load the newly trained model
                with open(reward_model_path, 'rb') as f:
                    self.reward_predictor = pickle.load(f)
                logger.info("✅ Trained and loaded new reward predictor")

        except Exception as e:
            logger.warning(f"Could not load/train reward predictor: {e}")
            # Fallback to untrained model
            self.reward_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )

        # Action selection model (always create new)
        self.action_selector = RandomForestRegressor(
            n_estimators=50,
            max_depth=8,
            random_state=42
        )

        logger.info("ML models initialized for advanced RL")
    
    def _create_advanced_state(self, raw_state: Dict[str, Any]) -> AdvancedState:
        """Create advanced state representation from raw state."""
        
        # Extract basic information
        user_type = raw_state.get("user_type", "common_person")
        current_domain = raw_state.get("domain", "unknown")
        domain_confidence = raw_state.get("confidence", 0.5)
        
        # Calculate derived features
        query = raw_state.get("query", "")
        query_complexity = self._assess_query_complexity(query)
        legal_urgency = self._assess_legal_urgency(query)
        
        # Get historical context
        session_id = raw_state.get("session_id", "")
        session_data = self.session_performance.get(session_id, {})
        
        recent_domains = session_data.get("recent_domains", [])
        feedback_history = session_data.get("feedback_history", [])
        success_rate = session_data.get("success_rate", 0.5)
        avg_response_time = session_data.get("avg_response_time", 5.0)
        
        # Temporal context
        now = datetime.now()
        time_of_day = now.hour
        day_of_week = now.weekday()
        session_duration = session_data.get("session_duration", 0.0)
        
        # User context
        user_satisfaction = session_data.get("user_satisfaction", 0.0)
        user_expertise = self._estimate_user_expertise(user_type, session_data)
        session_length = len(session_data.get("interactions", []))
        
        return AdvancedState(
            user_type=user_type,
            user_satisfaction=user_satisfaction,
            user_expertise_level=user_expertise,
            session_length=session_length,
            current_domain=current_domain,
            domain_confidence=domain_confidence,
            query_complexity=query_complexity,
            legal_urgency=legal_urgency,
            recent_domains=recent_domains[-5:],  # Last 5 domains
            feedback_history=feedback_history[-10:],  # Last 10 feedback
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            session_duration=session_duration
        )
    
    def _assess_query_complexity(self, query: str) -> float:
        """Assess query complexity on a scale of 0-1."""
        if not query:
            return 0.5
        
        complexity_indicators = {
            "high": ["constitutional", "federal", "supreme court", "appeal", "class action", 
                    "securities", "antitrust", "intellectual property", "merger", "acquisition",
                    "international", "treaty", "jurisdiction", "precedent"],
            "medium": ["contract", "employment", "discrimination", "negligence", "liability",
                      "damages", "breach", "violation", "dispute", "settlement", "statute"],
            "low": ["divorce", "custody", "traffic", "small claims", "landlord", "tenant",
                   "will", "estate", "name change", "restraining order", "parking"]
        }
        
        query_lower = query.lower()
        word_count = len(query.split())
        
        # Base complexity on word count
        base_complexity = min(1.0, word_count / 50.0)
        
        # Adjust based on keywords
        high_count = sum(1 for term in complexity_indicators["high"] if term in query_lower)
        medium_count = sum(1 for term in complexity_indicators["medium"] if term in query_lower)
        low_count = sum(1 for term in complexity_indicators["low"] if term in query_lower)
        
        if high_count > 0:
            keyword_complexity = 0.8 + (high_count * 0.05)
        elif medium_count > 0:
            keyword_complexity = 0.5 + (medium_count * 0.05)
        elif low_count > 0:
            keyword_complexity = 0.2 + (low_count * 0.05)
        else:
            keyword_complexity = 0.5
        
        # Combine base and keyword complexity
        final_complexity = (base_complexity + keyword_complexity) / 2
        return min(1.0, max(0.0, final_complexity))
    
    def _assess_legal_urgency(self, query: str) -> float:
        """Assess legal urgency on a scale of 0-1."""
        if not query:
            return 0.3
        
        urgent_keywords = [
            "emergency", "urgent", "deadline", "court date", "arrest", "warrant",
            "eviction", "foreclosure", "restraining order", "injunction", "appeal deadline",
            "statute of limitations", "time sensitive", "immediate", "asap"
        ]
        
        query_lower = query.lower()
        urgency_score = 0.3  # Base urgency
        
        for keyword in urgent_keywords:
            if keyword in query_lower:
                urgency_score += 0.1
        
        return min(1.0, urgency_score)
    
    def _estimate_user_expertise(self, user_type: str, session_data: Dict[str, Any]) -> float:
        """Estimate user's legal expertise level."""
        
        base_expertise = {
            "common_person": 0.2,
            "law_firm": 0.8,
            "legal_student": 0.5
        }.get(user_type, 0.3)
        
        # Adjust based on session history
        interactions = session_data.get("interactions", [])
        if len(interactions) > 10:
            # Experienced user
            base_expertise += 0.1
        
        success_rate = session_data.get("success_rate", 0.5)
        expertise_adjustment = (success_rate - 0.5) * 0.2
        
        return min(1.0, max(0.0, base_expertise + expertise_adjustment))
    
    async def get_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get action using advanced RL with pattern recognition."""
        
        # Create advanced state representation
        advanced_state = self._create_advanced_state(state)
        
        # Check memory for similar successful experiences
        similar_experiences = self.memory.retrieve_similar_experiences(advanced_state)
        
        # Get best action from procedural memory
        memory_action = self.memory.get_best_action_for_state(advanced_state)
        
        # Use ML prediction if available
        ml_action = None
        if SKLEARN_AVAILABLE and self.reward_predictor is not None:
            ml_action = self._predict_best_action(advanced_state)
        
        # Multi-armed bandit action selection
        bandit_action = self._select_action_bandit(advanced_state)
        
        # Combine different action selection strategies
        final_action = self._combine_action_strategies(
            memory_action, ml_action, bandit_action, similar_experiences
        )
        
        # Add advanced features to action
        enhanced_action = self._enhance_action(final_action, advanced_state)
        
        # Store state for learning
        self.last_advanced_state = advanced_state
        self.last_action = enhanced_action

        logger.info(f"Action Selected: {enhanced_action['action']} for {advanced_state.current_domain} (confidence: {enhanced_action.get('confidence', 0):.3f})")
        logger.debug(f"   Selection methods: memory={bool(memory_action)}, ml={bool(ml_action)}, bandit=True, similar_exp={len(similar_experiences)}")

        return enhanced_action
    
    def _predict_best_action(self, state: AdvancedState) -> Optional[Dict[str, Any]]:
        """Use ML model to predict best action."""
        if not SKLEARN_AVAILABLE or self.reward_predictor is None:
            return None

        try:
            # Create state vector with same features as training data (7 features)
            state_vector = np.array([
                {"common_person": 0, "law_firm": 1, "legal_student": 2}.get(state.user_type, 0),
                state.user_satisfaction,
                state.user_expertise_level,
                state.session_length / 100.0,  # Normalize
                {domain.value: i for i, domain in enumerate(LegalDomain)}.get(state.current_domain, 0) if hasattr(state, 'current_domain') else 0,
                state.domain_confidence,
                state.query_complexity
            ]).reshape(1, -1)

            # Predict rewards for different actions
            actions = ["simple", "balanced", "detailed", "professional"]
            best_action = "balanced"
            best_reward = -float('inf')

            for action in actions:
                # Create action vector with 2 features to match training (same as training)
                action_features = np.array([
                    {"simple": 0.25, "balanced": 0.5, "detailed": 0.75, "professional": 1.0}.get(action, 0.5),
                    {"simple": 0.2, "balanced": 0.5, "detailed": 0.8, "professional": 1.0}.get(action, 0.5)
                ]).reshape(1, -1)
                combined_vector = np.hstack([state_vector, action_features])

                if hasattr(self.reward_predictor, 'predict'):
                    predicted_reward = self.reward_predictor.predict(combined_vector)[0]
                    if predicted_reward > best_reward:
                        best_reward = predicted_reward
                        best_action = action

            return {"action": best_action, "predicted_reward": best_reward}

        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")
            return None
    
    def _select_action_bandit(self, state: AdvancedState) -> Dict[str, Any]:
        """Select action using multi-armed bandit approach."""
        
        state_key = state.to_string()
        
        # Initialize if new state
        if state_key not in self.action_rewards:
            self.action_rewards[state_key] = {}
            self.action_counts[state_key] = {}
        
        actions = ["simple", "balanced", "detailed", "professional"]
        
        # Epsilon-greedy with UCB
        if np.random.random() < self.exploration_rate:
            # Explore
            action = np.random.choice(actions)
        else:
            # Exploit with Upper Confidence Bound
            best_action = "balanced"
            best_value = -float('inf')
            
            total_counts = sum(self.action_counts[state_key].values()) + 1
            
            for action in actions:
                if action not in self.action_rewards[state_key]:
                    self.action_rewards[state_key][action] = 0.0
                    self.action_counts[state_key][action] = 0
                
                avg_reward = self.action_rewards[state_key][action]
                count = self.action_counts[state_key][action]
                
                # UCB formula
                if count > 0:
                    confidence = np.sqrt(2 * np.log(total_counts) / count)
                    ucb_value = avg_reward + confidence
                else:
                    ucb_value = float('inf')  # Prioritize unexplored actions
                
                if ucb_value > best_value:
                    best_value = ucb_value
                    best_action = action
            
            action = best_action
        
        return {"action": action, "selection_method": "bandit"}
    
    def _combine_action_strategies(
        self,
        memory_action: Optional[Dict[str, Any]],
        ml_action: Optional[Dict[str, Any]],
        bandit_action: Dict[str, Any],
        similar_experiences: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine different action selection strategies."""
        
        # Weight different strategies
        strategies = []
        
        if memory_action:
            strategies.append(("memory", memory_action, 0.4))
        
        if ml_action:
            strategies.append(("ml", ml_action, 0.3))
        
        strategies.append(("bandit", bandit_action, 0.3))
        
        # If we have similar successful experiences, boost their weight
        if similar_experiences:
            avg_similarity = np.mean([exp["similarity"] for exp in similar_experiences])
            if avg_similarity > 0.8:
                # Use action from most similar successful experience
                best_exp = max(similar_experiences, key=lambda x: x["reward"])
                similar_action = best_exp["action"]
                strategies.append(("similarity", similar_action, 0.5))
        
        # Select strategy based on weights and confidence
        if strategies:
            # For now, use the highest weighted strategy
            # In a more advanced version, we could use ensemble methods
            best_strategy = max(strategies, key=lambda x: x[2])
            return best_strategy[1]
        
        # Fallback
        return {"action": "balanced", "selection_method": "fallback"}
    
    def _enhance_action(self, action: Dict[str, Any], state: AdvancedState) -> Dict[str, Any]:
        """Enhance action with advanced features."""
        
        enhanced = action.copy()
        
        # Add confidence assessment
        domain_expertise = self.memory.get_domain_expertise(state.current_domain)
        enhanced["confidence"] = domain_expertise
        
        # Add response style based on user type and complexity
        if state.user_type == "law_firm" and state.query_complexity > 0.7:
            enhanced["response_style"] = "professional_detailed"
        elif state.user_type == "common_person" and state.query_complexity < 0.3:
            enhanced["response_style"] = "simple_explanatory"
        else:
            enhanced["response_style"] = "balanced_adaptive"
        
        # Add urgency handling
        if state.legal_urgency > 0.7:
            enhanced["priority"] = "high"
            enhanced["include_immediate_steps"] = True
        else:
            enhanced["priority"] = "normal"
        
        # Add personalization
        enhanced["personalization"] = {
            "user_expertise": state.user_expertise_level,
            "preferred_style": self._get_user_preference(state.user_type),
            "complexity_adjustment": state.query_complexity
        }
        
        return enhanced
    
    def _get_user_preference(self, user_type: str) -> str:
        """Get user preference based on type and history."""
        preferences = {
            "common_person": "simple_practical",
            "law_firm": "detailed_professional",
            "legal_student": "educational_comprehensive"
        }
        return preferences.get(user_type, "balanced")
    
    async def update_policy(self, state: Dict[str, Any], action: Dict[str, Any], reward: float):
        """Update policy with advanced learning."""
        
        if not hasattr(self, 'last_advanced_state'):
            return
        
        # Create advanced reward structure
        advanced_reward = self._create_advanced_reward(state, action, reward)
        
        # Store experience in advanced memory
        current_state = self._create_advanced_state(state)
        self.memory.store_experience(
            self.last_advanced_state,
            self.last_action,
            advanced_reward,
            current_state
        )
        
        # Update bandit rewards
        state_key = self.last_advanced_state.to_string()
        action_name = self.last_action.get("action", "balanced")
        
        if state_key in self.action_rewards:
            if action_name not in self.action_rewards[state_key]:
                self.action_rewards[state_key][action_name] = 0.0
                self.action_counts[state_key][action_name] = 0
            
            # Update running average
            count = self.action_counts[state_key][action_name]
            old_avg = self.action_rewards[state_key][action_name]
            new_avg = (old_avg * count + advanced_reward.total_reward()) / (count + 1)
            
            self.action_rewards[state_key][action_name] = new_avg
            self.action_counts[state_key][action_name] += 1

            logger.debug(f"Q-table updated: {state_key[:20]}... -> {action_name}: {new_avg:.3f} (count: {self.action_counts[state_key][action_name]})")
        
        # Update ML models if enough data
        if SKLEARN_AVAILABLE and len(self.memory.episodic_memory) > 50:
            try:
                self._update_ml_models()
                logger.info(f"🤖 ML models updated with {len(self.memory.episodic_memory)} experiences")
            except Exception as e:
                logger.warning(f"ML model update failed: {e}")
        
        # Decay exploration rate
        self.exploration_rate = max(
            self.min_exploration,
            self.exploration_rate * self.exploration_decay
        )

        logger.info(f"RL Policy Updated: domain={self.last_advanced_state.current_domain}, reward={advanced_reward.total_reward():.3f}, exploration={self.exploration_rate:.3f}")
        logger.debug(f"   Action: {self.last_action.get('action', 'unknown')}, Bandit rewards updated: {len(self.action_rewards)} states")
    
    def _create_advanced_reward(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        base_reward: float
    ) -> AdvancedReward:
        """Create advanced multi-dimensional reward."""
        
        # Extract feedback information
        feedback = state.get("feedback")
        time_spent = state.get("time_spent", 5.0)
        
        reward = AdvancedReward()
        
        # User satisfaction (from feedback)
        if feedback == "upvote":
            reward.user_satisfaction = 1.0
        elif feedback == "downvote":
            reward.user_satisfaction = -1.0
        else:
            reward.user_satisfaction = base_reward
        
        # Time efficiency (faster is better, but not too fast)
        if 2.0 <= time_spent <= 10.0:
            reward.time_efficiency = 1.0
        elif time_spent < 2.0:
            reward.time_efficiency = 0.5  # Too fast might mean low quality
        else:
            reward.time_efficiency = max(0.0, 1.0 - (time_spent - 10.0) / 30.0)
        
        # Legal accuracy (estimated from confidence and domain)
        confidence = state.get("confidence", 0.5)
        domain = state.get("domain", "unknown")
        domain_expertise = self.memory.get_domain_expertise(domain)
        reward.legal_accuracy = (confidence + domain_expertise) / 2
        
        # Response quality (combination of factors)
        reward.response_quality = (reward.user_satisfaction + reward.legal_accuracy) / 2
        
        # Domain expertise (improves over time)
        reward.domain_expertise = domain_expertise
        
        # User engagement (based on time spent and feedback)
        if time_spent > 1.0 and reward.user_satisfaction > 0:
            reward.user_engagement = min(1.0, time_spent / 20.0)
        else:
            reward.user_engagement = 0.0
        
        # Learning progress (how much we're improving)
        reward.learning_progress = self._calculate_learning_progress(domain)
        
        return reward
    
    def _calculate_learning_progress(self, domain: str) -> float:
        """Calculate learning progress for a domain."""
        
        domain_memories = self.memory.semantic_memory.get(domain, [])
        if len(domain_memories) < 10:
            return 0.5  # Not enough data
        
        # Compare recent performance to older performance
        recent_rewards = [m["reward"] for m in domain_memories[-10:]]
        older_rewards = [m["reward"] for m in domain_memories[-20:-10]] if len(domain_memories) >= 20 else []
        
        if not older_rewards:
            return 0.5
        
        recent_avg = np.mean(recent_rewards)
        older_avg = np.mean(older_rewards)
        
        # Progress is improvement over time
        progress = (recent_avg - older_avg + 2) / 4  # Normalize to [0, 1]
        return max(0.0, min(1.0, progress))
    
    def _update_ml_models(self):
        """Update ML models with recent experiences."""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            # Prepare training data
            experiences = list(self.memory.episodic_memory)[-1000:]  # Last 1000 experiences
            
            if len(experiences) < 50:
                return
            
            X = []
            y = []
            
            for exp in experiences:
                state_dict = exp["state"]
                state = AdvancedState(**state_dict)
                state_vector = state.to_vector()
                
                # Add action features
                action = exp["action"]
                action_features = np.array([
                    hash(action.get("action", "balanced")) % 100 / 100.0,
                    hash(action.get("response_style", "adaptive")) % 100 / 100.0
                ])
                
                combined_features = np.hstack([state_vector, action_features])
                X.append(combined_features)
                y.append(exp["total_reward"])
            
            X = np.array(X)
            y = np.array(y)
            
            # Train reward predictor
            if hasattr(self.reward_predictor, 'fit'):
                self.reward_predictor.fit(X, y)
                logger.debug("Updated ML reward predictor")
            
        except Exception as e:
            logger.warning(f"Failed to update ML models: {e}")
    
    async def save_policy(self, filepath: str):
        """Save advanced policy to file."""
        
        policy_data = {
            "action_rewards": self.action_rewards,
            "action_counts": self.action_counts,
            "domain_expertise": self.domain_expertise,
            "exploration_rate": self.exploration_rate,
            "memory_stats": self.memory.get_memory_stats(),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(policy_data, f, indent=2, default=str)
        
        logger.info(f"Advanced RL policy saved to {filepath}")
    
    async def load_policy(self, filepath: str):
        """Load advanced policy from file."""
        
        try:
            with open(filepath, 'r') as f:
                policy_data = json.load(f)
            
            self.action_rewards = policy_data.get("action_rewards", {})
            self.action_counts = policy_data.get("action_counts", {})
            self.domain_expertise = policy_data.get("domain_expertise", {})
            self.exploration_rate = policy_data.get("exploration_rate", 0.1)
            
            logger.info(f"Advanced RL policy loaded from {filepath}")
            
        except FileNotFoundError:
            logger.info("No advanced policy file found, starting fresh")

    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive performance analytics."""

        memory_stats = self.memory.get_memory_stats()

        analytics = {
            "learning_metrics": {
                "total_experiences": len(self.memory.episodic_memory),
                "exploration_rate": self.exploration_rate,
                "domains_learned": len(self.memory.domain_performance),
                "avg_domain_expertise": np.mean(list(self.domain_expertise.values())) if self.domain_expertise else 0.0
            },
            "performance_by_domain": {},
            "temporal_insights": memory_stats.get("temporal_insights", {}),
            "action_effectiveness": {},
            "user_adaptation": {
                "common_person": self._get_user_type_performance("common_person"),
                "law_firm": self._get_user_type_performance("law_firm"),
                "legal_student": self._get_user_type_performance("legal_student")
            },
            "learning_trends": self._get_learning_trends()
        }

        # Performance by domain
        for domain, perf in self.memory.domain_performance.items():
            analytics["performance_by_domain"][domain] = {
                "success_rate": perf["successes"] / perf["total"] if perf["total"] > 0 else 0.0,
                "avg_reward": perf["avg_reward"],
                "total_interactions": perf["total"],
                "expertise_level": self.memory.get_domain_expertise(domain)
            }

        # Action effectiveness
        for state_key, actions in self.action_rewards.items():
            for action, reward in actions.items():
                if action not in analytics["action_effectiveness"]:
                    analytics["action_effectiveness"][action] = {
                        "avg_reward": 0.0,
                        "usage_count": 0,
                        "states_used": 0
                    }

                analytics["action_effectiveness"][action]["avg_reward"] += reward
                analytics["action_effectiveness"][action]["usage_count"] += self.action_counts[state_key].get(action, 0)
                analytics["action_effectiveness"][action]["states_used"] += 1

        # Average the action effectiveness
        for action_data in analytics["action_effectiveness"].values():
            if action_data["states_used"] > 0:
                action_data["avg_reward"] /= action_data["states_used"]

        return analytics

    def _get_user_type_performance(self, user_type: str) -> Dict[str, Any]:
        """Get performance metrics for a specific user type."""

        user_experiences = [
            exp for exp in self.memory.episodic_memory
            if exp["state"]["user_type"] == user_type
        ]

        if not user_experiences:
            return {"interactions": 0, "avg_reward": 0.0, "satisfaction": 0.0}

        rewards = [exp["total_reward"] for exp in user_experiences]
        satisfactions = [exp["reward"]["user_satisfaction"] for exp in user_experiences]

        return {
            "interactions": len(user_experiences),
            "avg_reward": np.mean(rewards),
            "satisfaction": np.mean(satisfactions),
            "improvement_trend": self._calculate_trend(rewards)
        }

    def _get_learning_trends(self) -> Dict[str, Any]:
        """Calculate learning trends over time."""

        if len(self.memory.episodic_memory) < 10:
            return {"trend": "insufficient_data"}

        # Get rewards over time
        experiences = list(self.memory.episodic_memory)
        rewards = [exp["total_reward"] for exp in experiences]

        # Calculate trend
        trend = self._calculate_trend(rewards)

        # Recent vs. historical performance
        recent_rewards = rewards[-50:] if len(rewards) >= 50 else rewards
        historical_rewards = rewards[:-50] if len(rewards) >= 100 else []

        recent_avg = np.mean(recent_rewards)
        historical_avg = np.mean(historical_rewards) if historical_rewards else recent_avg

        return {
            "trend": trend,
            "recent_performance": recent_avg,
            "historical_performance": historical_avg,
            "improvement": recent_avg - historical_avg,
            "total_experiences": len(rewards)
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a list of values."""

        if len(values) < 5:
            return "insufficient_data"

        # Simple linear trend calculation
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.01:
            return "improving"
        elif slope < -0.01:
            return "declining"
        else:
            return "stable"
