#!/usr/bin/env python3
"""
Deploy Law Agent Frontend to Vercel
Step-by-step deployment guide and automation
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class VercelDeployer:
    """Deploy Law Agent Frontend to Vercel."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.frontend_path = self.project_root / "law-agent-frontend"
        
    def print_banner(self):
        """Print deployment banner."""
        print("🚀 LAW AGENT FRONTEND - VERCEL DEPLOYMENT")
        print("=" * 60)
        print("📦 Preparing React app for Vercel deployment...")
        print("=" * 60)
    
    def check_prerequisites(self):
        """Check deployment prerequisites."""
        print("🔍 Checking prerequisites...")
        
        # Check if frontend directory exists
        if not self.frontend_path.exists():
            print("❌ Frontend directory not found!")
            return False
        
        # Check package.json
        package_json = self.frontend_path / "package.json"
        if not package_json.exists():
            print("❌ package.json not found!")
            return False
        
        # Check if build directory exists or can be created
        build_dir = self.frontend_path / "build"
        if build_dir.exists():
            print("✅ Build directory exists")
        else:
            print("📦 Build directory will be created")
        
        print("✅ Prerequisites check passed")
        return True
    
    def install_dependencies(self):
        """Install frontend dependencies."""
        print("📦 Installing dependencies...")
        
        try:
            os.chdir(self.frontend_path)
            result = subprocess.run(
                ["npm", "install"], 
                check=True, 
                capture_output=True, 
                text=True
            )
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            print(f"Error output: {e.stderr}")
            return False
        except FileNotFoundError:
            print("❌ npm not found. Please install Node.js and npm")
            return False
    
    def build_frontend(self):
        """Build the frontend for production."""
        print("🔨 Building frontend for production...")
        
        try:
            # Set production environment
            env = os.environ.copy()
            env['NODE_ENV'] = 'production'
            env['CI'] = 'false'
            env['GENERATE_SOURCEMAP'] = 'false'
            
            result = subprocess.run(
                ["npm", "run", "build"], 
                check=True, 
                capture_output=True, 
                text=True,
                env=env
            )
            print("✅ Frontend built successfully")
            
            # Check build output
            build_dir = self.frontend_path / "build"
            if build_dir.exists():
                print(f"✅ Build directory created: {build_dir}")
                return True
            else:
                print("❌ Build directory not found after build")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def create_vercel_config(self):
        """Create optimized Vercel configuration."""
        print("⚙️ Creating Vercel configuration...")
        
        vercel_config = {
            "version": 2,
            "name": "law-agent-frontend",
            "framework": "create-react-app",
            "buildCommand": "npm run build",
            "outputDirectory": "build",
            "installCommand": "npm install",
            "devCommand": "npm start",
            "regions": ["iad1"],
            "functions": {},
            "headers": [
                {
                    "source": "/static/(.*)",
                    "headers": [
                        {
                            "key": "Cache-Control",
                            "value": "public, max-age=31536000, immutable"
                        }
                    ]
                },
                {
                    "source": "/(.*)",
                    "headers": [
                        {
                            "key": "X-Content-Type-Options",
                            "value": "nosniff"
                        },
                        {
                            "key": "X-Frame-Options",
                            "value": "DENY"
                        },
                        {
                            "key": "X-XSS-Protection",
                            "value": "1; mode=block"
                        }
                    ]
                }
            ],
            "rewrites": [
                {
                    "source": "/(.*)",
                    "destination": "/index.html"
                }
            ]
        }
        
        config_file = self.frontend_path / "vercel.json"
        with open(config_file, 'w') as f:
            json.dump(vercel_config, f, indent=2)
        
        print("✅ Vercel configuration created")
        return True
    
    def show_deployment_instructions(self):
        """Show manual deployment instructions."""
        print("\n🎯 DEPLOYMENT INSTRUCTIONS")
        print("=" * 50)
        print("Now deploy to Vercel using one of these methods:")
        print()
        
        print("📱 METHOD 1: Vercel CLI (Recommended)")
        print("1. Install Vercel CLI: npm i -g vercel")
        print("2. Login to Vercel: vercel login")
        print(f"3. Navigate to: cd {self.frontend_path}")
        print("4. Deploy: vercel --prod")
        print()
        
        print("🌐 METHOD 2: Vercel Dashboard")
        print("1. Go to: https://vercel.com/new")
        print("2. Import your GitHub repository")
        print("3. Select the law-agent-frontend folder")
        print("4. Framework: Create React App")
        print("5. Build Command: npm run build")
        print("6. Output Directory: build")
        print("7. Click Deploy")
        print()
        
        print("⚙️ ENVIRONMENT VARIABLES (Add in Vercel Dashboard):")
        env_vars = [
            "REACT_APP_API_URL=http://localhost:8000",
            "REACT_APP_ENVIRONMENT=production",
            "REACT_APP_ENABLE_ANALYTICS=true",
            "REACT_APP_ENABLE_DOCUMENT_UPLOAD=true",
            "REACT_APP_ENABLE_3D_VISUALIZATION=true"
        ]
        
        for var in env_vars:
            print(f"   • {var}")
        
        print("\n✅ Your frontend is ready for deployment!")
        print(f"📁 Frontend location: {self.frontend_path}")
        print(f"🔨 Build output: {self.frontend_path}/build")
    
    def deploy(self):
        """Run the complete deployment process."""
        self.print_banner()
        
        if not self.check_prerequisites():
            return False
        
        if not self.install_dependencies():
            return False
        
        if not self.build_frontend():
            return False
        
        self.create_vercel_config()
        self.show_deployment_instructions()
        
        return True

def main():
    """Main deployment function."""
    deployer = VercelDeployer()
    
    try:
        success = deployer.deploy()
        if success:
            print("\n🎉 Frontend is ready for Vercel deployment!")
        else:
            print("\n❌ Deployment preparation failed")
            return False
    except KeyboardInterrupt:
        print("\n👋 Deployment cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
