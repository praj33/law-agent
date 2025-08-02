#!/usr/bin/env python3
"""
Comprehensive smoke tests for production environment
"""

import os
import requests
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PRODUCTION_API_URL = os.getenv('PRODUCTION_API_URL', 'https://api.lawagent.dev')
PRODUCTION_FRONTEND_URL = os.getenv('PRODUCTION_FRONTEND_URL', 'https://lawagent.dev')

def test_health_endpoints():
    """Test all health endpoints"""
    endpoints = [
        f"{PRODUCTION_API_URL}/health",
        f"{PRODUCTION_API_URL}/api/v1/system/health",
        f"{PRODUCTION_API_URL}/api/v1/system/info",
        f"{PRODUCTION_API_URL}/api/v1/health/db",
        f"{PRODUCTION_API_URL}/api/v1/health/redis"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=15)
            assert response.status_code == 200, f"Health check failed for {endpoint}"
            print(f"✅ {endpoint} - OK")
        except Exception as e:
            print(f"❌ {endpoint} - FAILED: {e}")
            return False
    return True

def test_frontend_accessibility():
    """Test frontend is accessible"""
    try:
        response = requests.get(PRODUCTION_FRONTEND_URL, timeout=15)
        assert response.status_code == 200
        assert "Law Agent" in response.text
        print(f"✅ Frontend accessible at {PRODUCTION_FRONTEND_URL}")
        return True
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

def test_api_performance():
    """Test API response times"""
    try:
        start_time = time.time()
        response = requests.get(f"{PRODUCTION_API_URL}/health", timeout=10)
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0, f"Response time too slow: {response_time}s"
        print(f"✅ API response time: {response_time:.2f}s")
        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_concurrent_requests():
    """Test handling of concurrent requests"""
    def make_request():
        try:
            response = requests.get(f"{PRODUCTION_API_URL}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    try:
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.95, f"Success rate too low: {success_rate}"
        print(f"✅ Concurrent requests success rate: {success_rate:.2%}")
        return True
    except Exception as e:
        print(f"❌ Concurrent requests test failed: {e}")
        return False

def test_full_user_journey():
    """Test complete user journey"""
    try:
        # Create session
        session_response = requests.post(
            f"{PRODUCTION_API_URL}/api/v1/sessions",
            json={"user_id": "prod_smoke_test", "user_type": "common_person"},
            timeout=15
        )
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # Process query
        query_response = requests.post(
            f"{PRODUCTION_API_URL}/api/v1/query",
            json={"session_id": session_id, "query": "I need help with divorce"},
            timeout=30
        )
        assert query_response.status_code == 200
        interaction_id = query_response.json()["interaction_id"]
        
        # Submit feedback
        feedback_response = requests.post(
            f"{PRODUCTION_API_URL}/api/v1/feedback",
            json={
                "session_id": session_id,
                "interaction_id": interaction_id,
                "feedback": "upvote"
            },
            timeout=15
        )
        assert feedback_response.status_code == 200
        
        # Get session summary
        summary_response = requests.get(
            f"{PRODUCTION_API_URL}/api/v1/sessions/{session_id}/summary",
            timeout=15
        )
        assert summary_response.status_code == 200
        
        print("✅ Full user journey completed successfully")
        return True
    except Exception as e:
        print(f"❌ User journey test failed: {e}")
        return False

def main():
    """Run all production smoke tests"""
    print("🧪 Running production smoke tests...")
    
    tests = [
        ("Health Endpoints", test_health_endpoints),
        ("Frontend Accessibility", test_frontend_accessibility),
        ("API Performance", test_api_performance),
        ("Concurrent Requests", test_concurrent_requests),
        ("Full User Journey", test_full_user_journey)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        time.sleep(3)
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All production smoke tests passed!")
        sys.exit(0)
    else:
        print("❌ Some production smoke tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
