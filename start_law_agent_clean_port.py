#!/usr/bin/env python3
"""
Law Agent Startup with Complete Port Management
Handles all port conflicts and ensures clean startup.
"""

import os
import sys
import subprocess
import time
import socket
import psutil
from pathlib import Path

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class PortManager:
    """Complete port management for Law Agent."""
    
    @staticmethod
    def find_processes_on_port(port):
        """Find all processes using a specific port."""
        processes = []
        try:
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, text=True, shell=True
            )
            
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            processes.append(int(pid))
            
            return processes
        except Exception as e:
            print(f"⚠️ Error finding processes: {e}")
            return []
    
    @staticmethod
    def kill_processes_on_port(port):
        """Kill all processes using a specific port."""
        print(f"🔍 Checking for processes on port {port}...")
        
        processes = PortManager.find_processes_on_port(port)
        
        if not processes:
            print(f"✅ Port {port} is free")
            return True
        
        print(f"🎯 Found {len(processes)} process(es) using port {port}: {processes}")
        
        killed_count = 0
        for pid in processes:
            try:
                # Try graceful termination first
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()
                    proc.wait(timeout=3)
                    print(f"✅ Gracefully terminated process {pid}")
                    killed_count += 1
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    proc.kill()
                    print(f"🔥 Force killed process {pid}")
                    killed_count += 1
                except psutil.NoSuchProcess:
                    print(f"⚠️ Process {pid} already terminated")
                    killed_count += 1
                    
            except Exception as e:
                # Fallback to taskkill
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                 capture_output=True, check=True, shell=True)
                    print(f"✅ Killed process {pid} with taskkill")
                    killed_count += 1
                except subprocess.CalledProcessError:
                    print(f"❌ Could not kill process {pid}")
        
        if killed_count > 0:
            print(f"⏳ Waiting for port {port} to be released...")
            time.sleep(5)
            
            # Verify port is free
            remaining = PortManager.find_processes_on_port(port)
            if remaining:
                print(f"⚠️ Warning: {len(remaining)} process(es) still using port {port}")
                return False
            else:
                print(f"✅ Port {port} is now free")
                return True
        
        return killed_count > 0
    
    @staticmethod
    def kill_all_law_agent_processes():
        """Kill all Python processes that might be running Law Agent."""
        print("🔍 Searching for Law Agent processes...")
        
        killed_count = 0
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('law_agent' in str(cmd).lower() or 
                                         'run_law_agent' in str(cmd).lower() or
                                         'uvicorn' in str(cmd).lower()
                                         for cmd in cmdline):
                            pid = proc.info['pid']
                            proc.terminate()
                            print(f"✅ Terminated Law Agent process {pid}")
                            killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ Error searching for processes: {e}")
        
        if killed_count > 0:
            print(f"⏳ Waiting for {killed_count} process(es) to terminate...")
            time.sleep(3)
        else:
            print("✅ No Law Agent processes found")
        
        return killed_count
    
    @staticmethod
    def is_port_available(port):
        """Check if a port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    @staticmethod
    def find_available_port(start_port=8000, max_attempts=20):
        """Find an available port."""
        for port in range(start_port, start_port + max_attempts):
            if PortManager.is_port_available(port):
                return port
        raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")

def check_redis():
    """Check if Redis is running."""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis: Connected")
        return True
    except Exception as e:
        print(f"⚠️ Redis: {e}")
        print("💡 Start Redis with: python manage_redis.py start")
        return False

def main():
    """Main startup function."""
    print("🏛️  LAW AGENT - COMPLETE PORT CLEANUP & STARTUP")
    print("=" * 60)
    
    # Step 1: Kill all Law Agent processes
    PortManager.kill_all_law_agent_processes()
    
    # Step 2: Clean up port 8000 specifically
    port_cleaned = PortManager.kill_processes_on_port(8000)
    
    # Step 3: Find available port
    try:
        if PortManager.is_port_available(8000):
            port = 8000
            print("✅ Port 8000 is available")
        else:
            port = PortManager.find_available_port(8000)
            print(f"🔄 Using alternative port: {port}")
    except RuntimeError as e:
        print(f"❌ {e}")
        return False
    
    # Step 4: Check dependencies
    redis_ok = check_redis()
    if not redis_ok:
        print("⚠️ Redis is not running. Starting Redis...")
        try:
            subprocess.run([sys.executable, 'manage_redis.py', 'start'], 
                         check=True, timeout=30)
            redis_ok = check_redis()
        except Exception as e:
            print(f"❌ Could not start Redis: {e}")
    
    # Step 5: Start Law Agent
    print(f"\n🚀 Starting Law Agent on port {port}...")
    print("=" * 60)
    
    try:
        # Start with the robust script
        cmd = [
            sys.executable, 'run_law_agent_robust.py',
            '--port', str(port),
            '--host', '0.0.0.0'
        ]
        
        print(f"🎯 Command: {' '.join(cmd)}")
        print("🌐 Access at:")
        print(f"   • Web Interface: http://localhost:{port}")
        print(f"   • API Docs: http://localhost:{port}/api/docs")
        print(f"   • Health Check: http://localhost:{port}/health")
        print("\n💡 Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Execute the command
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Law Agent failed to start: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check Redis: python manage_redis.py status")
        print("2. Check dependencies: python fix_tensorflow_warnings.py")
        print("3. Try manual start: python run_law_agent_robust.py --port 8001")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
