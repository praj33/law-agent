#!/usr/bin/env python3
"""
Safe Law Agent Startup Script
Handles port conflicts, prevents auto-shutdown, and provides robust error recovery.
"""

import os
import sys
import time
import subprocess
import signal
import psutil
from pathlib import Path

# Suppress warnings before importing anything
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class SafeLawAgentStarter:
    """Safe startup manager for Law Agent."""
    
    def __init__(self, port=8000, host="0.0.0.0"):
        self.port = port
        self.host = host
        self.process = None
        self.restart_count = 0
        self.max_restarts = 3
    
    def kill_existing_processes(self):
        """Kill any existing Law Agent processes."""
        print("🔍 Checking for existing Law Agent processes...")
        
        killed_any = False
        
        # Kill processes by port
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
                                killed_any = True
                            except subprocess.CalledProcessError:
                                print(f"⚠️ Could not kill process {pid}")
        except Exception as e:
            print(f"⚠️ Error checking processes: {e}")
        
        # Kill Python processes running Law Agent
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and any('law_agent' in str(cmd).lower() for cmd in cmdline):
                            proc.terminate()
                            print(f"✅ Terminated Law Agent process {proc.info['pid']}")
                            killed_any = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ Error killing Python processes: {e}")
        
        if killed_any:
            print("⏳ Waiting for processes to terminate...")
            time.sleep(5)
        else:
            print("✅ No existing processes found")
    
    def check_dependencies(self):
        """Check if all dependencies are available."""
        print("🔍 Checking dependencies...")
        
        try:
            # Check Redis
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            print("✅ Redis: Connected")
        except Exception as e:
            print(f"⚠️ Redis: {e}")
            print("💡 Start Redis with: python manage_redis.py start")
        
        try:
            # Check TensorFlow
            import tensorflow as tf
            print(f"✅ TensorFlow: {tf.__version__}")
        except Exception as e:
            print(f"❌ TensorFlow: {e}")
        
        try:
            # Check PyTorch
            import torch
            print(f"✅ PyTorch: {torch.__version__}")
        except Exception as e:
            print(f"❌ PyTorch: {e}")
        
        try:
            # Check Transformers
            import transformers
            print(f"✅ Transformers: {transformers.__version__}")
        except Exception as e:
            print(f"❌ Transformers: {e}")
    
    def find_available_port(self):
        """Find an available port."""
        import socket
        
        for port in range(self.port, self.port + 20):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        raise RuntimeError(f"No available ports found starting from {self.port}")
    
    def start_law_agent(self):
        """Start Law Agent with error recovery."""
        print("\n🚀 STARTING LAW AGENT")
        print("=" * 50)
        
        # Kill existing processes
        self.kill_existing_processes()
        
        # Check dependencies
        self.check_dependencies()
        
        # Find available port
        try:
            available_port = self.find_available_port()
            if available_port != self.port:
                print(f"🔄 Using port {available_port} instead of {self.port}")
                self.port = available_port
        except RuntimeError as e:
            print(f"❌ {e}")
            return False
        
        # Start the server
        while self.restart_count < self.max_restarts:
            try:
                print(f"\n🎯 Attempt {self.restart_count + 1}/{self.max_restarts}")
                print(f"🌐 Starting on http://{self.host}:{self.port}")
                
                # Start Law Agent process
                self.process = subprocess.Popen([
                    sys.executable, 'run_law_agent_robust.py',
                    '--port', str(self.port),
                    '--host', self.host,
                    '--kill-existing'
                ], cwd=Path(__file__).parent)
                
                print(f"✅ Law Agent started with PID {self.process.pid}")
                print("🔗 Access at:")
                print(f"   • Web Interface: http://{self.host}:{self.port}")
                print(f"   • API Docs: http://{self.host}:{self.port}/api/docs")
                print(f"   • Health Check: http://{self.host}:{self.port}/health")
                print("\n💡 Press Ctrl+C to stop the server")
                
                # Monitor the process
                self.monitor_process()
                
                return True
                
            except Exception as e:
                print(f"❌ Startup failed: {e}")
                self.restart_count += 1
                
                if self.restart_count < self.max_restarts:
                    print(f"🔄 Restarting in 5 seconds... ({self.restart_count}/{self.max_restarts})")
                    time.sleep(5)
                else:
                    print("❌ Maximum restart attempts reached")
                    return False
        
        return False
    
    def monitor_process(self):
        """Monitor the Law Agent process."""
        try:
            while True:
                if self.process.poll() is not None:
                    print(f"\n⚠️ Law Agent process exited with code {self.process.returncode}")
                    
                    if self.restart_count < self.max_restarts:
                        print("🔄 Attempting automatic restart...")
                        self.restart_count += 1
                        time.sleep(3)
                        return self.start_law_agent()
                    else:
                        print("❌ Maximum restarts reached. Stopping.")
                        return False
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
            self.cleanup()
            return True
    
    def cleanup(self):
        """Clean up processes."""
        if self.process:
            try:
                print("🧹 Cleaning up...")
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
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe Law Agent Startup")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    
    args = parser.parse_args()
    
    print("🏛️  LAW AGENT - SAFE STARTUP")
    print("=" * 50)
    print("🛡️ Features:")
    print("   • Automatic port conflict resolution")
    print("   • Process cleanup and restart")
    print("   • Dependency checking")
    print("   • Graceful shutdown handling")
    print("=" * 50)
    
    starter = SafeLawAgentStarter(port=args.port, host=args.host)
    starter.setup_signal_handlers()
    
    success = starter.start_law_agent()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
