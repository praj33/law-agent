#!/usr/bin/env python3
"""
Check API Endpoints
Verify what endpoints are available in the Law Agent API.
"""

import requests
import json

def check_api_endpoints():
    """Check what API endpoints are available."""
    
    print("🔍 CHECKING LAW AGENT API ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Check health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Check OpenAPI schema
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi_data = response.json()
            print(f"✅ OpenAPI schema: {response.status_code}")
            print(f"📋 Title: {openapi_data.get('info', {}).get('title', 'N/A')}")
            print(f"📋 Version: {openapi_data.get('info', {}).get('version', 'N/A')}")
            
            paths = openapi_data.get('paths', {})
            print(f"\n📡 Available Endpoints ({len(paths)}):")
            
            for path in sorted(paths.keys()):
                methods = list(paths[path].keys())
                methods_str = "|".join(m.upper() for m in methods)
                print(f"   {path} [{methods_str}]")
            
            return True
        else:
            print(f"❌ OpenAPI schema failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OpenAPI schema error: {e}")
        return False

def test_specific_endpoints():
    """Test specific API endpoints."""
    
    print("\n🧪 TESTING SPECIFIC ENDPOINTS")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test endpoints that should exist
    endpoints_to_test = [
        ("/api/v1/system/info", "GET"),
        ("/api/v1/system/health", "GET"),
        ("/api/v1/analytics/domains", "GET"),
    ]
    
    for endpoint, method in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=5)
            
            print(f"✅ {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and len(str(data)) < 200:
                    print(f"   📄 Response: {data}")
                else:
                    print(f"   📄 Response: {type(data).__name__} with {len(str(data))} chars")
            
        except Exception as e:
            print(f"❌ {method} {endpoint}: {e}")

def main():
    """Main function."""
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Law Agent API is not running on port 8000")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Law Agent API: {e}")
        return False
    
    # Check endpoints
    schema_ok = check_api_endpoints()
    
    if schema_ok:
        test_specific_endpoints()
        
        print("\n🌐 ACCESS POINTS:")
        print("=" * 60)
        print("📚 API Documentation: http://localhost:8000/docs")
        print("📚 ReDoc Documentation: http://localhost:8000/redoc")
        print("🔍 OpenAPI Schema: http://localhost:8000/openapi.json")
        print("💚 Health Check: http://localhost:8000/health")
        
        return True
    else:
        print("\n❌ API schema check failed")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 API endpoints check completed successfully!")
    else:
        print("\n❌ API endpoints check failed!")
