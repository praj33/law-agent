#!/usr/bin/env python3
"""
Complete Endpoint Testing Suite
===============================

Tests ALL endpoints from both integrated systems to ensure 100% functionality.

Author: Integrated Law Agent Team
Version: 6.0.0 - Complete Integration Testing
Date: 2025-08-04
"""

import requests
import json
import time
from typing import Dict, List, Any

API_BASE = "http://localhost:8000"
session_id = None

def test_endpoint(name: str, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> bool:
    """Test a single endpoint"""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            print(f"❌ {name}: Unsupported method {method}")
            return False
        
        success = response.status_code == expected_status
        status_icon = "✅" if success else "❌"
        
        print(f"{status_icon} {name}: {response.status_code}")
        
        if success and response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, dict) and len(data) > 0:
                    # Show first key-value pair as sample
                    first_key = list(data.keys())[0]
                    first_value = data[first_key]
                    if isinstance(first_value, (str, int, float, bool)):
                        print(f"   Sample: {first_key}: {first_value}")
                    else:
                        print(f"   Sample: {first_key}: {type(first_value).__name__}")
            except:
                pass
        
        return success
        
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

def main():
    """Test all endpoints comprehensively"""
    global session_id
    
    print("🚀 COMPLETE ENDPOINT TESTING SUITE")
    print("=" * 60)
    
    results = []
    
    # System Health Endpoints
    print("\n🏥 SYSTEM HEALTH ENDPOINTS")
    print("-" * 40)
    results.append(test_endpoint("Health Check", "GET", "/health"))
    results.append(test_endpoint("System Info", "GET", "/api/v1/system/info"))
    results.append(test_endpoint("Enhanced Features", "GET", "/api/v1/system/enhanced-features"))
    results.append(test_endpoint("System Health", "GET", "/api/v1/system/health"))
    
    # Session Management
    print("\n👥 SESSION MANAGEMENT")
    print("-" * 40)
    
    # Create session first
    session_response = requests.post(f"{API_BASE}/api/v1/sessions", 
                                   json={"user_id": "test_user", "user_type": "common_person"})
    if session_response.status_code == 200:
        session_data = session_response.json()
        session_id = session_data.get('session_id')
        print(f"✅ Create Session: 200")
        print(f"   Sample: session_id: {session_id[:8]}...")
        results.append(True)
        
        # Test session endpoints
        results.append(test_endpoint("Get Session", "GET", f"/api/v1/sessions/{session_id}"))
        results.append(test_endpoint("Session Summary", "GET", f"/api/v1/sessions/{session_id}/summary"))
    else:
        print(f"❌ Create Session: {session_response.status_code}")
        results.append(False)
    
    # Enhanced Query Processing
    print("\n🤖 ENHANCED QUERY PROCESSING")
    print("-" * 40)
    if session_id:
        query_data = {
            "session_id": session_id,
            "query": "I want to file for divorce",
            "interaction_type": "query"
        }
        results.append(test_endpoint("Process Query", "POST", "/api/v1/query", query_data))
    
    # ML Domain Classification
    print("\n🧠 ML DOMAIN CLASSIFICATION")
    print("-" * 40)
    classify_data = {"query": "My employer fired me unfairly", "include_confidence": True}
    results.append(test_endpoint("Domain Classification", "POST", "/api/v1/domain/classify", classify_data))
    
    ml_feedback_data = {
        "query": "test query",
        "predicted_domain": "family_law",
        "actual_domain": "family_law",
        "helpful": True
    }
    results.append(test_endpoint("ML Feedback", "POST", "/api/v1/ml/feedback", ml_feedback_data))
    results.append(test_endpoint("ML Retrain", "POST", "/api/v1/ml/retrain"))
    
    # Constitutional Integration
    print("\n🏛️ CONSTITUTIONAL INTEGRATION")
    print("-" * 40)
    const_search_data = {"query": "equality", "limit": 3}
    results.append(test_endpoint("Constitutional Search", "POST", "/api/v1/constitutional/search", const_search_data))
    
    domain_backing_data = {
        "domain": "employment_law",
        "query": "workplace discrimination"
    }
    results.append(test_endpoint("Domain Constitutional Backing", "POST", "/api/v1/constitutional/domain-backing", domain_backing_data))
    
    # Legal Glossary
    print("\n📚 LEGAL GLOSSARY")
    print("-" * 40)
    results.append(test_endpoint("Get Term Definition", "GET", "/api/v1/glossary/term/custody?user_type=common"))
    results.append(test_endpoint("Domain Terms", "GET", "/api/v1/glossary/domain/family_law"))
    
    glossary_search_data = {"query": "custody", "limit": 5}
    results.append(test_endpoint("Glossary Search", "POST", "/api/v1/glossary/search", glossary_search_data))
    
    # Legal Routes
    print("\n🗺️ LEGAL ROUTES")
    print("-" * 40)
    route_search_data = {
        "domain": "family_law",
        "query": "divorce process",
        "user_type": "common_person"
    }
    results.append(test_endpoint("Route Search", "POST", "/api/v1/routes/search", route_search_data))
    results.append(test_endpoint("Domain Routes", "GET", "/api/v1/routes/domain/family_law"))
    
    route_get_data = {
        "domain": "family_law",
        "query": "divorce help",
        "user_type": "common_person"
    }
    results.append(test_endpoint("Get Legal Route", "POST", "/api/v1/routes/get-route", route_get_data))
    
    # RL Learning System
    print("\n📈 RL LEARNING SYSTEM")
    print("-" * 40)
    results.append(test_endpoint("RL Status", "GET", "/api/v1/rl/status"))
    results.append(test_endpoint("RL Metrics", "GET", "/api/v1/rl/metrics"))
    
    if session_id:
        # Need to create an interaction first for feedback
        feedback_data = {
            "session_id": session_id,
            "interaction_id": "test-interaction-id",
            "feedback": "upvote",
            "time_spent": 30.0
        }
        results.append(test_endpoint("Submit Feedback", "POST", "/api/v1/feedback", feedback_data))
    
    # Analytics
    print("\n📊 ANALYTICS")
    print("-" * 40)
    analytics_data = {"session_id": session_id if session_id else None}
    results.append(test_endpoint("Analytics Summary", "POST", "/api/v1/analytics/summary", analytics_data))
    results.append(test_endpoint("User Satisfaction", "GET", "/api/v1/analytics/user-satisfaction"))
    
    # Document Processing
    print("\n📄 DOCUMENT PROCESSING")
    print("-" * 40)
    results.append(test_endpoint("Document Upload", "POST", "/api/v1/documents/upload"))
    results.append(test_endpoint("Document Status", "GET", "/api/v1/documents/status/test-process-id"))
    
    # Administrative
    print("\n🔧 ADMINISTRATIVE")
    print("-" * 40)
    results.append(test_endpoint("Save RL Policy", "POST", "/api/v1/admin/save-policy"))
    
    # WebSocket Info
    print("\n🌐 WEBSOCKET")
    print("-" * 40)
    results.append(test_endpoint("WebSocket Info", "GET", "/api/v1/ws/realtime"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 COMPLETE ENDPOINT TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ PASSED: {passed}")
    print(f"❌ FAILED: {total - passed}")
    print(f"📊 SUCCESS RATE: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL ENDPOINTS WORKING PERFECTLY!")
        print("🚀 Your integrated law agent has COMPLETE API functionality!")
        print("\n🎯 INTEGRATION SUCCESS:")
        print("   ✅ System Health: Working")
        print("   ✅ Session Management: Working")
        print("   ✅ Enhanced Query Processing: Working")
        print("   ✅ ML Domain Classification: Working")
        print("   ✅ Constitutional Integration: Working")
        print("   ✅ Legal Glossary: Working")
        print("   ✅ Legal Routes: Working")
        print("   ✅ RL Learning System: Working")
        print("   ✅ Analytics: Working")
        print("   ✅ Document Processing: Working")
        print("   ✅ Administrative: Working")
        print("   ✅ WebSocket Support: Working")
        print("\n🏆 PRODUCTION-READY INTEGRATED LAW AGENT!")
    else:
        print(f"\n⚠️ {total - passed} endpoints need attention")
        print("Check the failed endpoints above for issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
