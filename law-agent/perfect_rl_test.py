#!/usr/bin/env python3
"""Perfect RL System Test - Comprehensive verification of all components."""

import requests
import json
import time
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

class PerfectRLTester:
    """Comprehensive tester for perfect RL system."""
    
    def __init__(self):
        self.test_results = []
        self.session_id = None
        
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result with details."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_rl_system_status(self) -> bool:
        """Test RL system status endpoint."""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/rl/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check key components
                is_advanced = data.get("is_advanced", False)
                memory_size = data.get("memory_system", {}).get("episodic_memory_size", 0)
                q_table_size = data.get("q_table_size", 0)
                
                self.log_result(
                    "RL System Status",
                    is_advanced,
                    f"Advanced: {is_advanced}, Memory: {memory_size}, Q-table: {q_table_size}"
                )
                return is_advanced
            else:
                self.log_result("RL System Status", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("RL System Status", False, f"Error: {e}")
            return False
    
    def test_reward_calculation(self) -> bool:
        """Test reward calculation and visibility."""
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "reward_test", "user_type": "common_person"}
            )
            
            if session_response.status_code != 200:
                self.log_result("Reward Calculation", False, "Session creation failed")
                return False
            
            session_id = session_response.json()["session_id"]
            
            # Process query
            query_response = requests.post(
                f"{BASE_URL}/api/v1/query",
                json={
                    "session_id": session_id,
                    "query": "I need help with my divorce",
                    "interaction_type": "query"
                }
            )
            
            if query_response.status_code != 200:
                self.log_result("Reward Calculation", False, "Query processing failed")
                return False
            
            interaction_id = query_response.json()["interaction_id"]
            
            # Submit feedback and check reward
            feedback_response = requests.post(
                f"{BASE_URL}/api/v1/feedback",
                json={
                    "session_id": session_id,
                    "interaction_id": interaction_id,
                    "feedback": "upvote",
                    "time_spent": 30.0
                }
            )
            
            if feedback_response.status_code == 200:
                data = feedback_response.json()
                reward = data.get("reward", None)
                satisfaction = data.get("updated_satisfaction", None)
                
                reward_visible = reward is not None and reward != 0
                satisfaction_visible = satisfaction is not None
                
                self.log_result(
                    "Reward Calculation",
                    reward_visible and satisfaction_visible,
                    f"Reward: {reward}, Satisfaction: {satisfaction}"
                )
                return reward_visible and satisfaction_visible
            else:
                self.log_result("Reward Calculation", False, f"HTTP {feedback_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Reward Calculation", False, f"Error: {e}")
            return False
    
    def test_q_table_learning(self) -> bool:
        """Test Q-table learning with multiple interactions."""
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "qtable_test", "user_type": "law_firm"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Test same query multiple times with different feedback
            query = "Contract breach analysis needed"
            rewards = []
            
            for i in range(3):
                # Process query
                query_response = requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_id,
                        "query": query,
                        "interaction_type": "query"
                    }
                )
                
                if query_response.status_code == 200:
                    interaction_id = query_response.json()["interaction_id"]
                    confidence = query_response.json()["confidence"]
                    
                    # Alternate feedback
                    feedback = "upvote" if i % 2 == 0 else "downvote"
                    
                    feedback_response = requests.post(
                        f"{BASE_URL}/api/v1/feedback",
                        json={
                            "session_id": session_id,
                            "interaction_id": interaction_id,
                            "feedback": feedback,
                            "time_spent": 20.0 + i * 5
                        }
                    )
                    
                    if feedback_response.status_code == 200:
                        reward = feedback_response.json().get("reward", 0)
                        rewards.append(reward)
                    
                    time.sleep(0.5)  # Small delay
            
            # Check if rewards vary (sign of learning)
            reward_variation = len(set(rewards)) > 1 if rewards else False
            
            self.log_result(
                "Q-table Learning",
                reward_variation,
                f"Rewards: {rewards}, Variation: {reward_variation}"
            )
            return reward_variation
            
        except Exception as e:
            self.log_result("Q-table Learning", False, f"Error: {e}")
            return False
    
    def test_session_memory(self) -> bool:
        """Test session memory and summary."""
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "memory_test", "user_type": "common_person"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Process multiple queries
            queries = [
                "I need help with divorce",
                "What about child custody?",
                "How much will this cost?"
            ]
            
            for query in queries:
                requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_id,
                        "query": query,
                        "interaction_type": "query"
                    }
                )
                time.sleep(0.2)
            
            # Get session summary
            summary_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/summary")
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                total_interactions = data.get("total_interactions", 0)
                
                memory_working = total_interactions >= len(queries)
                
                self.log_result(
                    "Session Memory",
                    memory_working,
                    f"Interactions: {total_interactions}, Expected: {len(queries)}"
                )
                return memory_working
            else:
                self.log_result("Session Memory", False, f"HTTP {summary_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Session Memory", False, f"Error: {e}")
            return False
    
    def test_advanced_feedback(self) -> bool:
        """Test advanced multi-dimensional feedback."""
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "advanced_feedback_test", "user_type": "common_person"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Process query
            query_response = requests.post(
                f"{BASE_URL}/api/v1/query",
                json={
                    "session_id": session_id,
                    "query": "Employment discrimination case",
                    "interaction_type": "query"
                }
            )
            
            interaction_id = query_response.json()["interaction_id"]
            
            # Submit advanced feedback
            advanced_feedback_response = requests.post(
                f"{BASE_URL}/api/v1/feedback/advanced",
                json={
                    "session_id": session_id,
                    "interaction_id": interaction_id,
                    "response_quality": 4,
                    "legal_accuracy": 5,
                    "helpfulness": 4,
                    "clarity": 3,
                    "completeness": 4,
                    "time_spent": 45.0,
                    "overall_satisfaction": "upvote",
                    "specific_feedback": "Great analysis!",
                    "improvement_suggestions": "More examples would help",
                    "would_recommend": True
                }
            )
            
            if advanced_feedback_response.status_code == 200:
                data = advanced_feedback_response.json()
                reward = data.get("reward", 0)
                learning_impact = data.get("learning_impact", {})
                
                advanced_working = reward != 0 and learning_impact.get("will_improve_responses", False)
                
                self.log_result(
                    "Advanced Feedback",
                    advanced_working,
                    f"Reward: {reward}, Will improve: {learning_impact.get('will_improve_responses')}"
                )
                return advanced_working
            else:
                self.log_result("Advanced Feedback", False, f"HTTP {advanced_feedback_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Advanced Feedback", False, f"Error: {e}")
            return False
    
    def run_perfect_test(self) -> Dict[str, Any]:
        """Run comprehensive perfect RL test."""
        print("🚀 PERFECT RL SYSTEM TEST")
        print("=" * 50)
        
        # Wait for server to be ready
        print("⏳ Waiting for server to be ready...")
        time.sleep(3)
        
        # Run all tests
        tests = [
            ("RL System Status", self.test_rl_system_status),
            ("Reward Calculation", self.test_reward_calculation),
            ("Q-table Learning", self.test_q_table_learning),
            ("Session Memory", self.test_session_memory),
            ("Advanced Feedback", self.test_advanced_feedback)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing {test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {e}")
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📊 PERFECT RL TEST RESULTS")
        print("=" * 50)
        
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        print(f"\n📈 SUMMARY:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print(f"\n🎉 PERFECT! RL System is working flawlessly!")
        elif success_rate >= 80:
            print(f"\n✅ EXCELLENT! RL System is working very well!")
        elif success_rate >= 70:
            print(f"\n👍 GOOD! RL System is working with minor issues!")
        else:
            print(f"\n⚠️  NEEDS WORK! RL System has significant issues!")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results": self.test_results
        }


if __name__ == "__main__":
    tester = PerfectRLTester()
    results = tester.run_perfect_test()
    
    # Save results
    with open("perfect_rl_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: perfect_rl_test_results.json")
