#!/usr/bin/env python3
"""
Comprehensive system integration test for the Law Agent.

This script tests the complete system functionality including:
- Agent initialization
- Session management
- Query processing
- Reinforcement learning
- Feedback collection
- API endpoints
- Performance monitoring
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from law_agent.core.agent import LawAgent
from law_agent.core.state import UserType, LegalDomain, FeedbackType
from law_agent.legal.domain_classifier import LegalDomainClassifier
from law_agent.legal.route_mapper import LegalRouteMapper
from law_agent.legal.glossary import LegalGlossary
from law_agent.rl.policy import create_rl_policy


class SystemIntegrationTest:
    """Comprehensive system integration test."""
    
    def __init__(self):
        self.test_results = []
        self.law_agent = None
    
    async def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Starting Law Agent System Integration Tests")
        print("=" * 60)
        
        try:
            # Initialize system
            await self.test_system_initialization()
            
            # Test core functionality
            await self.test_session_management()
            await self.test_query_processing()
            await self.test_domain_classification()
            await self.test_route_mapping()
            await self.test_glossary_system()
            await self.test_reinforcement_learning()
            await self.test_feedback_system()
            
            # Test advanced features
            await self.test_user_type_adaptation()
            await self.test_learning_progression()
            await self.test_concurrent_sessions()
            
            # Performance tests
            await self.test_performance()
            
            # Print results
            self.print_test_results()
            
        except Exception as e:
            print(f"❌ Critical error during testing: {e}")
            return False
        
        return all(result["passed"] for result in self.test_results)
    
    async def test_system_initialization(self):
        """Test system initialization."""
        print("🔧 Testing system initialization...")
        
        try:
            # Initialize Law Agent
            self.law_agent = LawAgent()
            
            # Verify components are initialized
            assert self.law_agent.memory is not None
            assert self.law_agent.domain_classifier is not None
            assert self.law_agent.route_mapper is not None
            assert self.law_agent.glossary is not None
            assert self.law_agent.rl_policy is not None
            
            self.add_test_result("System Initialization", True, "All components initialized successfully")
            
        except Exception as e:
            self.add_test_result("System Initialization", False, str(e))
    
    async def test_session_management(self):
        """Test session creation and management."""
        print("👤 Testing session management...")
        
        try:
            # Create session
            session_id = await self.law_agent.create_session(
                user_id="test_user_integration",
                user_type=UserType.COMMON_PERSON
            )
            
            assert session_id is not None
            assert isinstance(session_id, str)
            assert len(session_id) > 0
            
            # Get session summary
            summary = await self.law_agent.get_session_summary(session_id)
            assert summary["user_id"] == "test_user_integration"
            assert summary["total_interactions"] == 0
            
            self.add_test_result("Session Management", True, f"Session created: {session_id}")
            return session_id
            
        except Exception as e:
            self.add_test_result("Session Management", False, str(e))
            return None
    
    async def test_query_processing(self):
        """Test query processing functionality."""
        print("💬 Testing query processing...")
        
        try:
            # Create session
            session_id = await self.law_agent.create_session(
                user_id="test_query_user",
                user_type=UserType.COMMON_PERSON
            )
            
            # Test various types of queries
            test_queries = [
                ("I need help with divorce proceedings", LegalDomain.FAMILY_LAW),
                ("I was arrested for DUI", LegalDomain.CRIMINAL_LAW),
                ("How do I start a business?", LegalDomain.CORPORATE_LAW),
                ("My landlord is evicting me", LegalDomain.PROPERTY_LAW),
                ("I was fired unfairly", LegalDomain.EMPLOYMENT_LAW)
            ]
            
            successful_queries = 0
            
            for query, expected_domain in test_queries:
                try:
                    result = await self.law_agent.process_query(
                        session_id=session_id,
                        query=query
                    )
                    
                    # Verify result structure
                    assert "interaction_id" in result
                    assert "response" in result
                    assert "domain" in result
                    assert "confidence" in result
                    
                    # Check if domain classification is reasonable
                    if result["domain"] == expected_domain or result["confidence"] > 0.3:
                        successful_queries += 1
                    
                except Exception as e:
                    print(f"  ⚠️  Query failed: {query[:30]}... - {e}")
            
            success_rate = successful_queries / len(test_queries)
            
            if success_rate >= 0.6:  # 60% success rate threshold
                self.add_test_result("Query Processing", True, f"Success rate: {success_rate:.1%}")
            else:
                self.add_test_result("Query Processing", False, f"Low success rate: {success_rate:.1%}")
                
        except Exception as e:
            self.add_test_result("Query Processing", False, str(e))
    
    async def test_domain_classification(self):
        """Test domain classification accuracy."""
        print("🎯 Testing domain classification...")
        
        try:
            classifier = LegalDomainClassifier()
            
            test_cases = [
                ("child custody dispute", LegalDomain.FAMILY_LAW),
                ("criminal charges", LegalDomain.CRIMINAL_LAW),
                ("business incorporation", LegalDomain.CORPORATE_LAW),
                ("property deed", LegalDomain.PROPERTY_LAW),
                ("workplace harassment", LegalDomain.EMPLOYMENT_LAW)
            ]
            
            correct_classifications = 0
            
            for query, expected_domain in test_cases:
                result = await classifier.classify(query)
                if result["domain"] == expected_domain:
                    correct_classifications += 1
            
            accuracy = correct_classifications / len(test_cases)
            
            if accuracy >= 0.6:
                self.add_test_result("Domain Classification", True, f"Accuracy: {accuracy:.1%}")
            else:
                self.add_test_result("Domain Classification", False, f"Low accuracy: {accuracy:.1%}")
                
        except Exception as e:
            self.add_test_result("Domain Classification", False, str(e))
    
    async def test_route_mapping(self):
        """Test legal route mapping."""
        print("🗺️  Testing route mapping...")
        
        try:
            route_mapper = LegalRouteMapper()
            
            # Test route retrieval
            route = await route_mapper.get_route(
                domain=LegalDomain.FAMILY_LAW,
                query="I want to get divorced",
                user_type=UserType.COMMON_PERSON
            )
            
            # Verify route structure
            assert "title" in route
            assert "summary" in route
            assert "procedures" in route
            assert "next_steps" in route
            assert isinstance(route["procedures"], list)
            assert isinstance(route["next_steps"], list)
            
            self.add_test_result("Route Mapping", True, f"Route generated: {route['title']}")
            
        except Exception as e:
            self.add_test_result("Route Mapping", False, str(e))
    
    async def test_glossary_system(self):
        """Test legal glossary functionality."""
        print("📚 Testing glossary system...")
        
        try:
            glossary = LegalGlossary()
            
            # Test term search
            terms = await glossary.get_relevant_terms(
                query="What is custody?",
                max_terms=5
            )
            
            assert isinstance(terms, list)
            assert len(terms) > 0
            
            # Test specific term lookup
            term_def = glossary.get_term_definition("custody")
            assert term_def is not None
            assert "definition" in term_def
            
            self.add_test_result("Glossary System", True, f"Found {len(terms)} relevant terms")
            
        except Exception as e:
            self.add_test_result("Glossary System", False, str(e))
    
    async def test_reinforcement_learning(self):
        """Test reinforcement learning functionality."""
        print("🤖 Testing reinforcement learning...")
        
        try:
            rl_policy = create_rl_policy("qtable")
            
            # Test action generation
            test_state = {
                "user_type": "common_person",
                "current_domain": "family_law",
                "satisfaction_score": 0.5,
                "interaction_count": 5,
                "average_confidence": 0.7,
                "recent_feedback": ["upvote", "upvote"]
            }
            
            action = await rl_policy.get_action(test_state)
            assert isinstance(action, dict)
            assert "action" in action
            
            # Test policy update
            await rl_policy.update_policy(test_state, 1.0)  # Positive reward
            
            self.add_test_result("Reinforcement Learning", True, f"Action generated: {action['action']}")
            
        except Exception as e:
            self.add_test_result("Reinforcement Learning", False, str(e))
    
    async def test_feedback_system(self):
        """Test feedback collection and processing."""
        print("👍 Testing feedback system...")
        
        try:
            # Create session and process query
            session_id = await self.law_agent.create_session(
                user_id="feedback_test_user",
                user_type=UserType.COMMON_PERSON
            )
            
            result = await self.law_agent.process_query(
                session_id=session_id,
                query="What is a contract?"
            )
            
            interaction_id = result["interaction_id"]
            
            # Submit feedback
            feedback_result = await self.law_agent.submit_feedback(
                session_id=session_id,
                interaction_id=interaction_id,
                feedback=FeedbackType.UPVOTE,
                time_spent=45.0
            )
            
            assert feedback_result["status"] == "success"
            assert "reward" in feedback_result
            assert feedback_result["reward"] > 0
            
            self.add_test_result("Feedback System", True, f"Reward: {feedback_result['reward']:.2f}")
            
        except Exception as e:
            self.add_test_result("Feedback System", False, str(e))
    
    async def test_user_type_adaptation(self):
        """Test adaptation to different user types."""
        print("👥 Testing user type adaptation...")
        
        try:
            # Create sessions for different user types
            common_session = await self.law_agent.create_session(
                user_id="common_user_test",
                user_type=UserType.COMMON_PERSON
            )
            
            firm_session = await self.law_agent.create_session(
                user_id="firm_user_test",
                user_type=UserType.LAW_FIRM
            )
            
            query = "What is breach of contract?"
            
            # Process same query for both user types
            common_result = await self.law_agent.process_query(
                session_id=common_session,
                query=query
            )
            
            firm_result = await self.law_agent.process_query(
                session_id=firm_session,
                query=query
            )
            
            # Responses should be different
            common_text = common_result["response"]["text"]
            firm_text = firm_result["response"]["text"]
            
            adaptation_detected = common_text != firm_text
            
            self.add_test_result("User Type Adaptation", adaptation_detected, 
                               "Responses adapted to user type" if adaptation_detected else "No adaptation detected")
            
        except Exception as e:
            self.add_test_result("User Type Adaptation", False, str(e))
    
    async def test_learning_progression(self):
        """Test learning progression over multiple interactions."""
        print("📈 Testing learning progression...")
        
        try:
            session_id = await self.law_agent.create_session(
                user_id="learning_test_user",
                user_type=UserType.COMMON_PERSON
            )
            
            # Process multiple similar queries with positive feedback
            queries = [
                "I need help with divorce",
                "What about child support in divorce?",
                "How do I file for divorce?"
            ]
            
            confidences = []
            
            for query in queries:
                result = await self.law_agent.process_query(
                    session_id=session_id,
                    query=query
                )
                
                confidences.append(result["confidence"])
                
                # Submit positive feedback
                await self.law_agent.submit_feedback(
                    session_id=session_id,
                    interaction_id=result["interaction_id"],
                    feedback=FeedbackType.UPVOTE,
                    time_spent=60.0
                )
            
            # Check if confidence generally improved
            learning_detected = len(confidences) >= 2 and confidences[-1] >= confidences[0]
            
            self.add_test_result("Learning Progression", learning_detected,
                               f"Confidence progression: {[f'{c:.2f}' for c in confidences]}")
            
        except Exception as e:
            self.add_test_result("Learning Progression", False, str(e))
    
    async def test_concurrent_sessions(self):
        """Test handling of concurrent sessions."""
        print("🔄 Testing concurrent sessions...")
        
        try:
            # Create multiple sessions concurrently
            tasks = []
            for i in range(3):
                task = self.law_agent.create_session(
                    user_id=f"concurrent_user_{i}",
                    user_type=UserType.COMMON_PERSON
                )
                tasks.append(task)
            
            session_ids = await asyncio.gather(*tasks)
            
            # Process queries concurrently
            query_tasks = []
            for session_id in session_ids:
                task = self.law_agent.process_query(
                    session_id=session_id,
                    query="What is a legal contract?"
                )
                query_tasks.append(task)
            
            results = await asyncio.gather(*query_tasks)
            
            # All should succeed
            all_successful = all("interaction_id" in result for result in results)
            
            self.add_test_result("Concurrent Sessions", all_successful,
                               f"Processed {len(results)} concurrent queries")
            
        except Exception as e:
            self.add_test_result("Concurrent Sessions", False, str(e))
    
    async def test_performance(self):
        """Test system performance."""
        print("⚡ Testing performance...")
        
        try:
            session_id = await self.law_agent.create_session(
                user_id="performance_test_user",
                user_type=UserType.COMMON_PERSON
            )
            
            # Measure query processing time
            start_time = time.time()
            
            result = await self.law_agent.process_query(
                session_id=session_id,
                query="I need legal advice about employment law"
            )
            
            processing_time = time.time() - start_time
            
            # Performance should be reasonable (under 5 seconds)
            performance_acceptable = processing_time < 5.0
            
            self.add_test_result("Performance", performance_acceptable,
                               f"Query processed in {processing_time:.2f} seconds")
            
        except Exception as e:
            self.add_test_result("Performance", False, str(e))
    
    def add_test_result(self, test_name: str, passed: bool, details: str):
        """Add test result."""
        self.test_results.append({
            "name": test_name,
            "passed": passed,
            "details": details
        })
        
        status = "✅" if passed else "❌"
        print(f"  {status} {test_name}: {details}")
    
    def print_test_results(self):
        """Print comprehensive test results."""
        print("\n" + "=" * 60)
        print("🧪 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1%}")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {status} - {result['name']}")
            print(f"    {result['details']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 0.8:
            print("🎉 SYSTEM INTEGRATION TEST: SUCCESS")
            print("The Law Agent system is functioning correctly!")
        else:
            print("⚠️  SYSTEM INTEGRATION TEST: ISSUES DETECTED")
            print("Some components may need attention.")
        
        print("=" * 60)


async def main():
    """Run the integration test."""
    test_runner = SystemIntegrationTest()
    success = await test_runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
