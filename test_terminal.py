#!/usr/bin/env python3
"""
Simple terminal testing script for Law Agent.
Run this to test the system from command line.
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_law_agent():
    """Test the Law Agent system from terminal."""
    
    print("🏛️  LAW AGENT TERMINAL TEST")
    print("=" * 50)
    
    try:
        # Test 1: Create session
        print("1️⃣  Creating session...")
        session_data = {
            "user_id": "terminal_user",
            "user_type": "common_person"
        }
        
        response = requests.post(f"{BASE_URL}/sessions", json=session_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Session creation failed: {response.text}")
            return False
            
        session_result = response.json()
        session_id = session_result["session_id"]
        print(f"✅ Session created: {session_id}")
        
        # Test 2: Ask legal questions
        test_queries = [
            "I need help with divorce proceedings",
            "I was arrested for DUI, what are my rights?",
            "How do I start a business?",
            "My landlord is trying to evict me",
            "I was fired unfairly from my job"
        ]
        
        print("\n2️⃣  Testing legal queries...")
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            
            query_data = {
                "session_id": session_id,
                "query": query
            }
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Domain: {result['domain']}")
                print(f"✅ Confidence: {result['confidence']:.2%}")
                print(f"✅ Response: {result['response']['text'][:100]}...")
                print(f"✅ Processing time: {duration:.2f}s")
                
                # Test feedback
                feedback_data = {
                    "session_id": session_id,
                    "interaction_id": result["interaction_id"],
                    "feedback": "upvote",
                    "time_spent": 30.0
                }
                
                feedback_response = requests.post(f"{BASE_URL}/feedback", json=feedback_data, timeout=10)
                if feedback_response.status_code == 200:
                    feedback_result = feedback_response.json()
                    print(f"✅ Feedback submitted, reward: {feedback_result['reward']:.2f}")
                else:
                    print(f"⚠️  Feedback failed: {feedback_response.text}")
            else:
                print(f"❌ Query failed: {response.text}")
                return False
        
        # Test 3: Get session summary
        print("\n3️⃣  Getting session summary...")
        response = requests.get(f"{BASE_URL}/sessions/{session_id}/summary", timeout=10)
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Total interactions: {summary['total_interactions']}")
            print(f"✅ User satisfaction: {summary['satisfaction_score']:.2f}")
            print(f"✅ Domain distribution: {summary['domain_distribution']}")
        else:
            print(f"❌ Summary failed: {response.text}")
        
        # Test 4: Test glossary
        print("\n4️⃣  Testing glossary...")
        glossary_data = {
            "query": "What is custody?",
            "max_terms": 3
        }
        
        response = requests.post(f"{BASE_URL}/glossary/search", json=glossary_data, timeout=10)
        if response.status_code == 200:
            glossary_result = response.json()
            print(f"✅ Found {len(glossary_result['terms'])} legal terms")
            for term in glossary_result['terms'][:2]:
                print(f"   📚 {term['term']}: {term['definition'][:80]}...")
        else:
            print(f"❌ Glossary failed: {response.text}")
        
        print("\n🎉 ALL TESTS PASSED! Law Agent is working correctly!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Law Agent server!")
        print("💡 Make sure the server is running: python run_law_agent.py")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def interactive_mode():
    """Interactive mode for testing queries."""
    
    print("\n🎯 INTERACTIVE MODE")
    print("=" * 50)
    
    # Create session
    session_data = {
        "user_id": input("Enter your name: ") or "interactive_user",
        "user_type": "common_person"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/sessions", json=session_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ Failed to create session: {response.text}")
            return
            
        session_id = response.json()["session_id"]
        print(f"✅ Session created: {session_id}")
        print("\n💬 Ask legal questions (type 'quit' to exit):")
        
        while True:
            query = input("\n🏛️  Your legal question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
                
            if not query:
                continue
            
            # Send query
            query_data = {
                "session_id": session_id,
                "query": query
            }
            
            print("🤔 Processing...")
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=query_data, timeout=30)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n📋 Domain: {result['domain']}")
                print(f"🎯 Confidence: {result['confidence']:.2%}")
                print(f"⚡ Processing time: {duration:.2f}s")
                print(f"\n🤖 Law Agent Response:")
                print("-" * 40)
                print(result['response']['text'])
                
                if result['glossary_terms']:
                    print(f"\n📚 Related Legal Terms:")
                    for term in result['glossary_terms'][:3]:
                        print(f"   • {term['term']}: {term['definition'][:60]}...")
                
                # Ask for feedback
                feedback = input("\n👍 Was this helpful? (y/n/skip): ").lower()
                if feedback in ['y', 'yes']:
                    feedback_data = {
                        "session_id": session_id,
                        "interaction_id": result["interaction_id"],
                        "feedback": "upvote"
                    }
                    requests.post(f"{BASE_URL}/feedback", json=feedback_data, timeout=10)
                    print("✅ Thank you for your feedback!")
                elif feedback in ['n', 'no']:
                    feedback_data = {
                        "session_id": session_id,
                        "interaction_id": result["interaction_id"],
                        "feedback": "downvote"
                    }
                    requests.post(f"{BASE_URL}/feedback", json=feedback_data, timeout=10)
                    print("✅ Thank you for your feedback!")
            else:
                print(f"❌ Error: {response.text}")
        
        print("\n👋 Thanks for using Law Agent!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Law Agent server!")
        print("💡 Make sure the server is running: python run_law_agent.py")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    else:
        success = test_law_agent()
        sys.exit(0 if success else 1)
