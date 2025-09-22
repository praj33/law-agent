# 🔐 GitHub Secrets Configuration for Law Agent CI/CD

This document outlines all the GitHub Secrets required for the advanced CI/CD pipeline to function properly.

## 📋 Required Secrets

### 🌐 Frontend Deployment (Vercel)
```
VERCEL_TOKEN=your_vercel_token_here
VERCEL_ORG_ID=your_vercel_org_id_here
VERCEL_PROJECT_ID=your_vercel_project_id_here
```

### 🗄️ Database & Backend Services (Supabase)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 🐳 Docker Registry
```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password_or_token
```

### ☁️ AWS (for Kubernetes deployments)
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
EKS_CLUSTER_NAME=law-agent-cluster
```

### 🌍 Environment URLs
```
# Staging Environment
STAGING_API_URL=https://staging-api.lawagent.dev
STAGING_ANALYTICS_URL=https://staging-analytics.lawagent.dev
STAGING_DOCUMENTS_URL=https://staging-docs.lawagent.dev

# Production Environment
PRODUCTION_API_URL=https://api.lawagent.dev
PRODUCTION_ANALYTICS_URL=https://analytics.lawagent.dev
PRODUCTION_DOCUMENTS_URL=https://docs.lawagent.dev
PRODUCTION_FRONTEND_URL=https://lawagent.dev

# React App URLs
REACT_APP_API_URL=https://api.lawagent.dev
REACT_APP_ANALYTICS_URL=https://analytics.lawagent.dev
REACT_APP_DOCUMENT_URL=https://docs.lawagent.dev
```

### 📊 Monitoring & Analytics
```
DATADOG_API_KEY=your_datadog_api_key
DATADOG_APP_KEY=your_datadog_app_key
CODECOV_TOKEN=your_codecov_token
```

### 📧 Notifications
```
# Email Notifications
EMAIL_USERNAME=your_gmail_address@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
NOTIFICATION_EMAIL=team@lawagent.dev

# Slack Notifications
SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### 🔒 SSH Keys (for server deployments)
```
STAGING_HOST=staging.lawagent.dev
STAGING_USER=deploy
STAGING_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
your_staging_ssh_private_key_here
-----END OPENSSH PRIVATE KEY-----

PRODUCTION_HOST=production.lawagent.dev
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
your_production_ssh_private_key_here
-----END OPENSSH PRIVATE KEY-----
```

## 🚀 Quick Setup Guide

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Get your URL and keys from Settings > API

### 2. Setup Vercel
1. Go to [vercel.com](https://vercel.com)
2. Create account and get your token from Settings > Tokens
3. Import your GitHub repository
4. Get Org ID and Project ID from project settings

### 3. Configure Docker Hub
1. Create account at [hub.docker.com](https://hub.docker.com)
2. Generate access token from Account Settings > Security

### 4. Setup Monitoring (Optional)
1. **Datadog**: Create account at [datadoghq.com](https://datadoghq.com)
2. **Codecov**: Connect your GitHub repo at [codecov.io](https://codecov.io)

### 5. Add Secrets to GitHub
1. Go to your repository on GitHub
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Add each secret from the list above

## 🔧 Environment-Specific Configuration

### Development/Testing
For development, you can use these minimal secrets:
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Production
All secrets listed above are required for full production deployment.

## 🛡️ Security Best Practices

1. **Never commit secrets to code**
2. **Use environment-specific keys**
3. **Rotate keys regularly**
4. **Use least-privilege access**
5. **Monitor secret usage**

## 🆘 Troubleshooting

### Pipeline Fails Due to Missing Secrets
- Check GitHub Actions logs for specific missing secrets
- Verify secret names match exactly (case-sensitive)
- Ensure secrets have proper permissions

### Deployment Issues
- Verify environment URLs are accessible
- Check SSH keys have proper permissions
- Ensure Docker credentials are valid

## 📞 Support

If you need help setting up any of these services:
1. Check the official documentation for each service
2. Review GitHub Actions logs for specific error messages
3. Ensure all secrets are properly configured

---

**🎉 Once all secrets are configured, your advanced CI/CD pipeline will be fully operational!**
