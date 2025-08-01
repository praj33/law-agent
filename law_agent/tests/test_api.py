"""Tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient
from law_agent.api.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_system_info(self):
        """Test system info endpoint."""
        response = client.get("/api/v1/system/info")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "components" in data
        assert "supported_domains" in data
    
    def test_create_session(self):
        """Test session creation endpoint."""
        response = client.post("/api/v1/sessions", json={
            "user_id": "test_user",
            "user_type": "common_person"
        })
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "user_id" in data
        assert data["user_id"] == "test_user"
        return data["session_id"]
    
    def test_process_query(self):
        """Test query processing endpoint."""
        # First create a session
        session_response = client.post("/api/v1/sessions", json={
            "user_id": "test_user",
            "user_type": "common_person"
        })
        session_id = session_response.json()["session_id"]
        
        # Process a query
        response = client.post("/api/v1/query", json={
            "session_id": session_id,
            "query": "I need help with divorce proceedings"
        })
        assert response.status_code == 200
        data = response.json()
        assert "interaction_id" in data
        assert "response" in data
        assert "domain" in data
        assert "confidence" in data
        return session_id, data["interaction_id"]
    
    def test_submit_feedback(self):
        """Test feedback submission endpoint."""
        # First process a query
        session_id, interaction_id = self.test_process_query()
        
        # Submit feedback
        response = client.post("/api/v1/feedback", json={
            "session_id": session_id,
            "interaction_id": interaction_id,
            "feedback": "upvote",
            "time_spent": 30.0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "reward" in data
    
    def test_glossary_search(self):
        """Test glossary search endpoint."""
        response = client.post("/api/v1/glossary/search", json={
            "query": "contract",
            "max_terms": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert "terms" in data
        assert "count" in data
    
    def test_get_term_definition(self):
        """Test getting term definition."""
        response = client.get("/api/v1/glossary/term/custody")
        assert response.status_code == 200
        data = response.json()
        assert "term" in data
        assert "definition" in data
    
    def test_route_search(self):
        """Test route search endpoint."""
        response = client.post("/api/v1/routes/search", json={
            "domain": "family_law",
            "query": "I want to get divorced",
            "user_type": "common_person"
        })
        assert response.status_code == 200
        data = response.json()
        assert "route" in data
        assert "domain" in data
    
    def test_invalid_session_query(self):
        """Test query with invalid session."""
        response = client.post("/api/v1/query", json={
            "session_id": "invalid_session",
            "query": "test query"
        })
        assert response.status_code == 404
    
    def test_invalid_feedback(self):
        """Test feedback with invalid interaction."""
        # Create valid session first
        session_response = client.post("/api/v1/sessions", json={
            "user_id": "test_user",
            "user_type": "common_person"
        })
        session_id = session_response.json()["session_id"]
        
        response = client.post("/api/v1/feedback", json={
            "session_id": session_id,
            "interaction_id": "invalid_interaction",
            "feedback": "upvote"
        })
        assert response.status_code == 404
    
    def test_session_summary(self):
        """Test getting session summary."""
        # Create session and process some queries
        session_response = client.post("/api/v1/sessions", json={
            "user_id": "test_user",
            "user_type": "common_person"
        })
        session_id = session_response.json()["session_id"]
        
        # Process a few queries
        queries = ["What is divorce?", "How do I file for custody?"]
        for query in queries:
            client.post("/api/v1/query", json={
                "session_id": session_id,
                "query": query
            })
        
        # Get summary
        response = client.get(f"/api/v1/sessions/{session_id}/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_interactions" in data
        assert data["total_interactions"] == len(queries)


class TestAPIValidation:
    """Test API input validation."""
    
    def test_create_session_validation(self):
        """Test session creation validation."""
        # Missing user_id
        response = client.post("/api/v1/sessions", json={
            "user_type": "common_person"
        })
        assert response.status_code == 422
        
        # Invalid user_type
        response = client.post("/api/v1/sessions", json={
            "user_id": "test_user",
            "user_type": "invalid_type"
        })
        assert response.status_code == 422
    
    def test_query_validation(self):
        """Test query validation."""
        # Missing session_id
        response = client.post("/api/v1/query", json={
            "query": "test query"
        })
        assert response.status_code == 422
        
        # Missing query
        response = client.post("/api/v1/query", json={
            "session_id": "test_session"
        })
        assert response.status_code == 422
    
    def test_feedback_validation(self):
        """Test feedback validation."""
        # Invalid feedback type
        response = client.post("/api/v1/feedback", json={
            "session_id": "test_session",
            "interaction_id": "test_interaction",
            "feedback": "invalid_feedback"
        })
        assert response.status_code == 422


class TestAPIPerformance:
    """Test API performance characteristics."""
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)
        
        # Should complete reasonably quickly
        assert end_time - start_time < 5.0  # 5 seconds max
    
    def test_large_query(self):
        """Test handling large queries."""
        # Create session
        session_response = client.post("/api/v1/sessions", json={
            "user_id": "test_user",
            "user_type": "common_person"
        })
        session_id = session_response.json()["session_id"]
        
        # Large query (but within limits)
        large_query = "I need legal help with " + "a very complex situation " * 100
        
        response = client.post("/api/v1/query", json={
            "session_id": session_id,
            "query": large_query
        })
        
        # Should handle gracefully
        assert response.status_code in [200, 400]  # Either success or validation error


if __name__ == "__main__":
    pytest.main([__file__])
