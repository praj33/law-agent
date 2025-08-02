#!/usr/bin/env python3
"""
Simple Redis server starter for Law Agent
This script starts a Redis server using the best available method
"""

import subprocess
import sys
import time
import os
import signal
import redis
from pathlib import Path

def check_redis_connection(host='localhost', port=6379, timeout=5):
    """Check if Redis is accessible"""
    try:
        client = redis.Redis(host=host, port=port, decode_responses=True, socket_connect_timeout=timeout)
        client.ping()
        return True
    except Exception:
        return False

def start_redis_windows():
    """Start Redis on Windows"""
    redis_exe = Path("redis/redis-server.exe")
    
    if not redis_exe.exists():
        print("❌ Redis executable not found. Please run setup_redis.py first.")
        return None
    
    try:
        # Start Redis server
        print("🚀 Starting Redis server...")
        process = subprocess.Popen([
            str(redis_exe),
            "--port", "6379",
            "--bind", "127.0.0.1",
            "--save", "",  # Disable persistence for simplicity
            "--appendonly", "no"
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        # Wait a moment for Redis to start
        time.sleep(2)
        
        # Check if Redis is running
        if check_redis_connection():
            print("✅ Redis server started successfully!")
            return process
        else:
            print("❌ Redis server failed to start properly")
            process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
        return None

def start_redis_memurai():
    """Try to start Memurai (Redis for Windows alternative)"""
    try:
        # Check if Memurai is installed
        result = subprocess.run(["memurai", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("🚀 Starting Memurai server...")
            process = subprocess.Popen(["memurai", "--port", "6379"])
            time.sleep(2)
            
            if check_redis_connection():
                print("✅ Memurai server started successfully!")
                return process
                
    except Exception:
        pass
    
    return None

def install_redis_alternative():
    """Install redis-server as Python package alternative"""
    try:
        print("📦 Installing redis-server Python package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "redis-server"], check=True)
        
        # Try to start it
        import redis_server
        print("🚀 Starting Python Redis server...")
        
        # This is a simple in-memory Redis-compatible server
        process = subprocess.Popen([
            sys.executable, "-c", 
            "import redis_server; redis_server.main(['--port', '6379', '--bind', '127.0.0.1'])"
        ])
        
        time.sleep(2)
        if check_redis_connection():
            print("✅ Python Redis server started successfully!")
            return process
            
    except Exception as e:
        print(f"❌ Failed to install/start Python Redis server: {e}")
    
    return None

def main():
    """Main function to start Redis server"""
    print("🏛️  LAW AGENT REDIS SERVER STARTER")
    print("=" * 50)
    
    # Check if Redis is already running
    if check_redis_connection():
        print("✅ Redis is already running on localhost:6379")
        return True
    
    print("🔍 Redis not running, attempting to start...")
    
    # Try different methods to start Redis
    methods = [
        ("Windows Redis", start_redis_windows),
        ("Memurai", start_redis_memurai),
        ("Python Redis Alternative", install_redis_alternative)
    ]
    
    for method_name, method_func in methods:
        print(f"\n🔄 Trying {method_name}...")
        process = method_func()
        
        if process:
            print(f"✅ {method_name} started successfully!")
            
            # Keep the process running
            try:
                print("\n📡 Redis server is running. Press Ctrl+C to stop.")
                print("🌐 You can now start your Law Agent application.")
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping Redis server...")
                process.terminate()
                process.wait()
                print("✅ Redis server stopped.")
            
            return True
    
    print("\n❌ All Redis startup methods failed!")
    print("💡 Your Law Agent will use FakeRedis as fallback.")
    print("   For better performance, consider:")
    print("   1. Installing Docker: docker run -d -p 6379:6379 redis:alpine")
    print("   2. Installing Redis for Windows manually")
    print("   3. Using WSL with Redis")
    
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
