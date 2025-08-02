#!/usr/bin/env python3
"""
Analytics Database Schema and Management
Advanced database design for Law Agent analytics
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsDatabase:
    """Advanced analytics database manager"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
        logger.info(f"Analytics database initialized: {db_path}")

    def _initialize_database(self):
        """Initialize database with comprehensive schema"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Enable dict-like access
        
        # Create all tables
        self._create_tables()
        self._create_indexes()
        self._create_views()
        
        logger.info("Database schema created successfully")

    def _create_tables(self):
        """Create all analytics tables"""
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_sessions INTEGER DEFAULT 0,
                total_queries INTEGER DEFAULT 0,
                user_type TEXT DEFAULT 'anonymous',
                preferences TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_seconds REAL,
                page_views INTEGER DEFAULT 0,
                events_count INTEGER DEFAULT 0,
                user_agent TEXT,
                ip_address TEXT,
                referrer TEXT,
                context TEXT,  -- JSON
                summary TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                event_type TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                page_url TEXT,
                user_agent TEXT,
                ip_address TEXT,
                response_time_ms REAL,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                legal_domain TEXT,
                legal_complexity TEXT,
                confidence_score REAL,
                data TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Legal Routes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS legal_routes (
                route_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                route_type TEXT NOT NULL,
                route_description TEXT NOT NULL,
                suggested_at TIMESTAMP NOT NULL,
                user_response TEXT,  -- accepted, rejected, ignored
                response_time_seconds REAL,
                follow_up_actions TEXT,  -- JSON array
                success_outcome BOOLEAN,
                user_satisfaction INTEGER,  -- 1-5 scale
                legal_domain TEXT,
                complexity_level TEXT,
                confidence_score REAL,
                context TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Glossary Access table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS glossary_access (
                access_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                term TEXT NOT NULL,
                definition TEXT,
                access_method TEXT NOT NULL,  -- search, click, hover, voice
                context TEXT,  -- where accessed from
                timestamp TIMESTAMP NOT NULL,
                time_spent_seconds REAL,
                helpful_rating INTEGER,  -- 1-5 scale
                related_terms_accessed TEXT,  -- JSON array
                search_query TEXT,  -- if accessed via search
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Timeline Interactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS timeline_interactions (
                interaction_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                timeline_type TEXT NOT NULL,
                step_id TEXT NOT NULL,
                step_name TEXT NOT NULL,
                interaction_type TEXT NOT NULL,  -- view, click, hover
                timestamp TIMESTAMP NOT NULL,
                estimated_duration TEXT,
                actual_duration TEXT,
                completion_status TEXT,  -- pending, in_progress, completed, delayed
                user_notes TEXT,
                time_spent_seconds REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Performance Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                metric_id TEXT PRIMARY KEY,
                session_id TEXT,
                timestamp TIMESTAMP NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT NOT NULL,
                component TEXT NOT NULL,
                threshold_status TEXT DEFAULT 'normal',  -- normal, warning, critical
                additional_data TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # Document Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_analytics (
                doc_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                document_name TEXT NOT NULL,
                document_type TEXT,
                file_size INTEGER,
                processing_time_seconds REAL,
                classification_confidence REAL,
                key_info_extracted TEXT,  -- JSON
                complexity_analysis TEXT,  -- JSON
                legal_advice_generated TEXT,  -- JSON
                user_feedback INTEGER,  -- 1-5 scale
                timestamp TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                feedback_type TEXT NOT NULL,  -- rating, comment, bug_report
                rating INTEGER,  -- 1-5 scale
                comment TEXT,
                category TEXT,  -- ui, functionality, accuracy, speed
                component TEXT,  -- which part of the system
                timestamp TIMESTAMP NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                resolution_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # A/B Testing table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ab_tests (
                test_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT,
                test_name TEXT NOT NULL,
                variant TEXT NOT NULL,  -- A, B, C, etc.
                timestamp TIMESTAMP NOT NULL,
                conversion BOOLEAN DEFAULT FALSE,
                conversion_value REAL,
                additional_metrics TEXT,  -- JSON
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        self.connection.commit()

    def _create_indexes(self):
        """Create database indexes for performance"""
        cursor = self.connection.cursor()
        
        # Primary indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_events_session_id ON events (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_events_type ON events (event_type)",
            "CREATE INDEX IF NOT EXISTS idx_events_user_id ON events (user_id)",
            
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions (start_time)",
            
            "CREATE INDEX IF NOT EXISTS idx_legal_routes_session_id ON legal_routes (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_legal_routes_type ON legal_routes (route_type)",
            "CREATE INDEX IF NOT EXISTS idx_legal_routes_response ON legal_routes (user_response)",
            "CREATE INDEX IF NOT EXISTS idx_legal_routes_suggested_at ON legal_routes (suggested_at)",
            
            "CREATE INDEX IF NOT EXISTS idx_glossary_term ON glossary_access (term)",
            "CREATE INDEX IF NOT EXISTS idx_glossary_session_id ON glossary_access (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_glossary_timestamp ON glossary_access (timestamp)",
            
            "CREATE INDEX IF NOT EXISTS idx_timeline_session_id ON timeline_interactions (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_timeline_type ON timeline_interactions (timeline_type)",
            "CREATE INDEX IF NOT EXISTS idx_timeline_timestamp ON timeline_interactions (timestamp)",
            
            "CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_performance_component ON performance_metrics (component)",
            "CREATE INDEX IF NOT EXISTS idx_performance_status ON performance_metrics (threshold_status)",
            
            "CREATE INDEX IF NOT EXISTS idx_documents_session_id ON document_analytics (session_id)",
            "CREATE INDEX IF NOT EXISTS idx_documents_type ON document_analytics (document_type)",
            "CREATE INDEX IF NOT EXISTS idx_documents_timestamp ON document_analytics (timestamp)",
            
            "CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback (feedback_type)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_rating ON feedback (rating)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback (timestamp)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        self.connection.commit()

    def _create_views(self):
        """Create useful database views for analytics"""
        cursor = self.connection.cursor()
        
        # Legal Route Success Rate View
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS legal_route_success_rate AS
            SELECT 
                route_type,
                COUNT(*) as total_suggestions,
                COUNT(CASE WHEN user_response = 'accepted' THEN 1 END) as accepted,
                COUNT(CASE WHEN user_response = 'rejected' THEN 1 END) as rejected,
                COUNT(CASE WHEN user_response IS NULL THEN 1 END) as ignored,
                ROUND(COUNT(CASE WHEN user_response = 'accepted' THEN 1 END) * 100.0 / COUNT(*), 2) as acceptance_rate,
                AVG(response_time_seconds) as avg_response_time,
                AVG(user_satisfaction) as avg_satisfaction
            FROM legal_routes
            GROUP BY route_type
        """)
        
        # Popular Glossary Terms View
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS popular_glossary_terms AS
            SELECT 
                term,
                COUNT(*) as access_count,
                COUNT(DISTINCT session_id) as unique_sessions,
                AVG(time_spent_seconds) as avg_time_spent,
                AVG(helpful_rating) as avg_rating,
                access_method,
                MAX(timestamp) as last_accessed
            FROM glossary_access
            GROUP BY term, access_method
            ORDER BY access_count DESC
        """)
        
        # Timeline Completion Analysis View
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS timeline_completion_analysis AS
            SELECT 
                timeline_type,
                step_name,
                COUNT(*) as total_interactions,
                COUNT(CASE WHEN completion_status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN completion_status = 'delayed' THEN 1 END) as delayed,
                ROUND(COUNT(CASE WHEN completion_status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) as completion_rate,
                AVG(time_spent_seconds) as avg_time_spent
            FROM timeline_interactions
            GROUP BY timeline_type, step_name
        """)
        
        # Daily Analytics Summary View
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS daily_analytics_summary AS
            SELECT 
                DATE(timestamp) as date,
                COUNT(DISTINCT session_id) as unique_sessions,
                COUNT(*) as total_events,
                COUNT(CASE WHEN event_type = 'legal_query' THEN 1 END) as legal_queries,
                COUNT(CASE WHEN event_type = 'glossary_term_accessed' THEN 1 END) as glossary_accesses,
                COUNT(CASE WHEN event_type = 'document_uploaded' THEN 1 END) as document_uploads,
                AVG(response_time_ms) as avg_response_time
            FROM events
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
        """)
        
        # User Engagement Metrics View
        cursor.execute("""
            CREATE VIEW IF NOT EXISTS user_engagement_metrics AS
            SELECT 
                user_id,
                COUNT(DISTINCT session_id) as total_sessions,
                AVG(duration_seconds) as avg_session_duration,
                SUM(events_count) as total_events,
                MAX(start_time) as last_activity,
                MIN(start_time) as first_activity,
                ROUND(julianday(MAX(start_time)) - julianday(MIN(start_time)), 1) as days_active
            FROM sessions
            WHERE user_id IS NOT NULL
            GROUP BY user_id
        """)
        
        self.connection.commit()

    def insert_event(self, event_data: Dict[str, Any]) -> bool:
        """Insert analytics event into database"""
        try:
            cursor = self.connection.cursor()
            
            # Convert data dict to JSON string
            data_json = json.dumps(event_data.get('data', {}))
            
            cursor.execute("""
                INSERT INTO events (
                    event_id, session_id, user_id, event_type, timestamp,
                    page_url, user_agent, ip_address, response_time_ms,
                    success, error_message, legal_domain, legal_complexity,
                    confidence_score, data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_data.get('event_id'),
                event_data.get('session_id'),
                event_data.get('user_id'),
                event_data.get('event_type'),
                event_data.get('timestamp'),
                event_data.get('page_url', ''),
                event_data.get('user_agent', ''),
                event_data.get('ip_address', ''),
                event_data.get('response_time_ms'),
                event_data.get('success', True),
                event_data.get('error_message'),
                event_data.get('legal_domain'),
                event_data.get('legal_complexity'),
                event_data.get('confidence_score'),
                data_json
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting event: {e}")
            return False

    def insert_legal_route(self, route_data: Dict[str, Any]) -> bool:
        """Insert legal route data into database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO legal_routes (
                    route_id, session_id, user_id, route_type, route_description,
                    suggested_at, user_response, response_time_seconds,
                    follow_up_actions, success_outcome, user_satisfaction,
                    legal_domain, complexity_level, confidence_score, context
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                route_data.get('route_id'),
                route_data.get('session_id'),
                route_data.get('user_id'),
                route_data.get('route_type'),
                route_data.get('route_description'),
                route_data.get('suggested_at'),
                route_data.get('user_response'),
                route_data.get('response_time_seconds'),
                json.dumps(route_data.get('follow_up_actions', [])),
                route_data.get('success_outcome'),
                route_data.get('user_satisfaction'),
                route_data.get('legal_domain'),
                route_data.get('complexity_level'),
                route_data.get('confidence_score'),
                json.dumps(route_data.get('context', {}))
            ))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error inserting legal route: {e}")
            return False

    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive analytics summary"""
        try:
            cursor = self.connection.cursor()
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Basic metrics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as unique_sessions,
                    COUNT(*) as total_events,
                    AVG(response_time_ms) as avg_response_time
                FROM events 
                WHERE timestamp >= ?
            """, (start_date,))
            
            basic_metrics = dict(cursor.fetchone())
            
            # Legal route metrics
            cursor.execute("""
                SELECT * FROM legal_route_success_rate
            """)
            
            legal_routes = [dict(row) for row in cursor.fetchall()]
            
            # Popular glossary terms
            cursor.execute("""
                SELECT * FROM popular_glossary_terms LIMIT 10
            """)
            
            popular_terms = [dict(row) for row in cursor.fetchall()]
            
            # Timeline completion
            cursor.execute("""
                SELECT * FROM timeline_completion_analysis
            """)
            
            timeline_analysis = [dict(row) for row in cursor.fetchall()]
            
            return {
                "period_days": days,
                "basic_metrics": basic_metrics,
                "legal_routes": legal_routes,
                "popular_glossary_terms": popular_terms,
                "timeline_analysis": timeline_analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary: {e}")
            return {}

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

# Global database instance
analytics_db = AnalyticsDatabase()
