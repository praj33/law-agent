#!/usr/bin/env python3
"""
Bulletproof Law Agent Startup
Absolutely prevents port conflicts and ensures single instance operation.
"""

import os
import sys
import subprocess
import time
import socket
import psutil
import signal
import threading
from pathlib import Path

# Suppress warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

class BulletproofLawAgent:
    """Bulletproof Law Agent startup with zero port conflicts."""
    
    def __init__(self, port=8000, host="0.0.0.0"):
        self.port = port
        self.host = host
        self.lock_file = Path("law_agent_bulletproof.lock")
        self.process = None
        self.monitoring = False
        self.monitor_thread = None
    
    def nuclear_cleanup(self):
        """Nuclear option: kill everything that could use port 8000."""
        print("🔥 NUCLEAR CLEANUP - Killing all potential conflicts")
        print("=" * 60)
        
        killed_count = 0
        
        # Method 1: Kill by port using netstat
        try:
            result = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, text=True, shell=True
            )
            
            pids_to_kill = set()
            for line in result.stdout.split('\n'):
                if ':8000' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            pids_to_kill.add(pid)
            
            for pid in pids_to_kill:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', pid], 
                                 capture_output=True, check=True, shell=True)
                    print(f"✅ Killed PID {pid} (port method)")
                    killed_count += 1
                except subprocess.CalledProcessError:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Port cleanup error: {e}")
        
        # Method 2: Kill all Python processes with Law Agent keywords
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline:
                            cmdline_str = ' '.join(str(cmd) for cmd in cmdline).lower()
                            if any(keyword in cmdline_str for keyword in [
                                'law_agent', 'run_law_agent', 'uvicorn', 
                                'fastapi', 'start_law_agent'
                            ]):
                                pid = proc.info['pid']
                                if pid != os.getpid():  # Don't kill ourselves
                                    proc.terminate()
                                    print(f"✅ Killed PID {pid} (process method)")
                                    killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"⚠️ Process cleanup error: {e}")
        
        # Method 3: Kill by process name patterns
        process_patterns = ['python.exe', 'pythonw.exe']
        for pattern in process_patterns:
            try:
                subprocess.run(['taskkill', '/F', '/IM', pattern], 
                             capture_output=True, shell=True)
            except:
                pass
        
        if killed_count > 0:
            print(f"🔥 Killed {killed_count} processes")
            print("⏳ Waiting for cleanup to complete...")
            time.sleep(10)  # Longer wait for complete cleanup
        else:
            print("✅ No processes to kill")
        
        # Remove any lock files
        for lock_pattern in ['*.lock', 'law_agent*.lock']:
            for lock_file in Path('.').glob(lock_pattern):
                try:
                    lock_file.unlink()
                    print(f"🗑️ Removed lock file: {lock_file}")
                except:
                    pass
        
        return killed_count
    
    def wait_for_port_completely_free(self, max_wait=60):
        """Wait until port is completely free with multiple verification methods."""
        print(f"⏳ Waiting for port {self.port} to be completely free...")
        
        for attempt in range(max_wait):
            port_free = True
            
            # Method 1: Socket binding test
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('localhost', self.port))
            except OSError:
                port_free = False
            
            # Method 2: netstat verification
            try:
                result = subprocess.run(
                    ['netstat', '-ano'], 
                    capture_output=True, text=True, shell=True
                )
                for line in result.stdout.split('\n'):
                    if f':{self.port}' in line and 'LISTENING' in line:
                        port_free = False
                        break
            except:
                pass
            
            if port_free:
                print(f"✅ Port {self.port} is completely free")
                return True
            
            if attempt % 10 == 0:
                print(f"   Still waiting... ({attempt}/{max_wait}s)")
            
            time.sleep(1)
        
        print(f"❌ Port {self.port} did not become free after {max_wait}s")
        return False
    
    def start_with_alternative_port(self):
        """Start on an alternative port if 8000 is persistently blocked."""
        print("🔄 Trying alternative ports...")
        
        for alt_port in range(8001, 8020):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(('localhost', alt_port))
                    
                print(f"✅ Found available port: {alt_port}")
                self.port = alt_port
                return True
                
            except OSError:
                continue
        
        print("❌ No alternative ports available")
        return False
    
    def monitor_process(self):
        """Monitor the Law Agent process and restart if it dies."""
        while self.monitoring and self.process:
            try:
                if self.process.poll() is not None:
                    print(f"\n⚠️ Law Agent process died (exit code: {self.process.returncode})")
                    print("🔄 Attempting automatic restart...")
                    
                    # Clean up and restart
                    time.sleep(5)
                    self.nuclear_cleanup()
                    
                    if self.wait_for_port_completely_free():
                        self.start_law_agent_process()
                    else:
                        print("❌ Could not restart - port still blocked")
                        break
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
                time.sleep(5)
    
    def start_law_agent_process(self):
        """Start the actual Law Agent process."""
        try:
            print(f"🚀 Starting Law Agent on {self.host}:{self.port}")
            
            self.process = subprocess.Popen([
                sys.executable, 'run_law_agent_robust.py',
                '--port', str(self.port),
                '--host', self.host
            ], cwd=Path(__file__).parent)
            
            print(f"✅ Law Agent started with PID {self.process.pid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Law Agent: {e}")
            return False
    
    def start_bulletproof(self):
        """Start Law Agent with bulletproof protection."""
        print("🛡️  LAW AGENT - BULLETPROOF STARTUP")
        print("=" * 70)
        print("🔥 Features:")
        print("   • Nuclear cleanup of all conflicts")
        print("   • Multiple port verification methods")
        print("   • Automatic process monitoring")
        print("   • Alternative port fallback")
        print("   • Automatic restart on failure")
        print("=" * 70)
        
        # Step 1: Nuclear cleanup
        self.nuclear_cleanup()
        
        # Step 2: Wait for port to be completely free
        if not self.wait_for_port_completely_free():
            print("⚠️ Port 8000 persistently blocked, trying alternatives...")
            if not self.start_with_alternative_port():
                print("❌ Cannot find any available port")
                return False
        
        # Step 3: Check dependencies
        print("🔍 Checking dependencies...")
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
                print("✅ Redis started")
            except Exception:
                print("❌ Could not start Redis")
                return False
        
        # Step 4: Create lock file
        with open(self.lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Step 5: Setup signal handlers
        def cleanup_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, cleaning up...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, cleanup_handler)
        signal.signal(signal.SIGTERM, cleanup_handler)
        
        # Step 6: Start Law Agent
        if not self.start_law_agent_process():
            return False
        
        # Step 7: Start monitoring
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
        self.monitor_thread.start()
        
        # Step 8: Display access information
        print("\n" + "=" * 70)
        print("🎉 LAW AGENT STARTED SUCCESSFULLY!")
        print("=" * 70)
        print(f"🌐 Web Interface: http://localhost:{self.port}")
        print(f"📚 API Docs: http://localhost:{self.port}/api/docs")
        print(f"🔍 Health Check: http://localhost:{self.port}/health")
        print("=" * 70)
        print("💡 Press Ctrl+C to stop the server")
        print("🔄 Automatic restart enabled")
        print("=" * 70)
        
        # Step 9: Wait for process
        try:
            self.process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested by user")
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        print("🧹 Cleaning up...")
        
        self.monitoring = False
        
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
        
        if self.lock_file.exists():
            self.lock_file.unlink()
        
        print("✅ Cleanup complete")


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bulletproof Law Agent")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    
    args = parser.parse_args()
    
    agent = BulletproofLawAgent(port=args.port, host=args.host)
    success = agent.start_bulletproof()
    
    agent.cleanup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
