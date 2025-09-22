#!/usr/bin/env python3
"""
Real-time Analytics API
FastAPI endpoints for Law Agent analytics collection and reporting
"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
import logging

# Import our analytics modules
from analytics_collector import analytics, EventType
from analytics_database import analytics_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Law Agent Analytics API",
    description="Real-time analytics collection and reporting for Law Agent",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Pydantic models for API
class SessionStartRequest(BaseModel):
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class EventTrackingRequest(BaseModel):
    event_type: str
    session_id: str
    user_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    page_url: Optional[str] = ""
    user_agent: Optional[str] = ""
    response_time_ms: Optional[float] = None

class LegalRouteRequest(BaseModel):
    session_id: str
    route_type: str
    route_description: str
    suggested_context: Optional[Dict[str, Any]] = None

class LegalRouteResponseRequest(BaseModel):
    session_id: str
    route_id: str
    user_response: str  # accepted, rejected, ignored
    response_time_seconds: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None

class GlossaryAccessRequest(BaseModel):
    session_id: str
    term: str
    definition: str
    access_method: str  # search, click, hover, voice
    context: Optional[str] = ""
    additional_data: Optional[Dict[str, Any]] = None

class TimelineInteractionRequest(BaseModel):
    session_id: str
    timeline_type: str
    step_id: str
    step_name: str
    interaction_type: str = "view"
    additional_data: Optional[Dict[str, Any]] = None

class FeedbackRequest(BaseModel):
    session_id: str
    feedback_type: str  # rating, comment, bug_report
    rating: Optional[int] = None
    comment: Optional[str] = None
    category: Optional[str] = None
    component: Optional[str] = None

class AnalyticsResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# API Endpoints

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Law Agent Analytics API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "sessions": "/sessions/*",
            "events": "/events/*",
            "legal_routes": "/legal-routes/*",
            "glossary": "/glossary/*",
            "timeline": "/timeline/*",
            "analytics": "/analytics/*",
            "dashboard": "/dashboard/*",
            "realtime": "/ws"
        }
    }

@app.post("/sessions/start", response_model=AnalyticsResponse)
async def start_session(request: SessionStartRequest):
    """Start a new analytics session"""
    try:
        session_id = analytics.start_session(
            user_id=request.user_id,
            context=request.context
        )
        
        # Broadcast session start to connected clients
        await manager.broadcast(json.dumps({
            "type": "session_start",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Session started successfully",
            data={"session_id": session_id}
        )
        
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/end", response_model=AnalyticsResponse)
async def end_session(session_id: str, summary_data: Optional[Dict[str, Any]] = None):
    """End an analytics session"""
    try:
        analytics.end_session(session_id, summary_data)
        
        # Broadcast session end
        await manager.broadcast(json.dumps({
            "type": "session_end",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Session ended successfully"
        )
        
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/events/track", response_model=AnalyticsResponse)
async def track_event(request: EventTrackingRequest, background_tasks: BackgroundTasks):
    """Track an analytics event"""
    try:
        # Convert string event type to enum
        try:
            event_type = EventType(request.event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {request.event_type}")
        
        event_id = analytics.track_event(
            event_type=event_type,
            session_id=request.session_id,
            user_id=request.user_id,
            data=request.data,
            page_url=request.page_url,
            user_agent=request.user_agent,
            response_time_ms=request.response_time_ms
        )
        
        # Store in database (background task)
        background_tasks.add_task(store_event_in_db, {
            "event_id": event_id,
            "event_type": request.event_type,
            "session_id": request.session_id,
            "user_id": request.user_id,
            "timestamp": datetime.now().isoformat(),
            "data": request.data,
            "page_url": request.page_url,
            "user_agent": request.user_agent,
            "response_time_ms": request.response_time_ms
        })
        
        # Broadcast real-time event
        await manager.broadcast(json.dumps({
            "type": "event",
            "event_type": request.event_type,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Event tracked successfully",
            data={"event_id": event_id}
        )
        
    except Exception as e:
        logger.error(f"Error tracking event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/legal-routes/suggest", response_model=AnalyticsResponse)
async def track_legal_route_suggestion(request: LegalRouteRequest):
    """Track legal route suggestion"""
    try:
        route_id = analytics.track_legal_route(
            session_id=request.session_id,
            route_type=request.route_type,
            route_description=request.route_description,
            suggested_context=request.suggested_context
        )
        
        # Broadcast legal route suggestion
        await manager.broadcast(json.dumps({
            "type": "legal_route_suggested",
            "route_id": route_id,
            "route_type": request.route_type,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Legal route suggestion tracked",
            data={"route_id": route_id}
        )
        
    except Exception as e:
        logger.error(f"Error tracking legal route: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/legal-routes/response", response_model=AnalyticsResponse)
async def track_legal_route_response(request: LegalRouteResponseRequest):
    """Track user response to legal route"""
    try:
        analytics.track_legal_route_response(
            session_id=request.session_id,
            route_id=request.route_id,
            user_response=request.user_response,
            response_time_seconds=request.response_time_seconds,
            additional_data=request.additional_data
        )
        
        # Broadcast legal route response
        await manager.broadcast(json.dumps({
            "type": "legal_route_response",
            "route_id": request.route_id,
            "user_response": request.user_response,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Legal route response tracked"
        )
        
    except Exception as e:
        logger.error(f"Error tracking legal route response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/glossary/access", response_model=AnalyticsResponse)
async def track_glossary_access(request: GlossaryAccessRequest):
    """Track glossary term access"""
    try:
        analytics.track_glossary_access(
            session_id=request.session_id,
            term=request.term,
            definition=request.definition,
            access_method=request.access_method,
            context=request.context,
            additional_data=request.additional_data
        )
        
        # Broadcast glossary access
        await manager.broadcast(json.dumps({
            "type": "glossary_access",
            "term": request.term,
            "access_method": request.access_method,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Glossary access tracked"
        )
        
    except Exception as e:
        logger.error(f"Error tracking glossary access: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/timeline/interaction", response_model=AnalyticsResponse)
async def track_timeline_interaction(request: TimelineInteractionRequest):
    """Track timeline interaction"""
    try:
        analytics.track_timeline_interaction(
            session_id=request.session_id,
            timeline_type=request.timeline_type,
            step_id=request.step_id,
            step_name=request.step_name,
            interaction_type=request.interaction_type,
            additional_data=request.additional_data
        )
        
        # Broadcast timeline interaction
        await manager.broadcast(json.dumps({
            "type": "timeline_interaction",
            "timeline_type": request.timeline_type,
            "step_name": request.step_name,
            "interaction_type": request.interaction_type,
            "session_id": request.session_id,
            "timestamp": datetime.now().isoformat()
        }))
        
        return AnalyticsResponse(
            success=True,
            message="Timeline interaction tracked"
        )
        
    except Exception as e:
        logger.error(f"Error tracking timeline interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/summary")
async def get_analytics_summary(days: int = 30):
    """Get comprehensive analytics summary"""
    try:
        summary = analytics_db.get_analytics_summary(days=days)
        
        return {
            "success": True,
            "data": summary
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/legal-routes")
async def get_legal_route_analytics():
    """Get legal route performance analytics"""
    try:
        cursor = analytics_db.connection.cursor()
        cursor.execute("SELECT * FROM legal_route_success_rate")
        routes = [dict(row) for row in cursor.fetchall()]
        
        return {
            "success": True,
            "data": routes
        }
        
    except Exception as e:
        logger.error(f"Error getting legal route analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/glossary")
async def get_glossary_analytics():
    """Get glossary usage analytics"""
    try:
        cursor = analytics_db.connection.cursor()
        cursor.execute("SELECT * FROM popular_glossary_terms LIMIT 50")
        terms = [dict(row) for row in cursor.fetchall()]
        
        return {
            "success": True,
            "data": terms
        }
        
    except Exception as e:
        logger.error(f"Error getting glossary analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/timeline")
async def get_timeline_analytics():
    """Get timeline completion analytics"""
    try:
        cursor = analytics_db.connection.cursor()
        cursor.execute("SELECT * FROM timeline_completion_analysis")
        timeline_data = [dict(row) for row in cursor.fetchall()]
        
        return {
            "success": True,
            "data": timeline_data
        }
        
    except Exception as e:
        logger.error(f"Error getting timeline analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time analytics"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - can be extended for bidirectional communication
            await manager.send_personal_message(f"Received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Background tasks
async def store_event_in_db(event_data: Dict[str, Any]):
    """Store event in database (background task)"""
    try:
        analytics_db.insert_event(event_data)
    except Exception as e:
        logger.error(f"Error storing event in database: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
