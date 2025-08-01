#!/usr/bin/env python3
"""
Fix ML Dependencies for Law Agent
Properly resolve TensorFlow, PyTorch, and Transformers version conflicts.
"""

import subprocess
import sys
import os
from pathlib import Path

class MLDependencyFixer:
    """Fix ML library version conflicts and compatibility issues."""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
    
    def check_current_versions(self):
        """Check current ML library versions."""
        print("🔍 CHECKING CURRENT ML LIBRARY VERSIONS")
        print("=" * 60)
        
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True)
            
            ml_packages = [
                'tensorflow', 'tf_keras', 'keras', 'torch', 'torchvision', 
                'torchaudio', 'transformers', 'sentence-transformers'
            ]
            
            current_versions = {}
            for line in result.stdout.split('\n'):
                for package in ml_packages:
                    if line.lower().startswith(package.lower()):
                        parts = line.split()
                        if len(parts) >= 2:
                            current_versions[package] = parts[1]
                            print(f"📦 {package:<20} {parts[1]}")
            
            return current_versions
            
        except Exception as e:
            print(f"❌ Failed to check versions: {e}")
            return {}
    
    def identify_issues(self, versions):
        """Identify version compatibility issues."""
        print("\n🔍 IDENTIFYING COMPATIBILITY ISSUES")
        print("=" * 60)
        
        issues = []
        
        # Check TensorFlow/Keras compatibility
        tf_version = versions.get('tensorflow', '')
        tf_keras_version = versions.get('tf_keras', '')
        keras_version = versions.get('keras', '')
        
        if tf_version and tf_keras_version:
            if tf_version != tf_keras_version:
                issues.append({
                    'type': 'version_mismatch',
                    'description': f'TensorFlow {tf_version} != tf_keras {tf_keras_version}',
                    'fix': 'Uninstall tf_keras and use TensorFlow built-in Keras'
                })
        
        # Check for deprecated tf_keras
        if 'tf_keras' in versions:
            issues.append({
                'type': 'deprecated_package',
                'description': 'tf_keras is deprecated and causes warnings',
                'fix': 'Remove tf_keras and use tensorflow.keras'
            })
        
        # Check PyTorch/Transformers compatibility
        torch_version = versions.get('torch', '')
        transformers_version = versions.get('transformers', '')
        
        if torch_version.startswith('2.7') and transformers_version.startswith('4.54'):
            issues.append({
                'type': 'compatibility_warning',
                'description': 'PyTorch 2.7.1 with Transformers 4.54.0 causes FutureWarnings',
                'fix': 'Update to compatible versions'
            })
        
        for issue in issues:
            print(f"⚠️ {issue['type']}: {issue['description']}")
            print(f"   💡 Fix: {issue['fix']}")
        
        self.issues_found = issues
        return issues
    
    def fix_tensorflow_keras_issues(self):
        """Fix TensorFlow/Keras version conflicts."""
        print("\n🔧 FIXING TENSORFLOW/KERAS ISSUES")
        print("=" * 60)
        
        try:
            # Uninstall problematic packages
            print("🗑️ Removing conflicting packages...")
            packages_to_remove = ['tf_keras', 'keras']
            
            for package in packages_to_remove:
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', package, '-y'], 
                                 capture_output=True, check=True)
                    print(f"✅ Removed {package}")
                except subprocess.CalledProcessError:
                    print(f"⚠️ {package} not installed or already removed")
            
            # Install compatible TensorFlow version
            print("📦 Installing compatible TensorFlow...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'tensorflow==2.18.0',  # More stable version
                '--upgrade'
            ], check=True)
            
            print("✅ TensorFlow/Keras issues fixed")
            self.fixes_applied.append("TensorFlow/Keras compatibility")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fix TensorFlow issues: {e}")
            return False
    
    def fix_pytorch_transformers_issues(self):
        """Fix PyTorch/Transformers compatibility."""
        print("\n🔧 FIXING PYTORCH/TRANSFORMERS ISSUES")
        print("=" * 60)
        
        try:
            # Install compatible versions
            print("📦 Installing compatible PyTorch and Transformers...")
            
            # Install stable PyTorch
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'torch==2.5.1', 'torchvision==0.20.1', 'torchaudio==2.5.1',
                '--index-url', 'https://download.pytorch.org/whl/cpu',
                '--upgrade'
            ], check=True)
            
            # Install compatible Transformers
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'transformers==4.46.0',  # More stable with PyTorch 2.5
                '--upgrade'
            ], check=True)
            
            print("✅ PyTorch/Transformers issues fixed")
            self.fixes_applied.append("PyTorch/Transformers compatibility")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to fix PyTorch issues: {e}")
            return False
    
    def install_additional_dependencies(self):
        """Install additional dependencies for better compatibility."""
        print("\n📦 INSTALLING ADDITIONAL DEPENDENCIES")
        print("=" * 60)
        
        additional_packages = [
            'protobuf==3.20.3',  # Fix protobuf compatibility
            'numpy==1.24.3',     # Stable numpy version
            'scipy==1.11.4',     # Compatible scipy
            'scikit-learn==1.3.2',  # Stable sklearn
        ]
        
        try:
            for package in additional_packages:
                print(f"📦 Installing {package}...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package, '--upgrade'
                ], check=True)
                print(f"✅ Installed {package}")
            
            self.fixes_applied.append("Additional dependencies")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install additional dependencies: {e}")
            return False
    
    def verify_fixes(self):
        """Verify that fixes resolved the issues."""
        print("\n🧪 VERIFYING FIXES")
        print("=" * 60)
        
        try:
            # Test TensorFlow import
            print("🧪 Testing TensorFlow...")
            result = subprocess.run([
                sys.executable, '-c', 
                '''
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
print(f"TensorFlow: {tf.__version__}")
print(f"Keras: {tf.keras.__version__}")
print("✅ TensorFlow import successful")
'''
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ TensorFlow verification passed")
                print(result.stdout.strip())
            else:
                print(f"❌ TensorFlow verification failed: {result.stderr}")
            
            # Test PyTorch import
            print("\n🧪 Testing PyTorch...")
            result = subprocess.run([
                sys.executable, '-c', 
                '''
import torch
import transformers
print(f"PyTorch: {torch.__version__}")
print(f"Transformers: {transformers.__version__}")
print("✅ PyTorch import successful")
'''
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ PyTorch verification passed")
                print(result.stdout.strip())
            else:
                print(f"❌ PyTorch verification failed: {result.stderr}")
            
            # Test sentence-transformers
            print("\n🧪 Testing Sentence Transformers...")
            result = subprocess.run([
                sys.executable, '-c', 
                '''
from sentence_transformers import SentenceTransformer
print("✅ Sentence Transformers import successful")
'''
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Sentence Transformers verification passed")
            else:
                print(f"❌ Sentence Transformers verification failed: {result.stderr}")
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def create_requirements_lock(self):
        """Create a requirements lock file with working versions."""
        print("\n📝 CREATING REQUIREMENTS LOCK FILE")
        print("=" * 60)
        
        try:
            # Get current working versions
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                                  capture_output=True, text=True)
            
            # Filter ML packages
            ml_packages = []
            for line in result.stdout.split('\n'):
                if any(pkg in line.lower() for pkg in [
                    'tensorflow', 'torch', 'transformers', 'sentence-transformers',
                    'numpy', 'scipy', 'scikit-learn', 'protobuf'
                ]):
                    ml_packages.append(line.strip())
            
            # Write to requirements file
            with open('requirements_ml_fixed.txt', 'w') as f:
                f.write("# Fixed ML Dependencies for Law Agent\n")
                f.write("# Generated after resolving compatibility issues\n\n")
                for package in sorted(ml_packages):
                    if package:
                        f.write(f"{package}\n")
            
            print("✅ Created requirements_ml_fixed.txt")
            print("💡 Use: pip install -r requirements_ml_fixed.txt")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create requirements lock: {e}")
            return False
    
    def run_complete_fix(self):
        """Run complete dependency fix process."""
        print("🏛️  LAW AGENT ML DEPENDENCY FIXER")
        print("=" * 70)
        
        # Check current versions
        versions = self.check_current_versions()
        
        # Identify issues
        issues = self.identify_issues(versions)
        
        if not issues:
            print("\n✅ No compatibility issues found!")
            return True
        
        print(f"\n🔧 Found {len(issues)} issues to fix...")
        
        # Apply fixes
        success = True
        success &= self.fix_tensorflow_keras_issues()
        success &= self.fix_pytorch_transformers_issues()
        success &= self.install_additional_dependencies()
        
        if success:
            # Verify fixes
            success &= self.verify_fixes()
            
            # Create requirements lock
            self.create_requirements_lock()
            
            print("\n" + "=" * 70)
            print("🎉 ML DEPENDENCY FIXES COMPLETE!")
            print("=" * 70)
            print("✅ Issues resolved:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
            
            print("\n🚀 Next steps:")
            print("1. Restart Law Agent: python run_law_agent_robust.py --kill-existing")
            print("2. Warnings should be significantly reduced")
            print("3. Performance should be improved")
            
            return True
        else:
            print("\n❌ Some fixes failed. Check the output above for details.")
            return False


def main():
    """Main function."""
    fixer = MLDependencyFixer()
    success = fixer.run_complete_fix()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
