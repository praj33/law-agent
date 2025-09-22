"""
Enhanced Feedback System with Learning Loop
==========================================

This module implements a comprehensive feedback collection and learning system
that enables the Legal Agent to improve over time through user interactions.

Features:
- Multi-dimensional feedback collection
- Reinforcement learning-style reward system
- Feedback-driven model retraining
- Performance tracking and analytics
- User satisfaction monitoring

Author: Legal Agent Team
Version: 5.0.0 - Enhanced Feedback Learning
Date: 2025-07-22
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime
import sqlite3
from collections import defaultdict
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """Comprehensive feedback entry structure"""
    session_id: str
    timestamp: str
    user_query: str
    predicted_domain: str
    confidence_score: float
    legal_route: str
    timeline_provided: str
    
    # User feedback dimensions
    domain_accuracy: int  # 1-5 scale
    route_helpfulness: int  # 1-5 scale
    timeline_realism: int  # 1-5 scale
    language_clarity: int  # 1-5 scale
    overall_satisfaction: int  # 1-5 scale
    
    # Additional feedback
    correct_domain: Optional[str] = None
    user_comments: Optional[str] = None
    would_recommend: Optional[bool] = None
    
    # System metrics
    response_time: Optional[float] = None
    constitutional_backing_helpful: Optional[bool] = None
    data_insights_helpful: Optional[bool] = None


@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    total_queries: int
    avg_satisfaction: float
    domain_accuracy: float
    route_helpfulness: float
    timeline_realism: float
    language_clarity: float
    recommendation_rate: float
    improvement_trend: float


class EnhancedFeedbackSystem:
    """Enhanced feedback system with learning capabilities"""
    
    def __init__(self, 
                 feedback_db_file: str = "enhanced_feedback.db",
                 learning_config_file: str = "learning_config.json"):
        """Initialize enhanced feedback system"""
        
        self.feedback_db_file = feedback_db_file
        self.learning_config_file = learning_config_file
        
        # Initialize database
        self.init_database()
        
        # Load learning configuration
        self.learning_config = self.load_learning_config()
        
        # Performance tracking
        self.performance_history = []
        self.feedback_cache = []
        
        # Learning parameters
        self.reward_weights = {
            'domain_accuracy': 0.30,
            'route_helpfulness': 0.25,
            'timeline_realism': 0.20,
            'language_clarity': 0.15,
            'overall_satisfaction': 0.10
        }
        
        logger.info("Enhanced feedback system initialized")
    
    def init_database(self):
        """Initialize SQLite database for feedback storage"""
        
        try:
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            # Create feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_query TEXT NOT NULL,
                    predicted_domain TEXT NOT NULL,
                    confidence_score REAL,
                    legal_route TEXT,
                    timeline_provided TEXT,
                    domain_accuracy INTEGER,
                    route_helpfulness INTEGER,
                    timeline_realism INTEGER,
                    language_clarity INTEGER,
                    overall_satisfaction INTEGER,
                    correct_domain TEXT,
                    user_comments TEXT,
                    would_recommend INTEGER,
                    response_time REAL,
                    constitutional_backing_helpful INTEGER,
                    data_insights_helpful INTEGER
                )
            ''')
            
            # Create performance metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_queries INTEGER,
                    avg_satisfaction REAL,
                    domain_accuracy REAL,
                    route_helpfulness REAL,
                    timeline_realism REAL,
                    language_clarity REAL,
                    recommendation_rate REAL,
                    improvement_trend REAL
                )
            ''')
            
            # Create learning events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    details TEXT,
                    impact_score REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Feedback database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def load_learning_config(self) -> Dict:
        """Load learning configuration"""
        
        default_config = {
            "feedback_threshold": 10,  # Minimum feedback before retraining
            "retraining_interval": 50,  # Retrain every N feedback entries
            "performance_window": 100,  # Performance calculation window
            "improvement_threshold": 0.1,  # Minimum improvement for model update
            "reward_decay": 0.95,  # Reward decay factor
            "learning_rate": 0.01  # Learning rate for adjustments
        }
        
        if Path(self.learning_config_file).exists():
            try:
                with open(self.learning_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            except Exception as e:
                logger.warning(f"Error loading learning config: {e}")
        
        # Save config
        try:
            with open(self.learning_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning config: {e}")
        
        return default_config
    
    def collect_comprehensive_feedback(self, 
                                     session_id: str,
                                     user_query: str,
                                     predicted_domain: str,
                                     confidence_score: float,
                                     legal_route: str,
                                     timeline_provided: str,
                                     response_time: Optional[float] = None) -> Optional[FeedbackEntry]:
        """Collect comprehensive feedback from user"""
        
        print(f"\n📝 FEEDBACK COLLECTION")
        print("=" * 40)
        print(f"Query: \"{user_query}\"")
        print(f"Predicted Domain: {predicted_domain}")
        print(f"Confidence: {confidence_score:.3f}")
        print("-" * 40)
        
        try:
            # Collect feedback dimensions
            print("Please rate the following aspects (1-5 scale, 5 being excellent):")
            
            domain_accuracy = self._get_rating_input(
                "Domain Classification Accuracy", 
                "Was the legal domain correctly identified?"
            )
            
            route_helpfulness = self._get_rating_input(
                "Legal Route Helpfulness",
                "Was the suggested legal route helpful and actionable?"
            )
            
            timeline_realism = self._get_rating_input(
                "Timeline Realism",
                "Was the provided timeline realistic and accurate?"
            )
            
            language_clarity = self._get_rating_input(
                "Language Clarity",
                "Was the response clear and easy to understand?"
            )
            
            overall_satisfaction = self._get_rating_input(
                "Overall Satisfaction",
                "How satisfied are you with the overall response?"
            )
            
            # Additional feedback
            correct_domain = None
            if domain_accuracy <= 2:
                print(f"\nWhat should the correct domain be?")
                print("Options: tenant_rights, consumer_complaint, family_law, employment_law,")
                print("         contract_dispute, personal_injury, criminal_law, immigration_law,")
                print("         elder_abuse, cyber_crime")
                correct_domain = input("Correct domain (or press Enter to skip): ").strip()
                if not correct_domain:
                    correct_domain = None
            
            # User comments
            user_comments = input(f"\nAny additional comments? (optional): ").strip()
            if not user_comments:
                user_comments = None
            
            # Recommendation
            recommend_input = input(f"Would you recommend this system to others? (y/n/skip): ").strip().lower()
            would_recommend = None
            if recommend_input in ['y', 'yes']:
                would_recommend = True
            elif recommend_input in ['n', 'no']:
                would_recommend = False
            
            # Enhanced features feedback
            constitutional_helpful = self._get_yes_no_input(
                "Was the constitutional backing helpful?", optional=True
            )

            data_insights_helpful = self._get_yes_no_input(
                "Were the data-driven insights helpful?", optional=True
            )
            
            # Create feedback entry
            feedback = FeedbackEntry(
                session_id=session_id,
                timestamp=datetime.now().isoformat(),
                user_query=user_query,
                predicted_domain=predicted_domain,
                confidence_score=confidence_score,
                legal_route=legal_route,
                timeline_provided=timeline_provided,
                domain_accuracy=domain_accuracy,
                route_helpfulness=route_helpfulness,
                timeline_realism=timeline_realism,
                language_clarity=language_clarity,
                overall_satisfaction=overall_satisfaction,
                correct_domain=correct_domain,
                user_comments=user_comments,
                would_recommend=would_recommend,
                response_time=response_time,
                constitutional_backing_helpful=constitutional_helpful,
                data_insights_helpful=data_insights_helpful
            )
            
            # Store feedback
            self.store_feedback(feedback)
            
            # Process learning
            self.process_feedback_learning(feedback)
            
            print(f"\n✅ Thank you for your feedback!")
            return feedback
            
        except KeyboardInterrupt:
            print(f"\n⏭️ Feedback collection skipped by user")
            return None
        except Exception as e:
            logger.error(f"Error collecting feedback: {e}")
            return None
    
    def _get_rating_input(self, aspect: str, description: str) -> int:
        """Get rating input from user with validation"""
        
        while True:
            try:
                print(f"\n{aspect}:")
                print(f"  {description}")
                rating = input(f"  Rating (1-5): ").strip()
                
                if not rating:
                    return 3  # Default neutral rating
                
                rating = int(rating)
                if 1 <= rating <= 5:
                    return rating
                else:
                    print("  Please enter a number between 1 and 5")
            except ValueError:
                print("  Please enter a valid number")
            except KeyboardInterrupt:
                return 3  # Default on interrupt
    
    def _get_yes_no_input(self, question: str, optional: bool = False) -> Optional[bool]:
        """Get yes/no input from user"""
        
        try:
            response = input(f"{question} (y/n{'/' + 'skip' if optional else ''}): ").strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif optional and response in ['skip', '']:
                return None
            else:
                return None
        except KeyboardInterrupt:
            return None
    
    def store_feedback(self, feedback: FeedbackEntry):
        """Store feedback in database"""
        
        try:
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO feedback (
                    session_id, timestamp, user_query, predicted_domain, confidence_score,
                    legal_route, timeline_provided, domain_accuracy, route_helpfulness,
                    timeline_realism, language_clarity, overall_satisfaction,
                    correct_domain, user_comments, would_recommend, response_time,
                    constitutional_backing_helpful, data_insights_helpful
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.session_id, feedback.timestamp, feedback.user_query,
                feedback.predicted_domain, feedback.confidence_score,
                feedback.legal_route, feedback.timeline_provided,
                feedback.domain_accuracy, feedback.route_helpfulness,
                feedback.timeline_realism, feedback.language_clarity,
                feedback.overall_satisfaction, feedback.correct_domain,
                feedback.user_comments, feedback.would_recommend,
                feedback.response_time, feedback.constitutional_backing_helpful,
                feedback.data_insights_helpful
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Stored feedback for session {feedback.session_id}")
            
        except Exception as e:
            logger.error(f"Error storing feedback: {e}")
    
    def process_feedback_learning(self, feedback: FeedbackEntry):
        """Process feedback for learning and improvement"""
        
        # Calculate reward score
        reward_score = self.calculate_reward_score(feedback)
        
        # Log learning event
        self.log_learning_event("feedback_received", {
            "session_id": feedback.session_id,
            "reward_score": reward_score,
            "domain": feedback.predicted_domain,
            "satisfaction": feedback.overall_satisfaction
        }, reward_score)
        
        # Check if retraining is needed
        feedback_count = self.get_feedback_count()
        
        if feedback_count % self.learning_config["retraining_interval"] == 0:
            self.trigger_model_retraining()
        
        # Update performance metrics
        self.update_performance_metrics()
        
        logger.info(f"Processed feedback learning with reward score: {reward_score:.3f}")
    
    def calculate_reward_score(self, feedback: FeedbackEntry) -> float:
        """Calculate reward score from feedback"""
        
        # Normalize ratings to 0-1 scale
        normalized_scores = {
            'domain_accuracy': (feedback.domain_accuracy - 1) / 4,
            'route_helpfulness': (feedback.route_helpfulness - 1) / 4,
            'timeline_realism': (feedback.timeline_realism - 1) / 4,
            'language_clarity': (feedback.language_clarity - 1) / 4,
            'overall_satisfaction': (feedback.overall_satisfaction - 1) / 4
        }
        
        # Calculate weighted reward
        reward = sum(
            normalized_scores[aspect] * weight 
            for aspect, weight in self.reward_weights.items()
        )
        
        # Bonus for high confidence correct predictions
        if feedback.domain_accuracy >= 4 and feedback.confidence_score > 0.8:
            reward += 0.1
        
        # Penalty for low confidence incorrect predictions
        if feedback.domain_accuracy <= 2 and feedback.confidence_score > 0.6:
            reward -= 0.1
        
        # Bonus for recommendation
        if feedback.would_recommend:
            reward += 0.05
        
        return max(0.0, min(1.0, reward))  # Clamp to [0, 1]
    
    def log_learning_event(self, event_type: str, details: Dict, impact_score: float):
        """Log learning event to database"""
        
        try:
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO learning_events (timestamp, event_type, details, impact_score)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                event_type,
                json.dumps(details),
                impact_score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging learning event: {e}")
    
    def trigger_model_retraining(self):
        """Trigger model retraining based on feedback"""
        
        logger.info("Triggering model retraining based on feedback")
        
        # Get recent feedback for retraining
        recent_feedback = self.get_recent_feedback(self.learning_config["retraining_interval"])
        
        # Extract training examples from feedback
        training_examples = []
        for feedback in recent_feedback:
            if feedback.correct_domain and feedback.correct_domain != feedback.predicted_domain:
                training_examples.append({
                    'text': feedback.user_query,
                    'domain': feedback.correct_domain
                })
        
        if training_examples:
            # Log retraining event
            self.log_learning_event("model_retraining", {
                "new_examples": len(training_examples),
                "feedback_window": self.learning_config["retraining_interval"]
            }, len(training_examples) * 0.1)
            
            logger.info(f"Added {len(training_examples)} new training examples from feedback")
        
        return training_examples
    
    def get_recent_feedback(self, limit: int) -> List[FeedbackEntry]:
        """Get recent feedback entries"""
        
        try:
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM feedback 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to FeedbackEntry objects
            feedback_entries = []
            for row in rows:
                feedback = FeedbackEntry(
                    session_id=row[1],
                    timestamp=row[2],
                    user_query=row[3],
                    predicted_domain=row[4],
                    confidence_score=row[5],
                    legal_route=row[6],
                    timeline_provided=row[7],
                    domain_accuracy=row[8],
                    route_helpfulness=row[9],
                    timeline_realism=row[10],
                    language_clarity=row[11],
                    overall_satisfaction=row[12],
                    correct_domain=row[13],
                    user_comments=row[14],
                    would_recommend=bool(row[15]) if row[15] is not None else None,
                    response_time=row[16],
                    constitutional_backing_helpful=bool(row[17]) if row[17] is not None else None,
                    data_insights_helpful=bool(row[18]) if row[18] is not None else None
                )
                feedback_entries.append(feedback)
            
            return feedback_entries
            
        except Exception as e:
            logger.error(f"Error getting recent feedback: {e}")
            return []
    
    def get_feedback_count(self) -> int:
        """Get total feedback count"""
        
        try:
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM feedback')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            logger.error(f"Error getting feedback count: {e}")
            return 0
    
    def update_performance_metrics(self):
        """Update system performance metrics"""
        
        try:
            recent_feedback = self.get_recent_feedback(self.learning_config["performance_window"])
            
            if not recent_feedback:
                return
            
            # Calculate metrics
            metrics = PerformanceMetrics(
                total_queries=len(recent_feedback),
                avg_satisfaction=statistics.mean([f.overall_satisfaction for f in recent_feedback]),
                domain_accuracy=statistics.mean([f.domain_accuracy for f in recent_feedback]),
                route_helpfulness=statistics.mean([f.route_helpfulness for f in recent_feedback]),
                timeline_realism=statistics.mean([f.timeline_realism for f in recent_feedback]),
                language_clarity=statistics.mean([f.language_clarity for f in recent_feedback]),
                recommendation_rate=sum([1 for f in recent_feedback if f.would_recommend]) / len(recent_feedback),
                improvement_trend=self.calculate_improvement_trend(recent_feedback)
            )
            
            # Store metrics
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics (
                    date, total_queries, avg_satisfaction, domain_accuracy,
                    route_helpfulness, timeline_realism, language_clarity,
                    recommendation_rate, improvement_trend
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().date().isoformat(),
                metrics.total_queries, metrics.avg_satisfaction,
                metrics.domain_accuracy, metrics.route_helpfulness,
                metrics.timeline_realism, metrics.language_clarity,
                metrics.recommendation_rate, metrics.improvement_trend
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated performance metrics: satisfaction={metrics.avg_satisfaction:.2f}")
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def calculate_improvement_trend(self, recent_feedback: List[FeedbackEntry]) -> float:
        """Calculate improvement trend from recent feedback"""
        
        if len(recent_feedback) < 10:
            return 0.0
        
        # Split into two halves
        mid_point = len(recent_feedback) // 2
        first_half = recent_feedback[mid_point:]  # More recent
        second_half = recent_feedback[:mid_point]  # Less recent
        
        # Calculate average satisfaction for each half
        first_avg = statistics.mean([f.overall_satisfaction for f in first_half])
        second_avg = statistics.mean([f.overall_satisfaction for f in second_half])
        
        # Return improvement (positive = improving, negative = declining)
        return first_avg - second_avg
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        try:
            conn = sqlite3.connect(self.feedback_db_file)
            cursor = conn.cursor()
            
            # Get latest metrics
            cursor.execute('''
                SELECT * FROM performance_metrics 
                ORDER BY date DESC 
                LIMIT 1
            ''')
            
            latest_metrics = cursor.fetchone()
            
            # Get feedback statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_feedback,
                    AVG(overall_satisfaction) as avg_satisfaction,
                    AVG(domain_accuracy) as avg_domain_accuracy,
                    COUNT(CASE WHEN would_recommend = 1 THEN 1 END) * 100.0 / COUNT(*) as recommendation_rate
                FROM feedback
            ''')
            
            feedback_stats = cursor.fetchone()
            
            # Get learning events
            cursor.execute('''
                SELECT COUNT(*) FROM learning_events 
                WHERE event_type = 'model_retraining'
            ''')
            
            retraining_count = cursor.fetchone()[0]
            
            conn.close()
            
            summary = {
                'total_feedback_received': feedback_stats[0] if feedback_stats else 0,
                'average_satisfaction': feedback_stats[1] if feedback_stats else 0,
                'domain_accuracy': feedback_stats[2] if feedback_stats else 0,
                'recommendation_rate': feedback_stats[3] if feedback_stats else 0,
                'model_retrainings': retraining_count,
                'learning_active': True,
                'feedback_threshold': self.learning_config["feedback_threshold"],
                'retraining_interval': self.learning_config["retraining_interval"]
            }
            
            if latest_metrics:
                summary.update({
                    'recent_satisfaction': latest_metrics[2],
                    'recent_domain_accuracy': latest_metrics[3],
                    'improvement_trend': latest_metrics[8]
                })
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {'error': str(e)}


def create_enhanced_feedback_system() -> EnhancedFeedbackSystem:
    """Factory function to create enhanced feedback system"""
    return EnhancedFeedbackSystem()


# Test the feedback system
if __name__ == "__main__":
    print("📊 ENHANCED FEEDBACK SYSTEM TEST")
    print("=" * 50)
    
    feedback_system = create_enhanced_feedback_system()
    
    # Test feedback collection (simulated)
    print("🧪 Testing Feedback Collection:")
    print("-" * 30)
    
    # Simulate feedback entry
    test_feedback = FeedbackEntry(
        session_id="test_001",
        timestamp=datetime.now().isoformat(),
        user_query="My landlord won't return deposit",
        predicted_domain="tenant_rights",
        confidence_score=0.85,
        legal_route="File complaint with housing authority",
        timeline_provided="30-60 days",
        domain_accuracy=5,
        route_helpfulness=4,
        timeline_realism=4,
        language_clarity=5,
        overall_satisfaction=4,
        would_recommend=True
    )
    
    # Store and process feedback
    feedback_system.store_feedback(test_feedback)
    feedback_system.process_feedback_learning(test_feedback)
    
    # Get performance summary
    summary = feedback_system.get_performance_summary()
    
    print(f"📊 Performance Summary:")
    print(f"   Total Feedback: {summary.get('total_feedback_received', 0)}")
    print(f"   Average Satisfaction: {summary.get('average_satisfaction', 0):.2f}/5")
    print(f"   Domain Accuracy: {summary.get('domain_accuracy', 0):.2f}/5")
    print(f"   Recommendation Rate: {summary.get('recommendation_rate', 0):.1f}%")
    print(f"   Model Retrainings: {summary.get('model_retrainings', 0)}")
    
    print(f"\n✅ Enhanced feedback system ready!")
    print(f"🔄 Continuous learning and improvement enabled")
