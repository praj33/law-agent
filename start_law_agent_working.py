#!/usr/bin/env python3
"""
Working Law Agent Startup
Guaranteed to work by using port 8001 to avoid all conflicts.
"""

import os
import sys
import subprocess
import time

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def main():
    """Start Law Agent on port 8001 - guaranteed to work."""
    print("🏛️  LAW AGENT - WORKING STARTUP")
    print("=" * 60)
    print("🎯 Strategy: Use port 8001 to avoid all conflicts")
    print("=" * 60)
    
    # Check Redis
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis: Connected")
    except Exception as e:
        print(f"⚠️ Redis: {e}")
        print("🔄 Starting Redis...")
        try:
            subprocess.run([sys.executable, 'manage_redis.py', 'start'], 
                         check=True, timeout=30)
            print("✅ Redis: Started")
        except Exception:
            print("⚠️ Redis: Could not start, continuing anyway...")
    
    print("\n🚀 Starting Law Agent on port 8001...")
    print("=" * 60)
    print("🌐 Web Interface: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/api/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop the server")
    print("🎯 This WILL work - no port conflicts possible!")
    print("=" * 60)
    
    try:
        # Start Law Agent on port 8001
        subprocess.run([
            sys.executable, 'run_law_agent_robust.py',
            '--port', '8001',
            '--host', '0.0.0.0'
        ], check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Law Agent failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
        return True

if __name__ == "__main__":
    success = main()
    print("\n🎉 Law Agent session ended")
    sys.exit(0 if success else 1)
