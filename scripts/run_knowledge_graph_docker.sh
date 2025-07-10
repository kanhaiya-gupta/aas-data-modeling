#!/bin/bash

# Knowledge Graph Docker Runner Script
# Enhanced version with comprehensive management options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.knowledge-graph.yml"
CONTAINER_NAME="knowledge-graph"
SERVICE_NAME="knowledge-graph"

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
    echo "Knowledge Graph Docker Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --build                    Build the Docker image"
    echo "  --start                    Start the Knowledge Graph system"
    echo "  --stop                     Stop the Knowledge Graph system"
    echo "  --restart                  Restart the Knowledge Graph system"
    echo "  --logs                     Show logs"
    echo "  --clean                    Clean up containers and volumes"
    echo "  --status                   Show system status"
    echo "  --demo                     Run demo knowledge graph analysis"
    echo ""
    echo "Data Options:"
    echo "  --data-dir DIR             Specify data directory for graph data"
    echo "  --etl-output DIR           Load data from ETL output directory"
    echo "  --neo4j-only               Start only Neo4j (no knowledge graph processing)"
    echo "  --api-port PORT            Specify API port (default: 8004)"
    echo ""
    echo "Examples:"
    echo "  $0 --build --start"
    echo "  $0 --demo"
    echo "  $0 --etl-output output/etl_results"
    echo "  $0 --neo4j-only"
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
# Knowledge Graph Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123
KG_DATA_DIR=data/graph_data
KG_API_PORT=8004
EOF
        print_success "Created basic .env file"
    fi
    
    # Create necessary directories
    print_status "Creating data directories..."
    mkdir -p data/graph_data data/processed output logs
    print_success "Data directories created"
}

# Function to build the image
build_image() {
    print_status "Building Knowledge Graph Docker image..."
    docker-compose -f "$COMPOSE_FILE" build "$SERVICE_NAME"
    print_success "Image built successfully"
}

# Function to start the system
start_system() {
    print_status "Starting Knowledge Graph system..."
    
    # Set environment variables
    export KG_DATA_DIR="${KG_DATA_DIR:-data/graph_data}"
    export KG_API_PORT="${KG_API_PORT:-8004}"
    export ETL_OUTPUT_DIR="${ETL_OUTPUT_DIR:-}"
    
    docker-compose -f "$COMPOSE_FILE" up -d
    print_success "Knowledge Graph system started"
    
    # Wait a moment and show logs
    sleep 5
    show_logs
}

# Function to stop the system
stop_system() {
    print_status "Stopping Knowledge Graph system..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "Knowledge Graph system stopped"
}

# Function to restart the system
restart_system() {
    print_status "Restarting Knowledge Graph system..."
    stop_system
    sleep 2
    start_system
}

# Function to show logs
show_logs() {
    print_status "Showing Knowledge Graph logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Function to clean up
clean_up() {
    print_warning "Cleaning up Knowledge Graph containers and volumes..."
    docker-compose -f "$COMPOSE_FILE" down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "Knowledge Graph System Status:"
    echo ""
    
    # Check if containers are running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_success "Containers are running"
        docker-compose -f "$COMPOSE_FILE" ps
    else
        print_warning "No containers are running"
    fi
    
    echo ""
    
    # Check Neo4j
    if docker ps | grep -q "neo4j"; then
        print_success "Neo4j is running"
        print_status "Neo4j Browser: http://localhost:7474"
        print_status "Neo4j Bolt: bolt://localhost:7687"
    else
        print_warning "Neo4j is not running"
    fi
    
    # Check Knowledge Graph API
    if docker ps | grep -q "knowledge-graph"; then
        print_success "Knowledge Graph API is running"
        print_status "API URL: http://localhost:${KG_API_PORT:-8004}"
    else
        print_warning "Knowledge Graph API is not running"
    fi
    
    echo ""
    
    # Check data directories
    if [ -d "data/graph_data" ]; then
        data_count=$(find data/graph_data -name "*.json" -o -name "*.csv" 2>/dev/null | wc -l)
        print_status "Graph data files: $data_count files found"
    fi
    
    if [ -d "output/etl_results" ]; then
        etl_count=$(find output/etl_results -name "*.json" -o -name "*.csv" 2>/dev/null | wc -l)
        print_status "ETL output files: $etl_count files found"
    fi
}

# Function to run demo
run_demo() {
    print_status "Running Knowledge Graph Demo..."
    
    # Check if we have any data
    if [ -d "output/etl_results" ] && [ "$(ls -A output/etl_results 2>/dev/null)" ]; then
        print_status "Found ETL output data, using it for demo"
        export ETL_OUTPUT_DIR="output/etl_results"
    elif [ -d "data/graph_data" ] && [ "$(ls -A data/graph_data 2>/dev/null)" ]; then
        print_status "Found graph data, using it for demo"
    else
        print_warning "No data found for demo"
        print_status "Please run ETL pipeline first or place data in data/graph_data/"
        return 1
    fi
    
    # Start the system
    start_system
    
    print_success "Demo Knowledge Graph analysis started"
    print_status "Check logs for analysis details"
    print_status "Access Neo4j Browser at: http://localhost:7474"
    print_status "Access Knowledge Graph API at: http://localhost:${KG_API_PORT:-8004}"
}

# Function to start Neo4j only
start_neo4j_only() {
    print_status "Starting Neo4j only..."
    
    # Start only Neo4j service
    docker-compose -f "$COMPOSE_FILE" up -d neo4j
    print_success "Neo4j started"
    
    print_status "Neo4j Browser: http://localhost:7474"
    print_status "Neo4j Bolt: bolt://localhost:7687"
    print_status "Username: neo4j"
    print_status "Password: Neo4j123"
}

# Main script logic
main() {
    # Check if Docker is available
    check_docker
    
    # Initialize variables
    local has_action=false
    local neo4j_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                build_image
                has_action=true
                shift
                ;;
            --start)
                if [ "$neo4j_only" = true ]; then
                    start_neo4j_only
                else
                    start_system
                fi
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
            --data-dir)
                KG_DATA_DIR="$2"
                shift 2
                ;;
            --etl-output)
                ETL_OUTPUT_DIR="$2"
                shift 2
                ;;
            --neo4j-only)
                neo4j_only=true
                shift
                ;;
            --api-port)
                KG_API_PORT="$2"
                shift 2
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