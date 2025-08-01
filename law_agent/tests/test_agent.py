"""Tests for the main Law Agent functionality."""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from law_agent.core.agent import LawAgent
from law_agent.core.state import UserType, LegalDomain, InteractionType, FeedbackType


@pytest.fixture
async def law_agent():
    """Create a Law Agent instance for testing."""
    agent = LawAgent()
    return agent


@pytest.fixture
async def test_session(law_agent):
    """Create a test session."""
    session_id = await law_agent.create_session(
        user_id="test_user_123",
        user_type=UserType.COMMON_PERSON
    )
    return session_id


class TestLawAgent:
    """Test cases for the Law Agent."""
    
    @pytest.mark.asyncio
    async def test_create_session(self, law_agent):
        """Test session creation."""
        session_id = await law_agent.create_session(
            user_id="test_user",
            user_type=UserType.COMMON_PERSON
        )
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    @pytest.mark.asyncio
    async def test_process_query_family_law(self, law_agent, test_session):
        """Test processing a family law query."""
        query = "I need help with child custody arrangements after divorce"
        
        result = await law_agent.process_query(
            session_id=test_session,
            query=query
        )
        
        assert "interaction_id" in result
        assert "response" in result
        assert "domain" in result
        assert "confidence" in result
        
        # Should classify as family law
        assert result["domain"] == LegalDomain.FAMILY_LAW
        assert result["confidence"] > 0.5
        
        # Should have relevant content
        assert "custody" in result["response"]["text"].lower()
    
    @pytest.mark.asyncio
    async def test_process_query_criminal_law(self, law_agent, test_session):
        """Test processing a criminal law query."""
        query = "I was arrested for DUI and need to know my rights"
        
        result = await law_agent.process_query(
            session_id=test_session,
            query=query
        )
        
        assert result["domain"] == LegalDomain.CRIMINAL_LAW
        assert result["confidence"] > 0.5
        assert "rights" in result["response"]["text"].lower()
    
    @pytest.mark.asyncio
    async def test_submit_feedback(self, law_agent, test_session):
        """Test submitting feedback."""
        # First, process a query
        query = "What is a contract?"
        result = await law_agent.process_query(
            session_id=test_session,
            query=query
        )
        
        interaction_id = result["interaction_id"]
        
        # Submit positive feedback
        feedback_result = await law_agent.submit_feedback(
            session_id=test_session,
            interaction_id=interaction_id,
            feedback=FeedbackType.UPVOTE,
            time_spent=45.0
        )
        
        assert feedback_result["status"] == "success"
        assert "reward" in feedback_result
        assert "updated_satisfaction" in feedback_result
        assert feedback_result["reward"] > 0  # Positive feedback should give positive reward
    
    @pytest.mark.asyncio
    async def test_session_summary(self, law_agent, test_session):
        """Test getting session summary."""
        # Process a few queries
        queries = [
            "What is divorce?",
            "How do I file for custody?",
            "What are my rights in criminal case?"
        ]
        
        for query in queries:
            await law_agent.process_query(
                session_id=test_session,
                query=query
            )
        
        summary = await law_agent.get_session_summary(test_session)
        
        assert "session_id" in summary
        assert "total_interactions" in summary
        assert summary["total_interactions"] == len(queries)
        assert "domain_distribution" in summary
    
    @pytest.mark.asyncio
    async def test_invalid_session(self, law_agent):
        """Test handling invalid session ID."""
        with pytest.raises(ValueError):
            await law_agent.process_query(
                session_id="invalid_session_id",
                query="Test query"
            )
    
    @pytest.mark.asyncio
    async def test_empty_query(self, law_agent, test_session):
        """Test handling empty query."""
        with pytest.raises(Exception):
            await law_agent.process_query(
                session_id=test_session,
                query=""
            )
    
    @pytest.mark.asyncio
    async def test_multiple_interactions_learning(self, law_agent, test_session):
        """Test that the agent learns from multiple interactions."""
        # Process multiple similar queries
        family_queries = [
            "I need help with divorce",
            "What about child support?",
            "How do I modify custody?"
        ]
        
        results = []
        for query in family_queries:
            result = await law_agent.process_query(
                session_id=test_session,
                query=query
            )
            results.append(result)
            
            # Submit positive feedback
            await law_agent.submit_feedback(
                session_id=test_session,
                interaction_id=result["interaction_id"],
                feedback=FeedbackType.UPVOTE,
                time_spent=60.0
            )
        
        # All should be classified as family law
        for result in results:
            assert result["domain"] == LegalDomain.FAMILY_LAW
        
        # Confidence should generally improve or stay high
        confidences = [r["confidence"] for r in results]
        assert all(c > 0.5 for c in confidences)
    
    @pytest.mark.asyncio
    async def test_user_type_adaptation(self, law_agent):
        """Test that responses adapt to user type."""
        # Create sessions for different user types
        common_session = await law_agent.create_session(
            user_id="common_user",
            user_type=UserType.COMMON_PERSON
        )
        
        firm_session = await law_agent.create_session(
            user_id="law_firm_user",
            user_type=UserType.LAW_FIRM
        )
        
        query = "What is a contract breach?"
        
        # Process same query for both user types
        common_result = await law_agent.process_query(
            session_id=common_session,
            query=query
        )
        
        firm_result = await law_agent.process_query(
            session_id=firm_session,
            query=query
        )
        
        # Both should classify correctly
        assert common_result["domain"] == LegalDomain.CONTRACT_LAW
        assert firm_result["domain"] == LegalDomain.CONTRACT_LAW
        
        # Responses should be different based on user type
        common_text = common_result["response"]["text"]
        firm_text = firm_result["response"]["text"]
        
        assert common_text != firm_text
        
        # Common person response should be simpler
        assert "simple terms" in common_text.lower() or "what you need to know" in common_text.lower()
        
        # Law firm response should be more professional
        assert "professional" in firm_text.lower() or "analysis" in firm_text.lower()


@pytest.mark.asyncio
async def test_concurrent_sessions():
    """Test handling multiple concurrent sessions."""
    agent = LawAgent()
    
    # Create multiple sessions
    sessions = []
    for i in range(5):
        session_id = await agent.create_session(
            user_id=f"user_{i}",
            user_type=UserType.COMMON_PERSON
        )
        sessions.append(session_id)
    
    # Process queries concurrently
    async def process_query_for_session(session_id, query):
        return await agent.process_query(session_id=session_id, query=query)
    
    tasks = [
        process_query_for_session(session, f"Legal question {i}")
        for i, session in enumerate(sessions)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # All should succeed
    assert len(results) == 5
    for result in results:
        assert "interaction_id" in result
        assert "response" in result


if __name__ == "__main__":
    pytest.main([__file__])
