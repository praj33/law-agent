#!/usr/bin/env python3
"""
Law Agent Deployment Setup Script
Automated setup for CI/CD and deployment readiness
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentSetup:
    """Handles deployment setup and configuration"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.success_count = 0
        self.error_count = 0
        
    def print_status(self, message):
        """Print status message"""
        print(f"🔧 {message}")
        logger.info(message)
    
    def print_success(self, message):
        """Print success message"""
        print(f"✅ {message}")
        logger.info(message)
        self.success_count += 1
    
    def print_error(self, message):
        """Print error message"""
        print(f"❌ {message}")
        logger.error(message)
        self.error_count += 1
    
    def print_warning(self, message):
        """Print warning message"""
        print(f"⚠️ {message}")
        logger.warning(message)
    
    def check_dependencies(self):
        """Check if required tools are installed"""
        self.print_status("Checking deployment dependencies...")
        
        dependencies = {
            'git': 'Git version control',
            'docker': 'Docker containerization',
            'node': 'Node.js runtime',
            'npm': 'Node package manager',
            'python': 'Python runtime'
        }
        
        missing_deps = []
        
        for dep, description in dependencies.items():
            if shutil.which(dep):
                self.print_success(f"{description} is installed")
            else:
                self.print_error(f"{description} is missing")
                missing_deps.append(dep)
        
        if missing_deps:
            self.print_error(f"Please install missing dependencies: {', '.join(missing_deps)}")
            return False
        
        return True
    
    def setup_git_hooks(self):
        """Setup Git hooks for deployment"""
        self.print_status("Setting up Git hooks...")
        
        hooks_dir = self.project_root / '.git' / 'hooks'
        
        if not hooks_dir.exists():
            self.print_warning("Git repository not initialized")
            return
        
        # Pre-commit hook
        pre_commit_hook = hooks_dir / 'pre-commit'
        pre_commit_content = '''#!/bin/bash
# Law Agent pre-commit hook
echo "🔍 Running pre-commit checks..."

# Run frontend linting
cd law-agent-frontend
npm run lint
if [ $? -ne 0 ]; then
    echo "❌ Frontend linting failed"
    exit 1
fi

# Run backend linting
cd ..
python -m flake8 --max-line-length=100 *.py
if [ $? -ne 0 ]; then
    echo "❌ Backend linting failed"
    exit 1
fi

echo "✅ Pre-commit checks passed"
'''
        
        try:
            with open(pre_commit_hook, 'w') as f:
                f.write(pre_commit_content)
            
            # Make executable (Unix-like systems)
            if os.name != 'nt':
                os.chmod(pre_commit_hook, 0o755)
            
            self.print_success("Git pre-commit hook installed")
        except Exception as e:
            self.print_error(f"Failed to install Git hook: {e}")
    
    def setup_environment_files(self):
        """Setup environment configuration files"""
        self.print_status("Setting up environment files...")
        
        # Create environments directory
        env_dir = self.project_root / 'environments'
        env_dir.mkdir(exist_ok=True)
        
        # Check if environment files exist
        env_files = ['.env.development', '.env.staging', '.env.production']
        
        for env_file in env_files:
            env_path = env_dir / env_file
            if env_path.exists():
                self.print_success(f"Environment file exists: {env_file}")
            else:
                self.print_error(f"Environment file missing: {env_file}")
        
        # Create .env from example if it doesn't exist
        env_example = self.project_root / '.env.example'
        env_file = self.project_root / '.env'
        
        if env_example.exists() and not env_file.exists():
            try:
                shutil.copy(env_example, env_file)
                self.print_success("Created .env from .env.example")
                self.print_warning("Please edit .env with your actual configuration values")
            except Exception as e:
                self.print_error(f"Failed to create .env: {e}")
    
    def setup_docker_config(self):
        """Setup Docker configuration"""
        self.print_status("Setting up Docker configuration...")
        
        # Check Docker files
        docker_files = [
            'docker/Dockerfile.api',
            'docker/Dockerfile.analytics', 
            'docker/Dockerfile.documents',
            'docker-compose.yml'
        ]
        
        for docker_file in docker_files:
            docker_path = self.project_root / docker_file
            if docker_path.exists():
                self.print_success(f"Docker file exists: {docker_file}")
            else:
                self.print_error(f"Docker file missing: {docker_file}")
        
        # Test Docker Compose syntax
        try:
            result = subprocess.run(['docker-compose', 'config'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.returncode == 0:
                self.print_success("Docker Compose configuration is valid")
            else:
                self.print_error(f"Docker Compose configuration error: {result.stderr}")
        except FileNotFoundError:
            self.print_warning("Docker Compose not available for validation")
    
    def setup_github_actions(self):
        """Setup GitHub Actions workflow"""
        self.print_status("Setting up GitHub Actions...")
        
        # Create .github/workflows directory
        workflows_dir = self.project_root / '.github' / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if workflow file exists
        workflow_file = workflows_dir / 'ci-cd.yml'
        if workflow_file.exists():
            self.print_success("GitHub Actions workflow exists")
            
            # Validate YAML syntax
            try:
                import yaml
                with open(workflow_file, 'r') as f:
                    yaml.safe_load(f)
                self.print_success("GitHub Actions workflow syntax is valid")
            except ImportError:
                self.print_warning("PyYAML not installed - cannot validate workflow syntax")
            except yaml.YAMLError as e:
                self.print_error(f"GitHub Actions workflow syntax error: {e}")
        else:
            self.print_error("GitHub Actions workflow missing")
    
    def setup_vercel_config(self):
        """Setup Vercel configuration"""
        self.print_status("Setting up Vercel configuration...")
        
        # Check Vercel config files
        vercel_files = ['vercel.json', 'law-agent-frontend/vercel.json']
        
        for vercel_file in vercel_files:
            vercel_path = self.project_root / vercel_file
            if vercel_path.exists():
                self.print_success(f"Vercel config exists: {vercel_file}")
                
                # Validate JSON syntax
                try:
                    with open(vercel_path, 'r') as f:
                        json.load(f)
                    self.print_success(f"Vercel config syntax is valid: {vercel_file}")
                except json.JSONDecodeError as e:
                    self.print_error(f"Vercel config syntax error in {vercel_file}: {e}")
            else:
                self.print_error(f"Vercel config missing: {vercel_file}")
    
    def setup_supabase_config(self):
        """Setup Supabase configuration"""
        self.print_status("Setting up Supabase configuration...")
        
        # Check Supabase files
        supabase_files = [
            'supabase/migrations/001_initial_schema.sql',
            'law-agent-frontend/src/services/authService.ts'
        ]
        
        for supabase_file in supabase_files:
            supabase_path = self.project_root / supabase_file
            if supabase_path.exists():
                self.print_success(f"Supabase file exists: {supabase_file}")
            else:
                self.print_error(f"Supabase file missing: {supabase_file}")
    
    def setup_deployment_scripts(self):
        """Setup deployment scripts"""
        self.print_status("Setting up deployment scripts...")
        
        # Create scripts directory
        scripts_dir = self.project_root / 'scripts'
        scripts_dir.mkdir(exist_ok=True)
        
        # Check deployment scripts
        script_files = ['deploy.sh', 'test-deployment.sh']
        
        for script_file in script_files:
            script_path = scripts_dir / script_file
            if script_path.exists():
                self.print_success(f"Deployment script exists: {script_file}")
                
                # Make executable on Unix-like systems
                if os.name != 'nt':
                    try:
                        os.chmod(script_path, 0o755)
                        self.print_success(f"Made script executable: {script_file}")
                    except Exception as e:
                        self.print_warning(f"Could not make script executable: {e}")
            else:
                self.print_error(f"Deployment script missing: {script_file}")
    
    def test_frontend_build(self):
        """Test frontend build process"""
        self.print_status("Testing frontend build...")
        
        frontend_dir = self.project_root / 'law-agent-frontend'
        
        if not frontend_dir.exists():
            self.print_error("Frontend directory not found")
            return
        
        # Check package.json
        package_json = frontend_dir / 'package.json'
        if package_json.exists():
            self.print_success("Frontend package.json exists")
        else:
            self.print_error("Frontend package.json missing")
            return
        
        # Test npm install
        try:
            self.print_status("Installing frontend dependencies...")
            result = subprocess.run(['npm', 'ci'], cwd=frontend_dir, 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.print_success("Frontend dependencies installed successfully")
            else:
                self.print_error(f"Frontend dependency installation failed: {result.stderr}")
                return
        except subprocess.TimeoutExpired:
            self.print_error("Frontend dependency installation timed out")
            return
        except FileNotFoundError:
            self.print_error("npm not found - please install Node.js")
            return
        
        # Test build
        try:
            self.print_status("Testing frontend build...")
            result = subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir,
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.print_success("Frontend build successful")
                
                # Check build output
                build_dir = frontend_dir / 'build'
                if build_dir.exists():
                    self.print_success("Frontend build directory created")
                else:
                    self.print_error("Frontend build directory not found")
            else:
                self.print_error(f"Frontend build failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.print_error("Frontend build timed out")
        except Exception as e:
            self.print_error(f"Frontend build error: {e}")
    
    def generate_deployment_checklist(self):
        """Generate deployment checklist"""
        self.print_status("Generating deployment checklist...")
        
        checklist = """
# 🚀 Law Agent Deployment Checklist

## Pre-Deployment Setup
- [ ] Supabase project created and configured
- [ ] Environment variables configured in all environments
- [ ] GitHub repository secrets configured
- [ ] Vercel project connected to GitHub repository
- [ ] Docker Hub account and repositories created
- [ ] Domain names configured (if using custom domains)

## Environment Configuration
- [ ] Development environment tested locally
- [ ] Staging environment configured and accessible
- [ ] Production environment configured with proper security
- [ ] Database migrations ready and tested
- [ ] SSL certificates configured for production

## Security Configuration
- [ ] JWT secrets generated and configured
- [ ] API keys secured in environment variables
- [ ] CORS origins properly configured
- [ ] Security headers configured in Vercel
- [ ] Rate limiting configured for APIs

## Testing
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Frontend build successful
- [ ] Backend APIs responding to health checks
- [ ] Authentication flow tested
- [ ] Document upload and processing tested
- [ ] Analytics dashboard accessible

## Deployment
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Deploy to production
- [ ] Verify all services are running
- [ ] Test critical user flows
- [ ] Monitor for errors and performance issues

## Post-Deployment
- [ ] Set up monitoring alerts
- [ ] Configure backup schedules
- [ ] Document rollback procedures
- [ ] Train team on deployment process
- [ ] Schedule regular security updates

## Emergency Contacts
- [ ] DevOps team contact information
- [ ] Hosting provider support contacts
- [ ] Database administrator contacts
- [ ] Security team contacts
"""
        
        checklist_file = self.project_root / 'DEPLOYMENT_CHECKLIST.md'
        try:
            with open(checklist_file, 'w') as f:
                f.write(checklist)
            self.print_success("Deployment checklist generated")
        except Exception as e:
            self.print_error(f"Failed to generate checklist: {e}")
    
    def run_setup(self):
        """Run complete deployment setup"""
        print("🚀 Law Agent Deployment Setup")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            self.print_error("Please install missing dependencies before continuing")
            return False
        
        # Run setup steps
        self.setup_git_hooks()
        self.setup_environment_files()
        self.setup_docker_config()
        self.setup_github_actions()
        self.setup_vercel_config()
        self.setup_supabase_config()
        self.setup_deployment_scripts()
        self.test_frontend_build()
        self.generate_deployment_checklist()
        
        # Summary
        print("\n📊 Setup Summary")
        print("=" * 50)
        print(f"✅ Successful steps: {self.success_count}")
        print(f"❌ Failed steps: {self.error_count}")
        
        if self.error_count == 0:
            print("\n🎉 Deployment setup completed successfully!")
            print("📋 Next steps:")
            print("1. Review and edit environment files with your actual values")
            print("2. Set up Supabase project and configure authentication")
            print("3. Configure GitHub repository secrets")
            print("4. Run deployment test: python scripts/test-deployment.sh")
            print("5. Deploy to staging: ./scripts/deploy.sh -e staging")
            return True
        else:
            print(f"\n⚠️ Setup completed with {self.error_count} errors")
            print("Please resolve the errors before proceeding with deployment")
            return False

def main():
    """Main function"""
    setup = DeploymentSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
