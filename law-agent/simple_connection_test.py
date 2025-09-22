#!/usr/bin/env python3
"""
Simple connection test to check if the Render backend is accessible
"""

import requests
import sys

def test_connection(url):
    """Test if a URL is accessible"""
    try:
        print(f"Testing connection to: {url}")
        response = requests.get(url, timeout=10)
        print(f"✅ Success! Status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    urls_to_test = [
        "https://law-agent-by-grok.onrender.com",
        "https://law-agent-by-grok.onrender.com/health",
        "https://law-agent-by-grok.onrender.com/docs",
        "https://law-agent-by-grok.onrender.com/api/v1/sessions"
    ]
    
    print("🧪 Simple Connection Test")
    print("=" * 40)
    
    results = []
    for url in urls_to_test:
        success = test_connection(url)
        results.append((url, success))
        print()
    
    print("📋 SUMMARY:")
    print("=" * 40)
    for url, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {url}")