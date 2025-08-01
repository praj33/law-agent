"""Main Law Agent class with reinforcement learning and memory management."""

import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from loguru import logger

from .state import (
    AgentState, UserProfile, UserInteraction, UserType, 
    LegalDomain, InteractionType, FeedbackType
)
from .memory import AgentMemory
from ..legal.domain_classifier import LegalDomainClassifier
from ..legal.route_mapper import LegalRouteMapper
from ..legal.glossary import LegalGlossary
from ..rl.policy import create_rl_policy


class LawAgent:
    """Main Law Agent with reinforcement learning capabilities."""
    
    def __init__(self):
        """Initialize the Law Agent."""
        self.memory = AgentMemory()
        self.domain_classifier = LegalDomainClassifier()
        self.route_mapper = LegalRouteMapper()
        self.glossary = LegalGlossary()
        self.rl_policy = create_rl_policy("qtable")
        
        logger.info("Law Agent initialized successfully")
    
    async def create_session(self, user_id: str, user_type: UserType) -> str:
        """Create a new session for a user."""
        session_id = str(uuid.uuid4())
        
        # Get or create user profile
        user_profile = await self.memory.retrieve_user_profile(user_id)
        if not user_profile:
            user_profile = UserProfile(
                user_id=user_id,
                user_type=user_type
            )
            await self.memory.store_user_profile(user_profile)
        
        # Create agent state
        agent_state = AgentState(
            session_id=session_id,
            user_id=user_id,
            user_profile=user_profile
        )
        
        await self.memory.store_state(agent_state)
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return session_id
    
    async def process_query(
        self, 
        session_id: str, 
        query: str, 
        interaction_type: InteractionType = InteractionType.QUERY
    ) -> Dict[str, Any]:
        """Process a user query and return response with legal guidance."""
        
        # Retrieve agent state
        agent_state = await self.memory.retrieve_state(session_id)
        if not agent_state:
            raise ValueError(f"Session {session_id} not found")
        
        # Create interaction record
        interaction_id = str(uuid.uuid4())
        interaction = UserInteraction(
            interaction_id=interaction_id,
            user_id=agent_state.user_id,
            interaction_type=interaction_type,
            query=query
        )
        
        try:
            # Step 1: Classify legal domain
            domain_result = await self.domain_classifier.classify(query, agent_state)
            predicted_domain = domain_result["domain"]
            confidence_score = domain_result["confidence"]
            
            interaction.predicted_domain = predicted_domain
            interaction.confidence_score = confidence_score
            
            # Step 2: Get RL policy recommendation
            rl_state = self._create_rl_state(agent_state, predicted_domain)
            rl_action = await self.rl_policy.get_action(rl_state)
            
            # Step 3: Map to legal route
            route_result = await self.route_mapper.get_route(
                domain=predicted_domain,
                query=query,
                user_type=agent_state.user_profile.user_type,
                rl_recommendation=rl_action
            )
            
            # Step 4: Get relevant glossary terms
            glossary_terms = await self.glossary.get_relevant_terms(
                query=query,
                domain=predicted_domain
            )
            
            # Step 5: Generate response
            response = self._generate_response(
                query=query,
                domain_result=domain_result,
                route_result=route_result,
                glossary_terms=glossary_terms,
                user_profile=agent_state.user_profile
            )
            
            interaction.response = response["text"]
            
            # Update agent state
            agent_state.add_interaction(interaction)
            agent_state.current_domain = predicted_domain
            
            # Store updated state and interaction
            await self.memory.store_state(agent_state)
            await self.memory.store_interaction(interaction)
            await self.memory.store_user_profile(agent_state.user_profile)
            
            logger.info(f"Processed query for session {session_id}, domain: {predicted_domain}")
            
            return {
                "interaction_id": interaction_id,
                "response": response,
                "domain": predicted_domain,
                "confidence": confidence_score,
                "route": route_result,
                "glossary_terms": glossary_terms,
                "session_context": {
                    "total_interactions": len(agent_state.conversation_history),
                    "user_satisfaction": agent_state.user_profile.satisfaction_score,
                    "preferred_domains": agent_state.user_profile.preferred_domains
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            # Store failed interaction
            interaction.response = f"Error processing query: {str(e)}"
            agent_state.add_interaction(interaction)
            await self.memory.store_state(agent_state)
            await self.memory.store_interaction(interaction)
            
            raise e

    async def submit_feedback(
        self,
        session_id: str,
        interaction_id: str,
        feedback: FeedbackType,
        time_spent: Optional[float] = None
    ) -> Dict[str, Any]:
        """Submit user feedback for an interaction."""

        # Retrieve agent state
        agent_state = await self.memory.retrieve_state(session_id)
        if not agent_state:
            raise ValueError(f"Session {session_id} not found")

        # Find the interaction
        target_interaction = None
        for interaction in agent_state.conversation_history:
            if interaction.interaction_id == interaction_id:
                target_interaction = interaction
                break

        if not target_interaction:
            raise ValueError(f"Interaction {interaction_id} not found")

        # Update interaction with feedback
        target_interaction.feedback = feedback
        if time_spent:
            target_interaction.time_spent = time_spent

        # Calculate reward for RL
        reward = self._calculate_reward(feedback, time_spent)

        # Update RL policy
        rl_state = self._create_rl_state(agent_state, target_interaction.predicted_domain)
        await self.rl_policy.update_policy(rl_state, reward)

        # Update agent state
        agent_state.add_interaction(target_interaction)  # This updates satisfaction score

        # Store updated state
        await self.memory.store_state(agent_state)
        await self.memory.store_interaction(target_interaction)
        await self.memory.store_user_profile(agent_state.user_profile)

        logger.info(f"Received feedback {feedback} for interaction {interaction_id}")

        return {
            "status": "success",
            "reward": reward,
            "updated_satisfaction": agent_state.user_profile.satisfaction_score
        }

    def _create_rl_state(self, agent_state: AgentState, current_domain: Optional[LegalDomain]) -> Dict[str, Any]:
        """Create RL state representation."""
        domain_history = agent_state.get_domain_history()
        recent_interactions = agent_state.get_recent_interactions(5)

        return {
            "user_type": agent_state.user_profile.user_type.value,
            "current_domain": current_domain.value if current_domain else "unknown",
            "domain_history": {d.value: count for d, count in domain_history.items()},
            "satisfaction_score": agent_state.user_profile.satisfaction_score,
            "interaction_count": agent_state.user_profile.interaction_count,
            "recent_feedback": [i.feedback.value for i in recent_interactions if i.feedback],
            "average_confidence": agent_state.get_average_confidence()
        }

    def _calculate_reward(self, feedback: FeedbackType, time_spent: Optional[float] = None) -> float:
        """Calculate reward for RL based on feedback and time spent."""
        base_reward = 0.0

        # Feedback-based reward
        if feedback == FeedbackType.UPVOTE:
            base_reward = 1.0
        elif feedback == FeedbackType.DOWNVOTE:
            base_reward = -1.0
        else:  # NEUTRAL
            base_reward = 0.0

        # Time-based adjustment
        if time_spent:
            # Longer engagement (up to 5 minutes) is positive
            # Very short (<10s) or very long (>10min) engagement is negative
            if 10 <= time_spent <= 300:  # 10 seconds to 5 minutes
                time_bonus = min(0.5, time_spent / 600)  # Max 0.5 bonus
            elif time_spent < 10:
                time_bonus = -0.3  # Quick exit penalty
            else:  # > 10 minutes
                time_bonus = -0.2  # Confusion penalty

            base_reward += time_bonus

        return max(-2.0, min(2.0, base_reward))  # Clamp between -2 and 2

    def _generate_response(
        self,
        query: str,
        domain_result: Dict[str, Any],
        route_result: Dict[str, Any],
        glossary_terms: List[Dict[str, Any]],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Generate comprehensive response for the user."""

        domain = domain_result["domain"]
        confidence = domain_result["confidence"]

        # Base response structure
        response = {
            "text": "",
            "sections": [],
            "next_steps": route_result.get("next_steps", []),
            "forms": route_result.get("forms", []),
            "resources": route_result.get("resources", []),
            "glossary": glossary_terms[:5]  # Top 5 relevant terms
        }

        # Generate main response text
        if confidence > 0.8:
            confidence_text = "I'm confident this is a"
        elif confidence > 0.6:
            confidence_text = "This appears to be a"
        else:
            confidence_text = "This might be a"

        main_text = f"{confidence_text} {domain.value.replace('_', ' ')} matter. "

        # Add domain-specific guidance
        if route_result.get("summary"):
            main_text += route_result["summary"] + " "

        # Add user-type specific information
        if user_profile.user_type == UserType.COMMON_PERSON:
            main_text += "Here's what you need to know in simple terms: "
        elif user_profile.user_type == UserType.LAW_FIRM:
            main_text += "Professional analysis and recommendations: "

        response["text"] = main_text

        # Add sections based on route result
        if route_result.get("procedures"):
            response["sections"].append({
                "title": "Legal Procedures",
                "content": route_result["procedures"]
            })

        if route_result.get("timeline"):
            response["sections"].append({
                "title": "Expected Timeline",
                "content": route_result["timeline"]
            })

        if route_result.get("costs"):
            response["sections"].append({
                "title": "Estimated Costs",
                "content": route_result["costs"]
            })

        return response

    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of the current session."""
        agent_state = await self.memory.retrieve_state(session_id)
        if not agent_state:
            raise ValueError(f"Session {session_id} not found")

        domain_history = agent_state.get_domain_history()
        recent_interactions = agent_state.get_recent_interactions(10)

        return {
            "session_id": session_id,
            "user_id": agent_state.user_id,
            "user_type": agent_state.user_profile.user_type,
            "total_interactions": len(agent_state.conversation_history),
            "current_domain": agent_state.current_domain,
            "domain_distribution": domain_history,
            "satisfaction_score": agent_state.user_profile.satisfaction_score,
            "average_confidence": agent_state.get_average_confidence(),
            "recent_queries": [i.query for i in recent_interactions],
            "session_duration": (datetime.utcnow() - agent_state.created_at).total_seconds()
        }
