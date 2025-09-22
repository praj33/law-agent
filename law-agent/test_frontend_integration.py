#!/usr/bin/env python3
"""
Test the frontend integration with the Render backend
"""

import requests
import json

# Render backend URL
RENDER_BACKEND_URL = "https://law-agent-by-grok.onrender.com"

def test_frontend_backend_integration():
    """Test the integration between frontend and backend"""
    print("🧪 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    try:
        # Test 1: Health check
        print("1. Testing health endpoint...")
        health_response = requests.get(f"{RENDER_BACKEND_URL}/api/health", timeout=10)
        if health_response.status_code == 200:
            print("   ✅ Health check passed")
            health_data = health_response.json()
            print(f"   🏥 Status: {health_data.get('status')}")
            print(f"   📦 Version: {health_data.get('version')}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
        
        # Test 2: Query processing
        print("\n2. Testing query processing...")
        query_payload = {
            "query": "What are my rights if I'm being evicted?"
        }
        query_response = requests.post(
            f"{RENDER_BACKEND_URL}/api/ultimate-analysis",
            json=query_payload,
            timeout=30
        )
        
        if query_response.status_code == 200:
            print("   ✅ Query processing passed")
            query_data = query_response.json()
            print(f"   📝 Query: {query_data.get('query')}")
            print(f"   🏷️  Domain: {query_data.get('domain')}")
            print(f"   📊 Confidence: {query_data.get('domain_confidence_percentage')}")
            print(f"   🕐 Processing time: {query_data.get('processing_time')}")
        else:
            print(f"   ❌ Query processing failed: {query_response.status_code}")
            print(f"   📄 Response: {query_response.text[:200]}")
            return False
        
        # Test 3: Feedback submission
        print("\n3. Testing feedback submission...")
        feedback_payload = {
            "query": query_data.get('query', "What are my rights if I'm being evicted?"),
            "domain": query_data.get('domain', 'property_law'),
            "subdomain": query_data.get('subdomain', 'tenant_rights'),
            "confidence": query_data.get('domain_confidence', 0.8),
            "feedback": "helpful",
            "rating": 5
        }
        feedback_response = requests.post(
            f"{RENDER_BACKEND_URL}/api/feedback",
            json=feedback_payload,
            timeout=10
        )
        
        if feedback_response.status_code == 200:
            print("   ✅ Feedback submission passed")
            feedback_data = feedback_response.json()
            print(f"   💬 Message: {feedback_data.get('message')}")
            print(f"   📈 New confidence: {feedback_data.get('new_confidence')}")
        else:
            print(f"   ❌ Feedback submission failed: {feedback_response.status_code}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("The frontend should now be able to communicate with the Render backend successfully.")
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_backend_integration()
    if not success:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        print("1. Check if the Render backend is running")
        print("2. Verify the API endpoints are accessible")
        print("3. Ensure the frontend is configured with the correct API URL")
        print("4. Check network connectivity and firewall settings")