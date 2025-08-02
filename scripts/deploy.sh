#!/bin/bash

# Law Agent Deployment Script
# Automated deployment for different environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="staging"
SKIP_TESTS=false
SKIP_BUILD=false
FORCE_DEPLOY=false
DRY_RUN=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Target environment (development|staging|production)"
    echo "  -s, --skip-tests        Skip running tests"
    echo "  -b, --skip-build        Skip building Docker images"
    echo "  -f, --force             Force deployment without confirmation"
    echo "  -d, --dry-run           Show what would be deployed without actually deploying"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e staging                    # Deploy to staging"
    echo "  $0 -e production -f              # Force deploy to production"
    echo "  $0 -e staging --skip-tests       # Deploy to staging without tests"
    echo "  $0 -d                            # Dry run for staging"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        -b|--skip-build)
            SKIP_BUILD=true
            shift
            ;;
        -f|--force)
            FORCE_DEPLOY=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Valid environments: development, staging, production"
    exit 1
fi

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    local missing_deps=()
    
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("docker-compose")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All dependencies are installed"
}

# Load environment variables
load_environment() {
    print_status "Loading environment configuration for: $ENVIRONMENT"
    
    local env_file="environments/.env.$ENVIRONMENT"
    
    if [ ! -f "$env_file" ]; then
        print_error "Environment file not found: $env_file"
        exit 1
    fi
    
    # Export environment variables
    set -a
    source "$env_file"
    set +a
    
    print_success "Environment configuration loaded"
}

# Run tests
run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        print_warning "Skipping tests as requested"
        return 0
    fi
    
    print_status "Running tests..."
    
    # Frontend tests
    print_status "Running frontend tests..."
    cd law-agent-frontend
    npm ci
    npm run test -- --coverage --watchAll=false
    cd ..
    
    # Backend tests
    print_status "Running backend tests..."
    python -m pytest --cov=. --cov-report=xml
    
    # Analytics tests
    print_status "Running analytics tests..."
    python test_analytics_system.py
    
    print_success "All tests passed"
}

# Build Docker images
build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        print_warning "Skipping Docker build as requested"
        return 0
    fi
    
    print_status "Building Docker images for $ENVIRONMENT..."
    
    # Build main API
    print_status "Building Law Agent API..."
    docker build -f docker/Dockerfile.api -t law-agent-api:$ENVIRONMENT .
    
    # Build analytics API
    print_status "Building Analytics API..."
    docker build -f docker/Dockerfile.analytics -t law-agent-analytics:$ENVIRONMENT .
    
    # Build document API
    print_status "Building Document API..."
    docker build -f docker/Dockerfile.documents -t law-agent-documents:$ENVIRONMENT .
    
    print_success "Docker images built successfully"
}

# Deploy to environment
deploy_to_environment() {
    print_status "Deploying to $ENVIRONMENT environment..."
    
    if [ "$DRY_RUN" = true ]; then
        print_warning "DRY RUN MODE - No actual deployment will occur"
        print_status "Would deploy the following:"
        print_status "  - Environment: $ENVIRONMENT"
        print_status "  - Docker images: law-agent-api:$ENVIRONMENT, law-agent-analytics:$ENVIRONMENT, law-agent-documents:$ENVIRONMENT"
        print_status "  - Configuration: environments/.env.$ENVIRONMENT"
        return 0
    fi
    
    case $ENVIRONMENT in
        development)
            deploy_development
            ;;
        staging)
            deploy_staging
            ;;
        production)
            deploy_production
            ;;
    esac
}

# Deploy to development
deploy_development() {
    print_status "Deploying to development environment..."
    
    # Use local docker-compose
    docker-compose -f docker-compose.yml --env-file environments/.env.development up -d
    
    print_success "Development deployment completed"
}

