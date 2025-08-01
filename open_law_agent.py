#!/usr/bin/env python3
"""Open Law Agent web interface from terminal."""

import webbrowser
import requests
import time
import sys

def check_server():
    """Check if Law Agent server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def open_law_agent():
    """Open Law Agent in browser."""
    
    print("🏛️  Opening Law Agent...")
    
    # Check if server is running
    if not check_server():
        print("❌ Law Agent server is not running!")
        print("💡 Start the server first: python run_law_agent.py")
        return False
    
    print("✅ Server is running")
    
    # Open web interface
    url = "http://localhost:8000"
    print(f"🌐 Opening {url} in browser...")
    
    try:
        webbrowser.open(url)
        print("✅ Law Agent opened in browser!")
        
        # Also show API docs option
        print(f"📚 API Documentation: {url}/api/docs")
        print(f"🔍 System Info: {url}/api/api/v1/system/info")
        
        return True
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"💡 Manually visit: {url}")
        return False

if __name__ == "__main__":
    open_law_agent()
