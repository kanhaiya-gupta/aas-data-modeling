# Enhanced Docker Scripts Guide

This guide covers the enhanced Docker runner scripts for all components of the AAS Data Modeling framework. All scripts now follow a consistent pattern with comprehensive management options.

## 🚀 Overview

All scripts now provide:
- **Consistent Interface**: Same command-line options across all components
- **Comprehensive Management**: Build, start, stop, restart, logs, clean, status
- **Demo Mode**: Easy testing and demonstration
- **Colored Output**: Clear status indicators
- **Prerequisites Checking**: Automatic setup and validation
- **Cross-Platform**: Both Linux/macOS (`.sh`) and Windows (`.bat`) versions

## 📋 Available Scripts

### 1. AI/RAG System
- **Linux/macOS**: `scripts/run_ai_rag_docker.sh`
- **Windows**: `scripts/run_ai_rag_docker.bat`

### 2. ETL Pipeline
- **Linux/macOS**: `scripts/run_etl_docker.sh`
- **Windows**: `scripts/run_etl_docker.bat`

### 3. Knowledge Graph
- **Linux/macOS**: `scripts/run_knowledge_graph.sh`
- **Windows**: `scripts/run_knowledge_graph.bat`

## 🎯 Common Usage Patterns

### Basic Operations
```bash
# Build and start
./scripts/run_ai_rag_docker.sh --build --start
./scripts/run_etl_docker.sh --build --start
./scripts/run_knowledge_graph.sh --build --start

# Demo mode
./scripts/run_ai_rag_docker.sh --demo
./scripts/run_etl_docker.sh --demo
./scripts/run_knowledge_graph.sh --demo

# Status check
./scripts/run_ai_rag_docker.sh --status
./scripts/run_etl_docker.sh --status
./scripts/run_knowledge_graph.sh --status

# View logs
./scripts/run_ai_rag_docker.sh --logs
./scripts/run_etl_docker.sh --logs
./scripts/run_knowledge_graph.sh --logs

# Stop and clean
./scripts/run_ai_rag_docker.sh --stop
./scripts/run_etl_docker.sh --stop
./scripts/run_knowledge_graph.sh --stop

# Clean up everything
./scripts/run_ai_rag_docker.sh --clean
./scripts/run_etl_docker.sh --clean
./scripts/run_knowledge_graph.sh --clean
```

## 🔧 AI/RAG System Script

### Features
- **YAML Query Configuration**: Load queries from `config/ai_rag_queries.yaml`
- **Multiple Query Modes**: Specific queries, categories, custom queries, demo
- **Analysis Types**: General, quality, risk, optimization
- **Vector Collections**: aasx_assets, aasx_submodels, quality_standards, compliance_data

### Usage Examples
```bash
# List all available queries
./scripts/run_ai_rag_docker.sh --list-queries

# Run specific query
./scripts/run_ai_rag_docker.sh --query-name quality_issues

# Run all queries in a category
./scripts/run_ai_rag_docker.sh --category quality_analysis

# Custom query
./scripts/run_ai_rag_docker.sh --custom-query "What are the quality issues?" --analysis-type quality

# Demo mode (runs all demo queries)
./scripts/run_ai_rag_docker.sh --demo
```

### Environment Variables
- `RAG_QUERY_NAME`: Name of predefined query to run
- `RAG_CATEGORY`: Category of queries to run
- `RAG_QUERY`: Custom query text
- `RAG_ANALYSIS_TYPE`: Analysis type (general/quality/risk/optimization)
- `RAG_COLLECTION`: Vector collection to search
- `RAG_LIMIT`: Maximum number of results

## 🔄 ETL Pipeline Script

### Features
- **AASX Processing**: Process AASX files with .NET processor
- **Flexible Input/Output**: Configurable directories
- **Verbose Logging**: Detailed processing information
- **Automatic Setup**: Creates directories and config files

### Usage Examples
```bash
# Process AASX files with default settings
./scripts/run_etl_docker.sh --demo

# Custom input/output directories
./scripts/run_etl_docker.sh --input-dir data/my-aasx-files --output-dir output/my-results

# Verbose logging
./scripts/run_etl_docker.sh --verbose --demo

# Custom configuration
./scripts/run_etl_docker.sh --config-file scripts/my_config.yaml --demo
```

### Environment Variables
- `ETL_INPUT_DIR`: Input directory for AASX files (default: data/aasx-examples)
- `ETL_OUTPUT_DIR`: Output directory for results (default: output/etl_results)
- `ETL_CONFIG_FILE`: ETL configuration file (default: scripts/config_etl.yaml)
- `ETL_VERBOSE`: Enable verbose logging (default: false)

