#!/bin/bash

# OSPREY Immigration Platform Setup Script
# This script sets up the development environment

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

# Functions
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

print_banner() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════╗"
    echo "║      OSPREY Immigration Platform     ║"
    echo "║         Development Setup            ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

check_system_requirements() {
    log "Checking system requirements..."
    
    # Check OS
    OS=$(uname -s)
    log "Operating System: $OS"
    
    # Check if running on supported OS
    if [[ "$OS" != "Linux" && "$OS" != "Darwin" ]]; then
        warning "This setup script is designed for Linux and macOS"
    fi
    
    # Check available memory
    if command -v free &> /dev/null; then
        MEMORY_GB=$(free -g | awk 'NR==2{printf "%.1f", $2}')
        log "Available Memory: ${MEMORY_GB}GB"
        
        if (( $(echo "$MEMORY_GB < 4" | bc -l) )); then
            warning "Recommended minimum memory is 4GB. Current: ${MEMORY_GB}GB"
        fi
    fi
    
    success "System requirements check completed"
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Git
    if ! command -v git &> /dev/null; then
        error "Git is required but not installed"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is required but not installed. Please install Docker from https://docs.docker.com/get-docker/"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is required but not installed"
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3.11+ is required but not installed"
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
    log "Python version: $PYTHON_VERSION"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js is required but not installed. Please install Node.js 18+"
    fi
    
    NODE_VERSION=$(node --version)
    log "Node.js version: $NODE_VERSION"
    
    # Check Yarn
    if ! command -v yarn &> /dev/null; then
        warning "Yarn not found. Installing yarn..."
        npm install -g yarn
    fi
    
    success "Prerequisites check passed"
}

setup_environment_files() {
    log "Setting up environment files..."
    
    cd "$PROJECT_ROOT"
    
    # Copy .env.example to .env if not exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            success "Created .env file from .env.example"
            warning "Please update .env file with your configuration"
        else
            error ".env.example file not found"
        fi
    else
        log ".env file already exists"
    fi
    
    # Setup backend .env
    if [ ! -f "backend/.env" ]; then
        cat > "backend/.env" << EOF
# Backend Environment Variables
MONGO_URL=mongodb://osprey_user:osprey_pass_2024@localhost:27017/osprey_immigration?authSource=osprey_immigration
JWT_SECRET=development-jwt-secret-change-in-production
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
ENVIRONMENT=development
DEBUG=true
EOF
        success "Created backend/.env file"
    fi
    
    # Setup frontend .env
    if [ ! -f "frontend/.env" ]; then
        cat > "frontend/.env" << EOF
# Frontend Environment Variables
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_ENVIRONMENT=development
EOF
        success "Created frontend/.env file"
    fi
    
    success "Environment files setup completed"
}

install_backend_dependencies() {
    log "Installing backend dependencies..."
    
    cd "$PROJECT_ROOT/backend"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        log "Installing Python packages..."
        pip install -r requirements.txt
        success "Backend dependencies installed"
    else
        warning "requirements.txt not found in backend directory"
    fi
    
    # Install development dependencies
    log "Installing development dependencies..."
    pip install pytest pytest-cov pytest-asyncio black flake8 mypy
    
    success "Backend dependencies installation completed"
}

install_frontend_dependencies() {
    log "Installing frontend dependencies..."
    
    cd "$PROJECT_ROOT/frontend"
    
    if [ -f "package.json" ]; then
        log "Installing Node.js packages..."
        yarn install --frozen-lockfile
        success "Frontend dependencies installed"
    else
        warning "package.json not found in frontend directory"
    fi
    
    success "Frontend dependencies installation completed"
}

setup_database() {
    log "Setting up database..."
    
    cd "$PROJECT_ROOT"
    
    # Check if MongoDB is running via Docker
    if docker ps | grep -q "osprey-mongodb"; then
        log "MongoDB container already running"
    else
        log "Starting MongoDB container..."
        docker-compose up -d mongodb
        
        # Wait for MongoDB to be ready
        log "Waiting for MongoDB to be ready..."
        sleep 10
        
        # Check if MongoDB is accessible
        for i in {1..30}; do
            if docker exec osprey-mongodb mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
                success "MongoDB is ready"
                break
            fi
            log "Waiting for MongoDB... (attempt $i/30)"
            sleep 2
        done
    fi
    
    success "Database setup completed"
}

