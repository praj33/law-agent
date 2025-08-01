#!/usr/bin/env python3
"""
Cleanup and Start Law Agent - Solves Port Conflicts
"""

import subprocess
import time
import socket
import sys

def kill_processes_on_port(port):
    """Kill all processes using the specified port."""
    print(f"🔍 Checking for processes on port {port}...")
    try:
        # Get processes using the port
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
        lines = result.stdout.split('\n')
        
        pids_to_kill = []
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5 and parts[-1].isdigit():
                    pid = parts[-1]
                    pids_to_kill.append(pid)
                    print(f"   Found process PID {pid} using port {port}")
        
        # Kill the processes
        for pid in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True, shell=True)
                print(f"   ✅ Killed process PID {pid}")
            except:
                pass
        
        if not pids_to_kill:
            print(f"   ✅ No processes found on port {port}")
            
    except Exception as e:
        print(f"   ⚠️ Error checking port: {e}")

def kill_all_python():
    """Kill all Python processes."""
    print("🔥 Killing all Python processes...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], capture_output=True, shell=True)
        subprocess.run(['taskkill', '/F', '/IM', 'pythonw.exe'], capture_output=True, shell=True)
        print("   ✅ All Python processes killed")
    except:
        print("   ⚠️ No Python processes to kill")

def find_available_port(start_port=8000, max_attempts=20):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_law_agent(port):
    """Start the Law Agent on the specified port."""
    print(f"🚀 Starting Law Agent on port {port}...")
    try:
        # Start the Law Agent
        cmd = [sys.executable, 'law_agent_minimal.py', '--port', str(port)]
        process = subprocess.Popen(cmd)
        
        print(f"✅ Law Agent started successfully!")
        print(f"🌐 Web Interface: http://localhost:{port}")
        print(f"💬 Chat Interface: http://localhost:{port}/chat")
        print(f"📚 API Documentation: http://localhost:{port}/docs")
        print("=" * 60)
        print("💡 Press Ctrl+C to stop the server")
        print("🎉 Your Law Agent is ready to use!")
        print("=" * 60)
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Law Agent...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("✅ Law Agent stopped")
            
    except Exception as e:
        print(f"❌ Failed to start Law Agent: {e}")

def main():
    print("🔧 LAW AGENT CLEANUP AND STARTUP")
    print("=" * 50)
    
    # Step 1: Kill processes on common ports
    for port in [8000, 8001, 8002]:
        kill_processes_on_port(port)
    
    # Step 2: Kill all Python processes
    kill_all_python()
    
    # Step 3: Wait a moment
    print("⏳ Waiting for cleanup to complete...")
    time.sleep(3)
    
    # Step 4: Find available port
    available_port = find_available_port(8000)
    if not available_port:
        print("❌ No available ports found!")
        return
    
    print(f"✅ Found available port: {available_port}")
    
    # Step 5: Start Law Agent
    start_law_agent(available_port)

if __name__ == "__main__":
    main()
