#!/usr/bin/env python3
"""
Smoke tests for staging environment
"""

import os
import requests
import sys
import time

STAGING_API_URL = os.getenv('STAGING_API_URL', 'https://staging-api.lawagent.dev')

def test_health_endpoints():
    """Test all health endpoints"""
    endpoints = [
        f"{STAGING_API_URL}/health",
        f"{STAGING_API_URL}/api/v1/system/health",
        f"{STAGING_API_URL}/api/v1/system/info"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=10)
            assert response.status_code == 200, f"Health check failed for {endpoint}"
            print(f"✅ {endpoint} - OK")
        except Exception as e:
            print(f"❌ {endpoint} - FAILED: {e}")
            return False
    return True

def test_api_functionality():
    """Test basic API functionality"""
    try:
        # Create session
        session_response = requests.post(
            f"{STAGING_API_URL}/api/v1/sessions",
            json={"user_id": "smoke_test_user", "user_type": "common_person"},
            timeout=10
        )
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        print(f"✅ Session created: {session_id}")
        
        # Test query
        query_response = requests.post(
            f"{STAGING_API_URL}/api/v1/query",
            json={"session_id": session_id, "query": "What is a contract?"},
            timeout=30
        )
        assert query_response.status_code == 200
        print("✅ Query processed successfully")
        
        # Test glossary
        glossary_response = requests.post(
            f"{STAGING_API_URL}/api/v1/glossary/search",
            json={"query": "contract", "max_terms": 3},
            timeout=10
        )
        assert glossary_response.status_code == 200
        print("✅ Glossary search successful")
        
        return True
    except Exception as e:
        print(f"❌ API functionality test failed: {e}")
        return False

def main():
    """Run all smoke tests"""
    print("🧪 Running staging smoke tests...")
    
    tests = [
        test_health_endpoints,
        test_api_functionality
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        time.sleep(2)
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All smoke tests passed!")
        sys.exit(0)
    else:
        print("❌ Some smoke tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
