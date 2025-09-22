#!/usr/bin/env python3
"""
Auto-Start Redis for Law Agent
Automatically starts Redis when needed and provides manual control
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

def check_redis_running():
    """Check if Redis is currently running"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=3)
        client.ping()
        return True
    except:
        return False

def find_redis_executable():
    """Find Redis executable in the system"""
    # Check local Redis installations
    local_paths = [
        "redis/redis-server.exe",
        "redis_server/redis-server.exe",
        "redis/redis-server",
        "redis_server/redis-server"
    ]
    
    for path in local_paths:
        if Path(path).exists():
            return str(Path(path).absolute())
    
    # Check system PATH
    try:
        result = subprocess.run(["redis-server", "--version"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "redis-server"
    except:
        pass
    
    return None

def start_redis():
    """Start Redis server"""
    redis_exe = find_redis_executable()
    
    if not redis_exe:
        print("❌ Redis executable not found!")
        return False
    
    print(f"🚀 Starting Redis from: {redis_exe}")
    
    try:
        if platform.system() == "Windows":
            # Start Redis in a new console window
            subprocess.Popen([redis_exe], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Start Redis in background
            subprocess.Popen([redis_exe])
        
        print("✅ Redis server started!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
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

def stop_redis():
    """Stop Redis server"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=3)
        client.shutdown()
        print("✅ Redis server stopped gracefully")
        return True
    except:
        print("⚠️ Redis was not running or could not be stopped gracefully")
        return False

def create_startup_batch():
    """Create Windows batch file for easy Redis startup"""
    batch_content = f"""@echo off
echo 🚀 Starting Redis for Law Agent...
cd /d "{os.getcwd()}"
"{find_redis_executable()}"
pause
"""
    
    with open("start_redis.bat", "w") as f:
        f.write(batch_content)
    
    print("✅ Created start_redis.bat for manual Redis startup")

def main():
    """Main function"""
    print("🔧 REDIS AUTO-STARTER FOR LAW AGENT")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            if check_redis_running():
                print("✅ Redis is already running!")
                return True
            
            if start_redis():
                return wait_for_redis()
            return False
            
        elif command == "stop":
            return stop_redis()
            
        elif command == "status":
            if check_redis_running():
                print("✅ Redis is running")
                return True
            else:
                print("❌ Redis is not running")
                return False
                
        elif command == "restart":
            print("🔄 Restarting Redis...")
            stop_redis()
            time.sleep(2)
            if start_redis():
                return wait_for_redis()
            return False
    
    # Default behavior: ensure Redis is running
    print("🔍 Checking Redis status...")
    
    if check_redis_running():
        print("✅ Redis is already running!")
        return True
    
    print("❌ Redis is not running, starting automatically...")
    
    if start_redis():
        if wait_for_redis():
            print("🎉 Redis started successfully!")
            
            # Create convenience batch file
            if platform.system() == "Windows":
                create_startup_batch()
            
            return True
    
    print("❌ Failed to start Redis automatically")
    return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n💡 Manual Redis Control:")
            print("python auto_start_redis.py start   - Start Redis")
            print("python auto_start_redis.py stop    - Stop Redis")
            print("python auto_start_redis.py status  - Check status")
            print("python auto_start_redis.py restart - Restart Redis")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
