#!/usr/bin/env python3
"""Quick System Check - Fast verification of key components."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def quick_check():
    """Quick verification of all key system components."""
    
    print("⚡ QUICK SYSTEM CHECK")
    print("=" * 30)
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 30)
    
    results = []
    
    # 1. Server Health
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=3)
        server_ok = health.status_code == 200
        print(f"🔍 Server Health: {'✅ OK' if server_ok else '❌ FAIL'}")
        results.append(("Server", server_ok))
    except:
        print(f"🔍 Server Health: ❌ FAIL (Not responding)")
        results.append(("Server", False))
        return
    
    # 2. Advanced RL System
    try:
        rl_status = requests.get(f"{BASE_URL}/api/v1/rl/status", timeout=3)
        if rl_status.status_code == 200:
            rl_data = rl_status.json()
            advanced = rl_data.get("is_advanced", False)
            qtable_size = rl_data.get("q_table_size", 0)
            exploration = rl_data.get("learning_metrics", {}).get("exploration_rate", 0)
            
            print(f"🧠 Advanced RL: {'✅ ACTIVE' if advanced else '❌ BASIC'}")
            print(f"   Q-table: {qtable_size} states, Exploration: {exploration:.3f}")
            results.append(("RL System", advanced))
        else:
            print(f"🧠 Advanced RL: ❌ FAIL (HTTP {rl_status.status_code})")
            results.append(("RL System", False))
    except:
        print(f"🧠 Advanced RL: ❌ FAIL (Error)")
        results.append(("RL System", False))
    
    # 3. Session + Query + Feedback Flow
    try:
        # Create session
        session_resp = requests.post(
            f"{BASE_URL}/api/v1/sessions",
            json={"user_id": "quick_test", "user_type": "common_person"},
            timeout=5
        )
        
        if session_resp.status_code == 200:
            session_id = session_resp.json()["session_id"]
            print(f"📝 Session: ✅ CREATED ({session_id[:8]}...)")
            
            # Process query
            query_resp = requests.post(
                f"{BASE_URL}/api/v1/query",
                json={
                    "session_id": session_id,
                    "query": "Quick test divorce question",
                    "interaction_type": "query"
                },
                timeout=10
            )
            
            if query_resp.status_code == 200:
                query_data = query_resp.json()
                domain = query_data.get("domain")
                confidence = query_data.get("confidence", 0)
                interaction_id = query_data.get("interaction_id")
                
                print(f"🔍 Query: ✅ PROCESSED (Domain: {domain}, Confidence: {confidence:.3f})")
                results.append(("Query Processing", True))
                
                # Submit feedback
                feedback_resp = requests.post(
                    f"{BASE_URL}/api/v1/feedback",
                    json={
                        "session_id": session_id,
                        "interaction_id": interaction_id,
                        "feedback": "upvote",
                        "time_spent": 25.0
                    },
                    timeout=5
                )
                
                if feedback_resp.status_code == 200:
                    feedback_data = feedback_resp.json()
                    reward = feedback_data.get("reward")
                    satisfaction = feedback_data.get("updated_satisfaction")
                    
                    if reward is not None and satisfaction is not None:
                        print(f"💝 Feedback: ✅ WORKING (Reward: {reward:.3f}, Satisfaction: {satisfaction:.3f})")
                        results.append(("Feedback System", True))
                    else:
                        print(f"💝 Feedback: ❌ VALUES MISSING")
                        results.append(("Feedback System", False))
                else:
                    print(f"💝 Feedback: ❌ FAIL (HTTP {feedback_resp.status_code})")
                    results.append(("Feedback System", False))
            else:
                print(f"🔍 Query: ❌ FAIL (HTTP {query_resp.status_code})")
                results.append(("Query Processing", False))
        else:
            print(f"📝 Session: ❌ FAIL (HTTP {session_resp.status_code})")
            results.append(("Session", False))
    except Exception as e:
        print(f"🔄 Flow Test: ❌ FAIL ({e})")
        results.append(("Complete Flow", False))
    
    # Results Summary
    print("\n" + "=" * 30)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"📊 RESULTS: {passed}/{total} ({success_rate:.0f}%)")
    
    if success_rate >= 90:
        print("🎉 PERFECT! All systems working!")
    elif success_rate >= 75:
        print("👍 GOOD! Most systems working!")
    else:
        print("⚠️  ISSUES! Some systems need attention!")
    
    return success_rate >= 75

if __name__ == "__main__":
    quick_check()
