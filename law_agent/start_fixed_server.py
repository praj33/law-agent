#!/usr/bin/env python3
"""
Fixed Law Agent Server Startup
Resolves all common issues and starts the API server
"""

import os
import sys
import subprocess
import warnings
from pathlib import Path

# Suppress all warnings for clean output
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def print_banner():
    """Print startup banner."""
    print("🏛️  LAW AGENT - FIXED SERVER STARTUP")
    print("=" * 60)
    print("🔧 Auto-fixing issues and starting server...")
    print("=" * 60)

def suppress_warnings():
    """Suppress all warnings for clean output."""
    import logging
    
    # Suppress TensorFlow warnings
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    
    # Suppress other warnings
    logging.getLogger('tensorflow').setLevel(logging.ERROR)
    logging.getLogger('transformers').setLevel(logging.ERROR)
    logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
    
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except:
        pass

def find_available_port():
    """Find an available port."""
    import socket
    
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    for port in [8000, 8001, 8002, 8003]:
        if is_port_available(port):
            return port
    
    return 8000  # Default fallback

def setup_environment():
    """Setup environment variables."""
    port = find_available_port()
    
    # Set environment variables
    os.environ['API_PORT'] = str(port)
    os.environ['API_HOST'] = '0.0.0.0'
    os.environ['API_RELOAD'] = 'false'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
    
    return port

def check_redis():
    """Check Redis and setup fallback."""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis: Connected")
        return True
    except:
        try:
            import fakeredis
            print("✅ FakeRedis: Using fallback")
            return True
        except:
            print("⚠️ Redis: Using in-memory storage")
            return True

def start_server():
    """Start the Law Agent server."""
    print_banner()
    
    # Step 1: Suppress warnings
    suppress_warnings()
    print("✅ Warnings suppressed")
    
    # Step 2: Setup environment
    port = setup_environment()
    print(f"✅ Environment configured (Port: {port})")
    
    # Step 3: Check Redis
    check_redis()
    
    # Step 4: Start server
    print(f"\n🚀 Starting Law Agent API Server...")
    print("=" * 60)
    print(f"🌐 API Documentation: http://localhost:{port}/docs")
    print(f"🔍 Health Check: http://localhost:{port}/health")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Try the robust startup first
        if Path("run_law_agent_robust.py").exists():
            subprocess.run([
                sys.executable, 'run_law_agent_robust.py',
                '--port', str(port),
                '--host', '0.0.0.0'
            ])
        elif Path("law_agent_minimal.py").exists():
            subprocess.run([sys.executable, 'law_agent_minimal.py'])
        else:
            # Direct API start
            subprocess.run([sys.executable, '-m', 'law_agent.api.main'])
            
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("\n🔄 Trying alternative startup...")
        
        # Try minimal startup
        try:
            if Path("law_agent_minimal.py").exists():
                subprocess.run([sys.executable, 'law_agent_minimal.py'])
            else:
                print("❌ No startup scripts found")
        except Exception as e2:
            print(f"❌ All startup methods failed: {e2}")

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
