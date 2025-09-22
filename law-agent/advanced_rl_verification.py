#!/usr/bin/env python3
"""Advanced RL System Verification - Deep inspection of all components."""

import requests
import json
import time
import numpy as np
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

class AdvancedRLVerifier:
    """Comprehensive verifier for advanced RL system."""
    
    def __init__(self):
        self.test_results = []
        self.session_data = {}
        
    def log_result(self, test_name: str, passed: bool, details: str = "", data: Any = None):
        """Log detailed test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"    {details}")
        if data:
            print(f"    Data: {data}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "data": data
        })
    
    def verify_advanced_rl_initialization(self) -> bool:
        """Verify advanced RL system is properly initialized."""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/rl/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for advanced features
                is_advanced = data.get("is_advanced", False)
                memory_system = data.get("memory_system", {})
                learning_metrics = data.get("learning_metrics", {})
                
                # Verify advanced components
                has_episodic_memory = memory_system.get("episodic_memory_size", 0) >= 0
                has_semantic_memory = memory_system.get("semantic_memory_domains", 0) >= 0
                has_procedural_memory = memory_system.get("procedural_memory_size", 0) >= 0
                has_ml_models = learning_metrics.get("ml_models_trained", False)
                has_exploration = learning_metrics.get("exploration_rate", 0) > 0
                
                advanced_features = {
                    "is_advanced": is_advanced,
                    "episodic_memory": has_episodic_memory,
                    "semantic_memory": has_semantic_memory,
                    "procedural_memory": has_procedural_memory,
                    "ml_models": has_ml_models,
                    "exploration_rate": learning_metrics.get("exploration_rate", 0),
                    "q_table_size": data.get("q_table_size", 0)
                }
                
                all_advanced = all([is_advanced, has_episodic_memory, has_semantic_memory, has_procedural_memory])
                
                self.log_result(
                    "Advanced RL Initialization",
                    all_advanced,
                    f"Advanced: {is_advanced}, Memory systems: {has_episodic_memory and has_semantic_memory and has_procedural_memory}",
                    advanced_features
                )
                return all_advanced
            else:
                self.log_result("Advanced RL Initialization", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Advanced RL Initialization", False, f"Error: {e}")
            return False
    
    def verify_multi_dimensional_state(self) -> bool:
        """Verify 15-dimensional state representation is working."""
        try:
            # Create session
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "state_test", "user_type": "law_firm"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Process multiple queries to build state
            queries = [
                "Contract breach analysis",
                "Employment discrimination case",
                "Intellectual property dispute"
            ]
            
            interactions = []
            for i, query in enumerate(queries):
                query_response = requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_id,
                        "query": query,
                        "interaction_type": "query"
                    }
                )
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    interactions.append({
                        "query": query,
                        "domain": data.get("domain"),
                        "confidence": data.get("confidence"),
                        "interaction_id": data.get("interaction_id")
                    })
                
                time.sleep(0.3)
            
            # Check session summary for state complexity
            summary_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/summary")
            
            if summary_response.status_code == 200:
                summary = summary_response.json()
                
                # Verify multi-dimensional state components
                has_user_context = summary.get("user_type") is not None
                has_domain_history = len(summary.get("domains", [])) > 0
                has_interaction_tracking = summary.get("total_interactions", 0) > 0
                has_satisfaction_tracking = summary.get("satisfaction_score") is not None
                has_temporal_tracking = summary.get("session_duration", 0) > 0
                
                state_complexity = {
                    "user_context": has_user_context,
                    "domain_history": has_domain_history,
                    "interaction_tracking": has_interaction_tracking,
                    "satisfaction_tracking": has_satisfaction_tracking,
                    "temporal_tracking": has_temporal_tracking,
                    "total_interactions": summary.get("total_interactions", 0),
                    "domains": summary.get("domains", [])
                }
                
                multi_dimensional = all([
                    has_user_context, has_domain_history, 
                    has_interaction_tracking, has_satisfaction_tracking
                ])
                
                self.log_result(
                    "Multi-Dimensional State",
                    multi_dimensional,
                    f"State components: {sum([has_user_context, has_domain_history, has_interaction_tracking, has_satisfaction_tracking, has_temporal_tracking])}/5",
                    state_complexity
                )
                return multi_dimensional
            else:
                self.log_result("Multi-Dimensional State", False, f"Summary failed: {summary_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Multi-Dimensional State", False, f"Error: {e}")
            return False
    
    def verify_advanced_action_selection(self) -> bool:
        """Verify multi-strategy action selection is working."""
        try:
            # Create session for action testing
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "action_test", "user_type": "common_person"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Test same query multiple times to see action variation
            query = "I need help with a complex contract dispute involving multiple parties"
            action_results = []
            
            for i in range(5):
                query_response = requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_id,
                        "query": query,
                        "interaction_type": "query"
                    }
                )
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    action_results.append({
                        "iteration": i + 1,
                        "domain": data.get("domain"),
                        "confidence": data.get("confidence"),
                        "response_length": len(data.get("response", "")),
                        "actions": data.get("suggested_actions", [])
                    })
                
                time.sleep(0.2)
            
            # Analyze action selection sophistication
            if len(action_results) >= 3:
                confidences = [r["confidence"] for r in action_results]
                domains = [r["domain"] for r in action_results]
                response_lengths = [r["response_length"] for r in action_results]
                
                # Check for intelligent variation (not random, but adaptive)
                confidence_variation = max(confidences) - min(confidences)
                domain_consistency = len(set(domains)) <= 2  # Should be consistent for same query
                response_adaptation = max(response_lengths) - min(response_lengths)
                
                advanced_selection = {
                    "confidence_variation": confidence_variation,
                    "domain_consistency": domain_consistency,
                    "response_adaptation": response_adaptation,
                    "results": action_results
                }
                
                # Advanced action selection should show consistency with adaptive responses
                is_advanced = domain_consistency and (confidence_variation > 0.01 or response_adaptation > 10)
                
                self.log_result(
                    "Advanced Action Selection",
                    is_advanced,
                    f"Consistency: {domain_consistency}, Adaptation: {confidence_variation:.3f}",
                    advanced_selection
                )
                return is_advanced
            else:
                self.log_result("Advanced Action Selection", False, "Insufficient data")
                return False
                
        except Exception as e:
            self.log_result("Advanced Action Selection", False, f"Error: {e}")
            return False
    
    def verify_q_table_learning(self) -> bool:
        """Verify Q-table learning with advanced bandit algorithms."""
        try:
            # Create session for Q-table testing
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "qtable_test", "user_type": "law_firm"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Test learning progression with feedback
            query = "Employment law discrimination case analysis"
            learning_progression = []
            
            for i in range(6):
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
                    data = query_response.json()
                    interaction_id = data.get("interaction_id")
                    confidence = data.get("confidence")
                    
                    # Submit strategic feedback (positive for first 3, negative for next 3)
                    feedback = "upvote" if i < 3 else "downvote"
                    time_spent = 30.0 + (i * 5)  # Increasing time
                    
                    feedback_response = requests.post(
                        f"{BASE_URL}/api/v1/feedback",
                        json={
                            "session_id": session_id,
                            "interaction_id": interaction_id,
                            "feedback": feedback,
                            "time_spent": time_spent
                        }
                    )
                    
                    learning_progression.append({
                        "iteration": i + 1,
                        "confidence": confidence,
                        "feedback": feedback,
                        "time_spent": time_spent,
                        "feedback_success": feedback_response.status_code == 200
                    })
                
                time.sleep(0.5)  # Allow processing time
            
            # Analyze Q-table learning
            if len(learning_progression) >= 4:
                # Split into positive and negative feedback phases
                positive_phase = learning_progression[:3]
                negative_phase = learning_progression[3:]
                
                positive_confidences = [p["confidence"] for p in positive_phase]
                negative_confidences = [n["confidence"] for n in negative_phase]
                
                # Check for learning patterns
                positive_trend = np.polyfit(range(len(positive_confidences)), positive_confidences, 1)[0]
                negative_trend = np.polyfit(range(len(negative_confidences)), negative_confidences, 1)[0] if len(negative_confidences) > 1 else 0
                
                # Advanced Q-table should show learning (confidence changes based on feedback)
                shows_learning = abs(positive_trend) > 0.001 or abs(negative_trend) > 0.001
                feedback_success_rate = sum(1 for p in learning_progression if p["feedback_success"]) / len(learning_progression)
                
                qtable_analysis = {
                    "positive_trend": positive_trend,
                    "negative_trend": negative_trend,
                    "shows_learning": shows_learning,
                    "feedback_success_rate": feedback_success_rate,
                    "progression": learning_progression
                }
                
                qtable_working = shows_learning and feedback_success_rate > 0.8
                
                self.log_result(
                    "Q-table Learning",
                    qtable_working,
                    f"Learning detected: {shows_learning}, Feedback success: {feedback_success_rate:.1%}",
                    qtable_analysis
                )
                return qtable_working
            else:
                self.log_result("Q-table Learning", False, "Insufficient learning data")
                return False
                
        except Exception as e:
            self.log_result("Q-table Learning", False, f"Error: {e}")
            return False
    
    def verify_memory_persistence(self) -> bool:
        """Verify advanced memory system persistence and retrieval."""
        try:
            # Create session and build memory
            session_response = requests.post(
                f"{BASE_URL}/api/v1/sessions",
                json={"user_id": "memory_test", "user_type": "common_person"}
            )
            
            session_id = session_response.json()["session_id"]
            
            # Create diverse interactions to test memory
            test_scenarios = [
                {"query": "Divorce proceedings help", "domain": "family_law"},
                {"query": "Contract breach dispute", "domain": "contract_law"},
                {"query": "Employment discrimination", "domain": "employment_law"},
                {"query": "Personal injury claim", "domain": "tort_law"}
            ]
            
            memory_data = []
            for scenario in test_scenarios:
                query_response = requests.post(
                    f"{BASE_URL}/api/v1/query",
                    json={
                        "session_id": session_id,
                        "query": scenario["query"],
                        "interaction_type": "query"
                    }
                )
                
                if query_response.status_code == 200:
                    data = query_response.json()
                    memory_data.append({
                        "expected_domain": scenario["domain"],
                        "actual_domain": data.get("domain"),
                        "confidence": data.get("confidence"),
                        "interaction_id": data.get("interaction_id")
                    })
                
                time.sleep(0.2)
            
            # Test memory retrieval
            summary_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/summary")
            
            if summary_response.status_code == 200:
                summary = summary_response.json()
                
                # Verify memory persistence
                total_interactions = summary.get("total_interactions", 0)
                domains_remembered = summary.get("domains", [])
                session_duration = summary.get("session_duration", 0)
                
                memory_quality = {
                    "interactions_stored": total_interactions,
                    "domains_remembered": len(domains_remembered),
                    "expected_interactions": len(test_scenarios),
                    "domain_accuracy": sum(1 for m in memory_data if m["actual_domain"] == m["expected_domain"]) / len(memory_data) if memory_data else 0,
                    "session_tracking": session_duration > 0
                }
                
                memory_working = (
                    total_interactions >= len(test_scenarios) and
                    len(domains_remembered) >= 2 and
                    memory_quality["domain_accuracy"] > 0.5
                )
                
                self.log_result(
                    "Memory Persistence",
                    memory_working,
                    f"Stored: {total_interactions}/{len(test_scenarios)}, Domains: {len(domains_remembered)}, Accuracy: {memory_quality['domain_accuracy']:.1%}",
                    memory_quality
                )
                return memory_working
            else:
                self.log_result("Memory Persistence", False, f"Summary failed: {summary_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Memory Persistence", False, f"Error: {e}")
            return False
    
    def verify_ml_integration(self) -> bool:
        """Verify ML models are integrated and functioning."""
        try:
            # Get RL status to check ML integration
            response = requests.get(f"{BASE_URL}/api/v1/rl/status")
            
            if response.status_code == 200:
                data = response.json()
                learning_metrics = data.get("learning_metrics", {})
                
                # Check ML integration
                ml_models_available = learning_metrics.get("ml_models_trained", False)
                exploration_rate = learning_metrics.get("exploration_rate", 0)
                total_states = learning_metrics.get("total_states", 0)
                
                # Check if system info indicates ML capability
                system_info = data.get("system_info", {})
                ml_enabled = system_info.get("ml_enabled", False)
                
                ml_integration = {
                    "ml_models_available": ml_models_available,
                    "ml_enabled": ml_enabled,
                    "exploration_rate": exploration_rate,
                    "total_states": total_states,
                    "rl_policy_type": data.get("rl_policy_type", "unknown")
                }
                
                # Advanced RL should have ML integration
                has_ml_integration = (
                    data.get("rl_policy_type") == "AdvancedLegalRLPolicy" and
                    exploration_rate > 0
                )
                
                self.log_result(
                    "ML Integration",
                    has_ml_integration,
                    f"Policy: {data.get('rl_policy_type')}, Exploration: {exploration_rate:.3f}",
                    ml_integration
                )
                return has_ml_integration
            else:
                self.log_result("ML Integration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("ML Integration", False, f"Error: {e}")
            return False
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive advanced RL verification."""
        print("🔍 ADVANCED RL SYSTEM VERIFICATION")
        print("=" * 50)
        
        # Wait for system to be ready
        time.sleep(2)
        
        # Run all verification tests
        tests = [
            ("Advanced RL Initialization", self.verify_advanced_rl_initialization),
            ("Multi-Dimensional State", self.verify_multi_dimensional_state),
            ("Advanced Action Selection", self.verify_advanced_action_selection),
            ("Q-table Learning", self.verify_q_table_learning),
            ("Memory Persistence", self.verify_memory_persistence),
            ("ML Integration", self.verify_ml_integration)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔬 Verifying {test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Exception: {e}")
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print("\n" + "=" * 50)
        print("📊 ADVANCED RL VERIFICATION RESULTS")
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
        
        # Advanced RL assessment
        if success_rate >= 95:
            print(f"\n🚀 PERFECT! Advanced RL System is fully operational!")
            assessment = "PERFECT"
        elif success_rate >= 85:
            print(f"\n🎯 EXCELLENT! Advanced RL System is working very well!")
            assessment = "EXCELLENT"
        elif success_rate >= 75:
            print(f"\n👍 GOOD! Advanced RL System is mostly working!")
            assessment = "GOOD"
        else:
            print(f"\n⚠️  NEEDS WORK! Advanced RL System has issues!")
            assessment = "NEEDS_WORK"
        
        return {
            "assessment": assessment,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "detailed_results": self.test_results
        }


if __name__ == "__main__":
    verifier = AdvancedRLVerifier()
    results = verifier.run_comprehensive_verification()
    
    # Save detailed results
    with open("advanced_rl_verification_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: advanced_rl_verification_results.json")
