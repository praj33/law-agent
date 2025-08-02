#!/bin/bash

# Law Agent Deployment Testing Script
# Comprehensive testing for deployment readiness

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((TESTS_PASSED++))
    ((TOTAL_TESTS++))
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((TESTS_FAILED++))
    ((TOTAL_TESTS++))
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Test environment setup
test_environment_setup() {
    print_status "Testing environment setup..."
    
    # Check if environment files exist
    if [ -f "environments/.env.development" ]; then
        print_success "Development environment file exists"
    else
        print_error "Development environment file missing"
    fi
    
    if [ -f "environments/.env.staging" ]; then
        print_success "Staging environment file exists"
    else
        print_error "Staging environment file missing"
    fi
    
    if [ -f "environments/.env.production" ]; then
        print_success "Production environment file exists"
    else
        print_error "Production environment file missing"
    fi
}

# Test Docker configuration
test_docker_config() {
    print_status "Testing Docker configuration..."
    
    # Check Dockerfiles
    if [ -f "docker/Dockerfile.api" ]; then
        print_success "API Dockerfile exists"
    else
        print_error "API Dockerfile missing"
    fi
    
    if [ -f "docker/Dockerfile.analytics" ]; then
        print_success "Analytics Dockerfile exists"
    else
        print_error "Analytics Dockerfile missing"
    fi
    
    if [ -f "docker/Dockerfile.documents" ]; then
        print_success "Documents Dockerfile exists"
    else
        print_error "Documents Dockerfile missing"
    fi
    
    # Check docker-compose files
    if [ -f "docker-compose.yml" ]; then
        print_success "Docker Compose file exists"
    else
        print_error "Docker Compose file missing"
    fi
    
    # Validate docker-compose syntax
    if docker-compose config > /dev/null 2>&1; then
        print_success "Docker Compose syntax is valid"
    else
        print_error "Docker Compose syntax is invalid"
    fi
}

# Test GitHub Actions workflow
test_github_actions() {
    print_status "Testing GitHub Actions workflow..."
    
    if [ -f ".github/workflows/ci-cd.yml" ]; then
        print_success "GitHub Actions workflow exists"
    else
        print_error "GitHub Actions workflow missing"
    fi
    
    # Check workflow syntax (basic YAML validation)
    if python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-cd.yml'))" 2>/dev/null; then
        print_success "GitHub Actions workflow syntax is valid"
    else
        print_error "GitHub Actions workflow syntax is invalid"
    fi
}

# Test Vercel configuration
test_vercel_config() {
    print_status "Testing Vercel configuration..."
    
    if [ -f "vercel.json" ]; then
        print_success "Root Vercel config exists"
    else
        print_error "Root Vercel config missing"
    fi
    
    if [ -f "law-agent-frontend/vercel.json" ]; then
        print_success "Frontend Vercel config exists"
    else
        print_error "Frontend Vercel config missing"
    fi
    
    # Validate JSON syntax
    if python -c "import json; json.load(open('vercel.json'))" 2>/dev/null; then
        print_success "Vercel JSON syntax is valid"
    else
        print_error "Vercel JSON syntax is invalid"
    fi
}

# Test Supabase configuration
test_supabase_config() {
    print_status "Testing Supabase configuration..."
    
    if [ -f "supabase/migrations/001_initial_schema.sql" ]; then
        print_success "Supabase migration exists"
    else
        print_error "Supabase migration missing"
    fi
    
    if [ -f "law-agent-frontend/src/services/authService.ts" ]; then
        print_success "Auth service exists"
    else
        print_error "Auth service missing"
    fi
}

# Test deployment scripts
test_deployment_scripts() {
    print_status "Testing deployment scripts..."
    
    if [ -f "scripts/deploy.sh" ]; then
        print_success "Deployment script exists"
        
        # Check if script is executable
        if [ -x "scripts/deploy.sh" ]; then
            print_success "Deployment script is executable"
        else
            print_error "Deployment script is not executable"
        fi
    else
        print_error "Deployment script missing"
    fi
    
    # Test script syntax
    if bash -n scripts/deploy.sh 2>/dev/null; then
        print_success "Deployment script syntax is valid"
    else
        print_error "Deployment script syntax is invalid"
    fi
}

# Test frontend build
test_frontend_build() {
    print_status "Testing frontend build..."
    
    cd law-agent-frontend
    
    # Check package.json
    if [ -f "package.json" ]; then
        print_success "Frontend package.json exists"
    else
        print_error "Frontend package.json missing"
        cd ..
        return
    fi
    
    # Install dependencies
    if npm ci > /dev/null 2>&1; then
        print_success "Frontend dependencies installed"
    else
        print_error "Frontend dependency installation failed"
        cd ..
        return
    fi
    
    # Run build
    if npm run build > /dev/null 2>&1; then
        print_success "Frontend build successful"
    else
        print_error "Frontend build failed"
    fi
    
    # Check build output
    if [ -d "build" ]; then
        print_success "Frontend build directory created"
    else
        print_error "Frontend build directory missing"
    fi
    
    cd ..
}

# Test backend dependencies
test_backend_dependencies() {
    print_status "Testing backend dependencies..."
    
    # Check requirements files
    if [ -f "requirements.txt" ]; then
        print_success "Main requirements file exists"
    else
        print_error "Main requirements file missing"
    fi
    
    if [ -f "requirements_document_processing.txt" ]; then
        print_success "Document processing requirements file exists"
    else
        print_error "Document processing requirements file missing"
    fi
    
    # Test Python syntax for main files
    local python_files=("law_agent_minimal.py" "analytics_api.py" "document_api.py" "analytics_collector.py")
    
    for file in "${python_files[@]}"; do
        if [ -f "$file" ]; then
            if python -m py_compile "$file" 2>/dev/null; then
                print_success "Python syntax valid: $file"
            else
                print_error "Python syntax invalid: $file"
            fi
        else
            print_error "Python file missing: $file"
        fi
    done
}

