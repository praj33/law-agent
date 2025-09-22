#!/usr/bin/env python3
"""
Test the ultimate-analysis endpoint
"""

import requests
import json

# Render backend URL
RENDER_BACKEND_URL = "https://law-agent-by-grok.onrender.com"

def test_ultimate_analysis():
    """Test the ultimate-analysis endpoint"""
    try:
        print("🔍 Testing /api/ultimate-analysis endpoint...")
        
        # Sample query
        payload = {
            "query": "What are my rights if I'm being evicted?"
        }
        
        response = requests.post(
            f"{RENDER_BACKEND_URL}/api/ultimate-analysis",
            json=payload,
            timeout=30  # Longer timeout for analysis
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            print("✅ Success!")
            try:
                data = response.json()
                print("Response:")
                print(json.dumps(data, indent=2))
                return True
            except Exception as e:
                print(f"Response (text): {response.text[:500]}...")
                return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_feedback():
    """Test the feedback endpoint"""
    try:
        print("\n🔍 Testing /api/feedback endpoint...")
        
        # Sample feedback
        payload = {
            "query": "What are my rights if I'm being evicted?",
            "domain": "property_law",
            "subdomain": "tenant_rights",
            "confidence": 0.95,
            "feedback": "helpful",
            "rating": 5
        }
        
        response = requests.post(
            f"{RENDER_BACKEND_URL}/api/feedback",
            json=payload,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Feedback endpoint working!")
            try:
                data = response.json()
                print("Response:")
                print(json.dumps(data, indent=2))
            except:
                print(f"Response (text): {response.text[:200]}...")
        else:
            print(f"❌ Feedback endpoint error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Feedback endpoint exception: {e}")

if __name__ == "__main__":
    success = test_ultimate_analysis()
    if success:
        test_feedback()