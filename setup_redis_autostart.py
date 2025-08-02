#!/usr/bin/env python3
"""
Setup Redis Auto-Start for Windows
Creates Windows service and startup scripts for Redis
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def create_windows_service():
    """Create Windows service for Redis auto-start"""
    print("🔧 Setting up Redis Windows Service...")
    
    redis_exe = None
    config_file = None
    
    # Find Redis executable
    local_paths = [
        ("redis/redis-server.exe", "redis/redis.windows.conf"),
        ("redis_server/redis-server.exe", "redis_server/redis.windows.conf"),
        ("redis/redis-server.exe", "redis/redis.windows-service.conf"),
        ("redis_server/redis-server.exe", "redis_server/redis.windows-service.conf")
    ]
    
    for exe_path, conf_path in local_paths:
        if Path(exe_path).exists():
            redis_exe = str(Path(exe_path).absolute())
            if Path(conf_path).exists():
                config_file = str(Path(conf_path).absolute())
            break
    
    if not redis_exe:
        print("❌ Redis executable not found!")
        return False
    
    print(f"✅ Found Redis: {redis_exe}")
    if config_file:
        print(f"✅ Found config: {config_file}")
    
    try:
        # Install Redis as Windows service
        cmd = [redis_exe, "--service-install"]
        if config_file:
            cmd.extend(["--service-name", "Redis-LawAgent", "--port", "6379"])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Redis service installed successfully!")
            
            # Start the service
            try:
                subprocess.run(["net", "start", "Redis-LawAgent"], check=True, capture_output=True)
                print("✅ Redis service started!")
                return True
            except:
                try:
                    subprocess.run(["sc", "start", "Redis"], check=True, capture_output=True)
                    print("✅ Redis service started!")
                    return True
                except:
                    print("⚠️ Service installed but failed to start automatically")
                    return True
        else:
            print(f"❌ Service installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up service: {e}")
        return False

def create_startup_scripts():
    """Create startup scripts for Redis"""
    print("\n🔧 Creating startup scripts...")
    
    # Find Redis executable
    redis_exe = None
    for path in ["redis/redis-server.exe", "redis_server/redis-server.exe"]:
        if Path(path).exists():
            redis_exe = str(Path(path).absolute())
            break
    
    if not redis_exe:
        print("❌ Redis executable not found!")
        return False
    
    # Create batch file
    batch_content = f"""@echo off
title Redis Server for Law Agent
echo 🚀 Starting Redis Server for Law Agent...
echo ===============================================
echo Redis Path: {redis_exe}
echo Port: 6379
echo ===============================================
echo.
echo Redis is starting... (This window will stay open)
echo To stop Redis, close this window or press Ctrl+C
echo.
"{redis_exe}"
pause
"""
    
    with open("start_redis_server.bat", "w") as f:
        f.write(batch_content)
    
    print("✅ Created start_redis_server.bat")
    
    # Create PowerShell script
    ps_content = f"""# Redis Auto-Starter for Law Agent
Write-Host "🚀 Redis Auto-Starter for Law Agent" -ForegroundColor Cyan
Write-Host "=" * 50

$redisPath = "{redis_exe}"
$processName = "redis-server"

# Check if Redis is already running
$redisProcess = Get-Process -Name $processName -ErrorAction SilentlyContinue

if ($redisProcess) {{
    Write-Host "✅ Redis is already running (PID: $($redisProcess.Id))" -ForegroundColor Green
    exit 0
}}

Write-Host "🚀 Starting Redis server..." -ForegroundColor Yellow
Write-Host "Path: $redisPath" -ForegroundColor Gray

