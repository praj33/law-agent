"""
Advanced RL Model Trainer - Train ML models with synthetic legal data
"""

import numpy as np
import json
import pickle
import os
from typing import Dict, List, Tuple, Any
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from loguru import logger
from dataclasses import dataclass


@dataclass
class TrainingExample:
    """Training example for RL models"""
    state_features: List[float]
    action_features: List[float]
    reward: float
    domain: str
    user_type: str
    query_complexity: float


class RLModelTrainer:
    """Train RL models with comprehensive legal data"""
    
    def __init__(self):
        """Initialize trainer"""
        self.model_dir = "law_agent/models"
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Legal domains and their characteristics
        self.domains = [
            "family_law", "criminal_law", "employment_law", "property_law",
            "consumer_law", "tort_law", "contract_law", "constitutional_law"
        ]
        
        # Action types and their effectiveness
        self.actions = ["simple", "balanced", "detailed", "professional"]
        
        # User types and preferences
        self.user_types = ["common_person", "law_student", "law_firm", "government"]
        
        logger.info("✅ RL Model Trainer initialized")
    
    def generate_synthetic_training_data(self, num_examples: int = 5000) -> List[TrainingExample]:
        """Generate synthetic training data based on legal domain patterns"""
        
        examples = []
        
        for _ in range(num_examples):
            # Random domain and user type
            domain = np.random.choice(self.domains)
            user_type = np.random.choice(self.user_types)
            action = np.random.choice(self.actions)
            
            # Generate realistic state features
            query_complexity = np.random.uniform(0.1, 1.0)
            confidence = np.random.uniform(0.2, 0.95)
            urgency = np.random.uniform(0.0, 1.0)
            user_experience = self._get_user_experience(user_type)
            
            state_features = [
                query_complexity,
                confidence,
                urgency,
                user_experience,
                self._domain_to_numeric(domain),
                np.random.uniform(0.0, 1.0),  # session_length
                np.random.uniform(0.0, 1.0),  # interaction_count
            ]
            
            # Generate action features
            action_features = [
                self._action_to_numeric(action),
                self._get_action_complexity(action)
            ]
            
            # Calculate realistic reward based on domain patterns
            reward = self._calculate_realistic_reward(
                domain, user_type, action, query_complexity, confidence
            )
            
            examples.append(TrainingExample(
                state_features=state_features,
                action_features=action_features,
                reward=reward,
                domain=domain,
                user_type=user_type,
                query_complexity=query_complexity
            ))
        
        logger.info(f"✅ Generated {len(examples)} synthetic training examples")
        return examples
    
    def _get_user_experience(self, user_type: str) -> float:
        """Get user experience level"""
        experience_map = {
            "common_person": 0.1,
            "law_student": 0.4,
            "law_firm": 0.9,
            "government": 0.7
        }
        return experience_map.get(user_type, 0.5)
    
    def _domain_to_numeric(self, domain: str) -> float:
        """Convert domain to numeric representation"""
        domain_map = {
            "family_law": 0.1, "criminal_law": 0.2, "employment_law": 0.3,
            "property_law": 0.4, "consumer_law": 0.5, "tort_law": 0.6,
            "contract_law": 0.7, "constitutional_law": 0.8
        }
        return domain_map.get(domain, 0.5)
    
    def _action_to_numeric(self, action: str) -> float:
        """Convert action to numeric representation"""
        action_map = {
            "simple": 0.25, "balanced": 0.5, "detailed": 0.75, "professional": 1.0
        }
        return action_map.get(action, 0.5)
    
    def _get_action_complexity(self, action: str) -> float:
        """Get action complexity score"""
        complexity_map = {
            "simple": 0.2, "balanced": 0.5, "detailed": 0.8, "professional": 1.0
        }
        return complexity_map.get(action, 0.5)
    
    def _calculate_realistic_reward(self, domain: str, user_type: str, action: str, 
                                  complexity: float, confidence: float) -> float:
        """Calculate realistic reward based on legal domain patterns"""
        
        base_reward = 0.5
        
        # Domain-specific adjustments
        domain_rewards = {
            "criminal_law": 0.8,  # High stakes, high reward for good advice
            "family_law": 0.7,   # Emotional, needs careful handling
            "employment_law": 0.6, # Common issues, moderate complexity
            "property_law": 0.65, # Technical but straightforward
            "consumer_law": 0.55, # Routine complaints
            "tort_law": 0.75,    # Complex liability issues
            "contract_law": 0.7,  # Technical legal analysis
            "constitutional_law": 0.9  # Fundamental rights, high importance
        }
        
        # User type preferences
        user_preferences = {
            "common_person": {"simple": 0.8, "balanced": 0.6, "detailed": 0.3, "professional": 0.1},
            "law_student": {"simple": 0.3, "balanced": 0.7, "detailed": 0.8, "professional": 0.6},
            "law_firm": {"simple": 0.1, "balanced": 0.4, "detailed": 0.8, "professional": 0.9},
            "government": {"simple": 0.2, "balanced": 0.6, "detailed": 0.7, "professional": 0.8}
        }
        
        # Calculate reward
        domain_bonus = domain_rewards.get(domain, 0.5)
        user_preference = user_preferences.get(user_type, {}).get(action, 0.5)
        confidence_bonus = confidence * 0.3
        complexity_match = 1.0 - abs(complexity - self._get_action_complexity(action))
        
        reward = (base_reward + domain_bonus + user_preference + confidence_bonus + complexity_match) / 5.0
        
        # Add some noise for realism
        reward += np.random.normal(0, 0.1)
        
        # Clamp to valid range
        return max(-1.0, min(1.0, reward))
    
    def train_reward_predictor(self, examples: List[TrainingExample]) -> RandomForestRegressor:
        """Train RandomForest model to predict rewards"""
        
        # Prepare training data
        X = []
        y = []
        
        for example in examples:
            # Combine state and action features
            features = example.state_features + example.action_features
            X.append(features)
            y.append(example.reward)
        
        X = np.array(X)
        y = np.array(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"✅ Reward Predictor trained - MSE: {mse:.4f}, R²: {r2:.4f}")
        
        return model
    
    def save_trained_models(self, reward_predictor: RandomForestRegressor):
        """Save trained models to disk"""
        
        # Save reward predictor
        model_path = os.path.join(self.model_dir, "reward_predictor.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(reward_predictor, f)
        
        logger.info(f"✅ Models saved to {self.model_dir}")
    
    def train_all_models(self):
        """Train all RL models"""
        
        logger.info("🚀 Starting comprehensive RL model training...")
        
        # Generate training data
        examples = self.generate_synthetic_training_data(5000)
        
        # Train reward predictor
        reward_predictor = self.train_reward_predictor(examples)
        
        # Save models
        self.save_trained_models(reward_predictor)
        
        logger.info("🎉 All RL models trained successfully!")
        
        return {
            "reward_predictor": reward_predictor,
            "training_examples": len(examples),
            "model_dir": self.model_dir
        }


def train_rl_models():
    """Main function to train RL models"""
    trainer = RLModelTrainer()
    return trainer.train_all_models()


if __name__ == "__main__":
    train_rl_models()
