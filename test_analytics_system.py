#!/usr/bin/env python3
"""
Comprehensive Analytics System Test
Tests all analytics functionality including tracking, database, API, and insights
"""

import os
import sys
import json
import time
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Import analytics modules
from analytics_collector import analytics, EventType
from analytics_database import analytics_db
from analytics_engine import analytics_engine

def test_analytics_collector():
    """Test the analytics collector functionality"""
    print("\n🔧 Testing Analytics Collector...")
    
    # Start a test session
    session_id = analytics.start_session(
        user_id="test_user_123",
        context={"test_mode": True, "browser": "test"}
    )
    
    print(f"✅ Session started: {session_id}")
    
    # Track various events
    events_to_test = [
        (EventType.LEGAL_QUERY, {"query": "rental agreement help", "complexity": "medium"}),
        (EventType.GLOSSARY_TERM_ACCESSED, {"term": "lease", "method": "click"}),
        (EventType.TIMELINE_VIEWED, {"timeline": "eviction_process", "step": "notice_period"}),
        (EventType.CHAT_MESSAGE_SENT, {"message_length": 45, "intent": "legal_advice"}),
        (EventType.DOCUMENT_UPLOADED, {"file_type": "pdf", "file_size": 1024000})
    ]
    
    for event_type, data in events_to_test:
        event_id = analytics.track_event(
            event_type=event_type,
            session_id=session_id,
            data=data
        )
        print(f"✅ Tracked event: {event_type.value} -> {event_id}")
    
    # Track legal route
    route_id = analytics.track_legal_route(
        session_id=session_id,
        route_type="tenant_rights",
        route_description="Review your tenant rights and options for lease disputes",
        suggested_context={"confidence": 0.85, "complexity": "medium"}
    )
    print(f"✅ Legal route suggested: {route_id}")
    
    # Simulate user response
    analytics.track_legal_route_response(
        session_id=session_id,
        route_id=route_id,
        user_response="accepted",
        response_time_seconds=15.5
    )
    print(f"✅ Legal route response tracked: accepted")
    
    # Track glossary access
    analytics.track_glossary_access(
        session_id=session_id,
        term="Security Deposit",
        definition="Money paid by tenant as protection against damages",
        access_method="search",
        context="rental_agreement_analysis"
    )
    print(f"✅ Glossary access tracked")
    
    # Track timeline interaction
    analytics.track_timeline_interaction(
        session_id=session_id,
        timeline_type="eviction_process",
        step_id="step_1",
        step_name="Serve Notice",
        interaction_type="click"
    )
    print(f"✅ Timeline interaction tracked")
    
    # Get session summary
    summary = analytics.get_session_summary(session_id)
    print(f"✅ Session summary: {summary}")
    
    # End session
    analytics.end_session(session_id, {"test_completed": True, "events_tracked": len(events_to_test)})
    print(f"✅ Session ended: {session_id}")
    
    return True

