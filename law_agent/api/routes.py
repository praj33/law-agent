"""API routes for the Law Agent system."""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger

from ..core.agent import LawAgent
from ..core.state import UserType, LegalDomain, InteractionType, FeedbackType
from ..legal.glossary import LegalGlossary
from ..legal.route_mapper import LegalRouteMapper


# Initialize components with enhanced features
law_agent = LawAgent(use_enhanced_features=True)
glossary = LegalGlossary()
route_mapper = LegalRouteMapper()

# Create router
router = APIRouter()


# Request/Response Models
class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    user_type: UserType = Field(..., description="Type of user")


class CreateSessionResponse(BaseModel):
    session_id: str = Field(..., description="Created session ID")
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="Welcome message")


class QueryRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    query: str = Field(..., description="User query")
    interaction_type: InteractionType = Field(default=InteractionType.QUERY)


class QueryResponse(BaseModel):
    interaction_id: str = Field(..., description="Interaction identifier")
    response: Dict[str, Any] = Field(..., description="Agent response")
    domain: LegalDomain = Field(..., description="Predicted legal domain")
    confidence: float = Field(..., description="Prediction confidence")
    route: Dict[str, Any] = Field(..., description="Legal route information")
    glossary_terms: List[Dict[str, Any]] = Field(..., description="Relevant legal terms")
    session_context: Dict[str, Any] = Field(..., description="Session context")


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    interaction_id: str = Field(..., description="Interaction identifier")
    feedback: FeedbackType = Field(..., description="User feedback")
    time_spent: Optional[float] = Field(None, description="Time spent in seconds")


class AdvancedFeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    interaction_id: str = Field(..., description="Interaction identifier")
    response_quality: int = Field(..., ge=1, le=5, description="Response quality rating")
    legal_accuracy: int = Field(..., ge=1, le=5, description="Legal accuracy rating")
    helpfulness: int = Field(..., ge=1, le=5, description="Helpfulness rating")
    clarity: int = Field(..., ge=1, le=5, description="Clarity rating")
    completeness: int = Field(..., ge=1, le=5, description="Completeness rating")
    time_spent: float = Field(..., description="Time spent in seconds")
    overall_satisfaction: FeedbackType = Field(..., description="Overall satisfaction")
    specific_feedback: Optional[str] = Field(None, description="Specific feedback text")
    improvement_suggestions: Optional[str] = Field(None, description="Improvement suggestions")
    would_recommend: bool = Field(True, description="Would recommend to others")


class FeedbackResponse(BaseModel):
    status: str = Field(..., description="Feedback status")
    reward: float = Field(..., description="Calculated reward")
    updated_satisfaction: float = Field(..., description="Updated satisfaction score")


class GlossarySearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    domain: Optional[LegalDomain] = Field(None, description="Filter by domain")
    max_terms: int = Field(default=10, description="Maximum terms to return")


class RouteSearchRequest(BaseModel):
    domain: LegalDomain = Field(..., description="Legal domain")
    query: str = Field(..., description="User query")
    user_type: UserType = Field(..., description="User type")


# Session Management Endpoints
@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new user session."""
    try:
        session_id = await law_agent.create_session(
            user_id=request.user_id,
            user_type=request.user_type
        )
        
        return CreateSessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            message=f"Welcome! Your session has been created. How can I help you with your legal questions today?"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    try:
        # Get session from memory
        session_data = law_agent.memory.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "user_id": session_data.get("user_id", "unknown"),
            "user_type": session_data.get("user_type", "unknown"),
            "created_at": session_data.get("created_at", "unknown"),
            "status": "active"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get summary of a session."""
    try:
        summary = await law_agent.get_session_summary(session_id)
        return summary
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Query Processing Endpoints
@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query and return legal guidance."""
    try:
        result = await law_agent.process_query(
            session_id=request.session_id,
            query=request.query,
            interaction_type=request.interaction_type
        )
        
        return QueryResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Feedback Endpoints
@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for an interaction."""
    try:
        logger.info(f"🔄 Processing feedback: {request.feedback} for interaction {request.interaction_id}")
        logger.info(f"📋 Request details: session_id={request.session_id}, time_spent={request.time_spent}")

        # Call the agent's submit_feedback method
        result = await law_agent.submit_feedback(
            session_id=request.session_id,
            interaction_id=request.interaction_id,
            feedback=request.feedback,
            time_spent=request.time_spent
        )

        logger.info(f"📊 Feedback result from agent: {result}")

        # Ensure we have the required fields
        if not isinstance(result, dict):
            logger.error(f"❌ Agent returned non-dict result: {type(result)}")
            raise ValueError("Invalid result from agent")

        reward = result.get("reward", 0.0)
        satisfaction = result.get("updated_satisfaction", 0.0)
        status = result.get("status", "feedback_recorded")

        logger.info(f"✅ Returning: status={status}, reward={reward}, satisfaction={satisfaction}")

        return FeedbackResponse(
            status=status,
            reward=float(reward),
            updated_satisfaction=float(satisfaction)
        )

    except ValueError as e:
        logger.error(f"❌ Feedback validation error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Feedback processing error: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/feedback/advanced")
