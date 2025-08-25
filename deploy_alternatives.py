#!/usr/bin/env python3
"""
Law Agent Frontend - Alternative Deployment Options
Quick setup scripts for different platforms
"""

import os
import json
from pathlib import Path

class AlternativeDeployments:
    """Setup deployment configurations for various platforms."""
    
    def __init__(self):
        self.frontend_path = Path("law-agent-frontend")
    
    def setup_netlify(self):
        """Setup Netlify deployment."""
        print("🟢 Setting up Netlify deployment...")
        
        # Create netlify.toml
        netlify_config = """[build]
  base = "law-agent-frontend"
  publish = "build"
  command = "npm run build"

[build.environment]
  REACT_APP_API_URL = "http://localhost:8000"
  REACT_APP_ENVIRONMENT = "production"
  REACT_APP_ENABLE_ANALYTICS = "true"
  REACT_APP_ENABLE_DOCUMENT_UPLOAD = "true"
  REACT_APP_ENABLE_3D_VISUALIZATION = "true"
  CI = "false"
  GENERATE_SOURCEMAP = "false"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
"""
        
        with open("netlify.toml", "w") as f:
            f.write(netlify_config)
        
        print("✅ netlify.toml created")
        print("📝 Next steps:")
        print("1. Go to https://netlify.com/")
        print("2. Click 'Add new site' → 'Import from Git'")
        print("3. Select your repository")
        print("4. Deploy!")
    
    def setup_github_pages(self):
        """Setup GitHub Pages deployment."""
        print("🔵 Setting up GitHub Pages deployment...")
        
        package_json_path = self.frontend_path / "package.json"
        
        if package_json_path.exists():
            with open(package_json_path, "r") as f:
                package_data = json.load(f)
            
            # Add homepage and deploy scripts
            package_data["homepage"] = "https://yourusername.github.io/law_agent"
            
            if "scripts" not in package_data:
                package_data["scripts"] = {}
            
            package_data["scripts"]["predeploy"] = "npm run build"
            package_data["scripts"]["deploy"] = "gh-pages -d build"
            
            # Add gh-pages as dev dependency
            if "devDependencies" not in package_data:
                package_data["devDependencies"] = {}
            
            package_data["devDependencies"]["gh-pages"] = "^6.0.0"
            
            with open(package_json_path, "w") as f:
                json.dump(package_data, f, indent=2)
            
            print("✅ package.json updated")
            print("📝 Next steps:")
            print("1. cd law-agent-frontend")
            print("2. npm install")
            print("3. Update homepage URL in package.json")
            print("4. npm run deploy")
        else:
            print("❌ package.json not found")
    
    def setup_firebase(self):
        """Setup Firebase hosting."""
        print("🟠 Setting up Firebase hosting...")
        
        # Create firebase.json
        firebase_config = {
            "hosting": {
                "public": "law-agent-frontend/build",
                "ignore": [
                    "firebase.json",
                    "**/.*",
                    "**/node_modules/**"
                ],
                "rewrites": [
                    {
                        "source": "**",
                        "destination": "/index.html"
                    }
                ],
                "headers": [
                    {
                        "source": "/static/**",
                        "headers": [
                            {
                                "key": "Cache-Control",
                                "value": "public, max-age=31536000, immutable"
                            }
                        ]
                    }
                ]
            }
        }
        
        with open("firebase.json", "w") as f:
            json.dump(firebase_config, f, indent=2)
        
        # Create .firebaserc
        firebaserc = {
            "projects": {
                "default": "your-project-id"
            }
        }
        
        with open(".firebaserc", "w") as f:
            json.dump(firebaserc, f, indent=2)
        
        print("✅ firebase.json and .firebaserc created")
        print("📝 Next steps:")
        print("1. Install: npm install -g firebase-tools")
        print("2. Login: firebase login")
        print("3. Create project: firebase projects:create your-project-id")
        print("4. Update .firebaserc with your project ID")
        print("5. Build: cd law-agent-frontend && npm run build")
        print("6. Deploy: firebase deploy")
    
    def setup_surge(self):
        """Setup Surge.sh deployment."""
        print("🟣 Setting up Surge.sh deployment...")
        
        # Create CNAME file for custom domain
        cname_content = "your-app-name.surge.sh"
        
        cname_path = self.frontend_path / "public" / "CNAME"
        cname_path.write_text(cname_content)
        
        # Create surge deployment script
        deploy_script = """#!/bin/bash
# Surge.sh deployment script for Law Agent Frontend

echo "🟣 Deploying to Surge.sh..."

# Navigate to frontend
cd law-agent-frontend

# Install dependencies
npm install

# Build the app
npm run build

# Deploy to surge
cd build
surge --domain your-app-name.surge.sh

echo "✅ Deployed to https://your-app-name.surge.sh"
"""
        
        with open("deploy-surge.sh", "w") as f:
            f.write(deploy_script)
        
        os.chmod("deploy-surge.sh", 0o755)
        
        print("✅ Surge deployment configured")
        print("📝 Next steps:")
        print("1. Install: npm install -g surge")
        print("2. Update domain in CNAME and deploy script")
        print("3. Run: ./deploy-surge.sh")
    
    def create_deployment_comparison(self):
        """Create deployment comparison guide."""
        comparison = """# 🚀 Frontend Deployment Comparison

## 📊 Platform Comparison

| Platform | Free Tier | Bandwidth | Build Time | Ease | Custom Domain |
|----------|-----------|-----------|------------|------|---------------|
| **Vercel** | ✅ 100GB | 100GB/month | Fast | ⭐⭐⭐⭐⭐ | ✅ Free |
| **Netlify** | ✅ 100GB | 100GB/month | Fast | ⭐⭐⭐⭐⭐ | ✅ Free |
| **GitHub Pages** | ✅ Unlimited | Unlimited | Medium | ⭐⭐⭐⭐ | ✅ Free |
| **Firebase** | ✅ 10GB | 10GB/month | Fast | ⭐⭐⭐⭐ | ✅ Free |
| **Surge.sh** | ✅ Basic | Unlimited | Fast | ⭐⭐⭐⭐⭐ | ✅ Paid |
| **Render** | ✅ 100GB | 100GB/month | Medium | ⭐⭐⭐⭐ | ✅ Free |

## 🎯 Best Choice For:

- **🥇 Easiest Setup**: Netlify or Surge.sh
- **🥈 Best Free**: GitHub Pages (unlimited)
- **🥉 Best Performance**: Vercel or Firebase
- **🏆 Best for Beginners**: Netlify
- **💰 Most Cost-Effective**: GitHub Pages

## 🚀 Quick Commands:

### Netlify
```bash
# Drag & drop build folder to netlify.com
npm run build
# Then drag 'build' folder to Netlify dashboard
```

### GitHub Pages
```bash
npm install --save-dev gh-pages
npm run deploy
```

### Firebase
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
firebase deploy
```

### Surge.sh
```bash
npm install -g surge
npm run build
cd build && surge
```

Choose the platform that best fits your needs! 🎉
"""
        
        with open("DEPLOYMENT_COMPARISON.md", "w") as f:
            f.write(comparison)
        
        print("✅ Deployment comparison guide created")

def main():
    """Main function to setup all deployment options."""
    deployer = AlternativeDeployments()
    
    print("🚀 LAW AGENT FRONTEND - DEPLOYMENT ALTERNATIVES")
    print("=" * 60)
    
    print("\n1. Setting up Netlify...")
    deployer.setup_netlify()
    
    print("\n2. Setting up GitHub Pages...")
    deployer.setup_github_pages()
    
    print("\n3. Setting up Firebase...")
    deployer.setup_firebase()
    
    print("\n4. Setting up Surge.sh...")
    deployer.setup_surge()
    
    print("\n5. Creating comparison guide...")
    deployer.create_deployment_comparison()
    
    print("\n🎉 All deployment options configured!")
    print("📚 Check the generated files for setup instructions")
    print("🎯 Choose the platform that best fits your needs!")

if __name__ == "__main__":
    main()
