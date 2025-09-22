#!/usr/bin/env python3
"""Comprehensive test for RL system, Q-table, and feedback system."""

import asyncio
import json
import requests
import time
from typing import Dict, List, Any
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "rl_test_user"

class RLSystemTester:
    """Comprehensive tester for RL system components."""
    
    def __init__(self):
        self.session_id = None
        self.interactions = []
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_api_health(self) -> bool:
        """Test API health and connectivity."""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("API Health Check", True, f"Status: {health_data.get('status')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_session_creation(self) -> bool:
        """Test session creation."""
        try:
            payload = {
                "user_id": TEST_USER_ID,
                "user_type": "common_person"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                self.log_test("Session Creation", True, f"Session ID: {self.session_id}")
                return True
            else:
                self.log_test("Session Creation", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Session Creation", False, f"Error: {str(e)}")
            return False
    
    def test_query_processing(self, query: str, expected_domain: str = None) -> Dict[str, Any]:
        """Test query processing and RL action selection."""
        try:
            payload = {
                "session_id": self.session_id,
                "query": query,
                "interaction_type": "query"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/v1/query",
                json=payload,
                timeout=15
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                interaction_id = data.get("interaction_id")
                domain = data.get("domain")
                confidence = data.get("confidence")
                
                # Store interaction for feedback testing
                self.interactions.append({
                    "interaction_id": interaction_id,
                    "query": query,
                    "domain": domain,
                    "confidence": confidence,
                    "response_time": response_time
                })
                
                test_passed = True
                details = f"Domain: {domain}, Confidence: {confidence:.3f}, Time: {response_time:.3f}s"
                
                if expected_domain and domain != expected_domain:
                    test_passed = False
                    details += f" (Expected: {expected_domain})"
                
                self.log_test(f"Query Processing: '{query[:30]}...'", test_passed, details)
                return data
            else:
                self.log_test(f"Query Processing: '{query[:30]}...'", False, f"Status: {response.status_code}")
                return {}
                
        except Exception as e:
            self.log_test(f"Query Processing: '{query[:30]}...'", False, f"Error: {str(e)}")
            return {}
    
    def test_feedback_submission(self, interaction_id: str, feedback: str, time_spent: float = None) -> bool:
        """Test feedback submission and RL learning."""
        try:
            payload = {
                "session_id": self.session_id,
                "interaction_id": interaction_id,
                "feedback": feedback
            }
            
            if time_spent:
                payload["time_spent"] = time_spent
            
            response = requests.post(
                f"{BASE_URL}/api/v1/feedback",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                reward = data.get("reward", 0)
                satisfaction = data.get("updated_satisfaction", 0)
                
                self.log_test(
                    f"Feedback Submission ({feedback})", 
                    True, 
                    f"Reward: {reward:.3f}, Satisfaction: {satisfaction:.3f}"
                )
                return True
            else:
                self.log_test(f"Feedback Submission ({feedback})", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test(f"Feedback Submission ({feedback})", False, f"Error: {str(e)}")
            return False
    
    def test_rl_learning_progression(self) -> bool:
        """Test RL learning by submitting multiple queries and feedback."""
        print("\n🧠 Testing RL Learning Progression...")
        
        # Test queries with expected domains
        test_cases = [
            ("I need help with my divorce", "family_law"),
            ("My employer fired me unfairly", "employment_law"),
            ("I want to write a will", "property_law"),
            ("Someone hit my car", "tort_law"),
            ("I need to review a contract", "contract_law")
        ]
        
        learning_results = []
        
        for i, (query, expected_domain) in enumerate(test_cases):
            print(f"\n--- Test Case {i+1}: {query} ---")
            
            # Process query
            result = self.test_query_processing(query, expected_domain)
            if not result:
                continue
            
            interaction_id = result.get("interaction_id")
            confidence = result.get("confidence", 0)
            
            # Simulate user feedback based on domain accuracy
            actual_domain = result.get("domain")
            if actual_domain == expected_domain:
                feedback = "upvote"
                time_spent = 30.0 + (confidence * 20)  # More time for confident answers
            else:
                feedback = "downvote"
                time_spent = 10.0  # Less time for wrong answers
            
            # Submit feedback
            feedback_success = self.test_feedback_submission(interaction_id, feedback, time_spent)
            
            learning_results.append({
                "query": query,
                "expected_domain": expected_domain,
                "actual_domain": actual_domain,
                "confidence": confidence,
                "feedback": feedback,
                "feedback_submitted": feedback_success
            })
            
            # Small delay to simulate real usage
            time.sleep(1)
        
        # Analyze learning progression
        successful_feedbacks = sum(1 for r in learning_results if r["feedback_submitted"])
        correct_domains = sum(1 for r in learning_results if r["actual_domain"] == r["expected_domain"])
        
        learning_success = successful_feedbacks >= 3 and correct_domains >= 3
        
        self.log_test(
            "RL Learning Progression",
            learning_success,
            f"Successful feedbacks: {successful_feedbacks}/5, Correct domains: {correct_domains}/5"
        )
        
        return learning_success
    
    def test_session_memory(self) -> bool:
        """Test session memory and state persistence."""
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/sessions/{self.session_id}/summary",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                total_interactions = data.get("total_interactions", 0)
                satisfaction_score = data.get("satisfaction_score", 0)
                
                memory_working = total_interactions > 0
                
                self.log_test(
                    "Session Memory",
                    memory_working,
                    f"Interactions: {total_interactions}, Satisfaction: {satisfaction_score:.3f}"
                )
                return memory_working
            else:
                self.log_test("Session Memory", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Session Memory", False, f"Error: {str(e)}")
            return False
    
    def test_q_table_persistence(self) -> bool:
        """Test Q-table learning and persistence."""
        print("\n📊 Testing Q-table Learning...")
        
        # Submit the same query multiple times with different feedback
        # to see if the system learns
        test_query = "I have a contract dispute with my vendor"
        
        results = []
        for i in range(3):
            print(f"\n--- Q-table Test {i+1} ---")
            
            result = self.test_query_processing(test_query)
            if result:
                interaction_id = result.get("interaction_id")
                confidence = result.get("confidence", 0)
                
                # Alternate feedback to test learning
                feedback = "upvote" if i % 2 == 0 else "downvote"
                self.test_feedback_submission(interaction_id, feedback, 25.0)
                
                results.append({
                    "iteration": i + 1,
                    "confidence": confidence,
                    "feedback": feedback
                })
            
            time.sleep(1)
        
        # Check if confidence changes over iterations (sign of learning)
        if len(results) >= 2:
            confidence_changed = any(
                abs(results[i]["confidence"] - results[i-1]["confidence"]) > 0.01
                for i in range(1, len(results))
            )
            
            self.log_test(
                "Q-table Learning",
                confidence_changed,
                f"Confidence variations detected: {confidence_changed}"
            )
            return confidence_changed
        else:
            self.log_test("Q-table Learning", False, "Insufficient data")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        print("🚀 Starting Comprehensive RL System Test")
        print("=" * 50)
        
        # Test sequence
        tests = [
            ("API Health", self.test_api_health),
            ("Session Creation", self.test_session_creation),
            ("RL Learning Progression", self.test_rl_learning_progression),
            ("Session Memory", self.test_session_memory),
            ("Q-table Persistence", self.test_q_table_persistence)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running {test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Overall assessment
        if success_rate >= 80:
            print(f"\n🎉 OVERALL: EXCELLENT - RL System is working properly!")
        elif success_rate >= 60:
            print(f"\n⚠️  OVERALL: GOOD - RL System is mostly working with minor issues")
        else:
            print(f"\n❌ OVERALL: NEEDS ATTENTION - RL System has significant issues")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "detailed_results": self.test_results,
            "interactions_tested": len(self.interactions),
            "session_id": self.session_id
        }


def main():
    """Run the comprehensive RL system test."""
    tester = RLSystemTester()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    with open("rl_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Test results saved to: rl_test_results.json")
    
    return results


if __name__ == "__main__":
    main()