# Test API health endpoints
test_api_health() {
    print_status "Testing API health endpoints (if running)..."
    
    # Test main API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Main API health endpoint responding"
    else
        print_warning "Main API not running or health endpoint not responding"
    fi
    
    # Test analytics API
    if curl -f http://localhost:8002/health > /dev/null 2>&1; then
        print_success "Analytics API health endpoint responding"
    else
        print_warning "Analytics API not running or health endpoint not responding"
    fi
    
    # Test document API
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Document API health endpoint responding"
    else
        print_warning "Document API not running or health endpoint not responding"
    fi
}

# Test security configuration
test_security_config() {
    print_status "Testing security configuration..."
    
    # Check for security headers in Vercel config
    if grep -q "X-Content-Type-Options" vercel.json; then
        print_success "Security headers configured in Vercel"
    else
        print_error "Security headers missing in Vercel config"
    fi
    
    # Check for HTTPS enforcement
    if grep -q "FORCE_HTTPS" environments/.env.production; then
        print_success "HTTPS enforcement configured"
    else
        print_error "HTTPS enforcement not configured"
    fi
    
    # Check for secret management
    if grep -q "JWT_SECRET" environments/.env.example; then
        print_success "JWT secret configuration present"
    else
        print_error "JWT secret configuration missing"
    fi
}

# Test monitoring configuration
test_monitoring_config() {
    print_status "Testing monitoring configuration..."
    
    # Check for health check endpoints in code
    if grep -q "/health" law_agent_minimal.py; then
        print_success "Health check endpoint in main API"
    else
        print_error "Health check endpoint missing in main API"
    fi
    
    if grep -q "/health" analytics_api.py; then
        print_success "Health check endpoint in analytics API"
    else
        print_error "Health check endpoint missing in analytics API"
    fi
    
    # Check for monitoring tools in docker-compose
    if grep -q "prometheus" docker-compose.yml; then
        print_success "Prometheus monitoring configured"
    else
        print_error "Prometheus monitoring not configured"
    fi
    
    if grep -q "grafana" docker-compose.yml; then
        print_success "Grafana monitoring configured"
    else
        print_error "Grafana monitoring not configured"
    fi
}

# Test backup configuration
test_backup_config() {
    print_status "Testing backup configuration..."
    
    # Check for backup settings in environment files
    if grep -q "BACKUP_ENABLED" environments/.env.production; then
        print_success "Backup configuration present"
    else
        print_error "Backup configuration missing"
    fi
    
    # Check for database backup strategy
    if grep -q "BACKUP_S3_BUCKET" environments/.env.production; then
        print_success "S3 backup configuration present"
    else
        print_error "S3 backup configuration missing"
    fi
}

# Main test runner
run_all_tests() {
    print_status "Starting Law Agent Deployment Readiness Tests"
    echo "=" * 60
    
    test_environment_setup
    test_docker_config
    test_github_actions
    test_vercel_config
    test_supabase_config
    test_deployment_scripts
    test_frontend_build
    test_backend_dependencies
    test_api_health
    test_security_config
    test_monitoring_config
    test_backup_config
    
    echo ""
    print_status "Test Results Summary"
    echo "=" * 60
    print_success "Tests Passed: $TESTS_PASSED"
    if [ $TESTS_FAILED -gt 0 ]; then
        print_error "Tests Failed: $TESTS_FAILED"
    fi
    print_status "Total Tests: $TOTAL_TESTS"
    
    # Calculate success rate
    if [ $TOTAL_TESTS -gt 0 ]; then
        SUCCESS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
        print_status "Success Rate: $SUCCESS_RATE%"
        
        if [ $SUCCESS_RATE -ge 90 ]; then
            print_success "🎉 Deployment readiness: EXCELLENT ($SUCCESS_RATE%)"
            print_success "✅ Ready for production deployment!"
        elif [ $SUCCESS_RATE -ge 80 ]; then
            print_warning "⚠️ Deployment readiness: GOOD ($SUCCESS_RATE%)"
            print_warning "🔧 Address failed tests before production deployment"
        elif [ $SUCCESS_RATE -ge 70 ]; then
            print_warning "⚠️ Deployment readiness: FAIR ($SUCCESS_RATE%)"
            print_warning "🔧 Significant issues need to be resolved"
        else
            print_error "❌ Deployment readiness: POOR ($SUCCESS_RATE%)"
            print_error "🚫 NOT ready for deployment - critical issues present"
        fi
    fi
    
    echo ""
    print_status "Next Steps:"
    if [ $TESTS_FAILED -eq 0 ]; then
        print_status "1. Set up Supabase project and configure environment variables"
        print_status "2. Configure GitHub repository secrets for CI/CD"
        print_status "3. Deploy to staging: ./scripts/deploy.sh -e staging"
        print_status "4. Run integration tests on staging"
        print_status "5. Deploy to production: ./scripts/deploy.sh -e production"
    else
        print_status "1. Fix all failed tests"
        print_status "2. Re-run this test script"
        print_status "3. Proceed with deployment once all tests pass"
    fi
    
    # Exit with appropriate code
    if [ $TESTS_FAILED -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run all tests
run_all_tests
