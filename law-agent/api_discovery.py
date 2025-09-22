#!/usr/bin/env python3
"""
Discover what API endpoints are available on the Render backend
"""

import requests
import json

# Render backend URL
RENDER_BACKEND_URL = "https://law-agent-by-grok.onrender.com"

def test_endpoint(url, method="GET", data=None):
    """Test if an endpoint exists and return details"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            if data:
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.post(url, timeout=10)
        
        status = response.status_code
        content_type = response.headers.get('content-type', '')
        content_length = len(response.content)
        
        result = {
            'url': url,
            'method': method,
            'status': status,
            'content_type': content_type,
            'content_length': content_length
        }
        
        # Try to parse JSON response
        if status == 200 and content_type.startswith('application/json'):
            try:
                result['json'] = response.json()
            except:
                result['json'] = None
        
        return result
    except Exception as e:
        return {
            'url': url,
            'method': method,
            'status': 'ERROR',
            'error': str(e)
        }

def discover_api_endpoints():
    """Discover available API endpoints"""
    print("🔍 Discovering API endpoints...")
    print("=" * 60)
    
    # Common API patterns to test
    patterns = [
        # Base paths
        "/api",
        "/api/v1",
        "/v1",
        "/api/v2",
        "/v2",
        
        # Health endpoints
        "/health",
        "/api/health",
        "/v1/health",
        "/api/v1/health",
        
        # Documentation
        "/docs",
        "/api/docs",
        "/v1/docs",
        "/api/v1/docs",
        "/redoc",
        "/api/redoc",
        
        # Session management
        "/sessions",
        "/api/sessions",
        "/v1/sessions",
        "/api/v1/sessions",
        "/session",
        "/api/session",
        "/v1/session",
        "/api/v1/session",
        
        # Query/Chat endpoints
        "/query",
        "/api/query",
        "/v1/query",
        "/api/v1/query",
        "/chat",
        "/api/chat",
        "/v1/chat",
        "/api/v1/chat",
        "/ask",
        "/api/ask",
        "/v1/ask",
        "/api/v1/ask",
        
        # Legal specific endpoints
        "/legal",
        "/api/legal",
        "/v1/legal",
        "/api/v1/legal",
        "/legal-query",
        "/api/legal-query",
        "/v1/legal-query",
        "/api/v1/legal-query",
        
        # User management
        "/users",
        "/api/users",
        "/v1/users",
        "/api/v1/users",
        "/user",
        "/api/user",
        "/v1/user",
        "/api/v1/user",
    ]
    
    results = []
    for pattern in patterns:
        url = RENDER_BACKEND_URL + pattern
        result = test_endpoint(url, "GET")
        results.append(result)
        
        # For POST endpoints that might be relevant
        if any(word in pattern for word in ['session', 'query', 'chat', 'ask', 'legal']):
            # Test with sample data
            sample_data = {
                "query": "What are my rights if I'm being evicted?",
                "user_id": "test_user"
            }
            result_post = test_endpoint(url, "POST", sample_data)
            results.append(result_post)
    
    # Show results
    working_endpoints = [r for r in results if r['status'] == 200]
    non_404_endpoints = [r for r in results if r['status'] != 404 and r['status'] != 'ERROR']
    error_endpoints = [r for r in results if r['status'] == 'ERROR']
    
    print(f"📊 Scan Results:")
    print(f"   Total endpoints tested: {len(results)}")
    print(f"   Working endpoints (200): {len(working_endpoints)}")
    print(f"   Non-404 endpoints: {len(non_404_endpoints)}")
    print(f"   Error endpoints: {len(error_endpoints)}")
    
    print("\n✅ WORKING ENDPOINTS (Status 200):")
    print("-" * 60)
    if working_endpoints:
        for endpoint in working_endpoints:
            print(f"  {endpoint['method']} {endpoint['url']} -> {endpoint['status']}")
            print(f"    Content-Type: {endpoint['content_type']}")
            print(f"    Content-Length: {endpoint['content_length']}")
            if 'json' in endpoint and endpoint['json']:
                print(f"    JSON Preview: {json.dumps(endpoint['json'], indent=2)[:200]}...")
            print()
    else:
        print("  No endpoints returned 200 status")
    
    print("\n⚠️  NON-404 ENDPOINTS:")
    print("-" * 60)
    non_404_sorted = sorted(non_404_endpoints, key=lambda x: x['status'])
    for endpoint in non_404_sorted:
        if endpoint['status'] == 200:
            continue  # Skip already shown
        print(f"  {endpoint['method']} {endpoint['url']} -> {endpoint['status']}")
        if 'error' in endpoint:
            print(f"    Error: {endpoint['error']}")
        print()
    
    return results

def test_query_endpoints():
    """Test potential query endpoints with actual data"""
    print("\n🔍 Testing potential query endpoints with sample data...")
    print("=" * 60)
    
    # Potential query endpoints
    query_endpoints = [
        "/api/query",
        "/api/chat",
        "/api/ask",
        "/api/legal-query",
        "/query",
        "/chat",
        "/ask",
        "/legal-query"
    ]
    
    # Sample query data
    sample_data = {
        "user_input": "What are my rights if I'm being evicted?",
        "feedback": ""
    }
    
    results = []
    for endpoint in query_endpoints:
        url = RENDER_BACKEND_URL + endpoint
        result = test_endpoint(url, "POST", sample_data)
        results.append(result)
        print(f"  POST {url} -> {result['status']}")
    
    # Show successful endpoints
    success_endpoints = [r for r in results if r['status'] == 200]
    if success_endpoints:
        print("\n✅ SUCCESSFUL QUERY ENDPOINTS:")
        for endpoint in success_endpoints:
            print(f"  POST {endpoint['url']} -> {endpoint['status']}")
    else:
        print("\n❌ No query endpoints returned 200 status")

if __name__ == "__main__":
    all_results = discover_api_endpoints()
    test_query_endpoints()