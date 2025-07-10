# AI/RAG System Docker Guide

This guide covers running the AI/RAG system in Docker with YAML-based query configuration.

## Overview

The AI/RAG system provides intelligent analysis of AASX data using:
- **Vector Search**: Qdrant vector database for semantic search
- **Knowledge Graph**: Neo4j for graph-based analysis
- **AI Analysis**: OpenAI GPT models for intelligent responses
- **YAML Configuration**: Predefined queries organized by categories

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI/RAG System │    │     Qdrant      │    │     Neo4j       │
│   (Container)   │◄──►│  Vector DB      │    │  Graph DB       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  OpenAI GPT     │
│  API            │
└─────────────────┘
```

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- OpenAI API key (optional, for AI features)
- Neo4j running (optional, for graph features)

### 2. Environment Setup

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini-2025-04-14

# Neo4j Configuration (if running separately)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
```

### 3. Build and Run

#### Using Scripts (Recommended)

**Linux/macOS:**
```bash
# Build and start
./scripts/run_ai_rag_docker.sh --build --start

# Run a specific query
./scripts/run_ai_rag_docker.sh --query-name quality_issues

# Run all queries in a category
./scripts/run_ai_rag_docker.sh --category quality_analysis

# Run demo queries
./scripts/run_ai_rag_docker.sh --demo

# List all available queries
./scripts/run_ai_rag_docker.sh --list-queries
```

**Windows:**
```batch
# Build and start
scripts\run_ai_rag_docker.bat --build --start

# Run a specific query
scripts\run_ai_rag_docker.bat --query-name quality_issues

# Run all queries in a category
scripts\run_ai_rag_docker.bat --category quality_analysis

# Run demo queries
scripts\run_ai_rag_docker.bat --demo

# List all available queries
scripts\run_ai_rag_docker.bat --list-queries
```

#### Using Docker Compose Directly

```bash
# Build the image
docker-compose -f docker-compose.ai-rag.yml build

# Start with a specific query
RAG_QUERY_NAME=quality_issues docker-compose -f docker-compose.ai-rag.yml up

# Start with a category
RAG_CATEGORY=quality_analysis docker-compose -f docker-compose.ai-rag.yml up

# Start with a custom query
RAG_QUERY="What are the quality issues?" RAG_ANALYSIS_TYPE=quality docker-compose -f docker-compose.ai-rag.yml up
```

## Query Configuration

The system uses YAML configuration for managing queries. See `config/ai_rag_queries.yaml` for the complete configuration.

### Query Categories

1. **Quality Analysis**
   - `quality_issues`: Identify quality problems and compliance gaps
   - `compliance_status`: Check compliance and certification status
   - `quality_metrics`: Extract quality measurement data

2. **Risk Assessment**
   - `safety_risks`: Identify safety concerns and risk factors
   - `operational_risks`: Analyze operational risk factors
   - `compliance_risks`: Identify compliance-related risks

3. **Optimization**
   - `performance_optimization`: Find performance improvement opportunities
   - `efficiency_improvements`: Identify efficiency enhancement opportunities
   - `cost_optimization`: Find cost optimization strategies

4. **Asset Analysis**
   - `asset_overview`: Get overview of all available assets
   - `motor_assets`: Search for motor assets specifically
   - `sensor_assets`: Find sensor assets and their capabilities

5. **Submodel Analysis**
   - `submodel_overview`: Get overview of all submodels
   - `quality_submodels`: Find quality-focused submodels

6. **Compliance Analysis**
   - `certification_status`: Check certification requirements and status
   - `regulatory_compliance`: Identify regulatory compliance needs

### Demo Queries

For testing and demonstration:
- `demo_quality`: Demo quality analysis
- `demo_risk`: Demo risk assessment
- `demo_optimization`: Demo optimization analysis
- `demo_general`: Demo general analysis

## Usage Examples

### 1. Run a Specific Query

```bash
# Run quality issues analysis
./scripts/run_ai_rag_docker.sh --query-name quality_issues

# Run motor assets search
./scripts/run_ai_rag_docker.sh --query-name motor_assets
```

### 2. Run All Queries in a Category

```bash
# Run all quality analysis queries
./scripts/run_ai_rag_docker.sh --category quality_analysis

# Run all risk assessment queries
./scripts/run_ai_rag_docker.sh --category risk_assessment
```

### 3. Run Custom Queries

```bash
# Custom quality query
./scripts/run_ai_rag_docker.sh --custom-query "What are the main quality issues?" --analysis-type quality

# Custom asset search
./scripts/run_ai_rag_docker.sh --custom-query "Find all motor components" --collection aasx_assets --limit 10
```

### 4. Demo Mode

```bash
# Run all demo queries
./scripts/run_ai_rag_docker.sh --demo
```

### 5. System Management

