#!/usr/bin/env python3
"""
Law Agent API Launcher
Simple command to start the Law Agent API
"""

import subprocess
import sys
import os

def main():
    print("🏛️  LAW AGENT API LAUNCHER")
    print("=" * 40)
    print("🚀 Starting Law Agent API Server...")
    print("=" * 40)
    
    try:
        # Run the law agent minimal server
        subprocess.run([sys.executable, "law_agent_minimal.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Law Agent API stopped by user")
    except Exception as e:
        print(f"❌ Error starting Law Agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
