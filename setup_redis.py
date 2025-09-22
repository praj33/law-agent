#!/usr/bin/env python3
"""
Setup Redis for Law Agent on Windows.
This script will try multiple methods to get Redis running.
"""

import subprocess
import sys
import os
import requests
import zipfile
import shutil
from pathlib import Path

def check_redis_running():
    """Check if Redis is already running."""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis is already running!")
        return True
    except:
        return False

def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker found: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("❌ Docker not found")
    return False

def start_redis_docker():
    """Start Redis using Docker."""
    try:
        print("🐳 Starting Redis with Docker...")
        
        # Stop any existing Redis container
        subprocess.run(['docker', 'stop', 'law-agent-redis'], capture_output=True)
        subprocess.run(['docker', 'rm', 'law-agent-redis'], capture_output=True)
        
        # Start new Redis container
        cmd = [
            'docker', 'run', '-d',
            '--name', 'law-agent-redis',
            '-p', '6379:6379',
            'redis:alpine',
            'redis-server', '--appendonly', 'yes'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Redis Docker container started successfully!")
            print("🔗 Redis is now available at localhost:6379")
            return True
        else:
            print(f"❌ Failed to start Redis Docker: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Docker Redis setup failed: {e}")
        return False

def download_redis_windows():
    """Download and setup Redis for Windows."""
    try:
        print("📥 Downloading Redis for Windows...")
        
        # Create redis directory
        redis_dir = Path("redis")
        redis_dir.mkdir(exist_ok=True)
        
        # Download Redis for Windows (Memurai - Redis compatible)
        url = "https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
        zip_path = redis_dir / "redis.zip"
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("📦 Extracting Redis...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(redis_dir)
        
        # Remove zip file
        zip_path.unlink()
        
        print("✅ Redis for Windows downloaded and extracted!")
        return redis_dir
        
    except Exception as e:
        print(f"❌ Failed to download Redis: {e}")
        return None

def start_redis_windows(redis_dir):
    """Start Redis on Windows."""
    try:
        redis_exe = redis_dir / "redis-server.exe"
        if not redis_exe.exists():
            print(f"❌ Redis executable not found at {redis_exe}")
            return False
        
        print("🚀 Starting Redis server...")
        
        # Start Redis in background
        subprocess.Popen([str(redis_exe)], cwd=str(redis_dir))
        
        # Wait a moment for Redis to start
        import time
        time.sleep(3)
        
        # Test connection
        if check_redis_running():
            print("✅ Redis started successfully!")
            return True
        else:
            print("❌ Redis failed to start properly")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start Redis: {e}")
        return False

def setup_fakeredis():
    """Setup FakeRedis as fallback."""
    try:
        print("🔄 Setting up FakeRedis as fallback...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'fakeredis'], check=True)
        print("✅ FakeRedis installed successfully!")
        print("💡 Law Agent will use FakeRedis when Redis is not available")
        return True
    except Exception as e:
        print(f"❌ Failed to install FakeRedis: {e}")
        return False

def main():
    """Main setup function."""
    print("🏛️  LAW AGENT REDIS SETUP")
    print("=" * 50)
    
    # Check if Redis is already running
    if check_redis_running():
        return True
    
    print("🔍 Redis not running, setting up...")
    
    # Try Docker first
    if check_docker():
        if start_redis_docker():
            return True
    
    # Try downloading Redis for Windows
    print("\n📥 Trying to download Redis for Windows...")
    redis_dir = download_redis_windows()
    if redis_dir and start_redis_windows(redis_dir):
        return True
    
    # Fallback to FakeRedis
    print("\n🔄 Setting up FakeRedis fallback...")
    if setup_fakeredis():
        print("\n✅ Setup complete! Law Agent will use FakeRedis.")
        print("💡 For better performance, consider installing Docker and running:")
        print("   docker run -d --name law-agent-redis -p 6379:6379 redis:alpine")
        return True
    
    print("\n❌ All Redis setup methods failed!")
    print("💡 Law Agent will use in-memory storage (data will not persist)")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
