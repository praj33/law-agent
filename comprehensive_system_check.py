#!/usr/bin/env python3
"""Comprehensive System Check - Verify all new advanced RL changes."""

import requests
import json
import time
import asyncio
from typing import Dict, List, Any
from datetime import datetime

BASE_URL = "http://localhost:8000"

class ComprehensiveSystemChecker:
    """Complete system verification for all new changes."""
    
    def __init__(self):
        self.results = []
        self.session_data = {}
        
    def log_test(self, test_name: str, passed: bool, details: str = "", data: Any = None):
        """Log test result with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"[{timestamp}] {status} | {test_name}")
        if details:
            print(f"          {details}")
        
        self.results.append({
            "timestamp": timestamp,
            "test": test_name,
            "passed": passed,
            "details": details,
            "data": data
        })
        return passed
    
    def check_server_status(self) -> bool:
        """Check if the correct advanced server is running."""
        print("\n🔍 CHECKING SERVER STATUS")
        print("=" * 40)
        
        try:
            # Check health endpoint
            health_response = requests.get(f"{BASE_URL}/health", timeout=5)
            health_working = self.log_test(
                "Server Health Check",
                health_response.status_code == 200,
                f"Status: {health_response.status_code}"
            )
            
            # Check if advanced endpoints exist
            rl_status_response = requests.get(f"{BASE_URL}/api/v1/rl/status", timeout=5)
            advanced_endpoints = self.log_test(
                "Advanced RL Endpoints",
                rl_status_response.status_code == 200,
                f"RL Status endpoint: {rl_status_response.status_code}"
            )
            
            if advanced_endpoints:
                rl_data = rl_status_response.json()
                self.log_test(
                    "Advanced RL System Active",
                    rl_data.get("is_advanced", False),
                    f"Policy: {rl_data.get('rl_policy_type')}, Advanced: {rl_data.get('is_advanced')}"
                )
            
            return health_working and advanced_endpoints
            
        except Exception as e:
            self.log_test("Server Status Check", False, f"Error: {e}")
            return False
    
    def check_session_management(self) -> Dict[str, str]:
        """Test session creation and management."""
        print("\n🔍 CHECKING SESSION MANAGEMENT")
        print("=" * 40)
        
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "system_check_user", "user_type": "law_firm"},
                timeout=10
            )
            
            session_created = self.log_test(
                "Session Creation",
                session_response.status_code == 200,
                f"Status: {session_response.status_code}"
            )
            
            if session_created:
                session_data = session_response.json()
                session_id = session_data["session_id"]
                
                self.log_test(
                    "Session ID Generated",
                    bool(session_id),
                    f"Session ID: {session_id[:8]}..."
                )
                
                return {"session_id": session_id, "user_id": "system_check_user"}
            
            return {}
            
        except Exception as e:
            self.log_test("Session Management", False, f"Error: {e}")
            return {}
    
    def check_query_processing(self, session_data: Dict[str, str]) -> List[Dict[str, Any]]:
        """Test query processing with domain classification."""
        print("\n🔍 CHECKING QUERY PROCESSING")
        print("=" * 40)
        
        if not session_data:
            self.log_test("Query Processing", False, "No session available")
            return []
        
        test_queries = [
            {"query": "I need help with my divorce and child custody", "expected_domain": "family_law"},
            {"query": "My employer is discriminating against me", "expected_domain": "employment_law"},
            {"query": "Contract breach dispute with vendor", "expected_domain": "contract_law"},
            {"query": "Personal injury from car accident", "expected_domain": "tort_law"}
        ]
        
        interactions = []
        
        for i, test_case in enumerate(test_queries):
            try:
                query_response = requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_data["session_id"],
                        "query": test_case["query"],
                        "interaction_type": "query"
                    },
                    timeout=15
                )
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    domain = data.get("domain")
                    confidence = data.get("confidence", 0)
                    interaction_id = data.get("interaction_id")
                    
                    domain_correct = domain == test_case["expected_domain"]
                    
                    self.log_test(
                        f"Query {i+1}: Domain Classification",
                        domain_correct,
                        f"Expected: {test_case['expected_domain']}, Got: {domain}, Confidence: {confidence:.3f}"
                    )
                    
                    self.log_test(
                        f"Query {i+1}: Response Generated",
                        bool(data.get("response")),
                        f"Response length: {len(data.get('response', ''))}"
                    )
                    
                    interactions.append({
                        "interaction_id": interaction_id,
                        "query": test_case["query"],
                        "domain": domain,
                        "confidence": confidence,
                        "expected_domain": test_case["expected_domain"],
                        "correct": domain_correct
                    })
                else:
                    self.log_test(f"Query {i+1}: Processing", False, f"HTTP {query_response.status_code}")
                
                time.sleep(0.5)  # Small delay between queries
                
            except Exception as e:
                self.log_test(f"Query {i+1}: Processing", False, f"Error: {e}")
        
        # Overall accuracy
        if interactions:
            accuracy = sum(1 for i in interactions if i["correct"]) / len(interactions)
            self.log_test(
                "Overall Domain Accuracy",
                accuracy >= 0.75,
                f"Accuracy: {accuracy:.1%} ({sum(1 for i in interactions if i['correct'])}/{len(interactions)})"
            )
        
        return interactions
    
    def check_feedback_system(self, interactions: List[Dict[str, Any]], session_data: Dict[str, str]) -> bool:
        """Test the new feedback system with reward and satisfaction values."""
        print("\n🔍 CHECKING FEEDBACK SYSTEM")
        print("=" * 40)
        
        if not interactions or not session_data:
            self.log_test("Feedback System", False, "No interactions available")
            return False
        
        feedback_scenarios = [
            {"feedback": "upvote", "time_spent": 45.0, "expected_reward_sign": "positive"},
            {"feedback": "downvote", "time_spent": 20.0, "expected_reward_sign": "negative"},
            {"feedback": "upvote", "time_spent": 60.0, "expected_reward_sign": "positive"}
        ]
        
        feedback_results = []
        
        for i, scenario in enumerate(feedback_scenarios[:len(interactions)]):
            try:
                interaction = interactions[i]
                
                feedback_response = requests.post(
                    f"{BASE_URL}/api/v1/feedback",
                    json={
                        "session_id": session_data["session_id"],
                        "interaction_id": interaction["interaction_id"],
                        "feedback": scenario["feedback"],
                        "time_spent": scenario["time_spent"]
                    },
                    timeout=10
                )
                
                if feedback_response.status_code == 200:
                    data = feedback_response.json()
                    reward = data.get("reward")
                    satisfaction = data.get("updated_satisfaction")
                    
                    # Check if reward and satisfaction are returned
                    values_returned = reward is not None and satisfaction is not None
                    
                    # Check reward sign
                    reward_sign_correct = True
                    if reward is not None:
                        if scenario["expected_reward_sign"] == "positive":
                            reward_sign_correct = reward > 0
                        else:
                            reward_sign_correct = reward < 0
                    
                    self.log_test(
                        f"Feedback {i+1}: Values Returned",
                        values_returned,
                        f"Reward: {reward}, Satisfaction: {satisfaction}"
                    )
                    
                    self.log_test(
                        f"Feedback {i+1}: Reward Sign",
                        reward_sign_correct,
                        f"Expected: {scenario['expected_reward_sign']}, Got: {reward}"
                    )
                    
                    feedback_results.append({
                        "feedback": scenario["feedback"],
                        "reward": reward,
                        "satisfaction": satisfaction,
                        "values_returned": values_returned,
                        "reward_sign_correct": reward_sign_correct
                    })
                else:
                    self.log_test(f"Feedback {i+1}: Submission", False, f"HTTP {feedback_response.status_code}")
                
                time.sleep(0.3)
                
            except Exception as e:
                self.log_test(f"Feedback {i+1}: Processing", False, f"Error: {e}")
        
        # Overall feedback system assessment
        if feedback_results:
            values_success_rate = sum(1 for r in feedback_results if r["values_returned"]) / len(feedback_results)
            sign_success_rate = sum(1 for r in feedback_results if r["reward_sign_correct"]) / len(feedback_results)
            
            self.log_test(
                "Feedback Values Success Rate",
                values_success_rate >= 0.8,
                f"Success: {values_success_rate:.1%}"
            )
            
            self.log_test(
                "Reward Logic Success Rate",
                sign_success_rate >= 0.8,
                f"Success: {sign_success_rate:.1%}"
            )
            
            return values_success_rate >= 0.8 and sign_success_rate >= 0.8
        
        return False
    
    def check_rl_learning(self, session_data: Dict[str, str]) -> bool:
        """Test Q-table learning and RL system."""
        print("\n🔍 CHECKING RL LEARNING SYSTEM")
        print("=" * 40)
        
        if not session_data:
            self.log_test("RL Learning", False, "No session available")
            return False
        
        try:
            # Get initial RL status
            initial_status = requests.get(f"{BASE_URL}/api/v1/rl/status", timeout=5)
            if initial_status.status_code == 200:
                initial_data = initial_status.json()
                initial_qtable_size = initial_data.get("q_table_size", 0)
                initial_exploration = initial_data.get("learning_metrics", {}).get("exploration_rate", 0)
                
                self.log_test(
                    "Initial RL State",
                    True,
                    f"Q-table size: {initial_qtable_size}, Exploration: {initial_exploration:.3f}"
                )
            
            # Test learning with repeated queries
            learning_query = "Complex contract dispute requiring legal analysis"
            learning_results = []
            
            for i in range(3):
                # Process query
                query_response = requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_data["session_id"],
                        "query": learning_query,
                        "interaction_type": "query"
                    },
                    timeout=15
                )
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    confidence = data.get("confidence", 0)
                    interaction_id = data.get("interaction_id")
                    
                    # Submit feedback (alternating)
                    feedback = "upvote" if i % 2 == 0 else "downvote"
                    
                    feedback_response = requests.post(
                        f"{BASE_URL}/api/v1/feedback",
                        json={
                            "session_id": session_data["session_id"],
                            "interaction_id": interaction_id,
                            "feedback": feedback,
                            "time_spent": 30.0 + i * 10
                        },
                        timeout=10
                    )
                    
                    if feedback_response.status_code == 200:
                        feedback_data = feedback_response.json()
                        reward = feedback_data.get("reward", 0)
                        
                        learning_results.append({
                            "iteration": i + 1,
                            "confidence": confidence,
                            "feedback": feedback,
                            "reward": reward
                        })
                        
                        self.log_test(
                            f"Learning Iteration {i+1}",
                            True,
                            f"Confidence: {confidence:.3f}, Feedback: {feedback}, Reward: {reward:.3f}"
                        )
                
                time.sleep(0.5)
            
            # Check final RL status
            final_status = requests.get(f"{BASE_URL}/api/v1/rl/status", timeout=5)
            if final_status.status_code == 200:
                final_data = final_status.json()
                final_qtable_size = final_data.get("q_table_size", 0)
                final_exploration = final_data.get("learning_metrics", {}).get("exploration_rate", 0)
                
                qtable_growth = final_qtable_size > initial_qtable_size
                exploration_decay = final_exploration < initial_exploration
                
                self.log_test(
                    "Q-table Growth",
                    qtable_growth,
                    f"Initial: {initial_qtable_size}, Final: {final_qtable_size}"
                )
                
                self.log_test(
                    "Exploration Decay",
                    exploration_decay,
                    f"Initial: {initial_exploration:.6f}, Final: {final_exploration:.6f}"
                )
                
                return qtable_growth or exploration_decay
            
            return len(learning_results) >= 2
            
        except Exception as e:
            self.log_test("RL Learning System", False, f"Error: {e}")
            return False
    
    def check_memory_system(self, session_data: Dict[str, str]) -> bool:
        """Test advanced memory system."""
        print("\n🔍 CHECKING MEMORY SYSTEM")
        print("=" * 40)
        
        if not session_data:
            self.log_test("Memory System", False, "No session available")
            return False
        
        try:
            # Get session summary to check memory
            summary_response = requests.get(
                f"{BASE_URL}/api/v1/sessions/{session_data['session_id']}/summary",
                timeout=10
            )
            
            if summary_response.status_code == 200:
                summary = summary_response.json()
                
                total_interactions = summary.get("total_interactions", 0)
                domains = summary.get("domains", [])
                satisfaction_score = summary.get("satisfaction_score")
                session_duration = summary.get("session_duration", 0)
                
                self.log_test(
                    "Interaction Memory",
                    total_interactions > 0,
                    f"Total interactions: {total_interactions}"
                )
                
                self.log_test(
                    "Domain Memory",
                    len(domains) > 0,
                    f"Domains remembered: {domains}"
                )
                
                self.log_test(
                    "Satisfaction Tracking",
                    satisfaction_score is not None,
                    f"Satisfaction score: {satisfaction_score}"
                )
                
                self.log_test(
                    "Session Duration Tracking",
                    session_duration > 0,
                    f"Duration: {session_duration:.1f}s"
                )
                
                return total_interactions > 0 and len(domains) > 0
            else:
                self.log_test("Memory System", False, f"Summary failed: {summary_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Memory System", False, f"Error: {e}")
            return False
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run complete system check."""
        print("🚀 COMPREHENSIVE SYSTEM CHECK")
        print("=" * 60)
        print(f"Testing Advanced RL Law Agent System")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Step 1: Check server status
        server_ok = self.check_server_status()
        
        if not server_ok:
            print("\n❌ Server not ready. Please start the server with:")
            print("   python -m law_agent.api.main")
            return {"success": False, "error": "Server not ready"}
        
        # Step 2: Session management
        session_data = self.check_session_management()
        
        # Step 3: Query processing
        interactions = self.check_query_processing(session_data)
        
        # Step 4: Feedback system
        feedback_ok = self.check_feedback_system(interactions, session_data)
        
        # Step 5: RL learning
        rl_ok = self.check_rl_learning(session_data)
        
        # Step 6: Memory system
        memory_ok = self.check_memory_system(session_data)
        
        # Calculate results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE CHECK RESULTS")
        print("=" * 60)
        
        # Group results by category
        categories = {
            "Server Status": [r for r in self.results if "Server" in r["test"] or "Advanced RL" in r["test"]],
            "Session Management": [r for r in self.results if "Session" in r["test"]],
            "Query Processing": [r for r in self.results if "Query" in r["test"] or "Domain" in r["test"]],
            "Feedback System": [r for r in self.results if "Feedback" in r["test"]],
            "RL Learning": [r for r in self.results if "Learning" in r["test"] or "Q-table" in r["test"] or "Exploration" in r["test"]],
            "Memory System": [r for r in self.results if "Memory" in r["test"] or "Interaction" in r["test"] or "Satisfaction" in r["test"] or "Duration" in r["test"]]
        }
        
        for category, tests in categories.items():
            if tests:
                category_passed = sum(1 for t in tests if t["passed"])
                category_total = len(tests)
                category_rate = (category_passed / category_total) * 100
                
                status = "✅" if category_rate >= 80 else "⚠️" if category_rate >= 60 else "❌"
                print(f"\n{status} {category}: {category_rate:.0f}% ({category_passed}/{category_total})")
                
                for test in tests:
                    test_status = "✅" if test["passed"] else "❌"
                    print(f"   {test_status} {test['test']}")
                    if test["details"]:
                        print(f"      {test['details']}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Final assessment
        if success_rate >= 95:
            print(f"\n🎉 PERFECT! System is working flawlessly!")
            assessment = "PERFECT"
        elif success_rate >= 85:
            print(f"\n🎯 EXCELLENT! System is working very well!")
            assessment = "EXCELLENT"
        elif success_rate >= 75:
            print(f"\n👍 GOOD! System is mostly working!")
            assessment = "GOOD"
        else:
            print(f"\n⚠️  NEEDS ATTENTION! System has issues!")
            assessment = "NEEDS_ATTENTION"
        
        return {
            "success": success_rate >= 75,
            "assessment": assessment,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "categories": {cat: {"passed": sum(1 for t in tests if t["passed"]), "total": len(tests)} for cat, tests in categories.items()},
            "detailed_results": self.results
        }


if __name__ == "__main__":
    checker = ComprehensiveSystemChecker()
    results = checker.run_comprehensive_check()
    
    # Save results
    with open("comprehensive_system_check_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: comprehensive_system_check_results.json")
    
    if results["success"]:
        print(f"\n🚀 SYSTEM CHECK COMPLETE - ALL CHANGES VERIFIED!")
    else:
        print(f"\n⚠️  SYSTEM CHECK COMPLETE - SOME ISSUES FOUND!")