# Deploy to staging
deploy_staging() {
    print_status "Deploying to staging environment..."
    
    # Push images to registry
    docker tag law-agent-api:$ENVIRONMENT $DOCKER_REGISTRY/law-agent-api:$ENVIRONMENT
    docker tag law-agent-analytics:$ENVIRONMENT $DOCKER_REGISTRY/law-agent-analytics:$ENVIRONMENT
    docker tag law-agent-documents:$ENVIRONMENT $DOCKER_REGISTRY/law-agent-documents:$ENVIRONMENT
    
    docker push $DOCKER_REGISTRY/law-agent-api:$ENVIRONMENT
    docker push $DOCKER_REGISTRY/law-agent-analytics:$ENVIRONMENT
    docker push $DOCKER_REGISTRY/law-agent-documents:$ENVIRONMENT
    
    # Deploy to staging server
    if [ -n "$STAGING_HOST" ]; then
        print_status "Deploying to staging server: $STAGING_HOST"
        
        # Copy docker-compose file and environment
        scp docker-compose.staging.yml $STAGING_USER@$STAGING_HOST:/opt/law-agent/
        scp environments/.env.staging $STAGING_USER@$STAGING_HOST:/opt/law-agent/.env
        
        # Deploy on remote server
        ssh $STAGING_USER@$STAGING_HOST "cd /opt/law-agent && docker-compose -f docker-compose.staging.yml pull && docker-compose -f docker-compose.staging.yml up -d"
    fi
    
    print_success "Staging deployment completed"
}

# Deploy to production
deploy_production() {
    print_status "Deploying to production environment..."
    
    # Extra confirmation for production
    if [ "$FORCE_DEPLOY" != true ]; then
        print_warning "You are about to deploy to PRODUCTION!"
        read -p "Are you sure you want to continue? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            print_error "Production deployment cancelled"
            exit 1
        fi
    fi
    
    # Push images to registry
    docker tag law-agent-api:$ENVIRONMENT $DOCKER_REGISTRY/law-agent-api:latest
    docker tag law-agent-analytics:$ENVIRONMENT $DOCKER_REGISTRY/law-agent-analytics:latest
    docker tag law-agent-documents:$ENVIRONMENT $DOCKER_REGISTRY/law-agent-documents:latest
    
    docker push $DOCKER_REGISTRY/law-agent-api:latest
    docker push $DOCKER_REGISTRY/law-agent-analytics:latest
    docker push $DOCKER_REGISTRY/law-agent-documents:latest
    
    # Deploy to production server
    if [ -n "$PRODUCTION_HOST" ]; then
        print_status "Deploying to production server: $PRODUCTION_HOST"
        
        # Copy docker-compose file and environment
        scp docker-compose.production.yml $PRODUCTION_USER@$PRODUCTION_HOST:/opt/law-agent/
        scp environments/.env.production $PRODUCTION_USER@$PRODUCTION_HOST:/opt/law-agent/.env
        
        # Deploy on remote server with zero-downtime
        ssh $PRODUCTION_USER@$PRODUCTION_HOST "cd /opt/law-agent && docker-compose -f docker-compose.production.yml pull && docker-compose -f docker-compose.production.yml up -d"
    fi
    
    print_success "Production deployment completed"
}

# Health check
health_check() {
    print_status "Running health checks..."
    
    local api_url
    case $ENVIRONMENT in
        development)
            api_url="http://localhost:8000"
            ;;
        staging)
            api_url="$STAGING_API_URL"
            ;;
        production)
            api_url="$PRODUCTION_API_URL"
            ;;
    esac
    
    # Wait for services to start
    sleep 30
    
    # Check main API
    if curl -f "$api_url/health" > /dev/null 2>&1; then
        print_success "Main API health check passed"
    else
        print_error "Main API health check failed"
        return 1
    fi
    
    # Check analytics API
    if curl -f "${api_url/8000/8002}/health" > /dev/null 2>&1; then
        print_success "Analytics API health check passed"
    else
        print_error "Analytics API health check failed"
        return 1
    fi
    
    # Check document API
    if curl -f "${api_url/8000/8001}/health" > /dev/null 2>&1; then
        print_success "Document API health check passed"
    else
        print_error "Document API health check failed"
        return 1
    fi
    
    print_success "All health checks passed"
}

# Main deployment flow
main() {
    print_status "Starting Law Agent deployment..."
    print_status "Environment: $ENVIRONMENT"
    print_status "Skip tests: $SKIP_TESTS"
    print_status "Skip build: $SKIP_BUILD"
    print_status "Force deploy: $FORCE_DEPLOY"
    print_status "Dry run: $DRY_RUN"
    echo ""
    
    # Check dependencies
    check_dependencies
    
    # Load environment
    load_environment
    
    # Run tests
    run_tests
    
    # Build images
    build_images
    
    # Deploy
    deploy_to_environment
    
    # Health check
    if [ "$DRY_RUN" != true ]; then
        health_check
    fi
    
    print_success "Deployment completed successfully!"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        print_success "🚀 Law Agent is now live in production!"
        print_status "Frontend: $FRONTEND_URL"
        print_status "API: $PRODUCTION_API_URL"
    fi
}

# Run main function
main "$@"
