#!/usr/bin/env python3
"""
Simple Test Server to Check Connection
"""

import socket
import threading
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time

class TestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Law Agent Connection Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f0f0f0; }
                .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
                .success { color: #27ae60; font-size: 24px; font-weight: bold; }
                .info { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Connection Test Successful!</h1>
                <div class="success">✅ Your browser can connect to the server!</div>
                
                <div class="info">
                    <h3>🔍 Connection Details:</h3>
                    <p><strong>Server:</strong> Python HTTP Server</p>
                    <p><strong>Port:</strong> 8002</p>
                    <p><strong>Status:</strong> Working perfectly</p>
                </div>
                
                <div class="info">
                    <h3>🚀 Next Steps:</h3>
                    <ol>
                        <li>Stop this test server (Ctrl+C in terminal)</li>
                        <li>Start Law Agent with: <code>python law_agent_minimal.py --port 8002</code></li>
                        <li>Access Law Agent at: <code>http://localhost:8002/chat</code></li>
                    </ol>
                </div>
                
                <div class="info">
                    <h3>🔧 If Law Agent Still Doesn't Work:</h3>
                    <ul>
                        <li>Check Windows Firewall settings</li>
                        <li>Try running as Administrator</li>
                        <li>Use different port numbers</li>
                        <li>Check antivirus software</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())

def find_free_port():
    """Find a free port."""
    for port in range(8002, 8020):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('localhost', port))
                return port
        except OSError:
            continue
    return 8002

def start_test_server():
    port = find_free_port()
    
    print("🧪 STARTING CONNECTION TEST SERVER")
    print("=" * 50)
    print(f"🌐 Test URL: http://localhost:{port}")
    print("=" * 50)
    print("💡 This will test if your browser can connect to a Python server")
    print("💡 If this works, then Law Agent should work too")
    print("=" * 50)
    
    try:
        server = HTTPServer(('localhost', port), TestHandler)
        
        # Open browser automatically
        def open_browser():
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print(f"✅ Test server started on port {port}")
        print("🌐 Opening browser automatically...")
        print("💡 Press Ctrl+C to stop the test server")
        print("=" * 50)
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Test server stopped")
        server.shutdown()
    except Exception as e:
        print(f"❌ Error starting test server: {e}")

if __name__ == "__main__":
    start_test_server()