try {{
    Start-Process -FilePath $redisPath -WindowStyle Normal
    Start-Sleep -Seconds 2
    
    $newProcess = Get-Process -Name $processName -ErrorAction SilentlyContinue
    if ($newProcess) {{
        Write-Host "✅ Redis started successfully (PID: $($newProcess.Id))" -ForegroundColor Green
        Write-Host "🌐 Redis is running on localhost:6379" -ForegroundColor Cyan
    }} else {{
        Write-Host "❌ Redis failed to start" -ForegroundColor Red
        exit 1
    }}
}} catch {{
    Write-Host "❌ Error starting Redis: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}}
"""
    
    with open("start_redis.ps1", "w") as f:
        f.write(ps_content)
    
    print("✅ Created start_redis.ps1")
    
    # Create Python auto-starter
    py_content = f'''#!/usr/bin/env python3
"""Auto-start Redis for Law Agent"""
import subprocess
import sys
import time
from pathlib import Path

def check_redis_running():
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=3)
        client.ping()
        return True
    except:
        return False

def start_redis():
    if check_redis_running():
        print("✅ Redis is already running!")
        return True
    
    print("🚀 Starting Redis...")
    try:
        subprocess.Popen([r"{redis_exe}"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Wait for Redis to start
        for i in range(15):
            time.sleep(1)
            if check_redis_running():
                print("✅ Redis started successfully!")
                return True
            print(f"⏳ Waiting... ({{i+1}}/15)")
        
        print("❌ Redis failed to start within timeout")
        return False
        
    except Exception as e:
        print(f"❌ Error starting Redis: {{e}}")
        return False

if __name__ == "__main__":
    start_redis()
'''
    
    with open("auto_redis.py", "w") as f:
        f.write(py_content)
    
    print("✅ Created auto_redis.py")
    
    return True

def setup_windows_startup():
    """Setup Windows startup entry"""
    print("\n🔧 Setting up Windows startup...")
    
    try:
        # Get startup folder
        startup_folder = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        
        if not startup_folder.exists():
            print("❌ Windows startup folder not found")
            return False
        
        # Create startup batch file
        startup_batch = startup_folder / "Redis-LawAgent.bat"
        
        batch_content = f"""@echo off
cd /d "{os.getcwd()}"
python auto_redis.py
"""
        
        startup_batch.write_text(batch_content)
        print(f"✅ Created startup entry: {startup_batch}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Windows startup: {e}")
        return False

def main():
    """Main setup function"""
    print("🔧 REDIS AUTO-START SETUP FOR LAW AGENT")
    print("=" * 60)
    
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        return False
    
    print("🔍 Checking Redis installation...")
    
    # Check if Redis is available
    redis_found = False
    for path in ["redis/redis-server.exe", "redis_server/redis-server.exe"]:
        if Path(path).exists():
            print(f"✅ Found Redis: {path}")
            redis_found = True
            break
    
    if not redis_found:
        print("❌ Redis not found! Please install Redis first.")
        return False
    
    success_count = 0
    
    # Create startup scripts
    if create_startup_scripts():
        success_count += 1
    
    # Setup Windows service (optional)
    print("\n" + "=" * 60)
    print("🔧 WINDOWS SERVICE SETUP (Optional)")
    print("=" * 60)
    
    choice = input("Do you want to install Redis as a Windows service? (y/n): ").lower()
    if choice in ['y', 'yes']:
        if create_windows_service():
            success_count += 1
            print("✅ Redis will now start automatically with Windows!")
        else:
            print("⚠️ Service setup failed, but manual scripts are available")
    
    # Setup Windows startup (alternative)
    if success_count == 1:  # Only if service setup failed or was skipped
        print("\n" + "=" * 60)
        print("🔧 WINDOWS STARTUP SETUP (Alternative)")
        print("=" * 60)
        
        choice = input("Do you want Redis to start with Windows login? (y/n): ").lower()
        if choice in ['y', 'yes']:
            if setup_windows_startup():
                success_count += 1
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📝 Available Redis Control Options:")
    print("1. Manual Start: start_redis_server.bat")
    print("2. PowerShell: .\\start_redis.ps1")
    print("3. Python: python auto_redis.py")
    print("4. Auto-Start: python auto_start_redis.py")
    
    if success_count > 1:
        print("\n✅ Redis will start automatically with your system!")
    else:
        print("\n💡 Use the manual scripts to start Redis when needed")
    
    print("\n🚀 Start Law Agent with: python run_api.py")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)
