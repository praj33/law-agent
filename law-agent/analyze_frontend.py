#!/usr/bin/env python3
"""
Analyze the frontend HTML to understand how it communicates with the backend
"""

import requests
import re
import json

# Render backend URL
RENDER_BACKEND_URL = "https://law-agent-by-grok.onrender.com"

def analyze_frontend():
    """Analyze the frontend HTML to find API endpoints"""
    try:
        print("🔍 Analyzing frontend HTML...")
        response = requests.get(RENDER_BACKEND_URL, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch frontend: {response.status_code}")
            return
        
        html_content = response.text
        print(f"✅ Fetched frontend HTML ({len(html_content)} characters)")
        
        # Look for API endpoints in JavaScript code
        print("\n🔍 Searching for API endpoints in JavaScript...")
        
        # Find all URLs in the HTML
        urls = re.findall(r'https?://[^\s"\'<>]+', html_content)
        api_urls = [url for url in urls if 'api' in url.lower() or 'query' in url.lower() or 'chat' in url.lower()]
        
        print(f"Found {len(urls)} URLs in HTML, {len(api_urls)} potential API URLs:")
        for url in api_urls[:10]:  # Show first 10
            print(f"  {url}")
        if len(api_urls) > 10:
            print(f"  ... and {len(api_urls) - 10} more")
        
        # Look for JavaScript fetch/XHR calls
        print("\n🔍 Searching for JavaScript API calls...")
        
        # Look for fetch calls
        fetch_calls = re.findall(r'fetch\([^)]+\)', html_content)
        print(f"Found {len(fetch_calls)} fetch calls:")
        for call in fetch_calls[:5]:
            print(f"  {call}")
        
        # Look for XMLHttpRequest calls
        xhr_calls = re.findall(r'XMLHttpRequest\([^)]*\)', html_content)
        print(f"Found {len(xhr_calls)} XMLHttpRequest calls:")
        for call in xhr_calls[:5]:
            print(f"  {call}")
        
        # Look for JSON data being sent
        print("\n🔍 Searching for JSON data patterns...")
        json_patterns = re.findall(r'\{[^}]*"(query|input|message|text)"[^}]*\}', html_content)
        print(f"Found {len(json_patterns)} JSON-like patterns with query-related keys:")
        for pattern in json_patterns[:3]:
            print(f"  {pattern}")
        
        # Look for form actions
        print("\n🔍 Searching for form actions...")
        form_actions = re.findall(r'<form[^>]*action=["\']([^"\']*)', html_content)
        print(f"Found {len(form_actions)} form actions:")
        for action in form_actions:
            print(f"  {action}")
        
        # Look for JavaScript variables that might contain API URLs
        print("\n🔍 Searching for JavaScript variables with URLs...")
        js_vars = re.findall(r'(?:var|let|const)\s+(\w+)\s*=\s*["\']([^"\']*(?:api|query|chat)[^"\']*)["\']', html_content)
        print(f"Found {len(js_vars)} JavaScript variables with API-related URLs:")
        for var_name, url in js_vars:
            print(f"  {var_name} = {url}")
            
        # Save the HTML for further analysis
        with open('frontend_analysis.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 Saved HTML to frontend_analysis.html for manual inspection")
        
    except Exception as e:
        print(f"❌ Error analyzing frontend: {e}")

if __name__ == "__main__":
    analyze_frontend()