#!/usr/bin/env python3
"""
Law Agent - One-Click Startup Script
Automatically handles setup, dependencies, and startup with error recovery.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("\n" + "=" * 70)
    print("🏛️  LAW AGENT - ADVANCED LEGAL AI ASSISTANT")
    print("=" * 70)
    print("🚀 One-Click Startup System")
    print("✨ Automatic setup, dependency management, and error recovery")
    print("=" * 70)

def check_setup():
    """Check if system is properly set up."""
    print("\n🔍 Checking system setup...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found")
        return False
    
    # Check if Redis is running
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis is running")
    except:
        print("⚠️ Redis not running, will start automatically")
    
    # Check key dependencies
    try:
        import torch
        import transformers
        import fastapi
        print("✅ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False

def run_setup():
    """Run the advanced setup."""
    print("\n🔧 Running advanced system setup...")
    try:
        result = subprocess.run([sys.executable, "setup_advanced_system.py"], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Setup completed successfully")
            return True
        else:
            print(f"❌ Setup failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Setup timed out")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def start_redis():
    """Start Redis if not running."""
    print("\n🔄 Starting Redis...")
    try:
        result = subprocess.run([sys.executable, "setup_redis.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ Redis started successfully")
            return True
        else:
            print("⚠️ Redis setup had issues, continuing with fallback")
            return True  # Continue anyway, we have FakeRedis fallback
    except Exception as e:
        print(f"⚠️ Redis startup warning: {e}")
        return True  # Continue anyway

def start_law_agent():
    """Start the Law Agent system."""
    print("\n🚀 Starting Law Agent...")
    
    try:
        # Try robust startup first
        if Path("run_law_agent_robust.py").exists():
            print("🔧 Using robust startup system...")
            subprocess.run([sys.executable, "run_law_agent_robust.py", "--kill-existing"])
        else:
            # Fallback to regular startup
            print("🔄 Using standard startup...")
            subprocess.run([sys.executable, "run_law_agent.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        print("\n🔄 Trying alternative startup methods...")
        
        # Try alternative startup
        try:
            subprocess.run([sys.executable, "run_law_agent.py"])
        except Exception as e2:
            print(f"❌ All startup methods failed: {e2}")
            return False
    
    return True

def main():
    """Main startup function."""
    print_banner()
    
    # Step 1: Check if setup is needed
    if not check_setup():
        print("\n🔧 System setup required...")
        if not run_setup():
            print("\n❌ Setup failed. Please check the error messages above.")
            print("💡 Try running: python setup_advanced_system.py")
            return False
    
    # Step 2: Ensure Redis is running
    start_redis()
    
    # Step 3: Start Law Agent
    print("\n" + "=" * 70)
    print("🎯 STARTING LAW AGENT SYSTEM")
    print("=" * 70)
    print("🌐 Web Interface will be available at: http://localhost:8000")
    print("📡 API Documentation at: http://localhost:8000/api/docs")
    print("🔍 Health Check at: http://localhost:8000/health")
    print("=" * 70)
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 70)
    
    return start_law_agent()

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Law Agent failed to start")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Run: python setup_advanced_system.py")
            print("2. Check: python setup_redis.py")
            print("3. Try: python run_law_agent_robust.py --kill-existing")
            print("4. Manual: python run_law_agent.py")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
