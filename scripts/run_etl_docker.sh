#!/bin/bash

# ETL Pipeline Docker Runner Script
# Enhanced version with comprehensive management options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="manifests/independent/docker-compose.etl.yml"
CONTAINER_NAME="etl-pipeline"
SERVICE_NAME="etl-pipeline"

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
    echo "ETL Pipeline Docker Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --build                    Build the Docker image"
    echo "  --start                    Start the ETL pipeline"
    echo "  --stop                     Stop the ETL pipeline"
    echo "  --restart                  Restart the ETL pipeline"
    echo "  --logs                     Show logs"
    echo "  --clean                    Clean up containers and volumes"
    echo "  --status                   Show system status"
    echo "  --demo                     Run demo ETL processing"
    echo ""
    echo "Processing Options:"
    echo "  --input-dir DIR            Specify input directory for AASX files"
    echo "  --output-dir DIR           Specify output directory for results"
    echo "  --config-file FILE         Specify ETL configuration file"
    echo "  --verbose                  Enable verbose logging"
    echo ""
    echo "Examples:"
    echo "  $0 --build --start"
    echo "  $0 --demo"
    echo "  $0 --input-dir data/aasx-examples --output-dir output/results"
    echo "  $0 --status"
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating basic .env file..."
        cat > .env << EOF
# ETL Pipeline Configuration
ETL_INPUT_DIR=data/aasx-examples
ETL_OUTPUT_DIR=output/etl_results
ETL_CONFIG_FILE=scripts/config_etl.yaml
ETL_VERBOSE=false
EOF
        print_success "Created basic .env file"
    fi
    
    # Check if input directory exists
    if [ ! -d "data/aasx-examples" ]; then
        print_warning "Input directory data/aasx-examples not found. Creating..."
        mkdir -p data/aasx-examples
        print_success "Created input directory"
    fi
    
    # Check if AASX files exist
    if [ -z "$(ls -A data/aasx-examples/*.aasx 2>/dev/null)" ]; then
        print_warning "No AASX files found in data/aasx-examples/"
        print_status "Please place your .aasx files in the data/aasx-examples/ directory"
    else
        print_success "Found AASX files:"
        ls -la data/aasx-examples/*.aasx
    fi
}

# Function to build the image
build_image() {
    print_status "Building ETL Pipeline Docker image..."
    docker-compose -f "$COMPOSE_FILE" build "$SERVICE_NAME"
    print_success "Image built successfully"
}

# Function to start the system
start_system() {
    print_status "Starting ETL Pipeline..."
    
    # Set environment variables
    export ETL_INPUT_DIR="${ETL_INPUT_DIR:-data/aasx-examples}"
    export ETL_OUTPUT_DIR="${ETL_OUTPUT_DIR:-output/etl_results}"
    export ETL_CONFIG_FILE="${ETL_CONFIG_FILE:-scripts/config_etl.yaml}"
    export ETL_VERBOSE="${ETL_VERBOSE:-false}"
    
    docker-compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"
    print_success "ETL Pipeline started"
    
    # Wait a moment and show logs
    sleep 5
    show_logs
}

# Function to stop the system
stop_system() {
    print_status "Stopping ETL Pipeline..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "ETL Pipeline stopped"
}

# Function to restart the system
restart_system() {
    print_status "Restarting ETL Pipeline..."
    stop_system
    sleep 2
    start_system
}

# Function to show logs
show_logs() {
    print_status "Showing ETL Pipeline logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE_NAME"
}

# Function to clean up
clean_up() {
    print_warning "Cleaning up ETL Pipeline containers and volumes..."
    docker-compose -f "$COMPOSE_FILE" down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "ETL Pipeline Status:"
    echo ""
    
    # Check if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "Containers are running"
        docker-compose -f "$COMPOSE_FILE" ps
    else
        print_warning "No containers are running"
    fi
    
    echo ""
    
    # Check input files
    if [ -d "data/aasx-examples" ]; then
        aasx_count=$(ls -1 data/aasx-examples/*.aasx 2>/dev/null | wc -l)
        print_status "Input files: $aasx_count AASX files found"
        if [ $aasx_count -gt 0 ]; then
            ls -la data/aasx-examples/*.aasx
        fi
    fi
    
    # Check output directory
    if [ -d "output/etl_results" ]; then
        output_count=$(find output/etl_results -name "*.json" -o -name "*.csv" 2>/dev/null | wc -l)
        print_status "Output files: $output_count processed files found"
    fi
}

# Function to run demo
run_demo() {
    print_status "Running ETL Pipeline Demo..."
    
    # Check if demo files exist
    if [ -z "$(ls -A data/aasx-examples/*.aasx 2>/dev/null)" ]; then
        print_warning "No AASX files found for demo"
        print_status "Please place some .aasx files in data/aasx-examples/ directory"
        return 1
    fi
    
    # Start the pipeline
    start_system
    
    print_success "Demo ETL processing started"
    print_status "Check logs for processing details"
}

# Main script logic
main() {
    # Check if Docker is available
    check_docker
    
    # Initialize variables
    local has_action=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                build_image
                has_action=true
                shift
                ;;
            --start)
                start_system
                has_action=true
                shift
                ;;
            --stop)
                stop_system
                has_action=true
                shift
                ;;
            --restart)
                restart_system
                has_action=true
                shift
                ;;
            --logs)
                show_logs
                has_action=true
                shift
                ;;
            --clean)
                clean_up
                has_action=true
                shift
                ;;
            --status)
                show_status
                has_action=true
                shift
                ;;
            --demo)
                run_demo
                has_action=true
                shift
                ;;
            --input-dir)
                ETL_INPUT_DIR="$2"
                shift 2
                ;;
            --output-dir)
                ETL_OUTPUT_DIR="$2"
                shift 2
                ;;
            --config-file)
                ETL_CONFIG_FILE="$2"
                shift 2
                ;;
            --verbose)
                ETL_VERBOSE="true"
                shift
                ;;
            --help|-h)
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
    
    # If no action specified, check prerequisites and show usage
    if [[ "$has_action" == false ]]; then
        check_prerequisites
        show_usage
        exit 0
    fi
}

# Run main function with all arguments
main "$@" 