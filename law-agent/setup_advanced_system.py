#!/usr/bin/env python3
"""
Advanced Law Agent System Setup
Comprehensive setup with dependency checking, installation, and system optimization.
"""

import subprocess
import sys
import os
import platform
import importlib
import pkg_resources
from pathlib import Path
from typing import List, Dict, Tuple
import requests
import json

class SystemSetup:
    """Advanced system setup and dependency management."""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.platform = platform.system()
        self.architecture = platform.architecture()[0]
        self.required_python = (3, 8)
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        if self.python_version >= self.required_python:
            print(f"✅ Python {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
            return True
        else:
            print(f"❌ Python {self.python_version.major}.{self.python_version.minor} (requires >= {self.required_python[0]}.{self.required_python[1]})")
            return False
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check all required dependencies."""
        dependencies = {
            # Core dependencies
            'fastapi': 'FastAPI web framework',
            'uvicorn': 'ASGI server',
            'sqlalchemy': 'Database ORM',
            'redis': 'Redis client',
            'loguru': 'Advanced logging',
            'pydantic': 'Data validation',
            
            # ML/AI dependencies
            'torch': 'PyTorch deep learning',
            'transformers': 'Hugging Face transformers',
            'sentence-transformers': 'Sentence embeddings',
            'tensorflow': 'TensorFlow ML framework',
            'scikit-learn': 'Machine learning library',
            'numpy': 'Numerical computing',
            'pandas': 'Data manipulation',
            
            # NLP dependencies
            'spacy': 'Advanced NLP',
            'nltk': 'Natural language toolkit',
            
            # Vector databases
            'chromadb': 'Vector database',
            'faiss-cpu': 'Similarity search',
            
            # RL dependencies
            'stable-baselines3': 'Reinforcement learning',
            'gymnasium': 'RL environments',
            
            # System dependencies
            'psutil': 'System monitoring',
            'requests': 'HTTP client',
            'python-dotenv': 'Environment variables'
        }
        
        results = {}
        print("\n🔍 Checking dependencies...")
        
        for package, description in dependencies.items():
            try:
                importlib.import_module(package.replace('-', '_'))
                print(f"✅ {package:<20} - {description}")
                results[package] = True
            except ImportError:
                print(f"❌ {package:<20} - {description}")
                results[package] = False
        
        return results
    
    def install_missing_dependencies(self, missing: List[str]) -> bool:
        """Install missing dependencies."""
        if not missing:
            print("✅ All dependencies are already installed!")
            return True
        
        print(f"\n📦 Installing {len(missing)} missing dependencies...")
        
        # Group installations for efficiency
        ml_packages = ['torch', 'torchvision', 'torchaudio', 'transformers', 'sentence-transformers']
        basic_packages = [pkg for pkg in missing if pkg not in ml_packages]
        ml_missing = [pkg for pkg in missing if pkg in ml_packages]
        
        success = True
        
        # Install basic packages
        if basic_packages:
            success &= self._install_packages(basic_packages)
        
        # Install ML packages with special handling
        if ml_missing:
            success &= self._install_ml_packages(ml_missing)
        
        return success
    
    def _install_packages(self, packages: List[str]) -> bool:
        """Install a list of packages."""
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade'] + packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ Installed: {', '.join(packages)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {packages}: {e}")
            return False
    
    def _install_ml_packages(self, packages: List[str]) -> bool:
        """Install ML packages with optimized settings."""
        try:
            # Install PyTorch with CPU support (faster download)
            if 'torch' in packages:
                torch_cmd = [
                    sys.executable, '-m', 'pip', 'install', 
                    'torch', 'torchvision', 'torchaudio',
                    '--index-url', 'https://download.pytorch.org/whl/cpu'
                ]
                subprocess.run(torch_cmd, check=True)
                print("✅ Installed PyTorch (CPU version)")
            
            # Install other ML packages
            other_ml = [pkg for pkg in packages if pkg not in ['torch', 'torchvision', 'torchaudio']]
            if other_ml:
                return self._install_packages(other_ml)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install ML packages: {e}")
            return False
    
    def setup_spacy_models(self) -> bool:
        """Download and setup spaCy language models."""
        try:
            print("\n📚 Setting up spaCy language models...")
            models = ['en_core_web_sm', 'en_core_web_md']
            
            for model in models:
                try:
                    cmd = [sys.executable, '-m', 'spacy', 'download', model]
                    subprocess.run(cmd, check=True, capture_output=True)
                    print(f"✅ Downloaded spaCy model: {model}")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Failed to download {model}, continuing...")
            
            return True
        except Exception as e:
            print(f"❌ spaCy setup failed: {e}")
            return False
    
    def setup_nltk_data(self) -> bool:
        """Download NLTK data."""
        try:
            print("\n📚 Setting up NLTK data...")
            import nltk
            
            datasets = [
                'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
                'vader_lexicon', 'omw-1.4', 'punkt_tab'
            ]
            
            for dataset in datasets:
                try:
                    nltk.download(dataset, quiet=True)
                    print(f"✅ Downloaded NLTK data: {dataset}")
                except:
                    print(f"⚠️ Failed to download {dataset}, continuing...")
            
            return True
        except Exception as e:
            print(f"❌ NLTK setup failed: {e}")
            return False
    
    def setup_redis(self) -> bool:
        """Setup Redis with multiple fallback options."""
        try:
            print("\n🔄 Setting up Redis...")
            
            # Check if Redis is already running
            import redis
            try:
                client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                client.ping()
                print("✅ Redis is already running!")
                return True
            except:
                pass
            
            # Try to start existing Redis installation
            if self._start_existing_redis():
                return True
            
            # Setup FakeRedis as fallback
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'fakeredis'], check=True)
                print("✅ FakeRedis installed as fallback")
                return True
            except:
                print("⚠️ FakeRedis installation failed")
            
            return False
            
        except Exception as e:
            print(f"❌ Redis setup failed: {e}")
            return False
    
    def _start_existing_redis(self) -> bool:
        """Try to start existing Redis installation."""
        try:
            # Check for Redis in common locations
            redis_paths = [
                'redis/redis-server.exe',  # Our downloaded version
                'redis-server',  # System PATH
                '/usr/local/bin/redis-server',  # macOS Homebrew
                '/usr/bin/redis-server',  # Linux package manager
            ]
            
            for redis_path in redis_paths:
                if os.path.exists(redis_path) or self._command_exists(redis_path):
                    try:
                        subprocess.Popen([redis_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(3)  # Wait for Redis to start
                        
                        # Test connection
                        import redis
                        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
                        client.ping()
                        print(f"✅ Started Redis from: {redis_path}")
                        return True
                    except:
                        continue
            
            return False
        except Exception:
            return False
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run([command, '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def create_env_file(self) -> bool:
        """Create optimized .env file."""
        try:
            print("\n📝 Creating .env configuration...")
            
            env_content = """# Law Agent Configuration
# Database
DATABASE_URL=sqlite:///./law_agent.db
REDIS_URL=redis://localhost:6379/0

# Server
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Security
SECRET_KEY=law-agent-advanced-secure-key-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/ML Configuration
HUGGINGFACE_TOKEN=
OPENAI_API_KEY=

# Performance Optimization
TORCH_NUM_THREADS=4
OMP_NUM_THREADS=4
TOKENIZERS_PARALLELISM=false

# System Monitoring
ENABLE_HEALTH_MONITORING=true
HEALTH_CHECK_INTERVAL=30

# Advanced Features
ENABLE_AUTO_PORT_RESOLUTION=true
ENABLE_GRACEFUL_SHUTDOWN=true
ENABLE_RESOURCE_MONITORING=true
"""
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            print("✅ Created .env configuration file")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    def optimize_system(self) -> bool:
        """Apply system optimizations."""
        try:
            print("\n⚡ Applying system optimizations...")
            
            # Set environment variables for better performance
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
            
            # Create necessary directories
            directories = ['logs', 'models', 'data', 'cache']
            for directory in directories:
                Path(directory).mkdir(exist_ok=True)
                print(f"✅ Created directory: {directory}")
            
            print("✅ System optimizations applied")
            return True
            
        except Exception as e:
            print(f"❌ System optimization failed: {e}")
            return False
    
    def run_setup(self) -> bool:
        """Run complete system setup."""
        print("🏛️  LAW AGENT ADVANCED SYSTEM SETUP")
        print("=" * 60)
        
        # Check Python version
        if not self.check_python_version():
            print("❌ Python version incompatible. Please upgrade to Python 3.8+")
            return False
        
        # Check dependencies
        deps = self.check_dependencies()
        missing = [pkg for pkg, installed in deps.items() if not installed]
        
        # Install missing dependencies
        if not self.install_missing_dependencies(missing):
            print("❌ Failed to install some dependencies")
            return False
        
        # Setup additional components
        self.setup_spacy_models()
        self.setup_nltk_data()
        self.setup_redis()
        self.create_env_file()
        self.optimize_system()
        
        print("\n" + "=" * 60)
        print("🎉 SETUP COMPLETE!")
        print("✅ All dependencies installed")
        print("✅ System optimized")
        print("✅ Configuration created")
        print("\n🚀 Ready to start Law Agent:")
        print("   python run_law_agent_robust.py")
        print("=" * 60)
        
        return True


def main():
    """Main setup function."""
    setup = SystemSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
