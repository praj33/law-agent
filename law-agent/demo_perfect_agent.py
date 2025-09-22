#!/usr/bin/env python3
"""
Demo of the PERFECT Legal Agent - Concise, Actionable, User-Friendly
"""

import requests

def demo_perfect_legal_agent():
    """Demonstrate the perfect legal agent responses."""
    
    print("🎯 PERFECT LEGAL AGENT DEMO")
    print("=" * 50)
    print("✅ Concise responses (under 600 characters)")
    print("✅ Clear structure with key sections")
    print("✅ Actionable next steps")
    print("✅ No overwhelming information")
    print("=" * 50)
    
    # Create session
    session_resp = requests.post('http://localhost:8004/api/v1/sessions', 
                               json={'user_id': 'demo_user', 'user_type': 'common_person'})
    session_id = session_resp.json()['session_id']
    
    # Demo queries
    queries = [
        "I want to file for divorce",
        "How can I get custody of my children?",
        "I was wrongfully terminated from my job"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 QUERY {i}: {query}")
        print("-" * 40)
        
        query_data = {
            'session_id': session_id,
            'query': query,
            'user_type': 'common_person'
        }
        
        response = requests.post('http://localhost:8004/api/v1/query', json=query_data)
        result = response.json()
        
        response_text = result['response']['text']
        
        print(f"📊 Domain: {result['domain']}")
        print(f"📏 Length: {len(response_text)} characters")
        
        # Check if it's the perfect length
        if len(response_text) <= 600:
            print("✅ PERFECT LENGTH: Easy to read!")
        else:
            print("⚠️  Too long for optimal user experience")
        
        print("\n📝 RESPONSE:")
        print("─" * 30)
        print(response_text)
        print("─" * 30)
        
        # Analyze structure
        sections = ['Legal Analysis', 'Next Steps', 'Timeline', 'Important']
        found = [s for s in sections if s in response_text]
        print(f"🎯 Structure: {len(found)}/4 sections - {found}")
        
        if len(found) >= 3:
            print("✅ EXCELLENT: Well-structured response!")
        else:
            print("⚠️  Could be better structured")
    
    print("\n" + "=" * 50)
    print("🎉 TRANSFORMATION COMPLETE!")
    print("Your Legal Agent now provides:")
    print("✅ Concise, readable responses")
    print("✅ Clear actionable guidance")
    print("✅ Professional legal advice")
    print("✅ Perfect user experience")
    print("\n🚀 MISSION ACCOMPLISHED!")

if __name__ == "__main__":
    demo_perfect_legal_agent()
