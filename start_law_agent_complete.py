#!/usr/bin/env python3
"""
Complete Law Agent Startup Script
Starts all services: Main API, Document Processing, Analytics, and Dashboard
"""

import os
import sys
import time
import subprocess
import threading
import signal
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LawAgentOrchestrator:
    """Orchestrates all Law Agent services"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
        
        # Service configurations
        self.services = {
            'analytics_api': {
                'script': 'analytics_api.py',
                'port': 8002,
                'name': 'Analytics API',
                'description': 'Real-time analytics collection and reporting'
            },
            'document_api': {
                'script': 'document_api.py',
                'port': 8001,
                'name': 'Document Processing API',
                'description': 'Document upload, parsing, and analysis'
            },
            'main_api': {
                'script': 'law_agent_minimal.py',
                'port': 8000,
                'name': 'Main Law Agent API',
                'description': 'Core legal AI assistant functionality'
            }
        }

    def check_dependencies(self):
        """Check if all required dependencies are available"""
        logger.info("🔍 Checking dependencies...")
        
        required_packages = [
            'fastapi', 'uvicorn', 'sqlite3', 'pandas', 'numpy'
        ]
        
        optional_packages = [
            ('fitz', 'PyMuPDF - for PDF processing'),
            ('docx', 'python-docx - for Word document processing'),
            ('sklearn', 'scikit-learn - for ML analytics'),
            ('matplotlib', 'matplotlib - for analytics visualization')
        ]
        
        missing_required = []
        missing_optional = []
        
        # Check required packages
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_required.append(package)
        
        # Check optional packages
        for package, description in optional_packages:
            try:
                __import__(package)
            except ImportError:
                missing_optional.append((package, description))
        
        if missing_required:
            logger.error("❌ Missing required packages:")
            for package in missing_required:
                logger.error(f"   - {package}")
            logger.error("\n📦 Install with: pip install fastapi uvicorn pandas numpy")
            return False
        
        if missing_optional:
            logger.warning("⚠️ Missing optional packages (some features may be limited):")
            for package, description in missing_optional:
                logger.warning(f"   - {package}: {description}")
            logger.warning("\n📦 Install with: pip install -r requirements_document_processing.txt")
        
        logger.info("✅ All required dependencies available")
        return True

    def create_directories(self):
        """Create necessary directories"""
        directories = [
            'analytics_data',
            'analytics_data/events',
            'analytics_data/sessions',
            'analytics_data/legal_routes',
            'analytics_data/glossary',
            'analytics_data/timelines',
            'analytics_data/performance',
            'uploads',
            'processed',
            'logs'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
        
        logger.info("📁 Created necessary directories")

    def start_service(self, service_name, service_config):
        """Start a single service"""
        script_path = service_config['script']
        
        if not Path(script_path).exists():
            logger.error(f"❌ Script not found: {script_path}")
            return False
        
        try:
            logger.info(f"🚀 Starting {service_config['name']} on port {service_config['port']}...")
            
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.processes[service_name] = {
                'process': process,
                'config': service_config
            }
            
            # Give the service time to start
            time.sleep(2)
            
            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ {service_config['name']} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {service_config['name']} failed to start")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error starting {service_config['name']}: {e}")
            return False

    def check_service_health(self, service_name, service_config):
        """Check if a service is healthy"""
        try:
            import requests
            response = requests.get(f"http://localhost:{service_config['port']}/", timeout=5)
            return response.status_code == 200
        except:
            return False

    def start_all_services(self):
        """Start all Law Agent services"""
        logger.info("🎯 Starting Law Agent Complete System")
        logger.info("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Create directories
        self.create_directories()
        
        # Start services in order
        success_count = 0
        
        for service_name, service_config in self.services.items():
            if self.start_service(service_name, service_config):
                success_count += 1
            else:
                logger.error(f"Failed to start {service_config['name']}")
        
        if success_count == len(self.services):
            logger.info("\n🎉 All services started successfully!")
            self.print_service_status()
            return True
        else:
            logger.error(f"\n❌ Only {success_count}/{len(self.services)} services started successfully")
            return False

    def print_service_status(self):
        """Print status of all services"""
        logger.info("\n📊 Service Status:")
        logger.info("-" * 60)
        
        for service_name, service_info in self.processes.items():
            config = service_info['config']
            process = service_info['process']
            
            if process.poll() is None:
                status = "🟢 RUNNING"
                health = "🔍 Checking..." if self.check_service_health(service_name, config) else "⚠️ Unhealthy"
            else:
                status = "🔴 STOPPED"
                health = "❌ Not responding"
            
            logger.info(f"{config['name']:<25} | Port {config['port']} | {status} | {health}")
            logger.info(f"  └─ {config['description']}")
        
        logger.info("\n🌐 Access URLs:")
        logger.info(f"  • Main Law Agent API:     http://localhost:8000")
        logger.info(f"  • Document Processing:    http://localhost:8001")
        logger.info(f"  • Analytics API:          http://localhost:8002")
        logger.info(f"  • Frontend (if running):  http://localhost:3001")
        
        logger.info("\n📈 Analytics Dashboard:")
        logger.info(f"  • Real-time Analytics:    http://localhost:8002/analytics/summary")
        logger.info(f"  • Legal Routes:           http://localhost:8002/analytics/legal-routes")
        logger.info(f"  • Glossary Analytics:     http://localhost:8002/analytics/glossary")
        logger.info(f"  • Timeline Analytics:     http://localhost:8002/analytics/timeline")

    def monitor_services(self):
        """Monitor running services"""
        logger.info("\n👁️ Monitoring services... (Press Ctrl+C to stop)")
        
        try:
            while self.running:
                time.sleep(30)  # Check every 30 seconds
                
                for service_name, service_info in self.processes.items():
                    process = service_info['process']
                    config = service_info['config']
                    
                    if process.poll() is not None:
                        logger.warning(f"⚠️ {config['name']} has stopped unexpectedly")
                        # Attempt to restart
                        logger.info(f"🔄 Attempting to restart {config['name']}...")
                        if self.start_service(service_name, config):
                            logger.info(f"✅ {config['name']} restarted successfully")
                        else:
                            logger.error(f"❌ Failed to restart {config['name']}")
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutdown signal received")
            self.shutdown_all_services()

    def shutdown_all_services(self):
        """Shutdown all services gracefully"""
        logger.info("🛑 Shutting down all services...")
        
        self.running = False
        
        for service_name, service_info in self.processes.items():
            process = service_info['process']
            config = service_info['config']
            
            if process.poll() is None:
                logger.info(f"🛑 Stopping {config['name']}...")
                try:
                    process.terminate()
                    process.wait(timeout=10)
                    logger.info(f"✅ {config['name']} stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Force killing {config['name']}...")
                    process.kill()
                    process.wait()
                except Exception as e:
                    logger.error(f"❌ Error stopping {config['name']}: {e}")
        
        logger.info("✅ All services stopped")

    def run(self):
        """Main run method"""
        try:
            if self.start_all_services():
                self.monitor_services()
            else:
                logger.error("❌ Failed to start all services")
                sys.exit(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Interrupted by user")
            self.shutdown_all_services()
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            self.shutdown_all_services()
            sys.exit(1)

def main():
    """Main function"""
    print("🏛️ Law Agent Complete System Orchestrator")
    print("=" * 50)
    print("🎯 Starting comprehensive legal AI system with:")
    print("   • Core Legal AI Assistant")
    print("   • Document Processing & Analysis")
    print("   • Real-time Analytics & Monitoring")
    print("   • Professional Dashboard")
    print("=" * 50)
    
    orchestrator = LawAgentOrchestrator()
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"\n🛑 Received signal {signum}")
        orchestrator.shutdown_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the orchestrator
    orchestrator.run()

if __name__ == "__main__":
    main()
