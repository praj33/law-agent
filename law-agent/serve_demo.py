#!/usr/bin/env python3
"""Simple HTTP server to serve the RL demo interface."""

import http.server
import socketserver
import webbrowser
import threading
import time
import os
import subprocess
import sys
import signal

PORT = 3002
API_PORT = 8001  # Changed to 8001 to avoid conflicts

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support."""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_api_server():
    """Start the API server in a subprocess."""
    try:
        # Try to start the API server using the Python module approach
        # We need to modify the port via environment variable
        env = os.environ.copy()
        env['API_PORT'] = str(API_PORT)
        
        api_process = subprocess.Popen([
            sys.executable, 
            "-m", 
            "law_agent.api.main"
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"API server starting on port {API_PORT}...")
        return api_process
    except Exception as e:
        print(f"Failed to start API server: {e}")
        return None

def start_server():
    """Start the HTTP server."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print(f"Demo server running at http://localhost:{PORT}")
            print(f"Serving files from: {os.getcwd()}")
            print(f"Open http://localhost:{PORT}/rl_demo.html to see the interface")
            print("Press Ctrl+C to stop the server")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nDemo server stopped")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Error: Port {PORT} is already in use. Please stop the process using that port or change the PORT variable.")
        else:
            print(f"Error starting server: {e}")

def open_browser_delayed():
    """Open browser after a short delay."""
    time.sleep(3)  # Increased delay to allow both servers to start
    webbrowser.open(f'http://localhost:{PORT}/rl_demo.html')

if __name__ == "__main__":
    # Start API server in background
    print("Starting Law Agent API server...")
    api_process = start_api_server()
    
    # Give the API server a moment to start
    time.sleep(2)
    
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start demo server
        start_server()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
    finally:
        # Clean up processes
        if api_process and api_process.poll() is None:
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()