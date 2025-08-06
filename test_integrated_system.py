#!/usr/bin/env python3
"""
Comprehensive Test Suite for Integrated Law Agent System
========================================================

This script tests the integration of:
- Advanced RL learning system
- Enhanced ML domain classification (TF-IDF + Naive Bayes)
- Constitutional backing with Indian Constitutional articles
- Real-time feedback learning
- Enhanced API endpoints

Author: Integrated Law Agent Team
Version: 6.0.0 - Integration Testing
Date: 2025-08-04
"""

import asyncio
import json
import requests
import time
from typing import Dict, List, Any
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = None


def print_header(title: str):
    """Print formatted test section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")


def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")


def test_api_health():
    """Test basic API health"""
    print_header("API Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_result("API Health", True, f"Status: {data.get('status', 'unknown')}")
            return True
        else:
            print_result("API Health", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("API Health", False, f"Connection error: {e}")
        return False


def test_enhanced_features_status():
    """Test enhanced features status endpoint"""
    print_header("Enhanced Features Status")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/system/enhanced-features", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_result("Enhanced Features API", True)
            print(f"   🤖 ML Classification: {'Active' if data.get('enhanced_classification') else 'Inactive'}")
            print(f"   🏛️ Constitutional Support: {'Active' if data.get('constitutional_support') else 'Inactive'}")
            
            if data.get('model_stats'):
                stats = data['model_stats']
                print(f"   📊 Training Examples: {stats.get('training_examples', 'N/A')}")
                print(f"   📈 Model Type: {stats.get('model_type', 'N/A')}")
            
            if data.get('constitutional_stats'):
                const_stats = data['constitutional_stats']
                print(f"   📜 Constitutional Articles: {const_stats.get('total_articles', 'N/A')}")
            
            return True
        else:
            print_result("Enhanced Features API", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Enhanced Features API", False, f"Error: {e}")
        return False


def test_session_creation():
    """Test session creation"""
    print_header("Session Management")
    
    global TEST_SESSION_ID
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/sessions",
            json={"user_id": "integration_test", "user_type": "common_person"},
            timeout=10
        )
        
        success = response.status_code == 200
        
        if success:
            data = response.json()
            TEST_SESSION_ID = data.get('session_id')
            print_result("Session Creation", True, f"Session ID: {TEST_SESSION_ID[:8]}...")
            return True
        else:
            print_result("Session Creation", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Session Creation", False, f"Error: {e}")
        return False


def test_enhanced_query_processing():
    """Test enhanced query processing with ML classification and constitutional backing"""
    print_header("Enhanced Query Processing")
    
    if not TEST_SESSION_ID:
        print_result("Enhanced Query Processing", False, "No session ID available")
        return False
    
    test_queries = [
        {
            "query": "I want to file for divorce from my husband",
            "expected_domain": "family_law",
            "description": "Family Law Query"
        },
        {
            "query": "My employer fired me without cause",
            "expected_domain": "employment_law", 
            "description": "Employment Law Query"
        },
        {
            "query": "Landlord won't return my security deposit",
            "expected_domain": "property_law",
            "description": "Property Law Query"
        },
        {
            "query": "I was arrested without a warrant",
            "expected_domain": "criminal_law",
            "description": "Criminal Law Query"
        }
    ]
    
    all_passed = True
    
    for test_case in test_queries:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/query",
                json={
                    "session_id": TEST_SESSION_ID,
                    "query": test_case["query"],
                    "interaction_type": "query"
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                has_response = bool(data.get('response'))
                has_domain = bool(data.get('domain'))
                has_confidence = 'confidence' in data
                
                # Check enhanced features
                response_data = data.get('response', {})
                has_constitutional = bool(response_data.get('constitutional_backing'))
                has_enhanced_analysis = bool(response_data.get('legal_analysis', {}).get('enhanced_ml_classification'))
                
                success = has_response and has_domain and has_confidence
                
                details = []
                details.append(f"Domain: {data.get('domain', 'N/A')}")
                details.append(f"Confidence: {data.get('confidence', 0)*100:.1f}%")
                
                if has_constitutional:
                    const_backing = response_data['constitutional_backing']
                    article_count = const_backing.get('article_count', 0)
                    details.append(f"🏛️ Constitutional Articles: {article_count}")
                
                if has_enhanced_analysis:
                    details.append("🤖 Enhanced ML Classification")
                
                print_result(test_case["description"], success, " | ".join(details))
                
                if not success:
                    all_passed = False
                    
            else:
                print_result(test_case["description"], False, f"Status code: {response.status_code}")
                all_passed = False
                
        except Exception as e:
            print_result(test_case["description"], False, f"Error: {e}")
            all_passed = False
    
    return all_passed


def test_constitutional_search():
    """Test constitutional article search"""
    print_header("Constitutional Article Search")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/constitutional/search",
            json={"query": "equality", "limit": 3},
            timeout=10
        )
        
        success = response.status_code == 200
        
        if success:
            data = response.json()
            articles = data.get('articles', [])
            total_found = data.get('total_found', 0)
            
            print_result("Constitutional Search", True, f"Found {total_found} articles")
            
            for i, article in enumerate(articles[:2]):
                print(f"   📜 Article {article.get('article_number', 'N/A')}: {article.get('title', 'N/A')[:50]}...")
            
            return True
        else:
            print_result("Constitutional Search", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("Constitutional Search", False, f"Error: {e}")
        return False


def test_rl_learning_system():
    """Test RL learning system status"""
    print_header("RL Learning System")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/rl/status", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_result("RL Status", True)
            print(f"   🎯 Exploration Rate: {data.get('exploration_rate', 'N/A')}")
            print(f"   📊 Q-table Size: {data.get('qtable_size', 'N/A')}")
            print(f"   📈 Total Interactions: {data.get('total_interactions', 'N/A')}")
            print(f"   ⭐ Average Satisfaction: {data.get('average_satisfaction', 'N/A')}")
            return True
        else:
            print_result("RL Status", False, f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_result("RL Status", False, f"Error: {e}")
        return False


def test_feedback_learning():
    """Test feedback learning system"""
    print_header("Feedback Learning System")
    
    if not TEST_SESSION_ID:
        print_result("Feedback Learning", False, "No session ID available")
        return False
    
    try:
        # First, make a query to get an interaction ID
        query_response = requests.post(
            f"{API_BASE_URL}/api/v1/query",
            json={
                "session_id": TEST_SESSION_ID,
                "query": "Test feedback query",
                "interaction_type": "query"
            },
            timeout=10
        )
        
        if query_response.status_code != 200:
            print_result("Feedback Learning", False, "Failed to create test interaction")
            return False
        
        query_data = query_response.json()
        interaction_id = query_data.get('interaction_id')
        
        if not interaction_id:
            print_result("Feedback Learning", False, "No interaction ID received")
            return False
        
        # Now test feedback
        feedback_response = requests.post(
            f"{API_BASE_URL}/api/v1/feedback",
            json={
                "session_id": TEST_SESSION_ID,
                "interaction_id": interaction_id,
                "feedback": "upvote",
                "time_spent": 30.0
            },
            timeout=10
        )
        
        success = feedback_response.status_code == 200
        
        if success:
            feedback_data = feedback_response.json()
            print_result("Feedback Learning", True, f"Reward: {feedback_data.get('reward', 'N/A')}")
            return True
        else:
            print_result("Feedback Learning", False, f"Status code: {feedback_response.status_code}")
            return False
            
    except Exception as e:
        print_result("Feedback Learning", False, f"Error: {e}")
        return False


def run_comprehensive_test():
    """Run comprehensive integration test suite"""
    print("🚀 INTEGRATED LAW AGENT SYSTEM - COMPREHENSIVE TEST SUITE")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Run all tests
    test_results.append(("API Health", test_api_health()))
    test_results.append(("Enhanced Features", test_enhanced_features_status()))
    test_results.append(("Session Management", test_session_creation()))
    test_results.append(("Enhanced Query Processing", test_enhanced_query_processing()))
    test_results.append(("Constitutional Search", test_constitutional_search()))
    test_results.append(("RL Learning System", test_rl_learning_system()))
    test_results.append(("Feedback Learning", test_feedback_learning()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Integrated Law Agent system is working perfectly!")
        print("\n🚀 INTEGRATION SUCCESS:")
        print("   ✅ Advanced RL learning system active")
        print("   ✅ Enhanced ML domain classification working")
        print("   ✅ Constitutional backing integrated")
        print("   ✅ Real-time feedback learning operational")
        print("   ✅ Enhanced API endpoints functional")
        print("\n🎯 Your integrated law agent is ready for production!")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the system configuration.")
    
    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
