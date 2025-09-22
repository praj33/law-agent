#!/usr/bin/env python3
"""Quick test of the integrated Grok system."""

import requests
import json

def quick_test():
    print("🧪 QUICK TEST - INTEGRATED GROK SYSTEM")
    print("=" * 50)
    
    base_url = "http://localhost:8014/api/v1"
    
    # Create session
    session_resp = requests.post(f'{base_url}/sessions', 
                               json={'user_id': 'quick_test', 'user_type': 'common_person'})
    session_id = session_resp.json()['session_id']
    print(f"✅ Session: {session_id[:8]}...")
    
    # Test one query
    query = "I want to file for divorce from my abusive husband"
    print(f"🔍 Query: {query}")
    
    query_data = {
        'session_id': session_id,
        'query': query,
        'user_type': 'common_person'
    }
    
    response = requests.post(f'{base_url}/query', json=query_data, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS!")
        print(f"📊 Domain: {result['domain']}")
        print(f"🎯 Confidence: {result['confidence']:.3f}")
        
        # Check for advanced features
        response_data = result['response']
        
        if 'estimated_cost' in response_data:
            print(f"💰 Cost: {response_data['estimated_cost']}")
        
        if 'timeline' in response_data:
            print(f"⏱️  Timeline: {response_data['timeline']}")
        
        if 'success_rate' in response_data:
            print(f"📈 Success Rate: {response_data['success_rate']}")
        
        print(f"📝 Response: {response_data['text'][:200]}...")
        
        print(f"\n🎉 GROK INTEGRATION WORKING!")
        
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    quick_test()
