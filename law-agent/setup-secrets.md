# GitHub Secrets Setup for Complete Deployment

## 🔐 Required Secrets

Go to your GitHub repository: **Settings > Secrets and variables > Actions > New repository secret**

### 1. Supabase Configuration
```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2. Vercel Configuration
```
VERCEL_TOKEN=your_vercel_token
VERCEL_ORG_ID=your_org_id
VERCEL_PROJECT_ID=your_project_id
```

**To get Vercel values:**
1. Go to Vercel Dashboard > Settings > Tokens > Create Token
2. Copy the token as `VERCEL_TOKEN`
3. Go to your project settings:
   - Project ID is in Settings > General
   - Org ID is in your account settings

### 3. Optional (for full CI/CD)
```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
```

## 🚀 Quick Setup Commands

### For Supabase:
1. Copy Project URL from Supabase Dashboard
2. Go to Settings > API
3. Copy "anon public" key and "service_role" key

### For Vercel:
1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Link project: `vercel link`
4. Get project info: `vercel project ls`

## ✅ Verification

After adding secrets, your GitHub Actions will:
1. ✅ Build and test the application
2. ✅ Deploy frontend to Vercel
3. ✅ Run security scans
4. ✅ Send deployment notifications

## 🔧 Environment Variables for Vercel

Add these in Vercel Dashboard > Project Settings > Environment Variables:

```
REACT_APP_SUPABASE_URL=https://your-project-id.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_ENVIRONMENT=production
```
