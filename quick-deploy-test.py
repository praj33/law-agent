#!/usr/bin/env python3
"""
Quick Deployment Test Script for Law Agent
Tests all components before full deployment
"""

import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_service(url, name, timeout=30):
    """Check if a service is responding"""
    print(f"🔍 Checking {name} at {url}...")
    
    for i in range(timeout):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is healthy!")
                return True
        except:
            pass
        
        if i < timeout - 1:
            print(f"⏳ Waiting for {name}... ({i+1}/{timeout})")
            time.sleep(1)
    
    print(f"❌ {name} failed to respond")
    return False

def main():
    print("🏛️ Law Agent - Quick Deployment Test")
    print("=" * 50)
    
    # Check if Docker is running
    print("🐳 Checking Docker...")
    success, _, _ = run_command("docker --version")
    if not success:
        print("❌ Docker not found. Please install Docker first.")
        return False
    print("✅ Docker is available")
    
    # Check if docker-compose is available
    print("🔧 Checking Docker Compose...")
    success, _, _ = run_command("docker-compose --version")
    if not success:
        print("❌ Docker Compose not found. Please install Docker Compose.")
        return False
    print("✅ Docker Compose is available")
    
    # Start services
    print("\n🚀 Starting Law Agent services...")
    success, stdout, stderr = run_command("docker-compose up -d")
    if not success:
        print(f"❌ Failed to start services: {stderr}")
        return False
    print("✅ Services started successfully")
    
    # Wait for services to initialize
    print("\n⏳ Waiting for services to initialize...")
    time.sleep(10)
    
    # Test services
    services = [
        ("http://localhost:8000/health", "Main API"),
        ("http://localhost:8001/health", "Document API"),
        ("http://localhost:8002/health", "Analytics API"),
        ("http://localhost:6379", "Redis", False),  # Redis doesn't have HTTP endpoint
    ]
    
    all_healthy = True
    for service in services:
        if len(service) == 2 or service[2] != False:
            if not check_service(service[0], service[1]):
                all_healthy = False
    
    # Test Redis separately
    print("🔍 Checking Redis...")
    success, _, _ = run_command("docker exec law-agent-redis redis-cli ping")
    if success:
        print("✅ Redis is healthy!")
    else:
        print("❌ Redis is not responding")
        all_healthy = False
    
    # Test frontend build
    print("\n🎨 Testing frontend build...")
    frontend_path = Path("law-agent-frontend")
    if frontend_path.exists():
        print("📦 Installing frontend dependencies...")
        success, _, stderr = run_command("npm ci", cwd=frontend_path)
        if not success:
            print(f"❌ Frontend dependency installation failed: {stderr}")
            all_healthy = False
        else:
            print("✅ Frontend dependencies installed")
            
            print("🏗️ Building frontend...")
            success, _, stderr = run_command("npm run build", cwd=frontend_path)
            if not success:
                print(f"❌ Frontend build failed: {stderr}")
                all_healthy = False
            else:
                print("✅ Frontend build successful")
    
    # Summary
    print("\n" + "=" * 50)
    if all_healthy:
        print("🎉 ALL TESTS PASSED!")
        print("\n🌐 Your Law Agent is ready!")
        print("📍 Access points:")
        print("   • Main API: http://localhost:8000")
        print("   • Document API: http://localhost:8001") 
        print("   • Analytics API: http://localhost:8002")
        print("   • Frontend: http://localhost:3000 (after npm start)")
        print("\n🚀 Next steps:")
        print("   1. Set up Supabase project")
        print("   2. Configure GitHub secrets")
        print("   3. Deploy to Vercel")
        print("   4. Test production deployment")
    else:
        print("❌ SOME TESTS FAILED")
        print("\n🔧 Troubleshooting:")
        print("   • Check Docker logs: docker-compose logs")
        print("   • Restart services: docker-compose restart")
        print("   • Check ports: netstat -tulpn | grep :8000")
    
    return all_healthy

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
