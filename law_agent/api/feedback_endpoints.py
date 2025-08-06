"""
Advanced Feedback Collection Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from law_agent.core.agent import LawAgent
from law_agent.models.feedback import FeedbackRequest, FeedbackResponse
from law_agent.core.dependencies import get_law_agent


router = APIRouter(prefix="/feedback", tags=["feedback"])


class DetailedFeedbackRequest(BaseModel):
    """Detailed feedback request model"""
    session_id: str = Field(..., description="Session ID")
    query_id: Optional[str] = Field(None, description="Specific query ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    feedback_text: Optional[str] = Field(None, description="Detailed feedback text")
    feedback_type: str = Field("general", description="Type of feedback")
    domain_accuracy: Optional[int] = Field(None, ge=1, le=5, description="Domain classification accuracy")
    response_quality: Optional[int] = Field(None, ge=1, le=5, description="Response quality rating")
    constitutional_relevance: Optional[int] = Field(None, ge=1, le=5, description="Constitutional articles relevance")
    legal_accuracy: Optional[int] = Field(None, ge=1, le=5, description="Legal accuracy rating")
    user_satisfaction: Optional[int] = Field(None, ge=1, le=5, description="Overall satisfaction")
    improvement_suggestions: Optional[str] = Field(None, description="Suggestions for improvement")
    would_recommend: Optional[bool] = Field(None, description="Would recommend to others")
    time_spent_reading: Optional[int] = Field(None, description="Time spent reading response (seconds)")


class FeedbackAnalytics(BaseModel):
    """Feedback analytics response"""
    total_feedback: int
    average_rating: float
    rating_distribution: Dict[str, int]
    domain_performance: Dict[str, float]
    recent_feedback: List[Dict[str, Any]]
    improvement_areas: List[str]
    satisfaction_trend: List[Dict[str, Any]]


@router.post("/submit", response_model=FeedbackResponse)
async def submit_detailed_feedback(
    feedback: DetailedFeedbackRequest,
    agent: LawAgent = Depends(get_law_agent)
):
    """Submit detailed feedback for RL training"""
    
    try:
        logger.info(f"Received detailed feedback for session {feedback.session_id}")
        
        # Convert to internal feedback format
        feedback_data = {
            "session_id": feedback.session_id,
            "query_id": feedback.query_id,
            "rating": feedback.rating,
            "feedback_text": feedback.feedback_text,
            "feedback_type": feedback.feedback_type,
            "timestamp": datetime.now().isoformat(),
            "detailed_ratings": {
                "domain_accuracy": feedback.domain_accuracy,
                "response_quality": feedback.response_quality,
                "constitutional_relevance": feedback.constitutional_relevance,
                "legal_accuracy": feedback.legal_accuracy,
                "user_satisfaction": feedback.user_satisfaction
            },
            "improvement_suggestions": feedback.improvement_suggestions,
            "would_recommend": feedback.would_recommend,
            "time_spent_reading": feedback.time_spent_reading
        }
        
        # Submit to agent for RL training
        result = await agent.submit_feedback(
            session_id=feedback.session_id,
            rating=feedback.rating,
            feedback_text=feedback.feedback_text,
            time_spent=feedback.time_spent_reading or 30,
            detailed_feedback=feedback_data
        )
        
        # Calculate reward for RL system
        reward = calculate_rl_reward(feedback_data)
        
        # Update RL policy with feedback
        await update_rl_with_feedback(agent, feedback.session_id, reward, feedback_data)
        
        logger.info(f"✅ Processed detailed feedback with RL reward: {reward:.3f}")
        
        return FeedbackResponse(
            success=True,
            message="Detailed feedback submitted successfully and used for RL training",
            feedback_id=result.get("feedback_id"),
            rl_reward=reward
        )
        
    except Exception as e:
        logger.error(f"Error processing detailed feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics", response_model=FeedbackAnalytics)
async def get_feedback_analytics(
    agent: LawAgent = Depends(get_law_agent),
    days: int = 30
):
    """Get comprehensive feedback analytics"""
    
    try:
        # Get feedback data from agent
        feedback_data = await agent.get_feedback_analytics(days=days)
        
        # Calculate analytics
        analytics = FeedbackAnalytics(
            total_feedback=feedback_data.get("total_feedback", 0),
            average_rating=feedback_data.get("average_rating", 0.0),
            rating_distribution=feedback_data.get("rating_distribution", {}),
            domain_performance=feedback_data.get("domain_performance", {}),
            recent_feedback=feedback_data.get("recent_feedback", []),
            improvement_areas=identify_improvement_areas(feedback_data),
            satisfaction_trend=feedback_data.get("satisfaction_trend", [])
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train-rl")
async def trigger_rl_training(
    agent: LawAgent = Depends(get_law_agent),
    min_feedback_count: int = 10
):
    """Trigger RL model retraining with collected feedback"""
    
    try:
        # Check if enough feedback is available
        feedback_count = await agent.get_feedback_count()
        
        if feedback_count < min_feedback_count:
            return {
                "success": False,
                "message": f"Need at least {min_feedback_count} feedback entries for training. Current: {feedback_count}"
            }
        
        # Trigger RL training
        training_result = await agent.retrain_rl_models()
        
        logger.info(f"✅ RL models retrained with {feedback_count} feedback entries")
        
        return {
            "success": True,
            "message": f"RL models retrained successfully with {feedback_count} feedback entries",
            "training_metrics": training_result
        }
        
    except Exception as e:
        logger.error(f"Error triggering RL training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_rl_reward(feedback_data: Dict[str, Any]) -> float:
    """Calculate RL reward from detailed feedback"""
    
    base_reward = (feedback_data["rating"] - 3) / 2.0  # Convert 1-5 to -1 to 1
    
    # Weight detailed ratings
    detailed_ratings = feedback_data.get("detailed_ratings", {})
    detailed_reward = 0.0
    rating_count = 0
    
    for rating_type, rating in detailed_ratings.items():
        if rating is not None:
            detailed_reward += (rating - 3) / 2.0
            rating_count += 1
    
    if rating_count > 0:
        detailed_reward /= rating_count
    
    # Combine base and detailed rewards
    final_reward = (base_reward * 0.4) + (detailed_reward * 0.6)
    
    # Bonus for recommendations
    if feedback_data.get("would_recommend"):
        final_reward += 0.2
    elif feedback_data.get("would_recommend") is False:
        final_reward -= 0.2
    
    # Time spent bonus (longer reading = better engagement)
    time_spent = feedback_data.get("time_spent_reading", 30)
    if time_spent > 60:
        final_reward += 0.1
    elif time_spent < 10:
        final_reward -= 0.1
    
    return max(-1.0, min(1.0, final_reward))


async def update_rl_with_feedback(agent: LawAgent, session_id: str, reward: float, feedback_data: Dict[str, Any]):
    """Update RL policy with feedback reward"""
    
    try:
        # Get the last interaction for this session
        interaction = await agent.memory.get_last_interaction(session_id)
        
        if interaction:
            # Create RL state from interaction
            rl_state = {
                "user_type": interaction.user_type,
                "domain": interaction.predicted_domain.value if interaction.predicted_domain else "unknown",
                "confidence": interaction.confidence_score or 0.5,
                "query_complexity": len(interaction.query.split()) / 20.0,  # Rough complexity
                "session_length": 1.0,
                "interaction_count": 1.0
            }
            
            # Create RL action
            rl_action = {
                "action": "balanced",  # Default action
                "domain": rl_state["domain"],
                "confidence": rl_state["confidence"]
            }
            
            # Update RL policy
            await agent.rl_policy.update_policy(rl_state, rl_action, reward)
            
            logger.info(f"✅ Updated RL policy with reward {reward:.3f} for session {session_id}")
            
    except Exception as e:
        logger.error(f"Error updating RL with feedback: {e}")


def identify_improvement_areas(feedback_data: Dict[str, Any]) -> List[str]:
    """Identify areas for improvement based on feedback"""
    
    improvement_areas = []
    
    # Check domain performance
    domain_performance = feedback_data.get("domain_performance", {})
    for domain, score in domain_performance.items():
        if score < 3.5:
            improvement_areas.append(f"Improve {domain.replace('_', ' ')} responses")
    
    # Check overall rating
    avg_rating = feedback_data.get("average_rating", 0.0)
    if avg_rating < 3.5:
        improvement_areas.append("Overall response quality needs improvement")
    
    # Check recent negative feedback
    recent_feedback = feedback_data.get("recent_feedback", [])
    negative_feedback = [f for f in recent_feedback if f.get("rating", 5) <= 2]
    
    if len(negative_feedback) > len(recent_feedback) * 0.3:
        improvement_areas.append("Address recent negative feedback patterns")
    
    return improvement_areas[:5]  # Top 5 improvement areas
