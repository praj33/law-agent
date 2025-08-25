#!/usr/bin/env python3
"""Simple HTTP server to serve the RL demo interface."""

import http.server
import socketserver
import webbrowser
import threading
import time
import os

PORT = 3002

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

def start_server():
    """Start the HTTP server."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"Demo server running at http://localhost:{PORT}")
        print(f"Serving files from: {os.getcwd()}")
        print(f"Open http://localhost:{PORT}/rl_demo.html to see the interface")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDemo server stopped")

def open_browser_delayed():
    """Open browser after a short delay."""
    time.sleep(2)
    webbrowser.open(f'http://localhost:{PORT}/rl_demo.html')

if __name__ == "__main__":
    # Start browser in background
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server
    start_server()