create_directories() {
    log "Creating necessary directories..."
    
    cd "$PROJECT_ROOT"
    
    # Create directories
    mkdir -p logs
    mkdir -p uploads
    mkdir -p cache
    mkdir -p docs/generated
    mkdir -p nginx/ssl
    mkdir -p monitoring
    
    # Set permissions
    chmod 755 logs uploads cache
    
    success "Directories created"
}

generate_ssl_certificates() {
    log "Generating SSL certificates for development..."
    
    SSL_DIR="$PROJECT_ROOT/nginx/ssl"
    
    if [ ! -f "$SSL_DIR/cert.pem" ]; then
        # Generate self-signed certificate for development
        openssl req -x509 -newkey rsa:4096 -keyout "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem" -days 365 -nodes -subj "/C=US/ST=State/L=City/O=OSPREY/CN=localhost"
        success "SSL certificates generated"
    else
        log "SSL certificates already exist"
    fi
}

setup_git_hooks() {
    log "Setting up Git hooks..."
    
    cd "$PROJECT_ROOT"
    
    # Create pre-commit hook
    cat > ".git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook for OSPREY

# Run backend linting
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Running backend linting..."
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    black --check .
fi
cd ..

# Run frontend linting
cd frontend
if command -v yarn &> /dev/null && [ -f "package.json" ]; then
    echo "Running frontend linting..."
    yarn lint
fi
cd ..

echo "Pre-commit checks passed"
EOF
    
    chmod +x ".git/hooks/pre-commit"
    success "Git hooks setup completed"
}

run_initial_tests() {
    log "Running initial tests..."
    
    # Backend tests
    cd "$PROJECT_ROOT/backend"
    if [ -d "venv" ]; then
        source venv/bin/activate
        if command -v pytest &> /dev/null; then
            log "Running backend tests..."
            pytest --tb=short || warning "Some backend tests failed"
        fi
    fi
    
    # Frontend tests
    cd "$PROJECT_ROOT/frontend"
    if command -v yarn &> /dev/null && [ -f "package.json" ]; then
        log "Running frontend tests..."
        yarn test --watchAll=false || warning "Some frontend tests failed"
    fi
    
    success "Initial tests completed"
}

print_next_steps() {
    echo ""
    success "🎉 OSPREY development environment setup completed!"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Update your API keys in .env files:"
    echo "   - backend/.env: Add your OPENAI_API_KEY"
    echo "   - frontend/.env: Verify REACT_APP_BACKEND_URL"
    echo ""
    echo "2. Start the development environment:"
    echo -e "   ${GREEN}./scripts/deploy.sh development${NC}"
    echo ""
    echo "3. Access the application:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8001"
    echo "   - API Documentation: http://localhost:8001/docs"
    echo ""
    echo "4. Useful commands:"
    echo -e "   - View logs: ${GREEN}docker-compose logs -f${NC}"
    echo -e "   - Stop services: ${GREEN}docker-compose down${NC}"
    echo -e "   - Rebuild images: ${GREEN}docker-compose build${NC}"
    echo ""
    echo "📚 Documentation available in: docs/README.md"
    echo ""
}

main() {
    print_banner
    
    log "Starting OSPREY development environment setup..."
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Execute setup steps
    check_system_requirements
    check_prerequisites
    setup_environment_files
    create_directories
    install_backend_dependencies
    install_frontend_dependencies
    setup_database
    
    # Optional steps
    if command -v openssl &> /dev/null; then
        generate_ssl_certificates
    else
        warning "OpenSSL not found, skipping SSL certificate generation"
    fi
    
    setup_git_hooks
    run_initial_tests
    
    print_next_steps
}

# Run main function
main "$@"