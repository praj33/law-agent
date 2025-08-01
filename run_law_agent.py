#!/usr/bin/env python3
"""
Law Agent Startup Script

This script provides multiple ways to run the Law Agent system:
1. API server only
2. Web interface only  
3. Combined API + Web interface
4. Development mode with auto-reload
"""

import argparse
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from law_agent.api.main import app as api_app
from law_agent.ui.web_interface import create_web_app
from law_agent.core.config import settings


def create_combined_app() -> FastAPI:
    """Create combined API + Web interface app."""
    
    # Create main app
    app = FastAPI(
        title="Law Agent - Complete System",
        description="Legal AI Assistant with API and Web Interface",
        version="1.0.0"
    )
    
    # Mount API app at root to preserve its internal routing
    app.mount("/api", api_app)
    
    # Mount Web Interface
    web_app = create_web_app()
    app.mount("/", web_app)
    
    return app


def run_api_only():
    """Run API server only."""
    print("🚀 Starting Law Agent API Server...")
    print(f"📡 API will be available at: http://{settings.api_host}:{settings.api_port}")
    print(f"📚 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "law_agent.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )


def run_web_only():
    """Run web interface only."""
    print("🌐 Starting Law Agent Web Interface...")
    print(f"🖥️  Web Interface: http://{settings.api_host}:{settings.api_port}")
    
    web_app = create_web_app()
    uvicorn.run(
        web_app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )


def run_combined():
    """Run combined API + Web interface."""
    print("🚀 Starting Law Agent Complete System...")
    print(f"🌐 Web Interface: http://{settings.api_host}:{settings.api_port}")
    print(f"📡 API Endpoints: http://{settings.api_host}:{settings.api_port}/api")
    print(f"📚 API Documentation: http://{settings.api_host}:{settings.api_port}/api/docs")
    
    combined_app = create_combined_app()
    uvicorn.run(
        combined_app,
        host=settings.api_host,
        port=settings.api_port,
        reload=False,  # Disable reload for combined app
        log_level=settings.log_level.lower()
    )


def run_development():
    """Run in development mode with enhanced debugging."""
    print("🔧 Starting Law Agent in Development Mode...")
    print("📝 Enhanced logging and auto-reload enabled")
    
    # Override settings for development
    dev_settings = settings.copy()
    dev_settings.api_reload = True
    dev_settings.log_level = "DEBUG"
    
    combined_app = create_combined_app()
    uvicorn.run(
        combined_app,
        host="127.0.0.1",  # Localhost only for development
        port=8000,
        reload=True,
        log_level="debug",
        reload_dirs=["law_agent"],  # Watch for changes
        access_log=True
    )


def setup_environment():
    """Setup environment and check dependencies."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    
    # Check if required directories exist
    required_dirs = ["logs", "models", "data"]
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"📁 Created directory: {dir_name}")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  No .env file found. Using default settings.")
        print("💡 Copy .env.example to .env and customize for production use.")
    
    print("✅ Environment setup complete")


def show_system_info():
    """Show system information and status."""
    print("\n" + "="*60)
    print("🏛️  LAW AGENT - LEGAL AI ASSISTANT")
    print("="*60)
    print(f"Version: 1.0.0")
    print(f"Python: {sys.version}")
    print(f"Host: {settings.api_host}")
    print(f"Port: {settings.api_port}")
    print(f"Log Level: {settings.log_level}")
    print(f"Database: {settings.database_url}")
    print(f"Redis: {settings.redis_url}")
    print("="*60)
    
    print("\n🎯 FEATURES:")
    print("• Reinforcement Learning with user feedback")
    print("• Legal domain classification (14+ domains)")
    print("• Dynamic route mapping for legal procedures")
    print("• Comprehensive legal glossary")
    print("• Adaptive UI for different user types")
    print("• Persistent memory and learning")
    print("• RESTful API with OpenAPI documentation")
    print("• Web-based chat interface")
    
    print("\n📋 SUPPORTED LEGAL DOMAINS:")
    domains = [
        "Family Law", "Criminal Law", "Corporate Law", "Property Law",
        "Employment Law", "Immigration Law", "Intellectual Property",
        "Tax Law", "Constitutional Law", "Contract Law", "Tort Law",
        "Bankruptcy Law", "Environmental Law", "Healthcare Law"
    ]
    for i, domain in enumerate(domains, 1):
        print(f"{i:2d}. {domain}")
    
    print("\n" + "="*60)


async def run_tests():
    """Run the test suite."""
    print("🧪 Running Law Agent Test Suite...")
    
    try:
        import pytest
        exit_code = pytest.main([
            "law_agent/tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ])
        
        if exit_code == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed")
            
        return exit_code
        
    except ImportError:
        print("❌ pytest not installed. Install with: pip install pytest")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Law Agent - Robust Legal AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_law_agent.py                    # Run complete system (API + Web)
  python run_law_agent.py --api-only         # Run API server only
  python run_law_agent.py --web-only         # Run web interface only
  python run_law_agent.py --dev              # Run in development mode
  python run_law_agent.py --test             # Run test suite
  python run_law_agent.py --info             # Show system information
        """
    )
    
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Run API server only"
    )
    
    parser.add_argument(
        "--web-only", 
        action="store_true",
        help="Run web interface only"
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode with debugging"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test suite"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show system information"
    )
    
    parser.add_argument(
        "--host",
        default=settings.api_host,
        help="Host to bind to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=settings.api_port,
        help="Port to bind to"
    )
    
    args = parser.parse_args()
    
    # Update settings if provided
    if args.host != settings.api_host:
        settings.api_host = args.host
    if args.port != settings.api_port:
        settings.api_port = args.port
    
    # Show info and exit
    if args.info:
        show_system_info()
        return
    
    # Run tests and exit
    if args.test:
        exit_code = asyncio.run(run_tests())
        sys.exit(exit_code)
    
    # Setup environment
    setup_environment()
    show_system_info()
    
    try:
        # Determine run mode
        if args.api_only:
            run_api_only()
        elif args.web_only:
            run_web_only()
        elif args.dev:
            run_development()
        else:
            run_combined()
            
    except KeyboardInterrupt:
        print("\n👋 Law Agent shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error starting Law Agent: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
