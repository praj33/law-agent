#!/usr/bin/env python3
"""
Advanced Analytics Engine with ML Capabilities
Pattern recognition, predictive insights, and recommendation optimization
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
from pathlib import Path

# ML and analytics libraries
try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    import matplotlib.pyplot as plt
    import seaborn as sns
except ImportError:
    print("⚠️ ML libraries not installed. Install with: pip install scikit-learn matplotlib seaborn")

from analytics_database import analytics_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalyticsInsight:
    """Analytics insight data structure"""
    insight_id: str
    insight_type: str  # pattern, prediction, recommendation, anomaly
    title: str
    description: str
    confidence: float  # 0-1
    impact_level: str  # low, medium, high, critical
    data: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime

@dataclass
class UserBehaviorPattern:
    """User behavior pattern analysis"""
    pattern_id: str
    pattern_type: str
    user_segment: str
    characteristics: Dict[str, Any]
    frequency: int
    success_rate: float
    recommendations: List[str]

@dataclass
class PredictiveModel:
    """Predictive model results"""
    model_name: str
    model_type: str
    accuracy: float
    predictions: List[Dict[str, Any]]
    feature_importance: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]

class AdvancedAnalyticsEngine:
    """Advanced analytics engine with ML capabilities"""
    
    def __init__(self):
        self.insights_cache = {}
        self.models = {}
        self.patterns = {}
        
        # Initialize ML models
        self._initialize_models()
        
        logger.info("Advanced Analytics Engine initialized")

    def _initialize_models(self):
        """Initialize ML models"""
        try:
            # User behavior clustering model
            self.models['user_clustering'] = KMeans(n_clusters=5, random_state=42)
            
            # Legal route success prediction model
            self.models['route_success'] = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Glossary term recommendation model
            self.models['term_recommendation'] = RandomForestClassifier(n_estimators=50, random_state=42)
            
            # Timeline completion prediction
            self.models['timeline_prediction'] = RandomForestClassifier(n_estimators=75, random_state=42)
            
            logger.info("ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")

    def analyze_user_behavior_patterns(self) -> List[UserBehaviorPattern]:
        """Analyze user behavior patterns using clustering"""
        try:
            # Get user session data
            cursor = analytics_db.connection.cursor()
            cursor.execute("""
                SELECT 
                    user_id,
                    COUNT(DISTINCT session_id) as session_count,
                    AVG(duration_seconds) as avg_session_duration,
                    SUM(events_count) as total_events,
                    COUNT(CASE WHEN summary LIKE '%successful%' THEN 1 END) as successful_sessions
                FROM sessions 
                WHERE user_id IS NOT NULL 
                GROUP BY user_id
                HAVING session_count >= 2
            """)
            
            user_data = pd.DataFrame(cursor.fetchall(), columns=[
                'user_id', 'session_count', 'avg_session_duration', 
                'total_events', 'successful_sessions'
            ])
            
            if len(user_data) < 5:
                return []
            
            # Prepare features for clustering
            features = ['session_count', 'avg_session_duration', 'total_events', 'successful_sessions']
            X = user_data[features].fillna(0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform clustering
            clusters = self.models['user_clustering'].fit_predict(X_scaled)
            user_data['cluster'] = clusters
            
            # Analyze patterns for each cluster
            patterns = []
            for cluster_id in range(5):
                cluster_data = user_data[user_data['cluster'] == cluster_id]
                
                if len(cluster_data) == 0:
                    continue
                
                # Calculate cluster characteristics
                characteristics = {
                    'avg_sessions': float(cluster_data['session_count'].mean()),
                    'avg_duration': float(cluster_data['avg_session_duration'].mean()),
                    'avg_events': float(cluster_data['total_events'].mean()),
                    'success_rate': float(cluster_data['successful_sessions'].sum() / cluster_data['session_count'].sum())
                }
                
                # Determine user segment
                if characteristics['avg_sessions'] > 10 and characteristics['success_rate'] > 0.8:
                    segment = "Power Users"
                elif characteristics['avg_sessions'] > 5 and characteristics['success_rate'] > 0.6:
                    segment = "Regular Users"
                elif characteristics['avg_sessions'] < 3:
                    segment = "New Users"
                elif characteristics['success_rate'] < 0.4:
                    segment = "Struggling Users"
                else:
                    segment = "Casual Users"
                
                # Generate recommendations
                recommendations = self._generate_segment_recommendations(segment, characteristics)
                
                pattern = UserBehaviorPattern(
                    pattern_id=f"pattern_{cluster_id}",
                    pattern_type="user_clustering",
                    user_segment=segment,
                    characteristics=characteristics,
                    frequency=len(cluster_data),
                    success_rate=characteristics['success_rate'],
                    recommendations=recommendations
                )
                
                patterns.append(pattern)
            
            logger.info(f"Identified {len(patterns)} user behavior patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior patterns: {e}")
            return []

    def _generate_segment_recommendations(self, segment: str, characteristics: Dict[str, Any]) -> List[str]:
        """Generate recommendations for user segments"""
        recommendations = []
        
        if segment == "Power Users":
            recommendations.extend([
                "Provide advanced features and shortcuts",
                "Offer beta access to new functionality",
                "Create power user community features"
            ])
        elif segment == "Regular Users":
            recommendations.extend([
                "Enhance user experience with personalization",
                "Provide intermediate-level tutorials",
                "Implement loyalty rewards"
            ])
        elif segment == "New Users":
            recommendations.extend([
                "Improve onboarding experience",
                "Provide guided tutorials",
                "Simplify initial user interface"
            ])
        elif segment == "Struggling Users":
            recommendations.extend([
                "Implement proactive help system",
                "Provide additional support resources",
                "Simplify complex workflows"
            ])
        else:  # Casual Users
            recommendations.extend([
                "Send engagement reminders",
                "Highlight key features",
                "Provide quick-start guides"
            ])
        
        return recommendations

    def predict_legal_route_success(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict legal route success probability"""
        try:
            # Get historical legal route data
            cursor = analytics_db.connection.cursor()
            cursor.execute("""
                SELECT 
                    route_type,
                    legal_domain,
                    complexity_level,
                    confidence_score,
                    response_time_seconds,
                    CASE WHEN user_response = 'accepted' THEN 1 ELSE 0 END as success
                FROM legal_routes 
                WHERE user_response IS NOT NULL
            """)
            
            historical_data = pd.DataFrame(cursor.fetchall(), columns=[
                'route_type', 'legal_domain', 'complexity_level', 
                'confidence_score', 'response_time_seconds', 'success'
            ])
            
            if len(historical_data) < 10:
                return {"error": "Insufficient historical data for prediction"}
            
            # Prepare features
            features = pd.get_dummies(historical_data[['route_type', 'legal_domain', 'complexity_level']])
            features['confidence_score'] = historical_data['confidence_score'].fillna(0.5)
            features['response_time_seconds'] = historical_data['response_time_seconds'].fillna(30)
            
            y = historical_data['success']
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42)
            self.models['route_success'].fit(X_train, y_train)
            
            # Calculate accuracy
            y_pred = self.models['route_success'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Prepare prediction data
            pred_features = pd.get_dummies(pd.DataFrame([route_data]))[features.columns].fillna(0)
            
            # Make prediction
            success_probability = self.models['route_success'].predict_proba(pred_features)[0][1]
            
            # Get feature importance
            feature_importance = dict(zip(features.columns, self.models['route_success'].feature_importances_))
            
            return {
                "success_probability": float(success_probability),
                "model_accuracy": float(accuracy),
                "feature_importance": feature_importance,
                "recommendation": "high_confidence" if success_probability > 0.7 else "review_needed"
            }
            
        except Exception as e:
            logger.error(f"Error predicting legal route success: {e}")
            return {"error": str(e)}

    def analyze_glossary_usage_trends(self) -> Dict[str, Any]:
        """Analyze glossary usage trends and patterns"""
        try:
            cursor = analytics_db.connection.cursor()
            cursor.execute("""
                SELECT 
                    term,
                    access_method,
                    context,
                    DATE(timestamp) as date,
                    COUNT(*) as daily_count,
                    AVG(time_spent_seconds) as avg_time_spent,
                    AVG(helpful_rating) as avg_rating
                FROM glossary_access 
                WHERE timestamp >= date('now', '-30 days')
                GROUP BY term, access_method, context, DATE(timestamp)
                ORDER BY date DESC
            """)
            
            glossary_data = pd.DataFrame(cursor.fetchall(), columns=[
                'term', 'access_method', 'context', 'date', 
                'daily_count', 'avg_time_spent', 'avg_rating'
            ])
            
            if len(glossary_data) == 0:
                return {"error": "No glossary data available"}
            
            # Analyze trends
            trends = {
                "most_accessed_terms": glossary_data.groupby('term')['daily_count'].sum().nlargest(10).to_dict(),
                "preferred_access_methods": glossary_data.groupby('access_method')['daily_count'].sum().to_dict(),
                "context_analysis": glossary_data.groupby('context')['daily_count'].sum().to_dict(),
                "engagement_metrics": {
                    "avg_time_spent": float(glossary_data['avg_time_spent'].mean()),
                    "avg_rating": float(glossary_data['avg_rating'].mean()),
                    "total_accesses": int(glossary_data['daily_count'].sum())
                }
            }
            
            # Identify patterns
            patterns = []
            
            # Terms with declining usage
            declining_terms = glossary_data.groupby('term').apply(
                lambda x: x.sort_values('date')['daily_count'].diff().mean()
            ).sort_values().head(5)
            
            if len(declining_terms) > 0:
                patterns.append({
                    "type": "declining_usage",
                    "terms": declining_terms.to_dict(),
                    "recommendation": "Review and update definitions for declining terms"
                })
            
            # High engagement terms
            high_engagement = glossary_data[glossary_data['avg_rating'] > 4.0]['term'].unique()
            if len(high_engagement) > 0:
                patterns.append({
                    "type": "high_engagement",
                    "terms": high_engagement.tolist(),
                    "recommendation": "Use these terms as examples for improving other definitions"
                })
            
            trends["patterns"] = patterns
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing glossary trends: {e}")
            return {"error": str(e)}

    def predict_timeline_completion(self, timeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict timeline completion probability and duration"""
        try:
            cursor = analytics_db.connection.cursor()
            cursor.execute("""
                SELECT 
                    timeline_type,
                    step_name,
                    interaction_type,
                    time_spent_seconds,
                    CASE WHEN completion_status = 'completed' THEN 1 ELSE 0 END as completed
                FROM timeline_interactions 
                WHERE completion_status IS NOT NULL
            """)
            
            timeline_hist = pd.DataFrame(cursor.fetchall(), columns=[
                'timeline_type', 'step_name', 'interaction_type', 
                'time_spent_seconds', 'completed'
            ])
            
            if len(timeline_hist) < 10:
                return {"error": "Insufficient timeline data for prediction"}
            
            # Feature engineering
            features = pd.get_dummies(timeline_hist[['timeline_type', 'step_name', 'interaction_type']])
            features['time_spent_seconds'] = timeline_hist['time_spent_seconds'].fillna(60)
            
            y = timeline_hist['completed']
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42)
            self.models['timeline_prediction'].fit(X_train, y_train)
            
            # Calculate accuracy
            y_pred = self.models['timeline_prediction'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Prepare prediction data
            pred_features = pd.get_dummies(pd.DataFrame([timeline_data]))[features.columns].fillna(0)
            
            # Make prediction
            completion_probability = self.models['timeline_prediction'].predict_proba(pred_features)[0][1]
            
            # Estimate completion time based on historical data
            similar_timelines = timeline_hist[
                (timeline_hist['timeline_type'] == timeline_data.get('timeline_type')) &
                (timeline_hist['completed'] == 1)
            ]
            
            estimated_duration = similar_timelines['time_spent_seconds'].median() if len(similar_timelines) > 0 else 300
            
            return {
                "completion_probability": float(completion_probability),
                "estimated_duration_seconds": float(estimated_duration),
                "model_accuracy": float(accuracy),
                "confidence_level": "high" if completion_probability > 0.8 else "medium" if completion_probability > 0.6 else "low"
            }
            
        except Exception as e:
            logger.error(f"Error predicting timeline completion: {e}")
            return {"error": str(e)}

    def detect_anomalies(self) -> List[AnalyticsInsight]:
        """Detect anomalies in user behavior and system performance"""
        insights = []
        
        try:
            # Detect unusual response times
            cursor = analytics_db.connection.cursor()
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    AVG(response_time_ms) as avg_response_time,
                    COUNT(*) as event_count
                FROM events 
                WHERE timestamp >= date('now', '-7 days')
                AND response_time_ms IS NOT NULL
                GROUP BY DATE(timestamp)
                ORDER BY date
            """)
            
            response_data = pd.DataFrame(cursor.fetchall(), columns=['date', 'avg_response_time', 'event_count'])
            
            if len(response_data) > 3:
                # Calculate z-scores for response times
                mean_response = response_data['avg_response_time'].mean()
                std_response = response_data['avg_response_time'].std()
                
                anomalous_days = response_data[
                    abs(response_data['avg_response_time'] - mean_response) > 2 * std_response
                ]
                
                if len(anomalous_days) > 0:
                    insight = AnalyticsInsight(
                        insight_id=f"anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        insight_type="anomaly",
                        title="Unusual Response Times Detected",
                        description=f"Detected {len(anomalous_days)} days with abnormal response times",
                        confidence=0.85,
                        impact_level="medium",
                        data={"anomalous_days": anomalous_days.to_dict('records')},
                        recommendations=[
                            "Investigate server performance on anomalous days",
                            "Check for high-traffic periods or system issues",
                            "Consider scaling resources during peak times"
                        ],
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            # Detect unusual user behavior patterns
            cursor.execute("""
                SELECT 
                    session_id,
                    events_count,
                    duration_seconds
                FROM sessions 
                WHERE start_time >= date('now', '-7 days')
                AND events_count > 0
            """)
            
            session_data = pd.DataFrame(cursor.fetchall(), columns=['session_id', 'events_count', 'duration_seconds'])
            
            if len(session_data) > 10:
                # Detect sessions with unusually high event counts
                event_threshold = session_data['events_count'].quantile(0.95)
                unusual_sessions = session_data[session_data['events_count'] > event_threshold]
                
                if len(unusual_sessions) > 0:
                    insight = AnalyticsInsight(
                        insight_id=f"anomaly_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        insight_type="anomaly",
                        title="Unusual User Activity Detected",
                        description=f"Found {len(unusual_sessions)} sessions with exceptionally high activity",
                        confidence=0.75,
                        impact_level="low",
                        data={"unusual_sessions": len(unusual_sessions), "threshold": float(event_threshold)},
                        recommendations=[
                            "Investigate high-activity sessions for potential bot behavior",
                            "Analyze user patterns to improve engagement",
                            "Consider implementing rate limiting if necessary"
                        ],
                        created_at=datetime.now()
                    )
                    insights.append(insight)
            
            logger.info(f"Detected {len(insights)} anomalies")
            return insights
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []

    def generate_optimization_recommendations(self) -> List[AnalyticsInsight]:
        """Generate optimization recommendations based on analytics"""
        recommendations = []
        
        try:
            # Analyze legal route performance
            cursor = analytics_db.connection.cursor()
            cursor.execute("SELECT * FROM legal_route_success_rate")
            route_performance = pd.DataFrame(cursor.fetchall())
            
            if len(route_performance) > 0:
                # Find underperforming routes
                low_acceptance = route_performance[route_performance['acceptance_rate'] < 50]
                
                if len(low_acceptance) > 0:
                    insight = AnalyticsInsight(
                        insight_id=f"opt_routes_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        insight_type="recommendation",
                        title="Legal Route Optimization Needed",
                        description=f"Found {len(low_acceptance)} legal routes with low acceptance rates",
                        confidence=0.9,
                        impact_level="high",
                        data={"underperforming_routes": low_acceptance.to_dict('records')},
                        recommendations=[
                            "Review and improve descriptions for low-acceptance routes",
                            "Analyze user feedback for rejected routes",
                            "Consider A/B testing different route presentations",
                            "Provide more context and examples for complex routes"
                        ],
                        created_at=datetime.now()
                    )
                    recommendations.append(insight)
            
            # Analyze glossary engagement
            cursor.execute("SELECT * FROM popular_glossary_terms LIMIT 20")
            glossary_terms = pd.DataFrame(cursor.fetchall())
            
            if len(glossary_terms) > 0:
                # Find terms with low ratings
                low_rated = glossary_terms[glossary_terms['avg_rating'] < 3.0]
                
                if len(low_rated) > 0:
                    insight = AnalyticsInsight(
                        insight_id=f"opt_glossary_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        insight_type="recommendation",
                        title="Glossary Content Improvement Needed",
                        description=f"Found {len(low_rated)} glossary terms with low user ratings",
                        confidence=0.8,
                        impact_level="medium",
                        data={"low_rated_terms": low_rated.to_dict('records')},
                        recommendations=[
                            "Rewrite definitions for low-rated terms",
                            "Add examples and context to improve clarity",
                            "Consider adding visual aids or diagrams",
                            "Gather user feedback on specific improvements needed"
                        ],
                        created_at=datetime.now()
                    )
                    recommendations.append(insight)
            
            logger.info(f"Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def get_comprehensive_insights(self) -> Dict[str, Any]:
        """Get comprehensive analytics insights"""
        try:
            insights = {
                "user_behavior_patterns": self.analyze_user_behavior_patterns(),
                "glossary_trends": self.analyze_glossary_usage_trends(),
                "anomalies": self.detect_anomalies(),
                "optimization_recommendations": self.generate_optimization_recommendations(),
                "generated_at": datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            return {"error": str(e)}

# Global analytics engine instance
analytics_engine = AdvancedAnalyticsEngine()
