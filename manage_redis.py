#!/usr/bin/env python3
"""
Redis Management Script for Law Agent
Start, stop, monitor, and manage Redis server.
"""

import subprocess
import sys
import os
import time
import psutil
import argparse
from pathlib import Path

class RedisManager:
    """Manage Redis server for Law Agent."""
    
    def __init__(self):
        self.redis_dir = Path("redis_server")
        self.redis_exe = self.redis_dir / "redis-server.exe"
        self.redis_config = self.redis_dir / "redis.windows.conf"
        self.redis_process = None
        
    def is_redis_running(self) -> bool:
        """Check if Redis is running."""
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            return True
        except:
            return False
    
    def find_redis_process(self):
        """Find Redis process if running."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'redis-server' in proc.info['name'].lower():
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_redis(self) -> bool:
        """Start Redis server."""
        if self.is_redis_running():
            print("✅ Redis is already running!")
            return True
        
        if not self.redis_exe.exists():
            print("❌ Redis executable not found!")
            print("💡 Run: python install_real_redis.py")
            return False
        
        try:
            print("🚀 Starting Redis server...")
            
            # Start Redis in a new console window
            self.redis_process = subprocess.Popen(
                [str(self.redis_exe), str(self.redis_config)],
                cwd=str(self.redis_dir),
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            # Wait for Redis to start
            for i in range(10):
                time.sleep(1)
                if self.is_redis_running():
                    print("✅ Redis server started successfully!")
                    print(f"🔗 Connection: localhost:6379")
                    print(f"📊 Process ID: {self.redis_process.pid}")
                    return True
                print(f"   Waiting... {i+1}/10")
            
            print("❌ Redis failed to start within 10 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Redis: {e}")
            return False
    
    def stop_redis(self) -> bool:
        """Stop Redis server."""
        if not self.is_redis_running():
            print("✅ Redis is not running")
            return True
        
        try:
            print("🛑 Stopping Redis server...")
            
            # Find and terminate Redis process
            redis_proc = self.find_redis_process()
            if redis_proc:
                redis_proc.terminate()
                redis_proc.wait(timeout=5)
                print("✅ Redis server stopped successfully!")
                return True
            else:
                print("⚠️ Could not find Redis process")
                return False
                
        except psutil.TimeoutExpired:
            print("⚠️ Redis process did not stop gracefully, forcing...")
            try:
                redis_proc.kill()
                print("✅ Redis server killed")
                return True
            except:
                print("❌ Could not kill Redis process")
                return False
        except Exception as e:
            print(f"❌ Failed to stop Redis: {e}")
            return False
    
    def restart_redis(self) -> bool:
        """Restart Redis server."""
        print("🔄 Restarting Redis server...")
        self.stop_redis()
        time.sleep(2)
        return self.start_redis()
    
    def status_redis(self):
        """Show Redis status and statistics."""
        print("🔍 REDIS STATUS")
        print("=" * 40)
        
        if self.is_redis_running():
            print("✅ Status: Running")
            
            try:
                import redis
                client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                
                # Get Redis info
                info = client.info()
                print(f"📊 Version: {info.get('redis_version', 'Unknown')}")
                print(f"⏱️ Uptime: {info.get('uptime_in_seconds', 0)} seconds")
                print(f"🔗 Connected clients: {info.get('connected_clients', 0)}")
                print(f"💾 Used memory: {info.get('used_memory_human', 'Unknown')}")
                print(f"🔑 Total keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")
                
                # Check Law Agent specific data
                keys = client.keys('*')
                user_profiles = len([k for k in keys if k.startswith('user_profile:')])
                interactions = len([k for k in keys if k.startswith('interactions:')])
                agent_states = len([k for k in keys if k.startswith('agent_state:')])
                
                print(f"👤 User profiles: {user_profiles}")
                print(f"💬 User interactions: {interactions}")
                print(f"🤖 Agent states: {agent_states}")
                
            except Exception as e:
                print(f"⚠️ Could not get detailed info: {e}")
            
            # Find process info
            redis_proc = self.find_redis_process()
            if redis_proc:
                print(f"🆔 Process ID: {redis_proc.pid}")
                print(f"💾 Memory usage: {redis_proc.memory_info().rss / 1024 / 1024:.1f} MB")
                print(f"⚡ CPU usage: {redis_proc.cpu_percent():.1f}%")
        else:
            print("❌ Status: Not running")
            print("💡 Start with: python manage_redis.py start")
    
    def monitor_redis(self):
        """Monitor Redis in real-time."""
        print("📊 REDIS REAL-TIME MONITORING")
        print("=" * 50)
        print("Press Ctrl+C to stop monitoring...")
        
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            while True:
                if self.is_redis_running():
                    info = client.info()
                    keys_count = len(client.keys('*'))
                    memory_mb = info.get('used_memory', 0) / 1024 / 1024
                    
                    print(f"\r🔄 Keys: {keys_count:4d} | Memory: {memory_mb:6.1f}MB | "
                          f"Clients: {info.get('connected_clients', 0):2d} | "
                          f"Ops/sec: {info.get('instantaneous_ops_per_sec', 0):4d}", 
                          end="", flush=True)
                else:
                    print("\r❌ Redis not running" + " " * 50, end="", flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
    
    def backup_redis(self):
        """Create Redis backup."""
        if not self.is_redis_running():
            print("❌ Redis is not running")
            return False
        
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            print("💾 Creating Redis backup...")
            
            # Trigger background save
            client.bgsave()
            
            # Wait for save to complete
            while client.lastsave() == client.lastsave():
                time.sleep(0.1)
            
            # Copy dump file with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.redis_dir / f"dump_backup_{timestamp}.rdb"
            
            dump_file = self.redis_dir / "dump.rdb"
            if dump_file.exists():
                import shutil
                shutil.copy2(dump_file, backup_file)
                print(f"✅ Backup created: {backup_file}")
                return True
            else:
                print("❌ Dump file not found")
                return False
                
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Redis Management for Law Agent")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "monitor", "backup"],
                       help="Action to perform")
    
    args = parser.parse_args()
    manager = RedisManager()
    
    if args.action == "start":
        success = manager.start_redis()
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        success = manager.stop_redis()
        sys.exit(0 if success else 1)
    elif args.action == "restart":
        success = manager.restart_redis()
        sys.exit(0 if success else 1)
    elif args.action == "status":
        manager.status_redis()
    elif args.action == "monitor":
        manager.monitor_redis()
    elif args.action == "backup":
        success = manager.backup_redis()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
