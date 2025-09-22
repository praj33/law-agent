#!/usr/bin/env python3
"""Test feedback response fix."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_feedback_flow():
    """Test complete feedback flow with detailed logging."""
    
    print("🧪 TESTING FEEDBACK RESPONSE FIX")
    print("=" * 40)
    
    try:
        # Step 1: Create session
        print("\n1️⃣ Creating session...")
        session_response = requests.post(
            f"{BASE_URL}/api/v1/sessions",
            json={"user_id": "feedback_fix_test", "user_type": "common_person"}
        )
        
        if session_response.status_code != 200:
            print(f"❌ Session creation failed: {session_response.status_code}")
            print(f"Response: {session_response.text}")
            return False
        
        session_data = session_response.json()
        session_id = session_data["session_id"]
        print(f"✅ Session created: {session_id}")
        
        # Step 2: Process query
        print("\n2️⃣ Processing query...")
        query_response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "session_id": session_id,
                "query": "I need help with my divorce proceedings and child custody",
                "interaction_type": "query"
            }
        )
        
        if query_response.status_code != 200:
            print(f"❌ Query failed: {query_response.status_code}")
            print(f"Response: {query_response.text}")
            return False
        
        query_data = query_response.json()
        interaction_id = query_data["interaction_id"]
        domain = query_data["domain"]
        confidence = query_data["confidence"]
        
        print(f"✅ Query processed:")
        print(f"   Interaction ID: {interaction_id}")
        print(f"   Domain: {domain}")
        print(f"   Confidence: {confidence}")
        
        # Step 3: Submit feedback and check response
        print("\n3️⃣ Submitting feedback...")
        feedback_response = requests.post(
            f"{BASE_URL}/api/v1/feedback",
            json={
                "session_id": session_id,
                "interaction_id": interaction_id,
                "feedback": "upvote",
                "time_spent": 45.5
            }
        )
        
        print(f"Feedback response status: {feedback_response.status_code}")
        print(f"Feedback response headers: {dict(feedback_response.headers)}")
        print(f"Feedback response text: {feedback_response.text}")
        
        if feedback_response.status_code == 200:
            try:
                feedback_data = feedback_response.json()
                print(f"\n✅ Feedback response parsed:")
                print(f"   Status: {feedback_data.get('status')}")
                print(f"   Reward: {feedback_data.get('reward')}")
                print(f"   Updated Satisfaction: {feedback_data.get('updated_satisfaction')}")
                print(f"   Message: {feedback_data.get('message')}")
                
                # Check if reward and satisfaction are present and non-zero
                reward = feedback_data.get('reward')
                satisfaction = feedback_data.get('updated_satisfaction')
                
                if reward is not None and satisfaction is not None:
                    print(f"\n🎯 SUCCESS: Reward and satisfaction values returned!")
                    print(f"   Reward: {reward} (type: {type(reward)})")
                    print(f"   Satisfaction: {satisfaction} (type: {type(satisfaction)})")
                    return True
                else:
                    print(f"\n⚠️  ISSUE: Missing reward or satisfaction values")
                    print(f"   Reward present: {reward is not None}")
                    print(f"   Satisfaction present: {satisfaction is not None}")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw response: {feedback_response.text}")
                return False
        else:
            print(f"❌ Feedback failed: {feedback_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_feedback_scenarios():
    """Test multiple feedback scenarios."""
    
    print("\n🔄 TESTING MULTIPLE FEEDBACK SCENARIOS")
    print("=" * 40)
    
    scenarios = [
        {"feedback": "upvote", "time_spent": 30.0, "expected_reward_sign": "positive"},
        {"feedback": "downvote", "time_spent": 15.0, "expected_reward_sign": "negative"},
        {"feedback": "upvote", "time_spent": 60.0, "expected_reward_sign": "positive"}
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios):
        print(f"\n📋 Scenario {i+1}: {scenario['feedback']} feedback")
        
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": f"scenario_test_{i}", "user_type": "law_firm"}
            )
            
            if session_response.status_code != 200:
                print(f"   ❌ Session creation failed")
                continue
            
            session_id = session_response.json()["session_id"]
            
            # Process query
            query_response = requests.post(
                f"{BASE_URL}/api/v1/query",
                json={
                    "session_id": session_id,
                    "query": f"Contract law question {i+1}",
                    "interaction_type": "query"
                }
            )
            
            if query_response.status_code != 200:
                print(f"   ❌ Query failed")
                continue
            
            interaction_id = query_response.json()["interaction_id"]
            
            # Submit feedback
            feedback_response = requests.post(
                f"{BASE_URL}/api/v1/feedback",
                json={
                    "session_id": session_id,
                    "interaction_id": interaction_id,
                    "feedback": scenario["feedback"],
                    "time_spent": scenario["time_spent"]
                }
            )
            
            if feedback_response.status_code == 200:
                try:
                    data = feedback_response.json()
                    reward = data.get("reward")
                    satisfaction = data.get("updated_satisfaction")
                    
                    result = {
                        "scenario": i+1,
                        "feedback": scenario["feedback"],
                        "reward": reward,
                        "satisfaction": satisfaction,
                        "success": reward is not None and satisfaction is not None
                    }
                    
                    results.append(result)
                    
                    status = "✅" if result["success"] else "❌"
                    print(f"   {status} Reward: {reward}, Satisfaction: {satisfaction}")
                    
                except json.JSONDecodeError:
                    print(f"   ❌ JSON decode error")
            else:
                print(f"   ❌ Feedback failed: {feedback_response.status_code}")
            
            time.sleep(0.5)  # Small delay between scenarios
            
        except Exception as e:
            print(f"   ❌ Scenario error: {e}")
    
    # Analyze results
    successful_scenarios = sum(1 for r in results if r["success"])
    total_scenarios = len(results)
    
    print(f"\n📊 SCENARIO RESULTS:")
    print(f"   Successful: {successful_scenarios}/{total_scenarios}")
    
    for result in results:
        status = "✅" if result["success"] else "❌"
        print(f"   {status} Scenario {result['scenario']}: {result['feedback']} → R:{result['reward']}, S:{result['satisfaction']}")
    
    return successful_scenarios == total_scenarios

if __name__ == "__main__":
    print("🚀 FEEDBACK RESPONSE FIX TEST")
    print("=" * 50)
    
    # Wait for server to be ready
    time.sleep(2)
    
    # Test basic feedback flow
    basic_working = test_complete_feedback_flow()
    
    # Test multiple scenarios
    scenarios_working = test_multiple_feedback_scenarios()
    
    print("\n" + "=" * 50)
    print("📊 FEEDBACK FIX TEST RESULTS")
    print("=" * 50)
    print(f"✅ Basic Feedback Flow: {'WORKING' if basic_working else 'ISSUES'}")
    print(f"✅ Multiple Scenarios: {'WORKING' if scenarios_working else 'ISSUES'}")
    
    if basic_working and scenarios_working:
        print(f"\n🎉 PERFECT! Feedback response is working correctly!")
        print(f"🎯 Reward and satisfaction values are being returned!")
    elif basic_working:
        print(f"\n👍 GOOD! Basic feedback is working!")
    else:
        print(f"\n⚠️  NEEDS ATTENTION! Feedback response has issues!")
    
    print(f"\n💡 Check server logs for detailed feedback processing information")