def test_analytics_database():
    """Test the analytics database functionality"""
    print("\n🗄️ Testing Analytics Database...")
    
    # Test database connection
    try:
        cursor = analytics_db.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        event_count = cursor.fetchone()[0]
        print(f"✅ Database connected. Events in DB: {event_count}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test inserting sample data
    sample_event = {
        "event_id": f"test_event_{int(time.time())}",
        "session_id": "test_session_123",
        "user_id": "test_user_123",
        "event_type": "legal_query",
        "timestamp": datetime.now().isoformat(),
        "data": {"test": True},
        "success": True
    }
    
    success = analytics_db.insert_event(sample_event)
    if success:
        print("✅ Sample event inserted successfully")
    else:
        print("❌ Failed to insert sample event")
        return False
    
    # Test analytics views
    try:
        cursor.execute("SELECT * FROM daily_analytics_summary LIMIT 5")
        daily_summary = cursor.fetchall()
        print(f"✅ Daily analytics summary: {len(daily_summary)} records")
        
        cursor.execute("SELECT * FROM legal_route_success_rate LIMIT 5")
        route_success = cursor.fetchall()
        print(f"✅ Legal route success rates: {len(route_success)} records")
        
        cursor.execute("SELECT * FROM popular_glossary_terms LIMIT 5")
        popular_terms = cursor.fetchall()
        print(f"✅ Popular glossary terms: {len(popular_terms)} records")
        
    except Exception as e:
        print(f"❌ Error querying analytics views: {e}")
        return False
    
    # Test getting analytics summary
    summary = analytics_db.get_analytics_summary(days=7)
    if summary:
        print(f"✅ Analytics summary generated: {len(summary)} sections")
    else:
        print("❌ Failed to generate analytics summary")
        return False
    
    return True

def test_analytics_api():
    """Test the analytics API endpoints"""
    print("\n🌐 Testing Analytics API...")
    
    base_url = "http://localhost:8002"
    
    # Test if API is running
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Analytics API is running")
        else:
            print(f"❌ Analytics API returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Analytics API is not running. Start with: python analytics_api.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Analytics API: {e}")
        return False
    
    # Test session management
    try:
        # Start session
        session_response = requests.post(f"{base_url}/sessions/start", json={
            "user_id": "test_api_user",
            "context": {"test_mode": True}
        })
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            session_id = session_data["data"]["session_id"]
            print(f"✅ API session started: {session_id}")
        else:
            print(f"❌ Failed to start API session: {session_response.status_code}")
            return False
        
        # Track event via API
        event_response = requests.post(f"{base_url}/events/track", json={
            "event_type": "legal_query",
            "session_id": session_id,
            "data": {"query": "API test query", "test": True}
        })
        
        if event_response.status_code == 200:
            print("✅ Event tracked via API")
        else:
            print(f"❌ Failed to track event via API: {event_response.status_code}")
            return False
        
        # Test legal route tracking
        route_response = requests.post(f"{base_url}/legal-routes/suggest", json={
            "session_id": session_id,
            "route_type": "api_test_route",
            "route_description": "Test route for API validation"
        })
        
        if route_response.status_code == 200:
            route_data = route_response.json()
            route_id = route_data["data"]["route_id"]
            print(f"✅ Legal route tracked via API: {route_id}")
            
            # Track route response
            response_response = requests.post(f"{base_url}/legal-routes/response", json={
                "session_id": session_id,
                "route_id": route_id,
                "user_response": "accepted",
                "response_time_seconds": 12.3
            })
            
            if response_response.status_code == 200:
                print("✅ Legal route response tracked via API")
            else:
                print(f"❌ Failed to track route response: {response_response.status_code}")
        
        # Test analytics endpoints
        analytics_response = requests.get(f"{base_url}/analytics/summary?days=7")
        if analytics_response.status_code == 200:
            analytics_data = analytics_response.json()
            print(f"✅ Analytics summary retrieved: {analytics_data['success']}")
        else:
            print(f"❌ Failed to get analytics summary: {analytics_response.status_code}")
        
        # End session
        end_response = requests.post(f"{base_url}/sessions/{session_id}/end", json={
            "test_completed": True
        })
        
        if end_response.status_code == 200:
            print(f"✅ API session ended: {session_id}")
        else:
            print(f"❌ Failed to end API session: {end_response.status_code}")
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")
        return False
    
    return True

def test_analytics_engine():
    """Test the advanced analytics engine"""
    print("\n🧠 Testing Analytics Engine...")
    
    try:
        # Test user behavior pattern analysis
        patterns = analytics_engine.analyze_user_behavior_patterns()
        print(f"✅ User behavior patterns analyzed: {len(patterns)} patterns found")
        
        for pattern in patterns[:3]:  # Show first 3 patterns
            print(f"   • {pattern.user_segment}: {pattern.frequency} users, {pattern.success_rate:.2f} success rate")
        
        # Test legal route success prediction
        test_route_data = {
            "route_type": "tenant_rights",
            "legal_domain": "housing",
            "complexity_level": "medium",
            "confidence_score": 0.8
        }
        
        prediction = analytics_engine.predict_legal_route_success(test_route_data)
        if "error" not in prediction:
            print(f"✅ Legal route success prediction: {prediction['success_probability']:.2f} probability")
            print(f"   Model accuracy: {prediction['model_accuracy']:.2f}")
        else:
            print(f"⚠️ Legal route prediction: {prediction['error']}")
        
        # Test glossary usage trends
        glossary_trends = analytics_engine.analyze_glossary_usage_trends()
        if "error" not in glossary_trends:
            print(f"✅ Glossary trends analyzed: {glossary_trends['engagement_metrics']['total_accesses']} total accesses")
            print(f"   Most accessed terms: {len(glossary_trends['most_accessed_terms'])}")
        else:
            print(f"⚠️ Glossary trends: {glossary_trends['error']}")
        
        # Test timeline completion prediction
        test_timeline_data = {
            "timeline_type": "eviction_process",
            "step_name": "serve_notice",
            "interaction_type": "view"
        }
        
        timeline_prediction = analytics_engine.predict_timeline_completion(test_timeline_data)
        if "error" not in timeline_prediction:
            print(f"✅ Timeline completion prediction: {timeline_prediction['completion_probability']:.2f} probability")
            print(f"   Estimated duration: {timeline_prediction['estimated_duration_seconds']:.0f} seconds")
        else:
            print(f"⚠️ Timeline prediction: {timeline_prediction['error']}")
        
        # Test anomaly detection
        anomalies = analytics_engine.detect_anomalies()
        print(f"✅ Anomaly detection: {len(anomalies)} anomalies detected")
        
        for anomaly in anomalies[:2]:  # Show first 2 anomalies
            print(f"   • {anomaly.title}: {anomaly.impact_level} impact")
        
        # Test optimization recommendations
        recommendations = analytics_engine.generate_optimization_recommendations()
        print(f"✅ Optimization recommendations: {len(recommendations)} recommendations generated")
        
        for rec in recommendations[:2]:  # Show first 2 recommendations
            print(f"   • {rec.title}: {len(rec.recommendations)} action items")
        
        # Test comprehensive insights
        insights = analytics_engine.get_comprehensive_insights()
        if "error" not in insights:
            print(f"✅ Comprehensive insights generated successfully")
            print(f"   • User patterns: {len(insights.get('user_behavior_patterns', []))}")
            print(f"   • Anomalies: {len(insights.get('anomalies', []))}")
            print(f"   • Recommendations: {len(insights.get('optimization_recommendations', []))}")
        else:
            print(f"❌ Comprehensive insights error: {insights['error']}")
        
    except Exception as e:
        print(f"❌ Error testing analytics engine: {e}")
        return False
    
    return True

def run_comprehensive_test():
    """Run comprehensive analytics system test"""
    print("🧪 Law Agent Analytics System - Comprehensive Test")
    print("=" * 70)
    
    test_results = {
        "analytics_collector": False,
        "analytics_database": False,
        "analytics_api": False,
        "analytics_engine": False
    }
    
    # Test 1: Analytics Collector
    test_results["analytics_collector"] = test_analytics_collector()
    
    # Test 2: Analytics Database
    test_results["analytics_database"] = test_analytics_database()
    
    # Test 3: Analytics API
    test_results["analytics_api"] = test_analytics_api()
    
    # Test 4: Analytics Engine
    test_results["analytics_engine"] = test_analytics_engine()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title():<25} | {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All analytics tests passed! System is ready for production.")
        print("\n🚀 To start the complete system:")
        print("   python start_law_agent_complete.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        if not test_results["analytics_api"]:
            print("   • Start Analytics API: python analytics_api.py")
        if not test_results["analytics_database"]:
            print("   • Check database permissions and SQLite installation")
        if not test_results["analytics_engine"]:
            print("   • Install ML dependencies: pip install scikit-learn matplotlib")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
