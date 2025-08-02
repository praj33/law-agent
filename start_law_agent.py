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

def check_redis_installed():
    """Check if Redis is installed on the system"""
    try:
        result = subprocess.run(["redis-cli", "--version"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Redis CLI found")
            return True
    except:
        pass

    try:
        result = subprocess.run(["redis-server", "--version"],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Redis Server found")
            return True
    except:
        pass

    print("❌ Redis not found on system")
    return False

def check_redis_running():
    """Check if Redis is currently running"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=3)
        client.ping()
        print("✅ Redis is running and accessible")
        return True
    except ImportError:
        print("⚠️ Redis Python package not installed")
        return False
    except Exception as e:
        print(f"❌ Redis not running: {e}")
        return False

def start_redis():
    """Start Redis server automatically"""
    print("🚀 Starting Redis server...")

    import platform
    system = platform.system()

    if system == "Windows":
        try:
            # Try Windows service first
            result = subprocess.run(["net", "start", "redis"],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Started Redis Windows service")
                return True
        except:
            pass

        try:
            # Try direct Redis server start
            subprocess.Popen(["redis-server"],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("✅ Started Redis server directly")
            return True
        except FileNotFoundError:
            print("❌ Redis server executable not found")
            return False
    else:
        try:
            subprocess.run(["sudo", "systemctl", "start", "redis"],
                          capture_output=True, text=True)
            print("✅ Started Redis via systemctl")
            return True
        except:
            try:
                subprocess.Popen(["redis-server"])
                print("✅ Started Redis server directly")
                return True
            except FileNotFoundError:
                print("❌ Redis server not found")
                return False

    return False

def wait_for_redis(timeout=15):
    """Wait for Redis to become available"""
    print(f"⏳ Waiting for Redis to start (timeout: {timeout}s)...")

    for i in range(timeout):
        if check_redis_running():
            print("✅ Redis is ready!")
            return True

        print(f"⏳ Waiting... ({i+1}/{timeout})")
        time.sleep(1)

    print("❌ Redis failed to start within timeout")
    return False

def setup_redis():
    """Complete Redis setup process"""
    print("\n🔧 REDIS SETUP")
    print("-" * 30)

    # Install Redis Python package if needed
    try:
        import redis
        print("✅ Redis Python package available")
    except ImportError:
        print("📦 Installing Redis Python package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "redis"])
            print("✅ Redis Python package installed!")
        except Exception as e:
            print(f"❌ Failed to install Redis package: {e}")
            return False

    # Check if Redis is already running
    if check_redis_running():
        return True

    # Check if Redis is installed
    if not check_redis_installed():
        print("\n💡 Redis Installation Required:")
        print("Windows: Run PowerShell as Admin and execute: .\\install_redis.ps1")
        print("Linux: sudo apt-get install redis-server")
        print("Mac: brew install redis")
        print("\n🔄 Continuing with in-memory storage...")
        return False

    # Try to start Redis
    if start_redis():
        return wait_for_redis()

    return False

def check_setup():
    """Check if system is properly set up."""
    print("\n🔍 Checking system setup...")

    # Setup Redis
    redis_success = setup_redis()

    # Check key dependencies
    try:
        import fastapi
        print("✅ FastAPI available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Installing FastAPI...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"])
            print("✅ FastAPI installed!")
            return True
        except Exception as install_error:
            print(f"❌ Failed to install FastAPI: {install_error}")
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
