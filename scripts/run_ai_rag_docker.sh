#!/bin/bash

# AI/RAG System Docker Runner Script
# Supports YAML-based query configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="manifests/independent/docker-compose.ai-rag.yml"
CONTAINER_NAME="ai-rag"
SERVICE_NAME="ai-rag"

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
    echo "AI/RAG System Docker Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --build                    Build the Docker image"
    echo "  --start                    Start the AI/RAG system"
    echo "  --stop                     Stop the AI/RAG system"
    echo "  --restart                  Restart the AI/RAG system"
    echo "  --logs                     Show logs"
    echo "  --clean                    Clean up containers and volumes"
    echo "  --status                   Show system status"
    echo ""
    echo "Query Options:"
    echo "  --query-name NAME          Run a specific predefined query by name"
    echo "  --category CATEGORY        Run all queries in a category"
    echo "  --custom-query QUERY       Run a custom query"
    echo "  --demo                     Run demo queries"
    echo "  --list-queries             List all available queries"
    echo ""
    echo "Analysis Options (for custom queries):"
    echo "  --analysis-type TYPE       Analysis type (general, quality, risk, optimization)"
    echo "  --collection COLLECTION    Vector collection (aasx_assets, aasx_submodels, etc.)"
    echo "  --limit LIMIT              Maximum number of results"
    echo ""
    echo "Examples:"
    echo "  $0 --build --start"
    echo "  $0 --query-name quality_issues"
    echo "  $0 --category quality_analysis"
    echo "  $0 --custom-query 'What are the quality issues?' --analysis-type quality"
    echo "  $0 --demo"
    echo "  $0 --list-queries"
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to build the image
build_image() {
    print_status "Building AI/RAG system Docker image..."
    docker-compose -f "$COMPOSE_FILE" build "$SERVICE_NAME"
    print_success "Image built successfully"
}

# Function to start the system
start_system() {
    print_status "Starting AI/RAG system..."
    
    # Set environment variables for query
    export RAG_QUERY_NAME="$RAG_QUERY_NAME"
    export RAG_CATEGORY="$RAG_CATEGORY"
    export RAG_QUERY="$RAG_QUERY"
    export RAG_ANALYSIS_TYPE="${RAG_ANALYSIS_TYPE:-general}"
    export RAG_COLLECTION="${RAG_COLLECTION:-aasx_assets}"
    export RAG_LIMIT="${RAG_LIMIT:-5}"
    
    docker-compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"
    print_success "AI/RAG system started"
    
    # Wait a moment and show logs
    sleep 3
    show_logs
}

# Function to stop the system
stop_system() {
    print_status "Stopping AI/RAG system..."
    docker-compose -f "$COMPOSE_FILE" down
    print_success "AI/RAG system stopped"
}

# Function to restart the system
restart_system() {
    print_status "Restarting AI/RAG system..."
    stop_system
    sleep 2
    start_system
}

# Function to show logs
show_logs() {
    print_status "Showing AI/RAG system logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE_NAME"
}

# Function to clean up
clean_up() {
    print_warning "Cleaning up AI/RAG system containers and volumes..."
    docker-compose -f "$COMPOSE_FILE" down -v
    docker system prune -f
    print_success "Cleanup completed"
}

# Function to show status
show_status() {
    print_status "AI/RAG System Status:"
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
    else
        print_warning "Neo4j is not running"
    fi
    
    # Check Qdrant
    if docker ps | grep -q "qdrant"; then
        print_success "Qdrant is running"
    else
        print_warning "Qdrant is not running"
    fi
}

# Function to list queries
list_queries() {
    print_status "Listing available queries from YAML configuration..."
    python scripts/run_ai_rag.py --list-queries
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
            --query-name)
                RAG_QUERY_NAME="$2"
                has_action=true
                shift 2
                ;;
            --category)
                RAG_CATEGORY="$2"
                has_action=true
                shift 2
                ;;
            --custom-query)
                RAG_QUERY="$2"
                has_action=true
                shift 2
                ;;
            --demo)
                RAG_DEMO=true
                has_action=true
                shift
                ;;
            --list-queries)
                list_queries
                exit 0
                ;;
            --analysis-type)
                RAG_ANALYSIS_TYPE="$2"
                shift 2
                ;;
            --collection)
                RAG_COLLECTION="$2"
                shift 2
                ;;
            --limit)
                RAG_LIMIT="$2"
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
    
    # If we have query parameters, start the system
    if [[ "$has_action" == true ]] && [[ -n "$RAG_QUERY_NAME" || -n "$RAG_CATEGORY" || -n "$RAG_QUERY" || "$RAG_DEMO" == true ]]; then
        start_system
    elif [[ "$has_action" == false ]]; then
        show_usage
        exit 0
    fi
}

# Run main function with all arguments
main "$@" 