#!/usr/bin/env python3
"""
Advanced Analytics Data Collection System
Comprehensive tracking for Law Agent interactions and performance
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Analytics event types"""
    USER_SESSION_START = "user_session_start"
    USER_SESSION_END = "user_session_end"
    LEGAL_QUERY = "legal_query"
    LEGAL_ROUTE_SUGGESTED = "legal_route_suggested"
    LEGAL_ROUTE_ACCEPTED = "legal_route_accepted"
    LEGAL_ROUTE_REJECTED = "legal_route_rejected"
    GLOSSARY_TERM_ACCESSED = "glossary_term_accessed"
    GLOSSARY_TERM_SEARCHED = "glossary_term_searched"
    TIMELINE_VIEWED = "timeline_viewed"
    TIMELINE_STEP_CLICKED = "timeline_step_clicked"
    DOCUMENT_UPLOADED = "document_uploaded"
    DOCUMENT_ANALYZED = "document_analyzed"
    COURT_SECTION_VISITED = "court_section_visited"
    AVATAR_INTERACTION = "avatar_interaction"
    CHAT_MESSAGE_SENT = "chat_message_sent"
    CHAT_RESPONSE_RECEIVED = "chat_response_received"
    FEEDBACK_PROVIDED = "feedback_provided"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"

class UserAction(Enum):
    """User action types"""
    CLICK = "click"
    HOVER = "hover"
    SCROLL = "scroll"
    TYPE = "type"
    DRAG = "drag"
    VOICE = "voice"
    TOUCH = "touch"

