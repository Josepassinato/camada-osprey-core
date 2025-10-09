#!/bin/bash

# OSPREY Immigration Platform Deployment Script
# This script handles deployment to different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default values
ENVIRONMENT=""
DRY_RUN=false
SKIP_TESTS=false
SKIP_BUILD=false
FORCE_DEPLOY=false

# Functions
print_usage() {
    echo "Usage: $0 [OPTIONS] ENVIRONMENT"
    echo ""
    echo "ENVIRONMENT:"
    echo "  development    Deploy to development environment"
    echo "  staging        Deploy to staging environment"
    echo "  production     Deploy to production environment"
    echo ""
    echo "OPTIONS:"
    echo "  -d, --dry-run       Show what would be deployed without actually deploying"
    echo "  -s, --skip-tests    Skip running tests before deployment"
    echo "  -b, --skip-build    Skip building Docker images"
    echo "  -f, --force         Force deployment without confirmation (production only)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 development"
    echo "  $0 --dry-run production"
    echo "  $0 --skip-tests staging"
}

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

confirm() {
    if [ "$FORCE_DEPLOY" = true ]; then
        return 0
    fi
    
    read -p "Are you sure you want to deploy to $ENVIRONMENT? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Deployment cancelled by user"
    fi
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running"
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not available"
    fi
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        warning ".env file not found. Creating from .env.example..."
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            warning "Please update .env file with your configuration before deploying"
        else
            error ".env.example file not found"
        fi
    fi
    
    success "Prerequisites check passed"
}

run_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        warning "Skipping tests as requested"
        return 0
    fi
    
    log "Running tests..."
    
    # Backend tests
    log "Running backend tests..."
    cd "$PROJECT_ROOT/backend"
    if command -v python3 &> /dev/null; then
        python3 -m pytest --tb=short || error "Backend tests failed"
    else
        warning "Python3 not found, skipping backend tests"
    fi
    
    # Frontend tests
    log "Running frontend tests..."
    cd "$PROJECT_ROOT/frontend"
    if command -v yarn &> /dev/null; then
        yarn test --watchAll=false || error "Frontend tests failed"
    else
        warning "Yarn not found, skipping frontend tests"
    fi
    
    cd "$PROJECT_ROOT"
    success "Tests completed successfully"
}

build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        warning "Skipping build as requested"
        return 0
    fi
    
    log "Building Docker images..."
    
    # Build backend
    log "Building backend image..."
    docker build -t osprey-backend:$ENVIRONMENT ./backend
    
    # Build frontend
    log "Building frontend image..."
    docker build -t osprey-frontend:$ENVIRONMENT ./frontend
    
    success "Docker images built successfully"
}

deploy_development() {
    log "Deploying to development environment..."
    
    export COMPOSE_PROFILES="default"
    export ENVIRONMENT="development"
    
    if [ "$DRY_RUN" = true ]; then
        log "DRY RUN: Would execute: docker-compose up -d"
        return 0
    fi
    
    # Use docker-compose for development
    docker-compose down --remove-orphans
    docker-compose up -d
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Health checks
    check_service_health "http://localhost:8001/api/production/system/health" "Backend"
    check_service_health "http://localhost:3000" "Frontend"
    
    success "Development deployment completed"
    log "Frontend: http://localhost:3000"
    log "Backend API: http://localhost:8001"
    log "MongoDB: mongodb://localhost:27017"
}

deploy_staging() {
    log "Deploying to staging environment..."
    
    export COMPOSE_PROFILES="default,monitoring"
    export ENVIRONMENT="staging"
    
    if [ "$DRY_RUN" = true ]; then
        log "DRY RUN: Would execute staging deployment commands"
        return 0
    fi
    
    # Deploy to staging (could be Docker Compose or Kubernetes)
    docker-compose -f docker-compose.yml -f docker-compose.staging.yml down --remove-orphans
    docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
    
    success "Staging deployment completed"
}

deploy_production() {
    log "Deploying to production environment..."
    
    # Extra confirmation for production
    warning "PRODUCTION DEPLOYMENT - This will affect live users!"
    confirm
    
    export COMPOSE_PROFILES="production,monitoring"
    export ENVIRONMENT="production"
    
    if [ "$DRY_RUN" = true ]; then
        log "DRY RUN: Would execute production deployment commands"
        return 0
    fi
    
    # Production deployment (typically Kubernetes)
    if command -v kubectl &> /dev/null; then
        log "Deploying to Kubernetes..."
        
        # Apply Kubernetes manifests
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/pvc.yaml
        kubectl apply -f k8s/deployment.yaml
        kubectl apply -f k8s/service.yaml
        kubectl apply -f k8s/ingress.yaml
        
        # Wait for rollout
        kubectl rollout status deployment/osprey-backend -n osprey-production
        kubectl rollout status deployment/osprey-frontend -n osprey-production
        
    else
        warning "kubectl not found, using Docker Compose for production"
        docker-compose -f docker-compose.yml -f docker-compose.production.yml down --remove-orphans
        docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
    fi
    
    success "Production deployment completed"
}

check_service_health() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    log "Checking health of $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            success "$service_name is healthy"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 5
        ((attempt++))
    done
    
    error "$service_name failed to become healthy"
}

cleanup() {
    log "Cleaning up..."
    # Add cleanup logic here
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            DRY_RUN=true
            shift
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
        -h|--help)
            print_usage
            exit 0
            ;;
        development|staging|production)
            ENVIRONMENT=$1
            shift
            ;;
        *)
            error "Unknown option: $1"
            ;;
    esac
done

# Validate environment
if [ -z "$ENVIRONMENT" ]; then
    error "Environment is required. Use --help for usage information."
fi

if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    error "Invalid environment: $ENVIRONMENT. Must be one of: development, staging, production"
fi

# Main execution
main() {
    log "Starting OSPREY deployment to $ENVIRONMENT..."
    
    if [ "$DRY_RUN" = true ]; then
        warning "DRY RUN MODE - No actual changes will be made"
    fi
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Execute deployment pipeline
    check_prerequisites
    run_tests
    build_images
    
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
    
    success "Deployment to $ENVIRONMENT completed successfully! 🚀"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        log "Don't forget to:"
        log "- Monitor the application logs"
        log "- Check metrics and alerts"
        log "- Notify the team about the deployment"
    fi
}

# Run main function
main "$@"