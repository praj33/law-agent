#!/usr/bin/env python3
"""Quick test of Law Agent from terminal."""

import requests
import json

def quick_test():
    """Quick test of the Law Agent."""
    
    BASE_URL = "http://localhost:8000/api/api/v1"
    
    print("🏛️  Quick Law Agent Test")
    print("=" * 30)
    
    # Create session
    session_data = {"user_id": "quick_test", "user_type": "common_person"}
    response = requests.post(f"{BASE_URL}/sessions", json=session_data)
    session_id = response.json()["session_id"]
    print(f"✅ Session: {session_id[:8]}...")
    
    # Ask a question
    query = "What is a contract?"
    query_data = {"session_id": session_id, "query": query}
    response = requests.post(f"{BASE_URL}/query", json=query_data)
    result = response.json()
    
    print(f"📝 Query: {query}")
    print(f"🎯 Domain: {result['domain']}")
    print(f"📊 Confidence: {result['confidence']:.1%}")
    print(f"🤖 Response: {result['response']['text'][:150]}...")
    
    if result['glossary_terms']:
        print(f"📚 Legal Terms Found: {len(result['glossary_terms'])}")
        for term in result['glossary_terms'][:2]:
            print(f"   • {term['term']}")
    
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    quick_test()
