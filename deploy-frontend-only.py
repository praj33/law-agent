#!/usr/bin/env python3
"""
Frontend-Only Deployment Script for Law Agent
Deploys the React frontend to Vercel
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path

def run_command(cmd, cwd=None, env=None):
    """Run a command and return success status"""
    try:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        
        result = subprocess.run(cmd, shell=True, cwd=cwd, env=full_env, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_frontend_requirements():
    """Check if frontend requirements are met"""
    print("🔍 Checking frontend deployment requirements...")
    
    requirements = [
        ("node", "Node.js"),
        ("npm", "NPM"),
        ("git", "Git")
    ]
    
    for cmd, name in requirements:
        success, stdout, _ = run_command(f"{cmd} --version")
        if success:
            print(f"✅ {name} is available ({stdout.strip().split()[0] if stdout else 'unknown version'})")
        else:
            print(f"❌ {name} is not installed")
            return False
    
    return True

def setup_environment_file():
    """Create environment file for frontend"""
    print("📝 Setting up environment configuration...")
    
    frontend_path = Path("law-agent-frontend")
    env_file = frontend_path / ".env.production"
    
    env_content = """# Production Environment Variables for Law Agent Frontend
REACT_APP_ENVIRONMENT=production
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ANALYTICS_URL=http://localhost:8002
REACT_APP_DOCUMENTS_URL=http://localhost:8001

# Supabase Configuration (Update these with your actual values)
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_anon_key_here

# Feature Flags
REACT_APP_ENABLE_3D_VISUALIZATION=true
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_DOCUMENT_UPLOAD=true

# Legal System Configuration
REACT_APP_DEFAULT_JURISDICTION=india
REACT_APP_SUPPORTED_LANGUAGES=en,hi

# Performance Settings
REACT_APP_ENABLE_SERVICE_WORKER=true
REACT_APP_ENABLE_PWA=true

# Security Settings
REACT_APP_ENABLE_CSP=true
REACT_APP_SECURE_COOKIES=true
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created {env_file}")
    return True

def install_dependencies():
    """Install frontend dependencies"""
    print("📦 Installing frontend dependencies...")
    
    frontend_path = Path("law-agent-frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Clean install
    success, stdout, stderr = run_command("npm ci", cwd=frontend_path)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        print("💡 Trying with npm install...")
        success, stdout, stderr = run_command("npm install", cwd=frontend_path)
        if not success:
            print(f"❌ npm install also failed: {stderr}")
            return False
    
    print("✅ Dependencies installed successfully")
    return True

def build_frontend():
    """Build the frontend for production"""
    print("🏗️ Building frontend for production...")
    
    frontend_path = Path("law-agent-frontend")
    
    # Set production environment
    env = {
        "NODE_ENV": "production",
        "CI": "false"  # Disable CI mode to allow warnings
    }
    
    success, stdout, stderr = run_command("npm run build", cwd=frontend_path, env=env)
    if not success:
        print(f"❌ Frontend build failed: {stderr}")
        return False
    
    # Check if build directory was created
    build_dir = frontend_path / "build"
    if build_dir.exists():
        print("✅ Frontend built successfully")
        print(f"📁 Build output: {build_dir}")
        
        # Show build stats
        try:
            build_files = list(build_dir.rglob("*"))
            total_size = sum(f.stat().st_size for f in build_files if f.is_file())
            print(f"📊 Build size: {total_size / 1024 / 1024:.2f} MB ({len(build_files)} files)")
        except:
            pass
        
        return True
    else:
        print("❌ Build directory not created")
        return False

def setup_vercel_config():
    """Create Vercel configuration"""
    print("⚙️ Setting up Vercel configuration...")
    
    frontend_path = Path("law-agent-frontend")
    vercel_config = frontend_path / "vercel.json"
    
    config = {
        "version": 2,
        "name": "law-agent-frontend",
        "builds": [
            {
                "src": "package.json",
                "use": "@vercel/static-build",
                "config": {
                    "distDir": "build"
                }
            }
        ],
        "routes": [
            {
                "src": "/static/(.*)",
                "headers": {
                    "cache-control": "public, max-age=31536000, immutable"
                }
            },
            {
                "src": "/(.*)",
                "dest": "/index.html"
            }
        ],
        "headers": [
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
        ]
    }
    
    with open(vercel_config, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created {vercel_config}")
    return True

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    
    frontend_path = Path("law-agent-frontend")
    
    # Check if Vercel CLI is available
    success, version_output, _ = run_command("vercel --version")
    if not success:
        print("📥 Vercel CLI not found. Installing...")
        success, _, stderr = run_command("npm install -g vercel")
        if not success:
            print(f"❌ Failed to install Vercel CLI: {stderr}")
            print("💡 Manual installation:")
            print("   1. Run: npm install -g vercel")
            print("   2. Run: vercel login")
            print("   3. Run: cd law-agent-frontend && vercel --prod")
            return False
    else:
        print(f"✅ Vercel CLI available ({version_output.strip()})")
    
    # Deploy
    print("🌐 Deploying to Vercel...")
    success, stdout, stderr = run_command("vercel --prod --yes", cwd=frontend_path)
    
    if success:
        print("✅ Deployment successful!")
        
        # Extract deployment URL
        lines = stdout.split('\n')
        deployment_url = None
        for line in lines:
            if 'https://' in line and ('vercel.app' in line or 'vercel.com' in line):
                deployment_url = line.strip()
                break
        
        if deployment_url:
            print(f"🌐 Your Law Agent is live at: {deployment_url}")
        else:
            print("🌐 Check your Vercel dashboard for the deployment URL")
        
        return True
    else:
        print(f"❌ Deployment failed: {stderr}")
        if "login" in stderr.lower():
            print("💡 Please run: vercel login")
        return False

def main():
    print("🏛️ Law Agent - Frontend Deployment")
    print("=" * 50)
    
    # Check requirements
    if not check_frontend_requirements():
        print("\n❌ Missing requirements. Please install missing tools.")
        return False
    
    # Setup environment
    if not setup_environment_file():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Build frontend
    if not build_frontend():
        return False
    
    # Setup Vercel config
    if not setup_vercel_config():
        return False
    
    # Deploy to Vercel
    deploy_success = deploy_to_vercel()
    
    # Summary
    print("\n" + "=" * 50)
    if deploy_success:
        print("🎉 FRONTEND DEPLOYMENT SUCCESSFUL!")
        print("\n🌐 Your Law Agent frontend is now live!")
        print("\n📋 Next Steps:")
        print("   1. Update Supabase credentials in Vercel environment variables")
        print("   2. Test the deployed application")
        print("   3. Set up backend services (Docker required)")
        print("   4. Configure custom domain (optional)")
    else:
        print("⚠️ FRONTEND BUILT SUCCESSFULLY, MANUAL DEPLOYMENT NEEDED")
        print("\n📁 Build files are ready in: law-agent-frontend/build/")
        print("\n💡 Manual deployment options:")
        print("   • Vercel: vercel --prod (after vercel login)")
        print("   • Netlify: Drag & drop build folder to netlify.com/drop")
        print("   • GitHub Pages: Push to gh-pages branch")
    
    print("\n📚 Important Files Created:")
    print("   • law-agent-frontend/.env.production")
    print("   • law-agent-frontend/vercel.json")
    print("   • law-agent-frontend/build/ (production build)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)
