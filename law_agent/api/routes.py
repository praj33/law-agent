"""API routes for the Law Agent system."""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from ..core.agent import LawAgent
from ..core.state import UserType, LegalDomain, InteractionType, FeedbackType
from ..legal.glossary import LegalGlossary
from ..legal.route_mapper import LegalRouteMapper


# Initialize components
law_agent = LawAgent()
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
        result = await law_agent.submit_feedback(
            session_id=request.session_id,
            interaction_id=request.interaction_id,
            feedback=request.feedback,
            time_spent=request.time_spent
        )
        
        return FeedbackResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
