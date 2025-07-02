#!/bin/bash

# NeuraRoute Startup Script
# This script starts all services and performs health checks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f env.example ]; then
            cp env.example .env
            print_success "Created .env file from template"
            print_warning "Please update .env file with your API keys and configuration"
        else
            print_error "env.example not found. Please create .env file manually."
            exit 1
        fi
    else
        print_success ".env file found"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p backups
    mkdir -p frontend/build
    print_success "Directories created"
}

# Function to stop existing containers
stop_containers() {
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans
    print_success "Existing containers stopped"
}

# Function to start services
start_services() {
    print_status "Starting NeuraRoute services..."
    
    # Start database services first
    print_status "Starting database services..."
    docker-compose up -d postgres redis
    
    # Wait for databases to be ready
    print_status "Waiting for databases to be ready..."
    sleep 10
    
    # Check database health
    if docker-compose exec -T postgres pg_isready -U postgres -d neuraroute > /dev/null 2>&1; then
        print_success "PostgreSQL is ready"
    else
        print_error "PostgreSQL failed to start"
        exit 1
    fi
    
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is ready"
    else
        print_error "Redis failed to start"
        exit 1
    fi
    
    # Start backend
    print_status "Starting backend service..."
    docker-compose up -d backend
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    sleep 15
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is ready"
    else
        print_warning "Backend health check failed, but continuing..."
    fi
    
    # Start frontend
    print_status "Starting frontend service..."
    docker-compose up -d frontend
    
    # Wait for frontend to be ready
    print_status "Waiting for frontend to be ready..."
    sleep 10
    
    print_success "All services started"
}

# Function to perform health checks
health_check() {
    print_status "Performing health checks..."
    
    # Check if all containers are running
    if docker-compose ps | grep -q "Up"; then
        print_success "All containers are running"
    else
        print_error "Some containers are not running"
        docker-compose ps
        exit 1
    fi
    
    # Check API endpoints
    print_status "Checking API endpoints..."
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API is responding"
    else
        print_warning "Backend API health check failed"
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend is responding"
    else
        print_warning "Frontend health check failed"
    fi
    
    print_success "Health checks completed"
}

# Function to show status
show_status() {
    print_status "NeuraRoute System Status:"
    echo ""
    echo "Services:"
    docker-compose ps
    echo ""
    echo "Access URLs:"
    echo "  Frontend:     http://localhost:3000"
    echo "  Backend API:  http://localhost:8000"
    echo "  API Docs:     http://localhost:8000/docs"
    echo "  Health Check: http://localhost:8000/health"
    echo ""
    echo "Optional Tools (use --tools flag to start):"
    echo "  pgAdmin:      http://localhost:5050 (admin@neuraroute.com / admin123)"
    echo "  Redis Commander: http://localhost:8081"
    echo ""
    print_success "NeuraRoute is ready!"
}

# Function to start optional tools
start_tools() {
    print_status "Starting optional tools..."
    docker-compose --profile tools up -d
    print_success "Optional tools started"
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs..."
    docker-compose logs --tail=50
}

# Function to show help
show_help() {
    echo "NeuraRoute Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Show this help message"
    echo "  --tools        Start optional tools (pgAdmin, Redis Commander)"
    echo "  --logs         Show recent logs after startup"
    echo "  --stop         Stop all services"
    echo "  --restart      Restart all services"
    echo "  --status       Show current status"
    echo ""
    echo "Examples:"
    echo "  $0              Start all services"
    echo "  $0 --tools      Start services with optional tools"
    echo "  $0 --logs       Start services and show logs"
    echo "  $0 --stop       Stop all services"
}

# Main script logic
main() {
    case "${1:-}" in
        --help|-h)
            show_help
            exit 0
            ;;
        --stop)
            print_status "Stopping NeuraRoute services..."
            docker-compose down
            print_success "Services stopped"
            exit 0
            ;;
        --restart)
            print_status "Restarting NeuraRoute services..."
            docker-compose down
            sleep 5
            ;;
        --status)
            show_status
            exit 0
            ;;
        --tools)
            TOOLS=true
            ;;
        --logs)
            LOGS=true
            ;;
        "")
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    
    print_status "Starting NeuraRoute AI-Native Hyperlocal Logistics System..."
    echo ""
    
    # Perform checks and startup
    check_docker
    check_env
    create_directories
    stop_containers
    start_services
    
    # Start optional tools if requested
    if [ "${TOOLS:-false}" = true ]; then
        start_tools
    fi
    
    # Perform health checks
    health_check
    
    # Show status
    show_status
    
    # Show logs if requested
    if [ "${LOGS:-false}" = true ]; then
        echo ""
        show_logs
    fi
    
    echo ""
    print_success "NeuraRoute startup completed successfully!"
}

# Run main function with all arguments
main "$@" 