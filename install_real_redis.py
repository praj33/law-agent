#!/usr/bin/env python3
"""
Install Real Redis for Windows
Downloads and sets up a proper Redis server instance.
"""

import subprocess
import sys
import os
import requests
import zipfile
import shutil
import time
import threading
from pathlib import Path

class RedisInstaller:
    """Install and manage real Redis on Windows."""
    
    def __init__(self):
        self.redis_dir = Path("redis_server")
        self.redis_exe = None
        self.redis_process = None
        
    def check_existing_redis(self) -> bool:
        """Check if Redis is already running."""
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            print("✅ Redis is already running!")
            return True
        except:
            return False
    
    def download_redis_windows(self) -> bool:
        """Download Redis for Windows."""
        try:
            print("📥 Downloading Redis for Windows...")
            
            # Create redis directory
            self.redis_dir.mkdir(exist_ok=True)
            
            # Download Memurai (Redis-compatible for Windows)
            # Alternative: Use Redis from Microsoft's archive
            url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
            zip_path = self.redis_dir / "redis.zip"
            
            print(f"🌐 Downloading from: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📦 Progress: {percent:.1f}%", end="", flush=True)
            
            print(f"\n✅ Downloaded {downloaded // (1024*1024):.1f} MB")
            
            # Extract Redis
            print("📦 Extracting Redis...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.redis_dir)
            
            # Remove zip file
            zip_path.unlink()
            
            # Find redis-server.exe
            for exe_file in self.redis_dir.rglob("redis-server.exe"):
                self.redis_exe = exe_file
                break
            
            if not self.redis_exe:
                print("❌ redis-server.exe not found in extracted files")
                return False
            
            print(f"✅ Redis extracted to: {self.redis_exe}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download Redis: {e}")
            return False
    
    def install_redis_via_chocolatey(self) -> bool:
        """Try to install Redis via Chocolatey."""
        try:
            print("🍫 Trying to install Redis via Chocolatey...")
            
            # Check if chocolatey is available
            result = subprocess.run(['choco', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Chocolatey not available")
                return False
            
            print("✅ Chocolatey found, installing Redis...")
            result = subprocess.run(['choco', 'install', 'redis-64', '-y'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Redis installed via Chocolatey!")
                # Find redis installation
                redis_paths = [
                    Path("C:/ProgramData/chocolatey/lib/redis-64/tools/redis-server.exe"),
                    Path("C:/tools/redis/redis-server.exe"),
                ]
                
                for path in redis_paths:
                    if path.exists():
                        self.redis_exe = path
                        return True
                
                print("⚠️ Redis installed but executable not found in expected locations")
                return False
            else:
                print(f"❌ Chocolatey installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Chocolatey installation timed out")
            return False
        except Exception as e:
            print(f"❌ Chocolatey installation error: {e}")
            return False
    
    def install_redis_via_scoop(self) -> bool:
        """Try to install Redis via Scoop."""
        try:
            print("🪣 Trying to install Redis via Scoop...")
            
            # Check if scoop is available
            result = subprocess.run(['scoop', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Scoop not available")
                return False
            
            print("✅ Scoop found, installing Redis...")
            result = subprocess.run(['scoop', 'install', 'redis'], 
                                  capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                print("✅ Redis installed via Scoop!")
                
                # Find redis in scoop directory
                scoop_dir = Path.home() / "scoop" / "apps" / "redis" / "current"
                redis_exe = scoop_dir / "redis-server.exe"
                
                if redis_exe.exists():
                    self.redis_exe = redis_exe
                    return True
                else:
                    print("⚠️ Redis installed but executable not found")
                    return False
            else:
                print(f"❌ Scoop installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Scoop installation timed out")
            return False
        except Exception as e:
            print(f"❌ Scoop installation error: {e}")
            return False
    
    def create_redis_config(self) -> Path:
        """Create Redis configuration file."""
        config_content = """# Redis Configuration for Law Agent
port 6379
bind 127.0.0.1
timeout 0
tcp-keepalive 300
daemonize no
supervised no
pidfile redis.pid
loglevel notice
logfile redis.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ./
maxmemory 256mb
maxmemory-policy allkeys-lru
"""
        
        config_path = self.redis_dir / "redis.conf"
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Redis config created: {config_path}")
        return config_path
    
    def start_redis_server(self) -> bool:
        """Start Redis server."""
        try:
            if not self.redis_exe or not self.redis_exe.exists():
                print("❌ Redis executable not found")
                return False
            
            # Create config file
            config_path = self.create_redis_config()
            
            print(f"🚀 Starting Redis server: {self.redis_exe}")
            
            # Start Redis in background
            self.redis_process = subprocess.Popen(
                [str(self.redis_exe), str(config_path)],
                cwd=str(self.redis_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait for Redis to start
            print("⏳ Waiting for Redis to start...")
            for i in range(10):
                time.sleep(1)
                if self.check_existing_redis():
                    print("✅ Redis server started successfully!")
                    return True
                print(f"   Attempt {i+1}/10...")
            
            print("❌ Redis failed to start within 10 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start Redis: {e}")
            return False
    
    def install_redis(self) -> bool:
        """Main installation method."""
        print("🏛️  INSTALLING REAL REDIS FOR LAW AGENT")
        print("=" * 60)
        
        # Check if already running
        if self.check_existing_redis():
            return True
        
        # Try different installation methods
        installation_methods = [
            ("Chocolatey", self.install_redis_via_chocolatey),
            ("Scoop", self.install_redis_via_scoop),
            ("Direct Download", self.download_redis_windows),
        ]
        
        for method_name, method_func in installation_methods:
            print(f"\n🔄 Trying {method_name}...")
            try:
                if method_func():
                    print(f"✅ Redis installed via {method_name}")
                    
                    # Start Redis server
                    if self.start_redis_server():
                        print("\n" + "=" * 60)
                        print("🎉 REDIS INSTALLATION COMPLETE!")
                        print("✅ Real Redis server is now running")
                        print("🔗 Connection: localhost:6379")
                        print("📊 Memory limit: 256MB")
                        print("💾 Persistence: Enabled")
                        print("=" * 60)
                        return True
                    else:
                        print(f"❌ {method_name} installed Redis but failed to start")
                else:
                    print(f"❌ {method_name} installation failed")
            except Exception as e:
                print(f"❌ {method_name} error: {e}")
        
        print("\n❌ All Redis installation methods failed!")
        print("💡 Manual installation options:")
        print("   1. Install Docker and run: docker run -d -p 6379:6379 redis:alpine")
        print("   2. Download Redis from: https://github.com/microsoftarchive/redis/releases")
        print("   3. Install via WSL: wsl --install then apt install redis-server")
        
        return False
    
    def stop_redis(self):
        """Stop Redis server."""
        if self.redis_process:
            try:
                self.redis_process.terminate()
                self.redis_process.wait(timeout=5)
                print("✅ Redis server stopped")
            except:
                try:
                    self.redis_process.kill()
                    print("✅ Redis server killed")
                except:
                    print("⚠️ Could not stop Redis server")


def main():
    """Main installation function."""
    installer = RedisInstaller()
    
    try:
        success = installer.install_redis()
        
        if success:
            print("\n🎯 NEXT STEPS:")
            print("1. Redis is now running on localhost:6379")
            print("2. Restart Law Agent: python run_law_agent_robust.py --kill-existing")
            print("3. You should see: ✅ Redis connected successfully")
            
            # Test connection
            print("\n🧪 Testing Redis connection...")
            try:
                import redis
                client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                client.ping()
                client.set('test_key', 'Law Agent Redis Test')
                value = client.get('test_key')
                client.delete('test_key')
                print(f"✅ Redis test successful: {value}")
            except Exception as e:
                print(f"❌ Redis test failed: {e}")
        
        return success
        
    except KeyboardInterrupt:
        print("\n👋 Installation cancelled by user")
        installer.stop_redis()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
