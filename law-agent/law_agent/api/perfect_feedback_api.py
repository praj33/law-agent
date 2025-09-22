"""
Perfect Feedback API - Exactly matching your RL specifications
State: user domain + feedback history
Action: legal domain → legal route → glossary
Reward: user upvote/downvote or time spent
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from law_agent.core.agent import LawAgent
from law_agent.core.dependencies import get_law_agent


router = APIRouter(prefix="/perfect-feedback", tags=["perfect-feedback"])


class PerfectFeedbackRequest(BaseModel):
    """Perfect feedback request matching your specifications"""
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID for feedback history")
    
    # Reward: user upvote/downvote or time spent
    upvote: Optional[bool] = Field(None, description="True=upvote, False=downvote, None=neutral")
    time_spent: float = Field(..., description="Time spent reading response (seconds)")
    
    # Additional context
    user_satisfaction: float = Field(default=0.5, ge=-1.0, le=1.0, description="Overall satisfaction (-1 to 1)")
    domain_accuracy: Optional[bool] = Field(None, description="Was domain classification accurate?")
    route_helpful: Optional[bool] = Field(None, description="Was legal route helpful?")
    glossary_useful: Optional[bool] = Field(None, description="Were glossary terms useful?")


class PerfectFeedbackResponse(BaseModel):
    """Perfect feedback response"""
    success: bool
    message: str
    rl_reward: float
    q_value_update: Dict[str, float]
    user_expertise_update: Dict[str, float]
    feedback_history_length: int


class PerfectRLStatsResponse(BaseModel):
    """Perfect RL statistics response"""
    total_feedback_entries: int
    total_users: int
    total_states_learned: int
    average_rewards_by_domain: Dict[str, float]
    exploration_rate: float
    learning_rate: float
    q_table_size: int
    recent_learning_trend: List[Dict[str, Any]]


@router.post("/submit", response_model=PerfectFeedbackResponse)
async def submit_perfect_feedback(
    feedback: PerfectFeedbackRequest,
    agent: LawAgent = Depends(get_law_agent)
):
    """Submit perfect feedback for RL learning (your exact specifications)"""
    
    try:
        if not agent.perfect_rl_policy:
            raise HTTPException(status_code=500, detail="Perfect RL system not available")
        
        logger.info(f"Received perfect feedback for user {feedback.user_id}")
        
        # Get current session state
        session = agent.sessions.get(feedback.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get last interaction to determine current domain
        last_interaction = None
        if session.conversation_history:
            last_interaction = session.conversation_history[-1]
        
        current_domain = "unknown"
        if last_interaction and last_interaction.predicted_domain:
            current_domain = last_interaction.predicted_domain.value
        
        # Create perfect RL state: user domain + feedback history
        current_state = agent.perfect_rl_policy.get_user_state(
            user_id=feedback.user_id,
            current_domain=current_domain,
            user_type=session.user_profile.user_type,
            session_length=len(session.conversation_history)
        )
        
        # Calculate base reward from feedback components
        base_reward = feedback.user_satisfaction
        
        # Adjust reward based on specific feedback
        if feedback.domain_accuracy is True:
            base_reward += 0.2
        elif feedback.domain_accuracy is False:
            base_reward -= 0.2
            
        if feedback.route_helpful is True:
            base_reward += 0.2
        elif feedback.route_helpful is False:
            base_reward -= 0.2
            
        if feedback.glossary_useful is True:
            base_reward += 0.1
        elif feedback.glossary_useful is False:
            base_reward -= 0.1
        
        # Store Q-values before update for comparison
        state_key = current_state.to_key()
        old_q_values = {}
        if state_key in agent.perfect_rl_policy.q_table:
            old_q_values = agent.perfect_rl_policy.q_table[state_key].copy()
        
        # Update perfect RL policy with reward: upvote/downvote or time spent
        agent.perfect_rl_policy.update_policy(
            user_id=feedback.user_id,
            reward=base_reward,
            upvote=feedback.upvote,
            time_spent=feedback.time_spent,
            new_state=current_state  # For Q-learning update
        )
        
        # Calculate Q-value changes
        q_value_update = {}
        if state_key in agent.perfect_rl_policy.q_table:
            new_q_values = agent.perfect_rl_policy.q_table[state_key]
            for action_key in new_q_values:
                old_val = old_q_values.get(action_key, 0.0)
                new_val = new_q_values[action_key]
                if abs(new_val - old_val) > 0.001:  # Only show significant changes
                    q_value_update[action_key] = new_val - old_val
        
        # Get updated user expertise
        user_expertise = agent.perfect_rl_policy.domain_expertise.get(feedback.user_id, {})
        
        # Get feedback history length
        feedback_history_length = len(agent.perfect_rl_policy.feedback_history.get(feedback.user_id, []))
        
        # Calculate final RL reward
        final_reward = agent.perfect_rl_policy._calculate_perfect_reward(
            base_reward, feedback.upvote, feedback.time_spent
        )
        
        # Save policy periodically
        if feedback_history_length % 10 == 0:
            agent.perfect_rl_policy.save_policy()
        
        logger.info(f"Perfect RL updated - Reward: {final_reward:.3f}, History: {feedback_history_length}")
        
        return PerfectFeedbackResponse(
            success=True,
            message=f"Perfect RL feedback processed successfully",
            rl_reward=final_reward,
            q_value_update=q_value_update,
            user_expertise_update=user_expertise,
            feedback_history_length=feedback_history_length
        )
        
    except Exception as e:
        logger.error(f"Error processing perfect feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=PerfectRLStatsResponse)
async def get_perfect_rl_stats(
    agent: LawAgent = Depends(get_law_agent)
):
    """Get perfect RL system statistics"""
    
    try:
        if not agent.perfect_rl_policy:
            raise HTTPException(status_code=500, detail="Perfect RL system not available")
        
        # Get comprehensive stats
        stats = agent.perfect_rl_policy.get_policy_stats()
        
        # Add Q-table size
        stats["q_table_size"] = len(agent.perfect_rl_policy.q_table)
        
        # Get recent learning trend (last 20 feedback entries)
        recent_trend = []
        for user_id, history in agent.perfect_rl_policy.feedback_history.items():
            for feedback in history[-20:]:  # Last 20 entries
                recent_trend.append({
                    "timestamp": feedback.timestamp,
                    "domain": feedback.domain,
                    "reward": feedback.reward,
                    "upvote": feedback.upvote,
                    "time_spent": feedback.time_spent
                })
        
        # Sort by timestamp
        recent_trend.sort(key=lambda x: x["timestamp"], reverse=True)
        stats["recent_learning_trend"] = recent_trend[:20]
        
        return PerfectRLStatsResponse(**stats)
        
    except Exception as e:
        logger.error(f"Error getting perfect RL stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action-recommendation")
async def get_perfect_action_recommendation(
    user_id: str,
    current_domain: str,
    user_type: str = "common_person",
    agent: LawAgent = Depends(get_law_agent)
):
    """Get perfect action recommendation: legal domain → legal route → glossary"""
    
    try:
        if not agent.perfect_rl_policy:
            raise HTTPException(status_code=500, detail="Perfect RL system not available")
        
        # Get perfect RL state: user domain + feedback history
        current_state = agent.perfect_rl_policy.get_user_state(
            user_id=user_id,
            current_domain=current_domain,
            user_type=user_type,
            session_length=1
        )
        
        # Select perfect action: legal domain → legal route → glossary
        recommended_action = agent.perfect_rl_policy.select_action(current_state)
        
        return {
            "success": True,
            "state_summary": {
                "user_domain": current_state.user_domain,
                "feedback_history_length": len(current_state.feedback_history),
                "recent_satisfaction": current_state.recent_satisfaction,
                "domain_expertise": current_state.domain_expertise
            },
            "recommended_action": {
                "legal_domain": recommended_action.legal_domain,
                "legal_route": recommended_action.legal_route,
                "glossary_terms": recommended_action.glossary_terms,
                "response_style": recommended_action.response_style
            },
            "q_value": agent.perfect_rl_policy.q_table.get(
                current_state.to_key(), {}
            ).get(recommended_action.to_key(), 0.0)
        }
        
    except Exception as e:
        logger.error(f"Error getting perfect action recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-learning")
async def reset_perfect_rl_learning(
    confirm: bool = False,
    agent: LawAgent = Depends(get_law_agent)
):
    """Reset perfect RL learning (use with caution)"""
    
    if not confirm:
        return {
            "success": False,
            "message": "Add confirm=true to reset learning"
        }
    
    try:
        if not agent.perfect_rl_policy:
            raise HTTPException(status_code=500, detail="Perfect RL system not available")
        
        # Reset all learning
        agent.perfect_rl_policy.q_table = {}
        agent.perfect_rl_policy.feedback_history = {}
        agent.perfect_rl_policy.domain_expertise = {}
        
        logger.info("Perfect RL learning reset")
        
        return {
            "success": True,
            "message": "Perfect RL learning reset successfully"
        }
        
    except Exception as e:
        logger.error(f"Error resetting perfect RL learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))
