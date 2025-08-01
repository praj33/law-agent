#!/usr/bin/env python3
"""
Single Instance Law Agent Startup
Ensures only one instance runs at a time and prevents port conflicts.
"""

import os
import sys
import subprocess
import time
import socket
import psutil
import signal
from pathlib import Path

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class SingleInstanceLawAgent:
    """Ensures only one Law Agent instance runs at a time."""
    
    def __init__(self, port=8000, host="0.0.0.0"):
        self.port = port
        self.host = host
        self.lock_file = Path("law_agent.lock")
        self.process = None
    
    def is_another_instance_running(self):
        """Check if another instance is already running."""
        if self.lock_file.exists():
            try:
                with open(self.lock_file, 'r') as f:
                    pid = int(f.read().strip())
                
                # Check if process is still running
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        return True, pid
                except psutil.NoSuchProcess:
                    pass
                
                # Lock file exists but process is dead, remove it
                self.lock_file.unlink()
            except (ValueError, FileNotFoundError):
                # Invalid lock file, remove it
                if self.lock_file.exists():
                    self.lock_file.unlink()
        
        return False, None
    
    def create_lock_file(self):
        """Create lock file with current process ID."""
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def remove_lock_file(self):
        """Remove lock file."""
        if self.lock_file.exists():
            self.lock_file.unlink()
    
    def kill_all_law_agent_processes(self):
        """Kill all Law Agent processes."""
        print("🔍 Searching for existing Law Agent processes...")
        
        killed_count = 0
        
        # Kill by port
        try:
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, text=True, shell=True
            )
            
            for line in result.stdout.split('\n'):
                if f':{self.port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            try:
                                subprocess.run(['taskkill', '/F', '/PID', pid], 
                                             capture_output=True, check=True, shell=True)
                                print(f"✅ Killed process {pid} using port {self.port}")
                                killed_count += 1
                            except subprocess.CalledProcessError:
                                pass
        except Exception as e:
            print(f"⚠️ Error checking port: {e}")
        
        # Kill by process name and command line
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
                            if pid != os.getpid():  # Don't kill ourselves
                                proc.terminate()
                                print(f"✅ Terminated Law Agent process {pid}")
                                killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ Error searching processes: {e}")
        
        if killed_count > 0:
            print(f"⏳ Waiting for {killed_count} process(es) to terminate...")
            time.sleep(5)
        else:
            print("✅ No existing Law Agent processes found")
        
        return killed_count
    
    def is_port_available(self):
        """Check if the port is available."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', self.port))
                return True
        except OSError:
            return False
    
    def wait_for_port_available(self, max_wait=30):
        """Wait for port to become available."""
        print(f"⏳ Waiting for port {self.port} to become available...")
        
        for i in range(max_wait):
            if self.is_port_available():
                print(f"✅ Port {self.port} is now available")
                return True
            time.sleep(1)
            if i % 5 == 0:
                print(f"   Still waiting... ({i}/{max_wait}s)")
        
        print(f"❌ Port {self.port} did not become available after {max_wait}s")
        return False
    
    def check_dependencies(self):
        """Check if dependencies are available."""
        print("🔍 Checking dependencies...")
        
        # Check Redis
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            print("✅ Redis: Connected")
        except Exception as e:
            print(f"⚠️ Redis: {e}")
            print("💡 Starting Redis...")
            try:
                subprocess.run([sys.executable, 'manage_redis.py', 'start'], 
                             check=True, timeout=30)
                print("✅ Redis started successfully")
            except Exception as redis_error:
                print(f"❌ Could not start Redis: {redis_error}")
                return False
        
        return True
    
    def start_law_agent(self):
        """Start Law Agent with single instance protection."""
        print("🏛️  LAW AGENT - SINGLE INSTANCE STARTUP")
        print("=" * 60)
        
        # Check for existing instance
        is_running, existing_pid = self.is_another_instance_running()
        if is_running:
            print(f"⚠️ Another Law Agent instance is already running (PID: {existing_pid})")
            print("🔄 Stopping existing instance...")
            self.kill_all_law_agent_processes()
            time.sleep(3)
        
        # Kill any remaining processes
        self.kill_all_law_agent_processes()
        
        # Wait for port to be available
        if not self.wait_for_port_available():
            print("❌ Cannot start - port is not available")
            return False
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Cannot start - dependencies not available")
            return False
        
        # Create lock file
        self.create_lock_file()
        
        # Setup signal handlers for cleanup
        def cleanup_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, cleaning up...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
        
        try:
            print(f"\n🚀 Starting Law Agent on {self.host}:{self.port}")
            print("=" * 60)
            print("🌐 Access points:")
            print(f"   • Web Interface: http://localhost:{self.port}")
            print(f"   • API Docs: http://localhost:{self.port}/api/docs")
            print(f"   • Health Check: http://localhost:{self.port}/health")
            print("=" * 60)
            print("💡 Press Ctrl+C to stop the server")
            print("=" * 60)
            
            # Start Law Agent
            self.process = subprocess.Popen([
                sys.executable, 'run_law_agent_robust.py',
                '--port', str(self.port),
                '--host', self.host
            ], cwd=Path(__file__).parent)
            
            print(f"✅ Law Agent started with PID {self.process.pid}")
            
            # Monitor the process
            try:
                self.process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Law Agent: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("🧹 Cleaning up...")
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                print("✅ Law Agent stopped gracefully")
            except subprocess.TimeoutExpired:
                print("⚠️ Force killing Law Agent...")
                self.process.kill()
                self.process.wait()
                print("✅ Law Agent force stopped")
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")
        
        self.remove_lock_file()
        print("✅ Cleanup complete")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Single Instance Law Agent")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    
    args = parser.parse_args()
    
    agent = SingleInstanceLawAgent(port=args.port, host=args.host)
    success = agent.start_law_agent()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
