#!/bin/bash
# deploy.sh - Medical Referral Priority System Deployment Script

set -e

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="Medical Referral Priority System"

# Function to print colored output
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🏥 $1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        print_error "Docker is required but not installed."
        print_error "Please install Docker Desktop: https://docs.docker.com/desktop/"
        exit 1
    fi
    print_status "✓ Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose is required but not installed."
        print_error "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_status "✓ Docker Compose is installed"
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    print_status "✓ Docker is running"
    
    # Check for required files
    required_files=("docker-compose.yaml" "requirements.txt" "healthcheck.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$SCRIPT_DIR/$file" ]; then
            print_error "Required file not found: $file"
            exit 1
        fi
        print_status "✓ Found $file"
    done
}

# Function to create required directories
create_directories() {
    print_header "Creating Required Directories"
    
    directories=("uploads" "logs" "monitoring" "services/auth-service" "services/image-analysis" "frontend")
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$SCRIPT_DIR/$dir" ]; then
            mkdir -p "$SCRIPT_DIR/$dir"
            print_status "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
}

# Function to handle environment configuration
setup_environment() {
    print_header "Setting Up Environment"
    
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
            print_warning "Created .env from .env.example"
            print_warning "Please update .env file with your actual values"
            print_warning "Important: Change default passwords and API keys!"
            echo ""
            print_warning "Press Enter to continue after updating .env, or Ctrl+C to abort"
            read -r
        else
            print_error ".env file not found and no .env.example available"
            print_error "Creating a basic .env file..."
            create_basic_env_file
        fi
    else
        print_status "✓ .env file exists"
    fi
    
    # Load environment variables
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env" 2>/dev/null || print_warning "Could not load some .env variables"
        print_status "✓ Environment variables loaded"
    fi
}

# Function to create basic .env file if missing
create_basic_env_file() {
    cat > "$SCRIPT_DIR/.env" << 'EOF'
# Domain Configuration
DOMAIN=medical.localhost
ACME_EMAIL=admin@example.com

# Database Configuration
DB_USER=postgres
DB_PASSWORD=change_this_secure_password_123
DB_NAME=medical_referral
AUTH_DB_NAME=auth_db

# Application Security
SECRET_KEY=change_this_very_long_secret_key_for_production_use
JWT_SECRET=change_this_jwt_secret_key_for_production_use

# Redis Configuration
REDIS_PASSWORD=change_this_redis_password_123

# MinIO Configuration
MINIO_ACCESS_KEY=medical_admin
MINIO_SECRET_KEY=change_this_minio_password_123

# External APIs
GROQ_API_KEY=your_groq_api_key_here

# Environment Settings
NODE_ENV=production
DEBUG=false

# Admin Credentials
PGADMIN_EMAIL=admin@medical.com
PGADMIN_PASSWORD=change_this_admin_password_123
EOF
    print_status "Basic .env file created. Please update it with your actual values!"
}

# Function to setup Docker networks
setup_networks() {
    print_header "Setting Up Docker Networks"
    
    networks=("traefik-public")
    
    for network in "${networks[@]}"; do
        if ! docker network inspect "$network" >/dev/null 2>&1; then
            docker network create "$network"
            print_status "Created network: $network"
        else
            print_status "Network already exists: $network"
        fi
    done
}

# Function to cleanup existing containers
cleanup_containers() {
    print_header "Cleaning Up Existing Containers"
    
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Optional: Remove unused images and volumes
    read -p "Do you want to clean up unused Docker images and volumes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up unused Docker resources..."
        docker system prune -f
        print_status "Docker cleanup completed"
    fi
}

# Function to build and deploy services
deploy_services() {
    print_header "Building and Deploying Services"
    
    print_status "Pulling latest base images..."
    docker-compose pull --ignore-pull-failures
    
    print_status "Building application images..."
    docker-compose build --no-cache
    
    print_status "Starting services..."
    docker-compose up -d --remove-orphans
    
    print_status "Services deployment initiated"
}

# Function to wait for services with progress indicator
wait_for_services() {
    print_header "Waiting for Services to Initialize"
    
    print_status "Waiting for services to be healthy (this may take a few minutes)..."
    
    # Wait with progress indicator
    for i in {1..60}; do
        echo -n "."
        sleep 1
    done
    echo ""
    
    print_status "Initial wait period completed"
}

