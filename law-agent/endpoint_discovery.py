#!/usr/bin/env python3
"""
Discover what endpoints are available on the Render backend
"""

import requests
import json

# Render backend URL
RENDER_BACKEND_URL = "https://law-agent-by-grok.onrender.com"

def test_endpoint(url, method="GET"):
    """Test if an endpoint exists"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, timeout=10)
        
        print(f"  {method} {url} -> {response.status_code}")
        if response.status_code == 200 and response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"    Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"    Response: {response.text[:200]}...")
        return response.status_code
    except Exception as e:
        print(f"  {method} {url} -> ERROR: {e}")
        return None

def discover_endpoints():
    """Discover available endpoints"""
    print("🔍 Discovering available endpoints...")
    print("=" * 50)
    
    # Common endpoints to test
    endpoints = [
        # Health and info
        ("/health", "GET"),
        ("/api/health", "GET"),
        ("/v1/health", "GET"),
        ("/api/v1/health", "GET"),
        
        # Documentation
        ("/docs", "GET"),
        ("/api/docs", "GET"),
        ("/v1/docs", "GET"),
        ("/api/v1/docs", "GET"),
        ("/redoc", "GET"),
        ("/api/redoc", "GET"),
        
        # Session endpoints
        ("/sessions", "POST"),
        ("/api/sessions", "POST"),
        ("/v1/sessions", "POST"),
        ("/api/v1/sessions", "POST"),
        
        # Query endpoints
        ("/query", "POST"),
        ("/api/query", "POST"),
        ("/v1/query", "POST"),
        ("/api/v1/query", "POST"),
        
        # Root endpoints
        ("/", "GET"),
        ("/api", "GET"),
        ("/v1", "GET"),
    ]
    
    found_endpoints = []
    for endpoint, method in endpoints:
        url = RENDER_BACKEND_URL + endpoint
        status = test_endpoint(url, method)
        if status and status != 404:
            found_endpoints.append((endpoint, method, status))
    
    print("\n" + "=" * 50)
    print("📋 FOUND ENDPOINTS:")
    if found_endpoints:
        for endpoint, method, status in found_endpoints:
            print(f"  {method} {endpoint} -> {status}")
    else:
        print("  No non-404 endpoints found")

if __name__ == "__main__":
    discover_endpoints()