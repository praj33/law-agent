#!/usr/bin/env python3
"""
Integrated Law Agent Startup Script
===================================

This script starts the ultimate integrated law agent system with:
- Advanced RL learning
- Enhanced ML domain classification (TF-IDF + Naive Bayes)
- Constitutional backing with Indian Constitutional articles
- Real-time feedback learning
- Enhanced web interface

Author: Integrated Law Agent Team
Version: 6.0.0 - Integrated System
Date: 2025-08-04
"""

import subprocess
import sys
import time
import requests
import webbrowser
from pathlib import Path


def print_banner():
    """Print startup banner"""
    print("🚀" + "="*70 + "🚀")
    print("🎯 INTEGRATED LAW AGENT - ULTIMATE AI LEGAL ASSISTANT 🎯")
    print("="*74)
    print("✨ Features:")
    print("   🤖 Advanced RL Learning System")
    print("   🧠 Enhanced ML Domain Classification (TF-IDF + Naive Bayes)")
    print("   🏛️ Constitutional Backing (Indian Constitution)")
    print("   📈 Real-time Feedback Learning")
    print("   🌐 Enhanced Web Interface")
    print("   🔄 Continuous Model Improvement")
    print("="*74)


def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'redis', 'loguru', 'pandas', 
        'numpy', 'scikit-learn', 'sentence-transformers'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    print("✅ All dependencies satisfied")
    return True


def check_redis():
    """Check if Redis is running"""
    print("🔍 Checking Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis not available: {e}")
        print("💡 Starting Redis automatically...")
        
        # Try to start Redis
        try:
            if sys.platform == "win32":
                # Windows
                redis_paths = [
                    "redis/redis-server.exe",
                    "redis_server/redis-server.exe",
                    "C:/Program Files/Redis/redis-server.exe"
                ]
                
                for redis_path in redis_paths:
                    if Path(redis_path).exists():
                        subprocess.Popen([redis_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
                        time.sleep(3)
                        
                        # Test connection again
                        try:
                            r.ping()
                            print("✅ Redis started successfully")
                            return True
                        except:
                            continue
            else:
                # Linux/Mac
                subprocess.Popen(['redis-server'])
                time.sleep(3)
                
                try:
                    r.ping()
                    print("✅ Redis started successfully")
                    return True
                except:
                    pass
        
        except Exception as start_error:
            print(f"❌ Failed to start Redis: {start_error}")
        
        print("⚠️ Redis not available - some features may be limited")
        return False


def start_api_server():
    """Start the integrated API server"""
    print("🚀 Starting Integrated Law Agent API server...")
    
    try:
        # Start the API server
        process = subprocess.Popen([
            sys.executable, '-m', 'law_agent.api.main'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for API server to initialize...")
        
        for i in range(30):  # Wait up to 30 seconds
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                if response.status_code == 200:
                    print("✅ API server is running")
                    return process
            except:
                pass
            
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
        
        print("❌ API server failed to start within 30 seconds")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None


def start_demo_server():
    """Start the demo web server"""
    print("🌐 Starting Enhanced Web Demo server...")
    
    try:
        # Start the demo server
        process = subprocess.Popen([
            sys.executable, 'serve_demo.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(2)
        
        try:
            response = requests.get('http://localhost:3000/rl_demo.html', timeout=5)
            if response.status_code == 200:
                print("✅ Demo server is running")
                return process
        except:
            pass
        
        print("⚠️ Demo server may not be fully ready")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start demo server: {e}")
        return None


def test_integration():
    """Test the integrated system"""
    print("🧪 Testing integrated system...")
    
    try:
        # Test enhanced features
        response = requests.get('http://localhost:8000/api/v1/system/enhanced-features', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print("📊 Integration Status:")
            print(f"   🤖 ML Classification: {'✅ Active' if data.get('enhanced_classification') else '❌ Inactive'}")
            print(f"   🏛️ Constitutional Support: {'✅ Active' if data.get('constitutional_support') else '❌ Inactive'}")
            
            if data.get('model_stats'):
                stats = data['model_stats']
                print(f"   📈 Training Examples: {stats.get('training_examples', 'N/A')}")
                print(f"   🎯 Model Type: {stats.get('model_type', 'Basic')}")
            
            if data.get('constitutional_stats'):
                const_stats = data['constitutional_stats']
                print(f"   📜 Constitutional Articles: {const_stats.get('total_articles', 'N/A')}")
            
            return True
        else:
            print(f"❌ Integration test failed: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False


def open_web_interface():
    """Open the web interface in browser"""
    print("🌐 Opening Enhanced Web Interface...")
    
    try:
        webbrowser.open('http://localhost:3000/rl_demo.html')
        print("✅ Web interface opened in browser")
        return True
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print("🔗 Please open: http://localhost:3000/rl_demo.html")
        return False


def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return False
    
    # Check Redis
    redis_available = check_redis()
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        return False
    
    # Start demo server
    demo_process = start_demo_server()
    
    # Test integration
    if not test_integration():
        print("⚠️ Integration test failed - some features may not work")
    
    # Open web interface
    open_web_interface()
    
    # Success message
    print("\n🎉 INTEGRATED LAW AGENT SYSTEM IS READY!")
    print("="*50)
    print("🌐 Web Interface: http://localhost:3000/rl_demo.html")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    print("🧪 Enhanced Features: http://localhost:8000/api/v1/system/enhanced-features")
    print("="*50)
    print("\n✨ FEATURES AVAILABLE:")
    print("   🤖 Ask legal questions with ML-enhanced classification")
    print("   🏛️ Get constitutional backing for legal advice")
    print("   📈 Watch AI learn from your feedback in real-time")
    print("   🎯 See confidence scores improve over time")
    print("   🔄 Experience continuous model improvement")
    print("\n💡 TIP: Try asking questions like:")
    print("   • 'I want to file for divorce'")
    print("   • 'My employer fired me unfairly'")
    print("   • 'Landlord won't return my deposit'")
    print("   • 'I was arrested without warrant'")
    print("\n⚠️ Press Ctrl+C to stop all servers")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        if api_process:
            api_process.terminate()
            print("✅ API server stopped")
        
        if demo_process:
            demo_process.terminate()
            print("✅ Demo server stopped")
        
        print("👋 Integrated Law Agent system stopped")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
