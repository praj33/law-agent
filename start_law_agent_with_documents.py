#!/usr/bin/env python3
"""
Law Agent Startup Script with Document Processing
Starts both the main Law Agent API and Document Processing API
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path

def start_document_api():
    """Start the document processing API"""
    print("🔧 Starting Document Processing API on port 8001...")
    try:
        subprocess.run([
            sys.executable, "document_api.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Document API failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Document API stopped by user")

def start_main_law_agent():
    """Start the main Law Agent API"""
    print("⚖️ Starting Main Law Agent API on port 8000...")
    time.sleep(2)  # Give document API time to start
    try:
        subprocess.run([
            sys.executable, "law_agent_minimal.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Main Law Agent failed to start: {e}")
    except KeyboardInterrupt:
        print("🛑 Main Law Agent stopped by user")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'fitz', 'docx', 'pytesseract', 'PIL', 'textstat'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'fitz':
                import fitz
            elif package == 'docx':
                import docx
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements_document_processing.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'processed', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def main():
    """Main startup function"""
    print("🚀 Law Agent with Document Processing - Startup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    print("\n🎯 Starting services...")
    
    try:
        # Start document API in a separate thread
        doc_api_thread = threading.Thread(target=start_document_api, daemon=True)
        doc_api_thread.start()
        
        # Start main Law Agent API
        start_main_law_agent()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Law Agent services...")
        print("✅ All services stopped successfully")

if __name__ == "__main__":
    main()
