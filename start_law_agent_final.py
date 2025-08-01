#!/usr/bin/env python3
"""
Final Law Agent Startup Solution
Simple, direct, and bulletproof approach to starting Law Agent.
"""

import os
import sys
import subprocess
import time
import socket

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def kill_everything_on_port_8000():
    """Kill everything using port 8000 - no mercy."""
    print("🔥 KILLING EVERYTHING ON PORT 8000")
    print("=" * 50)
    
    # Method 1: netstat + taskkill
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
        pids = []
        for line in result.stdout.split('\n'):
            if ':8000' in line:
                parts = line.split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pids.append(parts[-1])
        
        for pid in set(pids):
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, shell=True)
                print(f"✅ Killed PID {pid}")
            except:
                pass
    except:
        pass
    
    # Method 2: Kill all python processes (nuclear option)
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True, shell=True)
        subprocess.run(['taskkill', '/F', '/IM', 'pythonw.exe'], capture_output=True, shell=True)
        print("✅ Killed all Python processes")
    except:
        pass
    
    print("⏳ Waiting 10 seconds for cleanup...")
    time.sleep(10)

def check_port_8000():
    """Check if port 8000 is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('localhost', 8000))
            return True
    except OSError:
        return False

def find_available_port():
    """Find an available port starting from 8000."""
    for port in range(8000, 8020):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_redis():
    """Start Redis if not running."""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis: Already running")
        return True
    except:
        print("🔄 Starting Redis...")
        try:
            subprocess.run([sys.executable, 'manage_redis.py', 'start'], 
                         check=True, timeout=30)
            print("✅ Redis: Started")
            return True
        except:
            print("❌ Redis: Failed to start")
            return False

def main():
    """Main function - simple and direct."""
    print("🏛️  LAW AGENT - FINAL STARTUP SOLUTION")
    print("=" * 60)
    
    # Step 1: Nuclear cleanup
    kill_everything_on_port_8000()
    
    # Step 2: Find available port
    port = find_available_port()
    if not port:
        print("❌ No available ports found")
        return False
    
    if port != 8000:
        print(f"⚠️ Port 8000 blocked, using port {port}")
    else:
        print("✅ Port 8000 is available")
    
    # Step 3: Start Redis
    if not start_redis():
        print("⚠️ Continuing without Redis...")
    
    # Step 4: Start Law Agent
    print(f"\n🚀 Starting Law Agent on port {port}...")
    print("=" * 60)
    print(f"🌐 Web Interface: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/api/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        # Start Law Agent directly
        subprocess.run([
            sys.executable, 'run_law_agent_robust.py',
            '--port', str(port),
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
    sys.exit(0 if success else 1)