```bash
# Check system status
./scripts/run_ai_rag_docker.sh --status

# View logs
./scripts/run_ai_rag_docker.sh --logs

# Stop the system
./scripts/run_ai_rag_docker.sh --stop

# Restart the system
./scripts/run_ai_rag_docker.sh --restart

# Clean up everything
./scripts/run_ai_rag_docker.sh --clean
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RAG_QUERY_NAME` | Name of predefined query to run | - |
| `RAG_CATEGORY` | Category of queries to run | - |
| `RAG_QUERY` | Custom query text | - |
| `RAG_ANALYSIS_TYPE` | Analysis type (general/quality/risk/optimization) | general |
| `RAG_COLLECTION` | Vector collection to search | aasx_assets |
| `RAG_LIMIT` | Maximum number of results | 5 |

### Analysis Types

- **general**: General analysis and information retrieval
- **quality**: Quality-focused analysis and compliance checking
- **risk**: Risk assessment and safety analysis
- **optimization**: Performance and efficiency optimization

### Vector Collections

- **aasx_assets**: Asset information and specifications
- **aasx_submodels**: Submodel definitions and relationships
- **quality_standards**: Quality standards and requirements
- **compliance_data**: Compliance and certification data

## Data Sources

The system can work with:

1. **ETL Pipeline Output**: Processed AASX data from the ETL pipeline
2. **Direct AASX Files**: Raw AASX files (requires indexing)
3. **Knowledge Graph**: Neo4j graph database with AAS relationships
4. **External APIs**: Additional data sources via API integration

## Integration with Other Components

### ETL Pipeline Integration

```bash
# Index ETL output data
python scripts/run_ai_rag.py --index-etl output/etl_results/

# Then run queries
./scripts/run_ai_rag_docker.sh --query-name quality_issues
```

### Knowledge Graph Integration

```bash
# Ensure Neo4j is running
docker-compose -f docker-compose.knowledge-graph.yml up -d

# Run AI/RAG with graph features
./scripts/run_ai_rag_docker.sh --query-name quality_issues
```

## Troubleshooting

### Common Issues

1. **Docker not running**
   ```bash
   # Check Docker status
   docker info
   ```

2. **Services not ready**
   ```bash
   # Check service status
   ./scripts/run_ai_rag_docker.sh --status
   ```

3. **OpenAI API errors**
   ```bash
   # Check API key in .env file
   cat .env | grep OPENAI_API_KEY
   ```

4. **Neo4j connection issues**
   ```bash
   # Check Neo4j status
   docker ps | grep neo4j
   ```

### Logs and Debugging

```bash
# View detailed logs
./scripts/run_ai_rag_docker.sh --logs

# Run with verbose output
python scripts/run_ai_rag.py --query-name quality_issues --verbose
```

### Performance Optimization

1. **Increase memory limits** for large datasets
2. **Use GPU acceleration** for vector operations
3. **Optimize batch sizes** for processing
4. **Cache frequently used queries**

## Advanced Configuration

### Custom Query Templates

Add custom query templates to `config/ai_rag_queries.yaml`:

```yaml
templates:
  asset_search:
    query: "Find assets related to {keyword}"
    analysis_type: "general"
    collection: "aasx_assets"
    parameters:
      - keyword
```

### Custom Analysis Types

Extend the system with custom analysis types by modifying the AI/RAG system code.

### Integration with External Systems

The system can be integrated with:
- Manufacturing execution systems (MES)
- Quality management systems (QMS)
- Enterprise resource planning (ERP)
- IoT platforms and sensors

## Security Considerations

1. **API Key Management**: Store OpenAI API keys securely
2. **Network Security**: Use VPN for production deployments
3. **Data Privacy**: Ensure compliance with data protection regulations
4. **Access Control**: Implement proper authentication and authorization

## Monitoring and Maintenance

### Health Checks

```bash
# System health check
./scripts/run_ai_rag_docker.sh --status

# Service-specific checks
curl http://localhost:6333/collections  # Qdrant
curl http://localhost:7474/browser/     # Neo4j
```

### Backup and Recovery

```bash
# Backup data
docker-compose -f docker-compose.ai-rag.yml exec qdrant qdrant backup /backup
docker-compose -f docker-compose.ai-rag.yml exec neo4j neo4j-admin backup

# Restore data
docker-compose -f docker-compose.ai-rag.yml exec qdrant qdrant restore /backup
docker-compose -f docker-compose.ai-rag.yml exec neo4j neo4j-admin restore
```

## Support and Resources

- **Documentation**: See `docs/` directory for detailed guides
- **Configuration**: Check `config/` directory for configuration files
- **Scripts**: Use `scripts/` directory for automation and utilities
- **Tests**: Run `test/` directory for validation and testing

For issues and questions, check the troubleshooting section or refer to the main project documentation. 