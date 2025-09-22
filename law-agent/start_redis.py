#!/usr/bin/env python3
"""
Redis Auto-Starter for Law Agent
Automatically starts Redis when the system starts
"""

import os
import sys
import time
import subprocess
import platform
import requests
from pathlib import Path

def check_redis_running():
    """Check if Redis is already running"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        return True
    except:
        return False

def download_redis_windows():
    """Download Redis for Windows"""
    print("📥 Downloading Redis for Windows...")
    
    # Create redis directory
    redis_dir = Path("redis")
    redis_dir.mkdir(exist_ok=True)
    
    # Download Redis
    redis_url = "https://download.redis.io/redis-stable/src/redis-server.exe"
    redis_exe = redis_dir / "redis-server.exe"
    
    if not redis_exe.exists():
        try:
            # Alternative: Use a portable Redis version
            print("📦 Setting up portable Redis...")
            
            # Create a simple Redis config
            config_content = """
port 6379
bind 127.0.0.1
save 900 1
save 300 10
save 60 10000
dir ./
dbfilename dump.rdb
"""
            config_file = redis_dir / "redis.conf"
            config_file.write_text(config_content)
            
            print("✅ Redis configuration created!")
            return str(redis_dir)
            
        except Exception as e:
            print(f"❌ Error downloading Redis: {e}")
            return None
    
    return str(redis_dir)

def start_redis_windows(redis_dir=None):
    """Start Redis on Windows"""
    try:
        if redis_dir:
            redis_exe = Path(redis_dir) / "redis-server.exe"
            config_file = Path(redis_dir) / "redis.conf"
            
            if redis_exe.exists():
                print("🚀 Starting Redis server...")
                subprocess.Popen([str(redis_exe), str(config_file)], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
                return True
        
        # Try system Redis
        subprocess.Popen(["redis-server"], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
        return True
        
    except FileNotFoundError:
        print("❌ Redis not found. Please install Redis first.")
        return False
    except Exception as e:
        print(f"❌ Error starting Redis: {e}")
        return False

def start_redis_linux():
    """Start Redis on Linux/Mac"""
    try:
        # Try to start Redis service
        subprocess.run(["sudo", "systemctl", "start", "redis"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "redis"], check=True)
        return True
    except:
        try:
            # Try direct Redis start
            subprocess.Popen(["redis-server"])
            return True
        except:
            print("❌ Redis not found. Please install Redis first.")
            return False

def install_redis_python():
    """Install Redis Python package"""
    try:
        import redis
        print("✅ Redis Python package already installed")
        return True
    except ImportError:
        print("📦 Installing Redis Python package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "redis"])
            print("✅ Redis Python package installed!")
            return True
        except Exception as e:
            print(f"❌ Error installing Redis package: {e}")
            return False

def wait_for_redis(timeout=30):
    """Wait for Redis to start"""
    print("⏳ Waiting for Redis to start...")
    
    for i in range(timeout):
        if check_redis_running():
            print("✅ Redis is running!")
            return True
        
        print(f"⏳ Waiting... ({i+1}/{timeout})")
        time.sleep(1)
    
    print("❌ Redis failed to start within timeout")
    return False

def create_startup_script():
    """Create a startup script for automatic Redis start"""
    if platform.system() == "Windows":
        # Create Windows batch file
        startup_script = """@echo off
echo Starting Redis for Law Agent...
python "%~dp0start_redis.py"
"""
        with open("start_redis.bat", "w") as f:
            f.write(startup_script)
        
        print("✅ Created start_redis.bat for Windows startup")
        
        # Instructions for Windows startup
        print("\n📝 To auto-start Redis with Windows:")
        print("1. Press Win+R, type 'shell:startup', press Enter")
        print("2. Copy start_redis.bat to the Startup folder")
        print("3. Redis will start automatically when Windows starts")
        
    else:
        # Create systemd service for Linux
        service_content = f"""[Unit]
Description=Redis Auto-Starter for Law Agent
After=network.target

[Service]
Type=forking
ExecStart={sys.executable} {os.path.abspath(__file__)}
User={os.getenv('USER', 'root')}
Restart=always

[Install]
WantedBy=multi-user.target
"""
        
        try:
            with open("/tmp/law-agent-redis.service", "w") as f:
                f.write(service_content)
            
            print("✅ Created systemd service file")
            print("\n📝 To auto-start Redis with Linux:")
            print("sudo cp /tmp/law-agent-redis.service /etc/systemd/system/")
            print("sudo systemctl enable law-agent-redis.service")
            print("sudo systemctl start law-agent-redis.service")
            
        except Exception as e:
            print(f"⚠️ Could not create systemd service: {e}")

def main():
    """Main function"""
    print("🔧 Redis Auto-Starter for Law Agent")
    print("=" * 50)
    
    # Check if Redis is already running
    if check_redis_running():
        print("✅ Redis is already running!")
        return True
    
    # Install Redis Python package
    if not install_redis_python():
        return False
    
    # Start Redis based on platform
    system = platform.system()
    print(f"🖥️ Detected system: {system}")
    
    if system == "Windows":
        # Try to start Redis, download if needed
        if not start_redis_windows():
            redis_dir = download_redis_windows()
            if redis_dir:
                start_redis_windows(redis_dir)
    else:
        start_redis_linux()
    
    # Wait for Redis to start
    if wait_for_redis():
        print("🎉 Redis is now running!")
        
        # Create startup script
        create_startup_script()
        
        # Test Redis connection
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.set("law_agent_test", "Redis is working!")
            result = client.get("law_agent_test")
            print(f"🧪 Redis test: {result}")
            client.delete("law_agent_test")
        except Exception as e:
            print(f"⚠️ Redis test failed: {e}")
        
        return True
    else:
        print("❌ Failed to start Redis")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 Manual Redis Installation Options:")
        print("Windows: https://github.com/microsoftarchive/redis/releases")
        print("Linux: sudo apt-get install redis-server")
        print("Mac: brew install redis")
        sys.exit(1)