## 🧠 Knowledge Graph Script

### Features
- **Neo4j Integration**: Full Neo4j database support
- **ETL Data Loading**: Load processed data from ETL pipeline
- **API Endpoints**: RESTful API for graph operations
- **Neo4j-Only Mode**: Start just Neo4j without processing

### Usage Examples
```bash
# Start with ETL output data
./scripts/run_knowledge_graph.sh --etl-output output/etl_results --demo

# Start only Neo4j (no processing)
./scripts/run_knowledge_graph.sh --neo4j-only --start

# Custom data directory
./scripts/run_knowledge_graph.sh --data-dir data/my-graph-data --demo

# Custom API port
./scripts/run_knowledge_graph.sh --api-port 8080 --demo
```

### Environment Variables
- `KG_DATA_DIR`: Data directory for graph data (default: data/graph_data)
- `KG_API_PORT`: API port (default: 8004)
- `ETL_OUTPUT_DIR`: Load data from ETL output directory

## 🎯 Demo Mode

All scripts support demo mode for easy testing:

### AI/RAG Demo
- Runs 4 predefined demo queries
- Tests quality, risk, optimization, and general analysis
- Shows system integration with vector search and knowledge graph

### ETL Demo
- Processes AASX files in the input directory
- Shows detailed processing logs
- Creates structured output for downstream systems

### Knowledge Graph Demo
- Loads available data (ETL output or graph data)
- Performs graph analysis
- Provides access to Neo4j Browser and API

## 🔍 Status Monitoring

All scripts provide comprehensive status information:

```bash
# Check system status
./scripts/run_ai_rag_docker.sh --status
./scripts/run_etl_docker.sh --status
./scripts/run_knowledge_graph.sh --status
```

Status includes:
- Container status
- Service availability
- Data file counts
- Access URLs
- Configuration information

## 🛠️ Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Check Docker status
   docker info
   ```

2. **Port conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :7474  # Neo4j
   netstat -tulpn | grep :6333  # Qdrant
   netstat -tulpn | grep :8004  # Knowledge Graph API
   ```

3. **Missing data**
   ```bash
   # Check data directories
   ls -la data/aasx-examples/
   ls -la output/etl_results/
   ls -la data/graph_data/
   ```

4. **Environment issues**
   ```bash
   # Check .env file
   cat .env
   
   # Check prerequisites
   ./scripts/run_ai_rag_docker.sh  # Shows usage and checks prerequisites
   ```

### Logs and Debugging

```bash
# View detailed logs
./scripts/run_ai_rag_docker.sh --logs
./scripts/run_etl_docker.sh --logs
./scripts/run_knowledge_graph.sh --logs

# Verbose mode (ETL)
./scripts/run_etl_docker.sh --verbose --demo
```

## 🔗 Integration Workflow

### Complete Pipeline Example

```bash
# 1. Process AASX files
./scripts/run_etl_docker.sh --demo

# 2. Load data into Knowledge Graph
./scripts/run_knowledge_graph.sh --etl-output output/etl_results --demo

# 3. Query with AI/RAG system
./scripts/run_ai_rag_docker.sh --query-name quality_issues

# 4. Check status of all systems
./scripts/run_etl_docker.sh --status
./scripts/run_knowledge_graph.sh --status
./scripts/run_ai_rag_docker.sh --status
```

### Quick Start

```bash
# Build all images
./scripts/run_ai_rag_docker.sh --build
./scripts/run_etl_docker.sh --build
./scripts/run_knowledge_graph.sh --build

# Run complete demo
./scripts/run_etl_docker.sh --demo
./scripts/run_knowledge_graph.sh --etl-output output/etl_results --demo
./scripts/run_ai_rag_docker.sh --demo
```

## 📊 System Requirements

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB free space
- **Network**: Internet access for Docker images

## 🔐 Security Notes

- Scripts create basic `.env` files if missing
- Default passwords are used for development
- Production deployments should use secure credentials
- Docker containers run with appropriate permissions

## 📚 Additional Resources

- **AI/RAG Documentation**: `docs/AI_RAG_DOCKER_GUIDE.md`
- **ETL Documentation**: `docs/AASX_ETL_PIPELINE.md`
- **Knowledge Graph Documentation**: `docs/KNOWLEDGE_GRAPH_GUIDE.md`
- **Configuration Files**: `config/` directory
- **Example Data**: `data/aasx-examples/` directory

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs with `--logs` option
3. Verify prerequisites with status checks
4. Consult component-specific documentation
5. Check Docker and system requirements 