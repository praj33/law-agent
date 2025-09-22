#!/usr/bin/env python3
"""
Test script to verify frontend-backend connection with Render deployment
"""

import requests
import json

# Render backend URL
RENDER_BACKEND_URL = "https://law-agent-by-grok.onrender.com"

def test_backend_health():
    """Test if the backend is accessible and healthy"""
    try:
        response = requests.get(f"{RENDER_BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check: PASSED")
            print(f"   Status: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend health check: FAILED (Error: {e})")
        return False

def test_api_docs():
    """Test if API documentation is accessible"""
    try:
        response = requests.get(f"{RENDER_BACKEND_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation access: PASSED")
            return True
        else:
            print(f"❌ API documentation access: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API documentation access: FAILED (Error: {e})")
        return False

def test_create_session():
    """Test session creation endpoint"""
    try:
        payload = {
            "user_id": "test_user_123",
            "user_type": "common"
        }
        response = requests.post(
            f"{RENDER_BACKEND_URL}/api/v1/sessions",
            json=payload,
            timeout=10
        )
        if response.status_code == 200:
            session_data = response.json()
            print("✅ Session creation: PASSED")
            print(f"   Session ID: {session_data.get('session_id')}")
            return session_data.get('session_id')
        else:
            print(f"❌ Session creation: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Session creation: FAILED (Error: {e})")
        return None

def test_query_endpoint(session_id):
    """Test query processing endpoint"""
    if not session_id:
        print("❌ Query test: SKIPPED (No session ID)")
        return False
        
    try:
        payload = {
            "session_id": session_id,
            "query": "What are my rights if I'm being evicted?",
        }
        response = requests.post(
            f"{RENDER_BACKEND_URL}/api/v1/query",
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            query_data = response.json()
            print("✅ Query processing: PASSED")
            print(f"   Domain: {query_data.get('domain')}")
            print(f"   Confidence: {query_data.get('confidence')}")
            return True
        else:
            print(f"❌ Query processing: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Query processing: FAILED (Error: {e})")
        return False

def main():
    """Run all connection tests"""
    print("🧪 Testing Frontend-Backend Connection with Render Deployment")
    print("=" * 60)
    
    # Test backend health
    health_ok = test_backend_health()
    
    # Test API docs
    docs_ok = test_api_docs()
    
    # Test session creation
    session_id = None
    if health_ok and docs_ok:
        session_id = test_create_session()
    
    # Test query endpoint
    query_ok = False
    if session_id:
        query_ok = test_query_endpoint(session_id)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 CONNECTION TEST SUMMARY:")
    print(f"   Backend Health: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   API Docs: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    print(f"   Session Creation: {'✅ PASS' if session_id else '❌ FAIL'}")
    print(f"   Query Processing: {'✅ PASS' if query_ok else '❌ FAIL'}")
    
    if health_ok and docs_ok and session_id and query_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("Frontend should be able to communicate with the Render backend successfully.")
    else:
        print("\n⚠️  SOME TESTS FAILED!")
        print("Please check the backend deployment and network configuration.")

if __name__ == "__main__":
    main()