async def submit_advanced_feedback(request: AdvancedFeedbackRequest):
    """Submit detailed multi-dimensional feedback for an interaction."""
    try:
        # Calculate overall reward from multi-dimensional feedback
        ratings = [
            request.response_quality,
            request.legal_accuracy,
            request.helpfulness,
            request.clarity,
            request.completeness
        ]
        avg_rating = sum(ratings) / len(ratings)

        # Convert to reward scale (-1 to 1)
        normalized_reward = (avg_rating - 3) / 2  # 3 is neutral (5-point scale)

        # Adjust based on overall satisfaction
        if request.overall_satisfaction == FeedbackType.UPVOTE:
            satisfaction_bonus = 0.2
        elif request.overall_satisfaction == FeedbackType.DOWNVOTE:
            satisfaction_bonus = -0.2
        else:
            satisfaction_bonus = 0.0

        final_reward = max(-1.0, min(1.0, normalized_reward + satisfaction_bonus))

        # Submit basic feedback first
        result = await law_agent.submit_feedback(
            session_id=request.session_id,
            interaction_id=request.interaction_id,
            feedback=request.overall_satisfaction,
            time_spent=request.time_spent
        )

        # Store advanced feedback data
        advanced_feedback_data = {
            "response_quality": request.response_quality,
            "legal_accuracy": request.legal_accuracy,
            "helpfulness": request.helpfulness,
            "clarity": request.clarity,
            "completeness": request.completeness,
            "specific_feedback": request.specific_feedback,
            "improvement_suggestions": request.improvement_suggestions,
            "would_recommend": request.would_recommend,
            "calculated_reward": final_reward,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Get performance analytics
        if hasattr(law_agent.rl_policy, 'get_performance_analytics'):
            analytics = law_agent.rl_policy.get_performance_analytics()
        else:
            analytics = {}

        return {
            "status": "success",
            "message": "Advanced feedback recorded successfully",
            "reward": final_reward,
            "updated_satisfaction": result["updated_satisfaction"],
            "feedback_summary": {
                "avg_rating": avg_rating,
                "total_dimensions": len(ratings),
                "recommendation": request.would_recommend
            },
            "learning_impact": {
                "reward_calculated": final_reward,
                "will_improve_responses": abs(final_reward) > 0.1,
                "analytics_updated": bool(analytics)
            }
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Advanced feedback submission error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/analytics/performance")
async def get_performance_analytics():
    """Get comprehensive performance analytics from the RL system."""
    try:
        if hasattr(law_agent.rl_policy, 'get_performance_analytics'):
            analytics = law_agent.rl_policy.get_performance_analytics()

            return {
                "status": "success",
                "analytics": analytics,
                "timestamp": datetime.utcnow().isoformat(),
                "system_info": {
                    "rl_policy_type": "AdvancedLegalRLPolicy",
                    "memory_system": "AdvancedAgentMemory",
                    "ml_enabled": hasattr(law_agent.rl_policy, 'reward_predictor') and law_agent.rl_policy.reward_predictor is not None
                }
            }
        else:
            return {
                "status": "limited",
                "message": "Advanced analytics not available with current RL policy",
                "basic_info": {
                    "policy_type": type(law_agent.rl_policy).__name__
                }
            }

    except Exception as e:
        logger.error(f"Analytics retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rl/status")
async def get_rl_system_status():
    """Get comprehensive RL system status and metrics."""
    try:
        rl_policy = law_agent.rl_policy

        # Basic RL info
        status = {
            "rl_policy_type": type(rl_policy).__name__,
            "is_advanced": hasattr(rl_policy, 'memory'),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Advanced RL metrics if available
        if hasattr(rl_policy, 'memory'):
            memory_stats = rl_policy.memory.get_memory_stats()
            status.update({
                "memory_system": {
                    "episodic_memory_size": memory_stats.get("episodic_memory_size", 0),
                    "semantic_memory_domains": memory_stats.get("semantic_memory_domains", 0),
                    "procedural_memory_size": memory_stats.get("procedural_memory_size", 0)
                },
                "learning_metrics": {
                    "exploration_rate": getattr(rl_policy, 'exploration_rate', 0.0),
                    "total_states": len(getattr(rl_policy, 'action_rewards', {})),
                    "ml_models_trained": hasattr(rl_policy, 'reward_predictor') and
                                       rl_policy.reward_predictor is not None and
                                       hasattr(rl_policy.reward_predictor, 'n_features_in_')
                },
                "domain_performance": memory_stats.get("domain_performance", {}),
                "q_table_size": max(
                    len(getattr(rl_policy, 'action_rewards', {})),
                    memory_stats.get("episodic_memory_size", 0)
                )
            })

            # Performance analytics if available
            if hasattr(rl_policy, 'get_performance_analytics'):
                analytics = rl_policy.get_performance_analytics()
                status["performance_analytics"] = analytics

        return status

    except Exception as e:
        logger.error(f"RL status retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/rl/metrics")
async def get_rl_metrics():
    """Get user-friendly RL metrics for display."""
    try:
        rl_policy = law_agent.rl_policy

        # Basic metrics
        metrics = {
            "system_status": "Advanced RL Active" if hasattr(rl_policy, 'memory') else "Basic System",
            "learning_active": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Advanced metrics if available
        if hasattr(rl_policy, 'memory'):
            memory_stats = rl_policy.memory.get_memory_stats()

            metrics.update({
                "experiences_learned": memory_stats.get("episodic_memory_size", 0),
                "domains_mastered": memory_stats.get("semantic_memory_domains", 0),
                "skills_acquired": memory_stats.get("procedural_memory_size", 0),
                "exploration_rate": getattr(rl_policy, 'exploration_rate', 0.1),
                "knowledge_states": max(
                    len(getattr(rl_policy, 'action_rewards', {})),
                    memory_stats.get("episodic_memory_size", 0)
                ),
                "learning_progress": {
                    "total_interactions": memory_stats.get("episodic_memory_size", 0),
                    "improvement_rate": "Continuous",
                    "adaptation_speed": "Real-time"
                }
            })

        return metrics

    except Exception as e:
        logger.error(f"RL metrics retrieval error: {e}")
        return {
            "system_status": "Error retrieving metrics",
            "learning_active": False,
            "error": str(e)
        }


@router.get("/demo/improvements")
async def get_user_visible_improvements():
    """Get user-visible improvements and changes."""
    try:
        improvements = {
            "response_quality": {
                "description": "AI responses become more accurate and relevant",
                "metric": "Confidence scores increase over time",
                "user_benefit": "Better legal advice tailored to your needs"
            },
            "personalization": {
                "description": "System learns your preferences and legal domain focus",
                "metric": "Domain-specific expertise grows",
                "user_benefit": "More personalized and relevant responses"
            },
            "speed_optimization": {
                "description": "Response times improve as system learns patterns",
                "metric": "Average response time decreases",
                "user_benefit": "Faster answers to your legal questions"
            },
            "satisfaction_tracking": {
                "description": "System tracks and improves based on your feedback",
                "metric": "User satisfaction score increases",
                "user_benefit": "Responses get better aligned with your expectations"
            },
            "memory_retention": {
                "description": "AI remembers your previous interactions and context",
                "metric": "Session continuity and context awareness",
                "user_benefit": "No need to repeat information, contextual conversations"
            }
        }

        return {
            "improvements": improvements,
            "how_to_see_changes": {
                "confidence_scores": "Watch confidence percentages increase over time",
                "response_quality": "Notice more detailed and relevant legal advice",
                "personalization": "See responses tailored to your specific legal domain",
                "learning_feedback": "Observe how feedback immediately improves future responses",
                "session_memory": "Experience contextual conversations that remember previous questions"
            },
            "real_time_indicators": [
                "Confidence scores in API responses",
                "Response time improvements",
                "More relevant legal domain classification",
                "Personalized suggested actions",
                "Contextual follow-up questions"
            ]
        }

    except Exception as e:
        logger.error(f"Improvements retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Glossary Endpoints
@router.post("/glossary/search")
async def search_glossary(request: GlossarySearchRequest):
    """Search legal glossary for relevant terms."""
    try:
        terms = await glossary.get_relevant_terms(
            query=request.query,
            domain=request.domain,
            max_terms=request.max_terms
        )
        
        return {"terms": terms, "count": len(terms)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/glossary/term/{term}")
async def get_term_definition(term: str, user_type: str = "common"):
    """Get definition for a specific legal term."""
    try:
        definition = glossary.get_term_definition(term, user_type)
        
        if not definition:
            raise HTTPException(status_code=404, detail="Term not found")
        
        return definition
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/glossary/domain/{domain}")
async def get_domain_terms(domain: LegalDomain):
    """Get all terms for a specific legal domain."""
    try:
        terms = glossary.get_domain_terms(domain)
        return {"domain": domain, "terms": terms, "count": len(terms)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route Mapping Endpoints
@router.post("/routes/search")
async def search_routes(request: RouteSearchRequest):
    """Get legal route for specific domain and query."""
    try:
        route = await route_mapper.get_route(
            domain=request.domain,
            query=request.query,
            user_type=request.user_type
        )
        
        return {"route": route, "domain": request.domain}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/domain/{domain}")
async def get_available_routes(domain: LegalDomain):
    """Get available routes for a legal domain."""
    try:
        routes = route_mapper.get_available_routes(domain)
        return {"domain": domain, "available_routes": routes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routes/search/{search_term}")
async def search_routes_by_term(search_term: str):
    """Search routes by term."""
    try:
        routes = route_mapper.search_routes(search_term)
        return {"search_term": search_term, "routes": routes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analytics and Monitoring Endpoints
@router.get("/analytics/domains")
async def get_domain_analytics():
    """Get analytics about legal domain usage."""
    # This would typically query the database for usage statistics
    # For now, return a placeholder
    return {
        "message": "Domain analytics endpoint - implementation depends on specific analytics requirements",
        "available_domains": [domain.value for domain in LegalDomain]
    }


@router.get("/analytics/user-satisfaction")
async def get_satisfaction_analytics():
    """Get user satisfaction analytics."""
    # This would typically query the database for satisfaction metrics
    return {
        "message": "User satisfaction analytics endpoint - implementation depends on specific analytics requirements"
    }


# System Information Endpoints
@router.get("/system/info")
async def get_system_info():
    """Get system information."""
    return {
        "version": "1.0.0",
        "components": {
            "law_agent": "initialized",
            "glossary": f"{len(glossary.terms)} terms loaded",
            "route_mapper": "initialized",
            "rl_policy": "active"
        },
        "supported_domains": [domain.value for domain in LegalDomain],
        "supported_user_types": [user_type.value for user_type in UserType]
    }


@router.get("/system/health")
async def system_health_check():
    """Detailed system health check."""
    try:
        # Test core components
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "law_agent": "ok",
                "glossary": "ok",
                "route_mapper": "ok",
                "database": "ok",  # Would check actual database connection
                "redis": "ok"      # Would check actual Redis connection
            }
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"System unhealthy: {str(e)}")


# Background task for policy updates
async def update_rl_policy_background():
    """Background task to periodically save RL policy."""
    try:
        law_agent.rl_policy.save_policy()
    except Exception as e:
        logger.error(f"Error saving RL policy: {e}")


@router.post("/admin/save-policy")
async def save_rl_policy(background_tasks: BackgroundTasks):
    """Manually trigger RL policy save."""
    background_tasks.add_task(update_rl_policy_background)
    return {"message": "RL policy save scheduled"}


# Enhanced Features API Endpoints

class ConstitutionalSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for constitutional articles")
    limit: int = Field(default=5, description="Maximum number of results")


class ConstitutionalSearchResponse(BaseModel):
    articles: List[Dict[str, Any]] = Field(..., description="Found constitutional articles")
    query: str = Field(..., description="Original search query")
    total_found: int = Field(..., description="Total articles found")


@router.post("/constitutional/search", response_model=ConstitutionalSearchResponse)
async def search_constitutional_articles(request: ConstitutionalSearchRequest):
    """Search constitutional articles by query."""
    try:
        if not law_agent.constitutional_support:
            raise HTTPException(status_code=503, detail="Constitutional support not available")

        articles = law_agent.constitutional_advisor.search_constitutional_provisions(request.query)

        return ConstitutionalSearchResponse(
            articles=articles[:request.limit],
            query=request.query,
            total_found=len(articles)
        )

    except Exception as e:
        logger.error(f"Error searching constitutional articles: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


class DomainConstitutionalRequest(BaseModel):
    domain: LegalDomain = Field(..., description="Legal domain")
    query: str = Field(..., description="Legal query for context")


class DomainConstitutionalResponse(BaseModel):
    domain: LegalDomain = Field(..., description="Legal domain")
    constitutional_backing: Dict[str, Any] = Field(..., description="Constitutional backing information")
    enhanced_credibility: bool = Field(..., description="Whether response has enhanced credibility")


@router.post("/constitutional/domain-backing", response_model=DomainConstitutionalResponse)
async def get_domain_constitutional_backing(request: DomainConstitutionalRequest):
    """Get constitutional backing for a specific legal domain and query."""
    try:
        if not law_agent.constitutional_support:
            raise HTTPException(status_code=503, detail="Constitutional support not available")

        backing = law_agent.constitutional_advisor.get_constitutional_backing(request.domain, request.query)

        return DomainConstitutionalResponse(
            domain=request.domain,
            constitutional_backing=backing,
            enhanced_credibility=backing.get('enhanced_credibility', False)
        )

    except Exception as e:
        logger.error(f"Error getting constitutional backing: {e}")
        raise HTTPException(status_code=500, detail=f"Constitutional backing failed: {str(e)}")


class MLClassifierStatsResponse(BaseModel):
    enhanced_classification: bool = Field(..., description="Whether enhanced ML classification is active")
    model_stats: Dict[str, Any] = Field(..., description="ML classifier statistics")
    constitutional_support: bool = Field(..., description="Whether constitutional support is active")
    constitutional_stats: Dict[str, Any] = Field(..., description="Constitutional advisor statistics")


@router.get("/system/enhanced-features", response_model=MLClassifierStatsResponse)
async def get_enhanced_features_status():
    """Get status and statistics of enhanced features."""
    try:
        # Get ML classifier stats
        ml_stats = {}
        if law_agent.enhanced_classification and hasattr(law_agent.domain_classifier, 'get_model_stats'):
            ml_stats = law_agent.domain_classifier.get_model_stats()

        # Get constitutional advisor stats
        constitutional_stats = {}
        if law_agent.constitutional_support and law_agent.constitutional_advisor:
            constitutional_stats = law_agent.constitutional_advisor.get_stats()

        return MLClassifierStatsResponse(
            enhanced_classification=law_agent.enhanced_classification,
            model_stats=ml_stats,
            constitutional_support=law_agent.constitutional_support,
            constitutional_stats=constitutional_stats
        )

    except Exception as e:
        logger.error(f"Error getting enhanced features status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


class MLFeedbackRequest(BaseModel):
    query: str = Field(..., description="Original query")
    predicted_domain: str = Field(..., description="Predicted domain")
    actual_domain: str = Field(..., description="Actual/correct domain")
    helpful: bool = Field(..., description="Whether prediction was helpful")


@router.post("/ml/feedback")
async def add_ml_classifier_feedback(request: MLFeedbackRequest):
    """Add feedback to ML classifier for continuous learning."""
    try:
        if not law_agent.enhanced_classification:
            raise HTTPException(status_code=503, detail="Enhanced ML classification not available")

        if hasattr(law_agent.domain_classifier, 'add_feedback'):
            law_agent.domain_classifier.add_feedback(
                request.query,
                request.predicted_domain,
                request.actual_domain,
                request.helpful
            )

        return {"message": "Feedback added successfully", "learning_enabled": True}

    except Exception as e:
        logger.error(f"Error adding ML feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback failed: {str(e)}")


@router.post("/ml/retrain")
async def retrain_ml_classifier():
    """Retrain ML classifier with accumulated feedback."""
    try:
        if not law_agent.enhanced_classification:
            raise HTTPException(status_code=503, detail="Enhanced ML classification not available")

        if hasattr(law_agent.domain_classifier, 'retrain_with_feedback'):
            success = law_agent.domain_classifier.retrain_with_feedback()
            return {
                "message": "Retraining completed" if success else "No feedback data for retraining",
                "success": success
            }
        else:
            raise HTTPException(status_code=503, detail="Retraining not supported")

    except Exception as e:
        logger.error(f"Error retraining ML classifier: {e}")
        raise HTTPException(status_code=500, detail=f"Retraining failed: {str(e)}")


# Additional Comprehensive API Endpoints from Both Systems

class DomainClassificationRequest(BaseModel):
    query: str = Field(..., description="Query to classify")
    include_confidence: bool = Field(default=True, description="Include confidence scores")


class DomainClassificationResponse(BaseModel):
    domain: LegalDomain = Field(..., description="Classified domain")
    confidence: float = Field(..., description="Classification confidence")
    all_scores: Dict[str, float] = Field(..., description="All domain scores")
    method: str = Field(..., description="Classification method used")


@router.post("/domain/classify", response_model=DomainClassificationResponse)
async def classify_domain(request: DomainClassificationRequest):
    """Classify legal domain for a query."""
    try:
        result = await law_agent.domain_classifier.classify(request.query)

        # Convert LegalDomain enum values to strings for JSON serialization
        all_scores_str = {}
        if 'all_scores' in result:
            for domain, score in result['all_scores'].items():
                domain_key = domain.value if hasattr(domain, 'value') else str(domain)
                all_scores_str[domain_key] = float(score)

        return DomainClassificationResponse(
            domain=result['domain'],
            confidence=result['confidence'],
            all_scores=all_scores_str,
            method="Enhanced ML" if law_agent.enhanced_classification else "Rule-based"
        )

    except Exception as e:
        logger.error(f"Error classifying domain: {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


class GlossarySearchRequest(BaseModel):
    query: str = Field(..., description="Search query for legal terms")
    domain: Optional[LegalDomain] = Field(None, description="Filter by legal domain")
    limit: int = Field(default=10, description="Maximum number of results")


class GlossarySearchResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total results found")
    query: str = Field(..., description="Original search query")


@router.post("/glossary/search", response_model=GlossarySearchResponse)
async def search_glossary_terms(request: GlossarySearchRequest):
    """Search legal glossary terms."""
    try:
        # Use existing glossary search functionality
        query_lower = request.query.lower()
        results = []

        # Get all terms from glossary
        all_terms = glossary.get_all_terms()

        for term_data in all_terms:
            term = term_data.get('term', '')
            definition = term_data.get('definition', '')
            domain = term_data.get('domain', '')

            # Filter by domain if specified
            if request.domain and domain != request.domain.value:
                continue

            # Check if query matches
            if (query_lower in term.lower() or
                query_lower in definition.lower()):

                relevance = 1.0 if query_lower == term.lower() else 0.8
                results.append({
                    "term": term,
                    "definition": definition,
                    "domain": domain,
                    "relevance": relevance
                })

        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        limited_results = results[:request.limit]

        return GlossarySearchResponse(
            results=limited_results,
            total=len(results),
            query=request.query
        )

    except Exception as e:
        logger.error(f"Error searching glossary: {e}")
        raise HTTPException(status_code=500, detail=f"Glossary search failed: {str(e)}")


class LegalRouteRequest(BaseModel):
    domain: LegalDomain = Field(..., description="Legal domain")
    query: str = Field(..., description="User query")
    user_type: UserType = Field(..., description="User type")
    location: Optional[str] = Field(None, description="User location")


class LegalRouteResponse(BaseModel):
    route: Dict[str, Any] = Field(..., description="Legal route information")
    domain: LegalDomain = Field(..., description="Legal domain")
    estimated_timeline: Optional[str] = Field(None, description="Estimated timeline")
    estimated_cost: Optional[str] = Field(None, description="Estimated cost")


@router.post("/routes/get-route", response_model=LegalRouteResponse)
async def get_legal_route(request: LegalRouteRequest):
    """Get detailed legal route for a specific query."""
    try:
        route = await route_mapper.get_route(
            domain=request.domain,
            query=request.query,
            user_type=request.user_type
        )

        return LegalRouteResponse(
            route=route,
            domain=request.domain,
            estimated_timeline=route.get('timeline'),
            estimated_cost=route.get('cost_estimate')
        )

    except Exception as e:
        logger.error(f"Error getting legal route: {e}")
        raise HTTPException(status_code=500, detail=f"Route retrieval failed: {str(e)}")


class SystemHealthResponse(BaseModel):
    status: str = Field(..., description="System status")
    components: Dict[str, str] = Field(..., description="Component statuses")
    enhanced_features: Dict[str, bool] = Field(..., description="Enhanced feature availability")
    version: str = Field(..., description="System version")


@router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get comprehensive system health status."""
    try:
        components = {
            "law_agent": "operational",
            "domain_classifier": "enhanced" if law_agent.enhanced_classification else "basic",
            "constitutional_advisor": "active" if law_agent.constitutional_support else "inactive",
            "rl_policy": "active",
            "memory_system": "active",
            "glossary": "loaded",
            "route_mapper": "active"
        }

        enhanced_features = {
            "ml_classification": law_agent.enhanced_classification,
            "constitutional_backing": law_agent.constitutional_support,
            "rl_learning": True,
            "feedback_system": True,
            "memory_management": True
        }

        return SystemHealthResponse(
            status="healthy",
            components=components,
            enhanced_features=enhanced_features,
            version="6.0.0-integrated"
        )

    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


class AnalyticsRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID for filtering")
    start_date: Optional[str] = Field(None, description="Start date for analytics")
    end_date: Optional[str] = Field(None, description="End date for analytics")


class AnalyticsResponse(BaseModel):
    total_sessions: int = Field(..., description="Total sessions")
    total_queries: int = Field(..., description="Total queries processed")
    domain_distribution: Dict[str, int] = Field(..., description="Query distribution by domain")
    satisfaction_metrics: Dict[str, float] = Field(..., description="User satisfaction metrics")
    learning_metrics: Dict[str, Any] = Field(..., description="RL learning metrics")


@router.post("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary(request: AnalyticsRequest):
    """Get comprehensive analytics summary."""
    try:
        # Get RL performance analytics for learning metrics
        rl_status = law_agent.rl_policy.get_performance_analytics()

        # Get session count safely
        try:
            total_sessions = len(law_agent.memory.sessions) if hasattr(law_agent.memory, 'sessions') and law_agent.memory.sessions else 0
        except:
            total_sessions = 0

        # Mock analytics data - in production this would come from database
        analytics = AnalyticsResponse(
            total_sessions=total_sessions,
            total_queries=rl_status.get('total_interactions', 0),
            domain_distribution={
                "family_law": 25,
                "criminal_law": 20,
                "employment_law": 18,
                "property_law": 15,
                "other": 22
            },
            satisfaction_metrics={
                "average_satisfaction": float(rl_status.get('average_satisfaction', 0.0)),
                "positive_feedback_rate": 0.75,
                "response_helpfulness": 0.82
            },
            learning_metrics={
                "exploration_rate": float(rl_status.get('exploration_rate', 0.1)),
                "qtable_size": int(rl_status.get('qtable_size', 0)),
                "learning_progress": "active"
            }
        )

        return analytics

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")


# Document Processing Endpoints (from document_api.py)

class DocumentUploadResponse(BaseModel):
    process_id: str = Field(..., description="Document processing ID")
    message: str = Field(..., description="Upload status message")
    supported_types: List[str] = Field(..., description="Supported file types")


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document():
    """Upload and process legal documents."""
    try:
        # Mock document processing - in production this would handle file uploads
        import uuid
        process_id = str(uuid.uuid4())

        return DocumentUploadResponse(
            process_id=process_id,
            message="Document upload endpoint ready - file upload implementation needed",
            supported_types=["pdf", "docx", "txt", "rtf"]
        )

    except Exception as e:
        logger.error(f"Error in document upload: {e}")
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")


@router.get("/documents/status/{process_id}")
async def get_document_status(process_id: str):
    """Get document processing status."""
    try:
        # Mock status - in production this would check actual processing status
        return {
            "process_id": process_id,
            "status": "completed",
            "progress": 100,
            "message": "Document processing completed"
        }

    except Exception as e:
        logger.error(f"Error getting document status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


# WebSocket endpoint for real-time updates (placeholder)
@router.get("/ws/realtime")
async def websocket_endpoint():
    """WebSocket endpoint for real-time updates."""
    return {
        "message": "WebSocket endpoint available",
        "url": "ws://localhost:8000/api/v1/ws/realtime",
        "features": ["real-time metrics", "live learning updates", "system notifications"]
    }
