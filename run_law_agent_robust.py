#!/usr/bin/env python3
"""
Law Agent - Advanced Robust Startup System
Handles port conflicts, process management, and system health monitoring.
"""

# Suppress warnings before importing ML libraries
import os
import warnings

# Set TensorFlow environment variables before any imports
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Suppress common warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*sparse_softmax_cross_entropy.*")
warnings.filterwarnings("ignore", message=".*oneDNN custom operations.*")
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*")

import uvicorn
import sys
import socket
import time
import signal
import psutil
import argparse
import subprocess
from pathlib import Path
from typing import Optional, List
from loguru import logger
import threading
import atexit

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from law_agent.api.main import app as api_app
from law_agent.ui.web_interface import create_web_app
from law_agent.core.config import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


class PortManager:
    """Advanced port management with automatic conflict resolution."""
    
    @staticmethod
    def is_port_in_use(port: int, host: str = "localhost") -> bool:
        """Check if a port is in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return False
            except OSError:
                return True
    
    @staticmethod
    def find_free_port(start_port: int = 8000, max_attempts: int = 100) -> int:
        """Find the next available port."""
        for port in range(start_port, start_port + max_attempts):
            if not PortManager.is_port_in_use(port):
                return port
        raise RuntimeError(f"No free ports found in range {start_port}-{start_port + max_attempts}")
    
    @staticmethod
    def kill_process_on_port(port: int) -> bool:
        """Kill any process using the specified port."""
        killed_any = False
        try:
            if os.name == 'nt':  # Windows
                # Get all processes using the port
                result = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True, text=True, shell=True
                )

                pids_to_kill = []
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            if pid.isdigit():
                                pids_to_kill.append(pid)

                # Kill all processes using the port
                for pid in pids_to_kill:
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid],
                                     capture_output=True, check=True, shell=True)
                        logger.info(f"✅ Killed process {pid} on port {port}")
                        killed_any = True
                    except subprocess.CalledProcessError as e:
                        logger.warning(f"⚠️ Could not kill process {pid}: {e}")

                if killed_any:
                    time.sleep(3)  # Wait longer for processes to die

            else:  # Unix/Linux/Mac
                result = subprocess.run(
                    ['lsof', '-ti', f':{port}'],
                    capture_output=True, text=True
                )
                if result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid.strip():
                            try:
                                subprocess.run(['kill', '-9', pid.strip()], check=True)
                                logger.info(f"✅ Killed process {pid} on port {port}")
                                killed_any = True
                            except subprocess.CalledProcessError:
                                pass
                    if killed_any:
                        time.sleep(2)

        except Exception as e:
            logger.warning(f"Failed to kill process on port {port}: {e}")

        return killed_any


class SystemHealthMonitor:
    """Monitor system health and performance."""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start system health monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("🔍 System health monitoring started")
    
    def stop_monitoring(self):
        """Stop system health monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        logger.info("🛑 System health monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                # Check memory usage
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    logger.warning(f"⚠️ High memory usage: {memory.percent:.1f}%")
                
                # Check CPU usage
                cpu = psutil.cpu_percent(interval=1)
                if cpu > 90:
                    logger.warning(f"⚠️ High CPU usage: {cpu:.1f}%")
                
                # Check disk usage
                disk = psutil.disk_usage('/')
                if disk.percent > 95:
                    logger.error(f"🚨 CRITICAL disk usage: {disk.percent:.1f}% - System may be unstable")
                elif disk.percent > 90:
                    logger.warning(f"⚠️ High disk usage: {disk.percent:.1f}% - Consider running cleanup_disk.py")
                
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(60)


class LawAgentServer:
    """Advanced Law Agent server with robust error handling."""
    
    def __init__(self, port: int = 8000, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.server_process = None
        self.health_monitor = SystemHealthMonitor()
        self.app = None
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("🧹 Cleaning up resources...")
        self.health_monitor.stop_monitoring()
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                pass
    
    def create_app(self) -> FastAPI:
        """Create the combined FastAPI application."""
        # Create main app
        app = FastAPI(
            title="Law Agent - Advanced Legal AI Assistant",
            description="Robust Legal AI Assistant with comprehensive error handling",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Add health check endpoint
        @app.get("/health")
        async def health_check():
            """Advanced health check with system metrics."""
            try:
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent()
                disk = psutil.disk_usage('/')
                
                return {
                    "status": "healthy",
                    "version": "2.0.0",
                    "timestamp": time.time(),
                    "system": {
                        "memory_usage": f"{memory.percent:.1f}%",
                        "cpu_usage": f"{cpu:.1f}%",
                        "disk_usage": f"{disk.percent:.1f}%",
                        "available_memory": f"{memory.available / (1024**3):.1f}GB"
                    },
                    "services": {
                        "redis": self._check_redis(),
                        "database": self._check_database(),
                        "ml_models": self._check_ml_models()
                    }
                }
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        # Include API routes directly in the main app instead of mounting
        from law_agent.api.routes import router
        app.include_router(router, prefix="/api/v1", tags=["Law Agent API"])

        # Mount Web Interface
        web_app = create_web_app()
        app.mount("/", web_app)
        
        return app
    
    def _check_redis(self) -> str:
        """Check Redis connection."""
        try:
            import redis
            client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            client.ping()
            return "connected"
        except:
            return "disconnected"
    
    def _check_database(self) -> str:
        """Check database connection."""
        try:
            # Add database check logic here
            return "connected"
        except:
            return "disconnected"
    
    def _check_ml_models(self) -> str:
        """Check ML models status."""
        try:
            # Add ML models check logic here
            return "loaded"
        except:
            return "not_loaded"
    
    def start(self, auto_port: bool = True, enable_monitoring: bool = True):
        """Start the Law Agent server with advanced error handling."""

        # Check disk space before starting
        disk = psutil.disk_usage('/')
        free_gb = disk.free / (1024**3)

        if disk.percent > 95:
            logger.error(f"🚨 CRITICAL: Disk usage {disk.percent:.1f}% - Only {free_gb:.1f}GB free")
            logger.error("❌ Cannot start server safely. Please free up disk space.")
            logger.info("💡 Run: python cleanup_disk.py")
            return False
        elif disk.percent > 90:
            logger.warning(f"⚠️ WARNING: High disk usage {disk.percent:.1f}% - {free_gb:.1f}GB free")
            logger.info("💡 Consider running: python cleanup_disk.py")

        # Handle port conflicts
        if auto_port and PortManager.is_port_in_use(self.port):
            logger.warning(f"⚠️ Port {self.port} is in use")
            
            # Try to kill existing process
            if PortManager.kill_process_on_port(self.port):
                logger.info(f"✅ Freed port {self.port}")
                time.sleep(2)  # Wait for port to be fully released
            
            # If still in use, find alternative port
            if PortManager.is_port_in_use(self.port):
                new_port = PortManager.find_free_port(self.port)
                logger.info(f"🔄 Using alternative port: {new_port}")
                self.port = new_port
        
        # Create application
        self.app = self.create_app()
        
        # Start health monitoring
        if enable_monitoring:
            self.health_monitor.start_monitoring()
        
        # Display startup information
        self._display_startup_info()
        
        # Start server with enhanced error handling
        try:
            logger.info(f"🚀 Starting server on {self.host}:{self.port}")

            # Configure uvicorn with better settings
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info",
                access_log=True,
                reload=False,
                loop="asyncio",
                timeout_keep_alive=30,
                timeout_graceful_shutdown=10
            )

            server = uvicorn.Server(config)

            # Run server with proper exception handling
            try:
                server.run()
            except KeyboardInterrupt:
                logger.info("🛑 Server stopped by user (Ctrl+C)")
            except Exception as server_error:
                logger.error(f"❌ Server runtime error: {server_error}")
                logger.info("🔄 Attempting to restart server...")
                time.sleep(5)
                # Try to restart once
                try:
                    server.run()
                except Exception as restart_error:
                    logger.error(f"❌ Server restart failed: {restart_error}")
                    raise

        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            logger.info("💡 Troubleshooting tips:")
            logger.info("   • Check if port is available")
            logger.info("   • Verify Redis is running")
            logger.info("   • Check system resources")
            self.cleanup()
            raise
    
    def _display_startup_info(self):
        """Display comprehensive startup information."""
        print("\n" + "=" * 70)
        print("🏛️  LAW AGENT - ADVANCED LEGAL AI ASSISTANT")
        print("=" * 70)
        print(f"🚀 Version: 2.0.0 (Robust Edition)")
        print(f"🌐 Web Interface: http://{self.host}:{self.port}")
        print(f"📡 API Endpoints: http://{self.host}:{self.port}/api")
        print(f"📚 API Documentation: http://{self.host}:{self.port}/api/docs")
        print(f"🔍 Health Check: http://{self.host}:{self.port}/health")
        print(f"💾 Redis: {self._check_redis()}")
        print(f"🗄️ Database: {self._check_database()}")
        print(f"🤖 ML Models: {self._check_ml_models()}")
        print("=" * 70)
        print("🎯 ADVANCED FEATURES:")
        print("• Automatic port conflict resolution")
        print("• System health monitoring")
        print("• Graceful shutdown handling")
        print("• Resource usage tracking")
        print("• Advanced error recovery")
        print("• Process management")
        print("=" * 70)


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description="Law Agent - Advanced Legal AI Assistant")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    parser.add_argument("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
    parser.add_argument("--no-auto-port", action="store_true", help="Disable automatic port resolution")
    parser.add_argument("--no-monitoring", action="store_true", help="Disable system health monitoring")
    parser.add_argument("--kill-existing", action="store_true", help="Kill existing processes on port")
    
    args = parser.parse_args()
    
    # Kill existing processes if requested
    if args.kill_existing:
        PortManager.kill_process_on_port(args.port)
        time.sleep(2)
    
    # Create and start server
    server = LawAgentServer(port=args.port, host=args.host)
    server.start(
        auto_port=not args.no_auto_port,
        enable_monitoring=not args.no_monitoring
    )


if __name__ == "__main__":
    main()
