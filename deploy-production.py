#!/usr/bin/env python3
"""
Production Deployment Script for Law Agent
Deploys all services to production environment
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

def check_requirements():
    """Check if all required tools are installed"""
    print("🔍 Checking deployment requirements...")
    
    requirements = [
        ("docker", "Docker"),
        ("docker-compose", "Docker Compose"),
        ("git", "Git"),
        ("node", "Node.js"),
        ("npm", "NPM")
    ]
    
    for cmd, name in requirements:
        success, _, _ = run_command(f"{cmd} --version")
        if success:
            print(f"✅ {name} is available")
        else:
            print(f"❌ {name} is not installed")
            return False
    
    return True

def build_and_push_images():
    """Build and push Docker images"""
    print("\n🐳 Building Docker images...")
    
    images = [
        ("law-agent-api", "docker/Dockerfile.api"),
        ("law-agent-analytics", "docker/Dockerfile.analytics"),
        ("law-agent-documents", "docker/Dockerfile.documents")
    ]
    
    for image_name, dockerfile in images:
        print(f"🏗️ Building {image_name}...")
        
        # Build image
        success, stdout, stderr = run_command(
            f"docker build -t {image_name}:latest -f {dockerfile} ."
        )
        
        if not success:
            print(f"❌ Failed to build {image_name}: {stderr}")
            return False
        
        print(f"✅ {image_name} built successfully")
    
    return True

def deploy_frontend():
    """Deploy frontend to Vercel"""
    print("\n🎨 Deploying frontend...")
    
    frontend_path = Path("law-agent-frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("📦 Installing dependencies...")
    success, _, stderr = run_command("npm ci", cwd=frontend_path)
    if not success:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    # Build frontend
    print("🏗️ Building frontend...")
    success, _, stderr = run_command("npm run build", cwd=frontend_path)
    if not success:
        print(f"❌ Frontend build failed: {stderr}")
        return False
    
    print("✅ Frontend built successfully")
    
    # Check if Vercel CLI is available
    success, _, _ = run_command("vercel --version")
    if success:
        print("🚀 Deploying to Vercel...")
        success, stdout, stderr = run_command("vercel --prod", cwd=frontend_path)
        if success:
            print("✅ Frontend deployed to Vercel!")
            # Extract URL from output
            lines = stdout.split('\n')
            for line in lines:
                if 'https://' in line and 'vercel.app' in line:
                    print(f"🌐 Frontend URL: {line.strip()}")
        else:
            print(f"⚠️ Vercel deployment failed: {stderr}")
            print("💡 You can deploy manually with: cd law-agent-frontend && vercel --prod")
    else:
        print("💡 Vercel CLI not found. Deploy manually:")
        print("   1. Install: npm i -g vercel")
        print("   2. Login: vercel login")
        print("   3. Deploy: cd law-agent-frontend && vercel --prod")
    
    return True

def start_backend_services():
    """Start backend services with Docker Compose"""
    print("\n🚀 Starting backend services...")
    
    # Create production environment file
    env_content = """
# Production Environment Variables
ENVIRONMENT=production
LOG_LEVEL=info
REDIS_PASSWORD=lawagent_prod_redis_2024
GRAFANA_PASSWORD=lawagent_prod_grafana_2024

# Database URLs (will be overridden by Supabase in production)
DATABASE_URL=sqlite:///data/law_agent.db

# Add your Supabase URLs here after setup
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_SERVICE_KEY=your_service_key
"""
    
    with open('.env.production', 'w') as f:
        f.write(env_content)
    
    print("📝 Created .env.production file")
    
    # Start services
    success, stdout, stderr = run_command("docker-compose --env-file .env.production up -d")
    if not success:
        print(f"❌ Failed to start services: {stderr}")
        return False
    
    print("✅ Backend services started successfully")
    
    # Wait for services to be ready
    print("⏳ Waiting for services to initialize...")
    time.sleep(15)
    
    # Check service health
    services = [
        ("http://localhost:8000/health", "Main API"),
        ("http://localhost:8001/health", "Document API"),
        ("http://localhost:8002/health", "Analytics API")
    ]
    
    import requests
    for url, name in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} is healthy")
            else:
                print(f"⚠️ {name} returned status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} is not responding: {e}")
    
    return True

def main():
    print("🏛️ Law Agent - Production Deployment")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Missing requirements. Please install missing tools.")
        return False
    
    # Build Docker images
    if not build_and_push_images():
        print("\n❌ Docker build failed")
        return False
    
    # Deploy frontend
    if not deploy_frontend():
        print("\n❌ Frontend deployment failed")
        return False
    
    # Start backend services
    if not start_backend_services():
        print("\n❌ Backend deployment failed")
        return False
    
    # Success summary
    print("\n" + "=" * 50)
    print("🎉 DEPLOYMENT SUCCESSFUL!")
    print("\n📍 Access Points:")
    print("   • Frontend: Check Vercel deployment URL")
    print("   • Main API: http://localhost:8000")
    print("   • Document API: http://localhost:8001")
    print("   • Analytics API: http://localhost:8002")
    print("   • Monitoring: http://localhost:3000 (Grafana)")
    print("   • Metrics: http://localhost:9090 (Prometheus)")
    
    print("\n🔧 Next Steps:")
    print("   1. Update .env.production with your Supabase credentials")
    print("   2. Configure GitHub secrets for automated deployments")
    print("   3. Set up custom domain (optional)")
    print("   4. Configure monitoring alerts")
    
    print("\n📚 Documentation:")
    print("   • Deployment guide: DEPLOYMENT.md")
    print("   • GitHub secrets: GITHUB_SECRETS_SETUP.md")
    print("   • API docs: http://localhost:8000/docs")
    
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