# Function to verify service health
verify_services() {
    print_header "Verifying Service Health"
    
    print_status "Current service status:"
    docker-compose ps
    
    echo ""
    print_status "Verifying critical services..."
    
    # List of critical services to check
    critical_services=("medical_referral_app" "medical_postgres" "medical_redis")
    
    all_healthy=true
    for service in "${critical_services[@]}"; do
        if docker ps --format "table {{.Names}}" | grep -q "$service" 2>/dev/null; then
            print_success "✓ $service is running"
        else
            print_error "✗ $service is not running"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All critical services are running!"
    else
        print_warning "Some services may need additional time to start"
    fi
}

# Function to show application logs
show_logs() {
    print_header "Recent Application Logs"
    
    print_status "Recent logs from main application:"
    docker-compose logs --tail=20 medical-app 2>/dev/null || docker-compose logs --tail=20
}

# Function to display deployment results
show_deployment_info() {
    print_header "Deployment Complete!"
    
    echo ""
    print_success " $PROJECT_NAME has been deployed successfully!"
    echo ""
    
    echo " Application URLs:"
    echo "   Main Application: https://${DOMAIN:-medical.localhost}"
    echo "   Patient Search: https://${DOMAIN:-medical.localhost}/patient_search"
    echo "   Dashboard: https://${DOMAIN:-medical.localhost}/dashboard"
    echo "   Database Admin: https://pgadmin.${DOMAIN:-localhost}"
    echo "   Object Storage: https://minio.${DOMAIN:-localhost}"
    echo "   API Gateway: https://traefik.${DOMAIN:-localhost}"
    echo ""
    
    echo " Management Commands:"
    echo "   View all logs: docker-compose logs -f"
    echo "   View service logs: docker-compose logs -f [service-name]"
    echo "   Restart service: docker-compose restart [service-name]"
    echo "   Stop all services: docker-compose down"
    echo "   Update deployment: ./deploy.sh"
    echo ""
    
    echo " Troubleshooting Commands:"
    echo "   Check service status: docker-compose ps"
    echo "   Execute into container: docker exec -it [container-name] /bin/bash"
    echo "   View container stats: docker stats"
    echo "   Check logs: docker-compose logs [service-name]"
    echo ""
    
    echo " Important Directories:"
    echo "   Uploads: ./uploads"
    echo "   Logs: ./logs"
    echo "   Configuration: ./.env"
    echo ""
    
    print_warning "Security Reminder:"
    print_warning "- Ensure you've changed all default passwords in .env"
    print_warning "- Consider using proper SSL certificates for production"
    print_warning "- Review firewall settings for production deployment"
}

# Function to handle script interruption
cleanup_on_exit() {
    print_warning "Deployment interrupted!"
    exit 1
}

# Main deployment function
main() {
    # Handle script interruption
    trap cleanup_on_exit INT
    
    print_header "Starting Deployment of $PROJECT_NAME"
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run deployment steps
    check_prerequisites
    create_directories
    setup_environment
    setup_networks
    cleanup_containers
    deploy_services
    wait_for_services
    verify_services
    show_logs
    show_deployment_info
    
    print_success "Deployment script completed successfully!"
}

# Script help function
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Deploy the Medical Referral Priority System using Docker"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --clean        Perform clean deployment (rebuild everything)"
    echo "  --no-wait      Skip waiting for services to initialize"
    echo "  --logs         Show logs after deployment"
    echo ""
    echo "Examples:"
    echo "  $0                 # Normal deployment"
    echo "  $0 --clean         # Clean deployment"
    echo "  $0 --logs          # Show logs after deployment"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --clean)
        print_status "Clean deployment mode enabled"
        export CLEAN_DEPLOY=true
        ;;
    --no-wait)
        print_status "Skipping service initialization wait"
        export NO_WAIT=true
        ;;
    --logs)
        print_status "Will show detailed logs after deployment"
        export SHOW_LOGS=true
        ;;
    "")
        # Normal deployment, no arguments
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

# Run main deployment
main