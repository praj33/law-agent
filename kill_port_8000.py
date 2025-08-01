#!/usr/bin/env python3
"""
Simple Port 8000 Killer
Kills all processes using port 8000.
"""

import subprocess
import time
import sys

def kill_port_8000():
    """Kill all processes using port 8000."""
    print("🔍 Finding processes using port 8000...")
    
    try:
        # Find processes using port 8000
        result = subprocess.run(
            ['netstat', '-ano'], 
            capture_output=True, text=True, shell=True
        )
        
        pids_to_kill = []
        for line in result.stdout.split('\n'):
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        if not pids_to_kill:
            print("✅ No processes using port 8000")
            return True
        
        print(f"🎯 Found {len(pids_to_kill)} process(es) using port 8000: {pids_to_kill}")
        
        # Kill the processes
        killed_count = 0
        for pid in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], 
                             capture_output=True, check=True, shell=True)
                print(f"✅ Killed process {pid}")
                killed_count += 1
            except subprocess.CalledProcessError:
                print(f"⚠️ Could not kill process {pid}")
        
        if killed_count > 0:
            print("⏳ Waiting for port to be released...")
            time.sleep(5)
            
            # Verify port is free
            result2 = subprocess.run(
                ['netstat', '-ano'], 
                capture_output=True, text=True, shell=True
            )
            
            still_used = False
            for line in result2.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    still_used = True
                    break
            
            if still_used:
                print("⚠️ Port 8000 is still in use")
                return False
            else:
                print("✅ Port 8000 is now free")
                return True
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    print("🔥 PORT 8000 KILLER")
    print("=" * 30)
    
    success = kill_port_8000()
    
    if success:
        print("\n🎉 Port 8000 cleanup complete!")
        print("💡 You can now start Law Agent:")
        print("   python run_law_agent_robust.py --port 8000")
    else:
        print("\n❌ Port cleanup failed")
        print("💡 Try using a different port:")
        print("   python run_law_agent_robust.py --port 8001")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
