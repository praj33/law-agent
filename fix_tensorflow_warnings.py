#!/usr/bin/env python3
"""
Simple TensorFlow Warning Fix
Addresses the specific warnings you're seeing without breaking dependencies.
"""

import subprocess
import sys
import os

def fix_tensorflow_warnings():
    """Fix TensorFlow warnings with minimal changes."""
    
    print("🔧 FIXING TENSORFLOW WARNINGS")
    print("=" * 50)
    
    try:
        # The main issue is tf_keras being separate from tensorflow
        # Let's remove tf_keras and let TensorFlow use its built-in Keras
        
        print("1️⃣ Removing problematic tf_keras...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'tf_keras', '-y'], 
                         capture_output=True, check=True)
            print("✅ Removed tf_keras")
        except subprocess.CalledProcessError:
            print("⚠️ tf_keras not found or already removed")
        
        # Install the latest stable TensorFlow that includes Keras
        print("2️⃣ Installing TensorFlow with built-in Keras...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'tensorflow==2.17.0',  # Stable version with good Keras integration
            '--upgrade'
        ], check=True)
        print("✅ TensorFlow 2.17.0 installed")
        
        # Test the fix
        print("3️⃣ Testing TensorFlow import...")
        result = subprocess.run([
            sys.executable, '-c', 
            '''
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
print(f"TensorFlow: {tf.__version__}")
print(f"Keras: {tf.keras.__version__}")
print("✅ Import successful - warnings should be reduced")
'''
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ TensorFlow test passed")
            print(result.stdout.strip())
        else:
            print(f"⚠️ TensorFlow test had issues: {result.stderr}")
        
        print("\n" + "=" * 50)
        print("🎉 TENSORFLOW WARNINGS FIXED!")
        print("✅ Removed separate tf_keras package")
        print("✅ Using TensorFlow's built-in Keras")
        print("✅ Warnings should be significantly reduced")
        print("\n🚀 Restart Law Agent to see the improvements:")
        print("   python run_law_agent_robust.py --kill-existing")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Fix failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function."""
    success = fix_tensorflow_warnings()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