@dataclass
class AnalyticsEvent:
    """Analytics event data structure"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    session_id: str
    user_id: Optional[str] = None
    
    # Event-specific data
    data: Dict[str, Any] = None
    
    # Context information
    page_url: str = ""
    user_agent: str = ""
    ip_address: str = ""
    
    # Performance metrics
    response_time_ms: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # Legal-specific fields
    legal_domain: Optional[str] = None
    legal_complexity: Optional[str] = None
    confidence_score: Optional[float] = None

@dataclass
class LegalRouteEvent:
    """Legal route tracking event"""
    route_id: str
    route_type: str
    route_description: str
    suggested_at: datetime
    user_response: Optional[str] = None  # accepted, rejected, ignored
    response_time_seconds: Optional[float] = None
    follow_up_actions: List[str] = None
    success_outcome: Optional[bool] = None
    user_satisfaction: Optional[int] = None  # 1-5 scale

@dataclass
class GlossaryEvent:
    """Glossary access tracking event"""
    term: str
    definition: str
    access_method: str  # search, click, hover, voice
    context: str  # where the term was accessed from
    time_spent_seconds: Optional[float] = None
    helpful_rating: Optional[int] = None  # 1-5 scale
    related_terms_accessed: List[str] = None

@dataclass
class TimelineEvent:
    """Timeline interaction tracking"""
    timeline_type: str  # case_timeline, legal_process, etc.
    step_id: str
    step_name: str
    estimated_duration: Optional[str] = None
    actual_duration: Optional[str] = None
    completion_status: Optional[str] = None  # pending, in_progress, completed, delayed
    user_notes: Optional[str] = None

@dataclass
class PerformanceMetric:
    """Performance tracking metrics"""
    metric_name: str
    metric_value: float
    metric_unit: str
    component: str  # which part of the system
    threshold_status: str  # normal, warning, critical

class AnalyticsCollector:
    """Advanced analytics data collector"""
    
    def __init__(self, storage_path: str = "analytics_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Create subdirectories for different data types
        (self.storage_path / "events").mkdir(exist_ok=True)
        (self.storage_path / "sessions").mkdir(exist_ok=True)
        (self.storage_path / "legal_routes").mkdir(exist_ok=True)
        (self.storage_path / "glossary").mkdir(exist_ok=True)
        (self.storage_path / "timelines").mkdir(exist_ok=True)
        (self.storage_path / "performance").mkdir(exist_ok=True)
        
        # Active sessions tracking
        self.active_sessions = {}
        
        # Event buffers for batch processing
        self.event_buffer = []
        self.buffer_size = 100
        
        logger.info(f"Analytics collector initialized with storage: {self.storage_path}")

    def generate_event_id(self) -> str:
        """Generate unique event ID"""
        return f"evt_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"

    def generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"sess_{int(time.time())}_{uuid.uuid4().hex[:12]}"

    def start_session(self, user_id: Optional[str] = None, context: Dict[str, Any] = None) -> str:
        """Start a new user session"""
        session_id = self.generate_session_id()
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "start_time": datetime.now().isoformat(),
            "context": context or {},
            "events": [],
            "legal_routes": [],
            "glossary_accesses": [],
            "timeline_interactions": [],
            "performance_metrics": []
        }
        
        self.active_sessions[session_id] = session_data
        
        # Track session start event
        self.track_event(
            event_type=EventType.USER_SESSION_START,
            session_id=session_id,
            user_id=user_id,
            data={"context": context}
        )
        
        logger.info(f"Started session: {session_id}")
        return session_id

    def end_session(self, session_id: str, summary_data: Dict[str, Any] = None):
        """End a user session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session not found: {session_id}")
            return
        
        session_data = self.active_sessions[session_id]
        session_data["end_time"] = datetime.now().isoformat()
        session_data["summary"] = summary_data or {}
        
        # Calculate session duration
        start_time = datetime.fromisoformat(session_data["start_time"])
        end_time = datetime.fromisoformat(session_data["end_time"])
        session_data["duration_seconds"] = (end_time - start_time).total_seconds()
        
        # Track session end event
        self.track_event(
            event_type=EventType.USER_SESSION_END,
            session_id=session_id,
            data={
                "duration_seconds": session_data["duration_seconds"],
                "summary": summary_data
            }
        )
        
        # Save session data
        self._save_session_data(session_id, session_data)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Ended session: {session_id}")

    def track_event(self, 
                   event_type: EventType, 
                   session_id: str,
                   user_id: Optional[str] = None,
                   data: Dict[str, Any] = None,
                   **kwargs) -> str:
        """Track a general analytics event"""
        
        event = AnalyticsEvent(
            event_id=self.generate_event_id(),
            event_type=event_type,
            timestamp=datetime.now(),
            session_id=session_id,
            user_id=user_id,
            data=data or {},
            **kwargs
        )
        
        # Add to session if active
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["events"].append(asdict(event))
        
        # Add to buffer
        self.event_buffer.append(event)
        
        # Flush buffer if full
        if len(self.event_buffer) >= self.buffer_size:
            self._flush_event_buffer()
        
        logger.debug(f"Tracked event: {event_type.value} for session {session_id}")
        return event.event_id

    def track_legal_route(self, 
                         session_id: str,
                         route_type: str,
                         route_description: str,
                         suggested_context: Dict[str, Any] = None) -> str:
        """Track legal route suggestion"""
        
        route_id = f"route_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        route_event = LegalRouteEvent(
            route_id=route_id,
            route_type=route_type,
            route_description=route_description,
            suggested_at=datetime.now()
        )
        
        # Track the suggestion event
        self.track_event(
            event_type=EventType.LEGAL_ROUTE_SUGGESTED,
            session_id=session_id,
            data={
                "route_id": route_id,
                "route_type": route_type,
                "route_description": route_description,
                "context": suggested_context or {}
            }
        )
        
        # Add to session
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["legal_routes"].append(asdict(route_event))
        
        logger.info(f"Tracked legal route suggestion: {route_id}")
        return route_id

    def track_legal_route_response(self, 
                                  session_id: str,
                                  route_id: str,
                                  user_response: str,
                                  response_time_seconds: float = None,
                                  additional_data: Dict[str, Any] = None):
        """Track user response to legal route"""
        
        # Update route event in session
        if session_id in self.active_sessions:
            for route in self.active_sessions[session_id]["legal_routes"]:
                if route["route_id"] == route_id:
                    route["user_response"] = user_response
                    route["response_time_seconds"] = response_time_seconds
                    break
        
        # Track response event
        event_type = (EventType.LEGAL_ROUTE_ACCEPTED if user_response == "accepted" 
                     else EventType.LEGAL_ROUTE_REJECTED)
        
        self.track_event(
            event_type=event_type,
            session_id=session_id,
            data={
                "route_id": route_id,
                "user_response": user_response,
                "response_time_seconds": response_time_seconds,
                **(additional_data or {})
            }
        )
        
        logger.info(f"Tracked legal route response: {route_id} -> {user_response}")

    def track_glossary_access(self, 
                             session_id: str,
                             term: str,
                             definition: str,
                             access_method: str,
                             context: str = "",
                             additional_data: Dict[str, Any] = None):
        """Track glossary term access"""
        
        glossary_event = GlossaryEvent(
            term=term,
            definition=definition,
            access_method=access_method,
            context=context
        )
        
        # Track the access event
        self.track_event(
            event_type=EventType.GLOSSARY_TERM_ACCESSED,
            session_id=session_id,
            data={
                "term": term,
                "access_method": access_method,
                "context": context,
                **(additional_data or {})
            }
        )
        
        # Add to session
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["glossary_accesses"].append(asdict(glossary_event))
        
        logger.info(f"Tracked glossary access: {term} via {access_method}")

    def track_timeline_interaction(self, 
                                  session_id: str,
                                  timeline_type: str,
                                  step_id: str,
                                  step_name: str,
                                  interaction_type: str = "view",
                                  additional_data: Dict[str, Any] = None):
        """Track timeline interaction"""
        
        timeline_event = TimelineEvent(
            timeline_type=timeline_type,
            step_id=step_id,
            step_name=step_name
        )
        
        # Track the interaction event
        event_type = (EventType.TIMELINE_STEP_CLICKED if interaction_type == "click" 
                     else EventType.TIMELINE_VIEWED)
        
        self.track_event(
            event_type=event_type,
            session_id=session_id,
            data={
                "timeline_type": timeline_type,
                "step_id": step_id,
                "step_name": step_name,
                "interaction_type": interaction_type,
                **(additional_data or {})
            }
        )
        
        # Add to session
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["timeline_interactions"].append(asdict(timeline_event))
        
        logger.info(f"Tracked timeline interaction: {step_name} ({interaction_type})")

    def track_performance_metric(self, 
                                session_id: str,
                                metric_name: str,
                                metric_value: float,
                                metric_unit: str,
                                component: str,
                                threshold_status: str = "normal"):
        """Track performance metrics"""
        
        performance_metric = PerformanceMetric(
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            component=component,
            threshold_status=threshold_status
        )
        
        # Track the performance event
        self.track_event(
            event_type=EventType.PERFORMANCE_METRIC,
            session_id=session_id,
            data=asdict(performance_metric)
        )
        
        # Add to session
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["performance_metrics"].append(asdict(performance_metric))
        
        logger.debug(f"Tracked performance metric: {metric_name} = {metric_value} {metric_unit}")

    def _flush_event_buffer(self):
        """Flush event buffer to storage"""
        if not self.event_buffer:
            return
        
        # Group events by date for efficient storage
        events_by_date = {}
        for event in self.event_buffer:
            date_key = event.timestamp.strftime("%Y-%m-%d")
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(asdict(event))
        
        # Save events to files
        for date_key, events in events_by_date.items():
            file_path = self.storage_path / "events" / f"events_{date_key}.json"
            
            # Load existing events if file exists
            existing_events = []
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        existing_events = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading existing events: {e}")
            
            # Append new events
            existing_events.extend(events)
            
            # Save back to file
            try:
                with open(file_path, 'w') as f:
                    json.dump(existing_events, f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving events: {e}")
        
        # Clear buffer
        self.event_buffer.clear()
        logger.debug(f"Flushed {len(self.event_buffer)} events to storage")

    def _save_session_data(self, session_id: str, session_data: Dict[str, Any]):
        """Save session data to storage"""
        file_path = self.storage_path / "sessions" / f"session_{session_id}.json"
        
        try:
            with open(file_path, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            logger.debug(f"Saved session data: {session_id}")
        except Exception as e:
            logger.error(f"Error saving session data: {e}")

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of session analytics"""
        if session_id not in self.active_sessions:
            # Try to load from storage
            file_path = self.storage_path / "sessions" / f"session_{session_id}.json"
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        session_data = json.load(f)
                except Exception as e:
                    logger.error(f"Error loading session data: {e}")
                    return {}
            else:
                return {}
        else:
            session_data = self.active_sessions[session_id]
        
        # Calculate summary statistics
        summary = {
            "session_id": session_id,
            "total_events": len(session_data.get("events", [])),
            "legal_routes_suggested": len(session_data.get("legal_routes", [])),
            "legal_routes_accepted": len([r for r in session_data.get("legal_routes", []) 
                                        if r.get("user_response") == "accepted"]),
            "glossary_terms_accessed": len(session_data.get("glossary_accesses", [])),
            "timeline_interactions": len(session_data.get("timeline_interactions", [])),
            "performance_metrics": len(session_data.get("performance_metrics", []))
        }
        
        return summary

# Global analytics collector instance
analytics = AnalyticsCollector()
