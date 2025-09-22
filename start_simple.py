#!/usr/bin/env python3
"""
Simple Law Agent Startup
Direct startup with port conflict resolution.
"""

import os
import sys
import subprocess
import time

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

def kill_port_8000():
    """Kill any process using port 8000."""
    print("🔍 Checking port 8000...")
    
    try:
        # Find processes using port 8000
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, text=True, shell=True
        )
        
        pids_to_kill = []
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # Kill the processes
        for pid in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], 
                             capture_output=True, check=True, shell=True)
                print(f"✅ Killed process {pid} using port 8000")
            except subprocess.CalledProcessError:
                print(f"⚠️ Could not kill process {pid}")
        
        if pids_to_kill:
            print("⏳ Waiting for port to be released...")
            time.sleep(3)
        else:
            print("✅ Port 8000 is available")
            
    except Exception as e:
        print(f"⚠️ Error checking port: {e}")

def main():
    """Main function."""
    print("🏛️  LAW AGENT - SIMPLE STARTUP")
    print("=" * 50)
    
    # Kill existing processes on port 8000
    kill_port_8000()
    
    # Start Law Agent
    print("🚀 Starting Law Agent...")
    
    try:
        # Use the robust startup script with kill-existing flag
        subprocess.run([
            sys.executable, 'run_law_agent_robust.py',
            '--kill-existing',
            '--port', '8000',
            '--host', '0.0.0.0'
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Law Agent failed to start: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Check if Redis is running: python manage_redis.py status")
        print("2. Check dependencies: pip list | findstr tensorflow")
        print("3. Try different port: python run_law_agent_robust.py --port 8001")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
