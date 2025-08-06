"""Enhanced Reinforcement Learning Policy for Legal Decision Making."""

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from loguru import logger

from ..core.state import LegalDomain, UserType, FeedbackType
from ..rl.policy import RLPolicy


class EnhancedLegalRLPolicy(RLPolicy):
    """Enhanced RL policy that learns from legal outcomes and user feedback."""
    
    def __init__(self):
        """Initialize enhanced legal RL policy."""
        super().__init__()
        self.legal_outcome_memory = {}  # Track legal outcomes
        self.domain_expertise = {}  # Track expertise by domain
        self.user_satisfaction_history = {}  # Track user satisfaction
        self.case_success_rates = {}  # Track success rates by case type
        
        # Legal-specific reward weights
        self.reward_weights = {
            "user_satisfaction": 0.4,
            "legal_accuracy": 0.3,
            "case_outcome": 0.2,
            "response_time": 0.1
        }
        
        logger.info("✅ Enhanced Legal RL Policy initialized")
    
    async def get_action(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get action based on enhanced legal reasoning."""

        domain = state.get("domain", "unknown")
        user_type = state.get("user_type", "common_person")
        query_complexity = self._assess_query_complexity(state.get("query", ""))

        # Create base action directly instead of calling parent
        base_action = {
            "action": "balanced",
            "policy_type": "enhanced_legal",
            "route_preference": ["comprehensive"],
            "glossary_emphasis": "balanced",
            "response_style": "adaptive",
            "confidence_adjustment": 0.0
        }

        # Enhance with legal-specific considerations
        enhanced_action = self._enhance_with_legal_reasoning(
            base_action, domain, user_type, query_complexity, state
        )
        
        # Add legal strategy recommendations
        enhanced_action["legal_strategy"] = self._recommend_legal_strategy(
            domain, user_type, query_complexity
        )
        
        # Add confidence assessment
        enhanced_action["confidence_assessment"] = self._assess_confidence(
            domain, query_complexity, state
        )
        
        return enhanced_action
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess the complexity of a legal query."""
        
        query_lower = query.lower()
        
        # High complexity indicators
        high_complexity_terms = [
            "constitutional", "federal", "supreme court", "appeal", "class action",
            "securities", "antitrust", "intellectual property", "merger", "acquisition"
        ]
        
        # Medium complexity indicators
        medium_complexity_terms = [
            "contract", "employment", "discrimination", "negligence", "liability",
            "damages", "breach", "violation", "dispute", "settlement"
        ]
        
        # Simple query indicators
        simple_terms = [
            "divorce", "custody", "traffic", "small claims", "landlord", "tenant",
            "will", "estate", "name change", "restraining order"
        ]
        
        if any(term in query_lower for term in high_complexity_terms):
            return "high"
        elif any(term in query_lower for term in medium_complexity_terms):
            return "medium"
        elif any(term in query_lower for term in simple_terms):
            return "low"
        else:
            return "medium"  # Default to medium
    
    def _enhance_with_legal_reasoning(
        self,
        base_action: Dict[str, Any],
        domain: str,
        user_type: str,
        complexity: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance action with legal reasoning."""

        # Ensure base_action is not None
        if base_action is None:
            base_action = {"action": "balanced", "policy_type": "enhanced_legal"}

        enhanced_action = base_action.copy()
        
        # Adjust response style based on user type and complexity
        if user_type == "law_firm" and complexity == "high":
            enhanced_action["response_style"] = "detailed_professional"
            enhanced_action["include_citations"] = True
            enhanced_action["include_precedents"] = True
        elif user_type == "common_person" and complexity == "low":
            enhanced_action["response_style"] = "simple_explanatory"
            enhanced_action["include_citations"] = False
            enhanced_action["include_precedents"] = False
        else:
            enhanced_action["response_style"] = "balanced"
            enhanced_action["include_citations"] = True
            enhanced_action["include_precedents"] = True
        
        # Add domain-specific enhancements
        domain_expertise = self.domain_expertise.get(domain, 0.5)
        if domain_expertise > 0.8:
            enhanced_action["use_advanced_analysis"] = True
        else:
            enhanced_action["use_advanced_analysis"] = False
        
        # Add urgency assessment
        enhanced_action["urgency"] = self._assess_urgency(state.get("query", ""))
        
        return enhanced_action
    
    def _recommend_legal_strategy(
        self,
        domain: str,
        user_type: str,
        complexity: str
    ) -> Dict[str, Any]:
        """Recommend legal strategy based on domain and complexity."""
        
        strategies = {
            "family_law": {
                "low": ["mediation", "collaborative_divorce", "self_representation"],
                "medium": ["attorney_consultation", "mediation", "document_preparation"],
                "high": ["experienced_attorney", "expert_witnesses", "litigation_preparation"]
            },
            "criminal_law": {
                "low": ["public_defender", "plea_negotiation"],
                "medium": ["private_attorney", "investigation", "plea_negotiation"],
                "high": ["experienced_criminal_attorney", "expert_witnesses", "trial_preparation"]
            },
            "contract_law": {
                "low": ["contract_review", "negotiation"],
                "medium": ["attorney_review", "contract_drafting", "negotiation"],
                "high": ["specialized_attorney", "due_diligence", "litigation_readiness"]
            },
            "employment_law": {
                "low": ["hr_consultation", "documentation"],
                "medium": ["employment_attorney", "eeoc_filing", "documentation"],
                "high": ["specialized_attorney", "expert_witnesses", "class_action_consideration"]
            },
            "property_law": {
                "low": ["title_search", "contract_review"],
                "medium": ["real_estate_attorney", "due_diligence", "contract_negotiation"],
                "high": ["specialized_attorney", "environmental_assessment", "zoning_analysis"]
            }
        }
        
        domain_strategies = strategies.get(domain, {
            "low": ["legal_consultation"],
            "medium": ["attorney_consultation", "document_review"],
            "high": ["specialized_attorney", "comprehensive_analysis"]
        })
        
        recommended_strategies = domain_strategies.get(complexity, domain_strategies["medium"])
        
        return {
            "primary_strategies": recommended_strategies[:2],
            "alternative_strategies": recommended_strategies[2:],
            "complexity_level": complexity,
            "domain": domain
        }
    
    def _assess_confidence(
        self,
        domain: str,
        complexity: str,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess confidence in the legal analysis."""
        
        base_confidence = 0.7
        
        # Adjust based on domain expertise
        domain_expertise = self.domain_expertise.get(domain, 0.5)
        confidence_adjustment = (domain_expertise - 0.5) * 0.4
        
        # Adjust based on complexity
        complexity_adjustments = {
            "low": 0.1,
            "medium": 0.0,
            "high": -0.2
        }
        confidence_adjustment += complexity_adjustments.get(complexity, 0.0)
        
        # Adjust based on available information
        if state.get("relevant_cases"):
            confidence_adjustment += 0.1
        if state.get("precedent_analysis"):
            confidence_adjustment += 0.1
        
        final_confidence = max(0.1, min(0.95, base_confidence + confidence_adjustment))
        
        return {
            "confidence_score": final_confidence,
            "confidence_level": self._get_confidence_level(final_confidence),
            "factors": {
                "domain_expertise": domain_expertise,
                "complexity": complexity,
                "available_precedents": bool(state.get("relevant_cases")),
                "precedent_analysis": bool(state.get("precedent_analysis"))
            }
        }
    
    def _get_confidence_level(self, score: float) -> str:
        """Convert confidence score to level."""
        if score >= 0.8:
            return "high"
        elif score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _assess_urgency(self, query: str) -> str:
        """Assess urgency of legal matter."""
        
        urgent_keywords = [
            "emergency", "urgent", "deadline", "court date", "arrest", "warrant",
            "eviction", "foreclosure", "restraining order", "injunction", "appeal deadline"
        ]
        
        moderate_keywords = [
            "soon", "quickly", "asap", "time sensitive", "statute of limitations",
            "contract expires", "notice period"
        ]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in urgent_keywords):
            return "high"
        elif any(keyword in query_lower for keyword in moderate_keywords):
            return "medium"
        else:
            return "low"
    
    async def update_from_legal_outcome(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        outcome: Dict[str, Any]
    ):
        """Update policy based on legal outcome."""
        
        domain = state.get("domain", "unknown")
        case_type = f"{domain}_{outcome.get('case_type', 'general')}"
        
        # Track case success rates
        if case_type not in self.case_success_rates:
            self.case_success_rates[case_type] = {"successes": 0, "total": 0}
        
        self.case_success_rates[case_type]["total"] += 1
        if outcome.get("successful", False):
            self.case_success_rates[case_type]["successes"] += 1
        
        # Update domain expertise
        if domain not in self.domain_expertise:
            self.domain_expertise[domain] = 0.5
        
        # Adjust expertise based on outcome
        if outcome.get("successful", False):
            self.domain_expertise[domain] = min(1.0, self.domain_expertise[domain] + 0.05)
        else:
            self.domain_expertise[domain] = max(0.1, self.domain_expertise[domain] - 0.02)
        
        # Calculate enhanced reward
        reward = self._calculate_legal_reward(state, action, outcome)
        
        # Update base RL policy
        await super().update_policy(state, action, reward)
        
        logger.info(f"Updated legal RL policy for {domain} with reward {reward:.3f}")
    
    def _calculate_legal_reward(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        outcome: Dict[str, Any]
    ) -> float:
        """Calculate reward based on legal outcome."""
        
        reward = 0.0
        
        # User satisfaction component
        user_satisfaction = outcome.get("user_satisfaction", 0.5)
        reward += self.reward_weights["user_satisfaction"] * (user_satisfaction - 0.5) * 2
        
        # Legal accuracy component
        legal_accuracy = outcome.get("legal_accuracy", 0.5)
        reward += self.reward_weights["legal_accuracy"] * (legal_accuracy - 0.5) * 2
        
        # Case outcome component
        if outcome.get("successful", False):
            reward += self.reward_weights["case_outcome"] * 1.0
        else:
            reward -= self.reward_weights["case_outcome"] * 0.5
        
        # Response time component (faster is better, but not at expense of quality)
        response_time = outcome.get("response_time", 5.0)  # seconds
        if response_time < 3.0:
            reward += self.reward_weights["response_time"] * 0.5
        elif response_time > 10.0:
            reward -= self.reward_weights["response_time"] * 0.3
        
        return max(-2.0, min(2.0, reward))  # Clamp between -2 and 2

    async def update_policy(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
        reward: float
    ):
        """Update the RL policy with new experience."""
        # Update base policy
        await super().update_policy(state, action, reward)

        # Update legal-specific metrics
        domain = state.get("domain", "unknown")
        if domain not in self.domain_expertise:
            self.domain_expertise[domain] = 0.5

        # Adjust domain expertise based on reward
        if reward > 0:
            self.domain_expertise[domain] = min(1.0, self.domain_expertise[domain] + 0.01)
        else:
            self.domain_expertise[domain] = max(0.1, self.domain_expertise[domain] - 0.005)

    async def save_policy(self, filepath: str):
        """Save the enhanced policy to file."""
        await super().save_policy(filepath)

        # Save enhanced policy data
        enhanced_data = {
            "legal_outcome_memory": self.legal_outcome_memory,
            "domain_expertise": self.domain_expertise,
            "user_satisfaction_history": self.user_satisfaction_history,
            "case_success_rates": self.case_success_rates,
            "reward_weights": self.reward_weights
        }

        enhanced_filepath = filepath.replace(".json", "_enhanced.json")
        with open(enhanced_filepath, 'w') as f:
            json.dump(enhanced_data, f, indent=2)

        logger.info(f"Enhanced legal RL policy saved to {enhanced_filepath}")

    async def load_policy(self, filepath: str):
        """Load the enhanced policy from file."""
        await super().load_policy(filepath)

        # Load enhanced policy data
        enhanced_filepath = filepath.replace(".json", "_enhanced.json")
        try:
            with open(enhanced_filepath, 'r') as f:
                enhanced_data = json.load(f)

            self.legal_outcome_memory = enhanced_data.get("legal_outcome_memory", {})
            self.domain_expertise = enhanced_data.get("domain_expertise", {})
            self.user_satisfaction_history = enhanced_data.get("user_satisfaction_history", {})
            self.case_success_rates = enhanced_data.get("case_success_rates", {})
            self.reward_weights = enhanced_data.get("reward_weights", self.reward_weights)

            logger.info(f"Enhanced legal RL policy loaded from {enhanced_filepath}")
        except FileNotFoundError:
            logger.info("No enhanced policy file found, starting with defaults")
