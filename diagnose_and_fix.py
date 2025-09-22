#!/usr/bin/env python3
"""
Diagnose and Fix Law Agent Connection Issues
"""

import subprocess
import socket
import requests
import time
import webbrowser
import sys

def check_port_listening(port):
    """Check if a port is listening."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def test_http_connection(port):
    """Test HTTP connection to the port."""
    try:
        response = requests.get(f'http://localhost:{port}/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_firewall():
    """Check Windows Firewall status."""
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'], 
                              capture_output=True, text=True)
        return 'State                                 ON' in result.stdout
    except:
        return None

def diagnose_connection(port=8001):
    print("🔍 DIAGNOSING CONNECTION ISSUES")
    print("=" * 50)
    
    # Check 1: Is the port listening?
    print(f"1. Checking if port {port} is listening...")
    if check_port_listening(port):
        print(f"   ✅ Port {port} is listening")
    else:
        print(f"   ❌ Port {port} is NOT listening")
        print("   💡 Make sure Law Agent is running")
        return False
    
    # Check 2: Can we make HTTP requests?
    print(f"2. Testing HTTP connection to port {port}...")
    if test_http_connection(port):
        print(f"   ✅ HTTP connection successful")
    else:
        print(f"   ❌ HTTP connection failed")
        print("   💡 Server might not be responding to HTTP requests")
    
    # Check 3: Firewall status
    print("3. Checking Windows Firewall...")
    firewall_on = check_firewall()
    if firewall_on is True:
        print("   ⚠️ Windows Firewall is ON - this might block connections")
        print("   💡 Try running as Administrator or add firewall exception")
    elif firewall_on is False:
        print("   ✅ Windows Firewall is OFF")
    else:
        print("   ❓ Could not determine firewall status")
    
    # Check 4: Process information
    print("4. Checking running processes...")
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        found_process = False
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                print(f"   ✅ Found process listening on port {port}")
                print(f"   📋 {line.strip()}")
                found_process = True
                break
        if not found_process:
            print(f"   ❌ No process found listening on port {port}")
    except:
        print("   ❓ Could not check processes")
    
    return True

def fix_connection_issues(port=8001):
    print("\n🔧 APPLYING FIXES")
    print("=" * 30)
    
    # Fix 1: Add firewall exception
    print("1. Adding Windows Firewall exception...")
    try:
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name=Law Agent', 'dir=in', 'action=allow', 'protocol=TCP',
            f'localport={port}'
        ], capture_output=True)
        print("   ✅ Firewall exception added")
    except:
        print("   ⚠️ Could not add firewall exception (try running as Administrator)")
    
    # Fix 2: Test with curl (if available)
    print("2. Testing with direct HTTP request...")
    try:
        response = requests.get(f'http://127.0.0.1:{port}/health', timeout=5)
        print(f"   ✅ Direct request successful: {response.status_code}")
        return True
    except Exception as e:
        print(f"   ❌ Direct request failed: {e}")
        return False

def start_working_law_agent():
    print("\n🚀 STARTING LAW AGENT WITH FIXES")
    print("=" * 40)
    
    # Find available port
    for port in range(8002, 8010):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(('127.0.0.1', port))
                print(f"✅ Found available port: {port}")
                
                # Start Law Agent
                print(f"🚀 Starting Law Agent on port {port}...")
                cmd = [sys.executable, 'law_agent_minimal.py', '--host', '127.0.0.1', '--port', str(port)]
                
                print("📋 Command:", ' '.join(cmd))
                print("=" * 40)
                print(f"🌐 Once started, access at:")
                print(f"   💬 Chat: http://127.0.0.1:{port}/chat")
                print(f"   🏠 Main: http://127.0.0.1:{port}")
                print(f"   📚 API:  http://127.0.0.1:{port}/docs")
                print("=" * 40)
                
                # Execute the command
                subprocess.run(cmd)
                return
                
        except OSError:
            continue
    
    print("❌ No available ports found")

def main():
    print("🏛️ LAW AGENT CONNECTION DIAGNOSTICS")
    print("=" * 60)
    
    # Check if Law Agent is currently running
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8001
    
    print(f"🔍 Checking Law Agent on port {port}...")
    
    # Diagnose issues
    if diagnose_connection(port):
        # Try to fix issues
        if fix_connection_issues(port):
            print("\n🎉 Connection issues resolved!")
            print(f"💬 Try accessing: http://127.0.0.1:{port}/chat")
            
            # Open browser
            try:
                webbrowser.open(f'http://127.0.0.1:{port}/chat')
                print("🌐 Opening browser...")
            except:
                pass
        else:
            print("\n🔄 Starting fresh Law Agent instance...")
            start_working_law_agent()
    else:
        print("\n🔄 Starting fresh Law Agent instance...")
        start_working_law_agent()

if __name__ == "__main__":
    main()
