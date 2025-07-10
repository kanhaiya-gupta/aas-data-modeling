# Manifest Structure Documentation

This document describes the organized structure of Docker manifests and Dockerfiles in the AAS Data Modeling framework.

## 📁 Directory Structure

```
manifests/
├── independent/          # Standalone component configurations
│   ├── docker-compose.etl.yml
│   ├── docker-compose.knowledge-graph.yml
│   └── docker-compose.ai-rag.yml
└── framework/           # Full integrated system configurations
    ├── docker-compose.yml
    ├── docker-compose.framework.yml
    └── docker-compose.local.yml

docker/
├── independent/         # Standalone component Dockerfiles
│   ├── Dockerfile.etl-pipeline
│   ├── Dockerfile.knowledge-graph
│   ├── Dockerfile.ai-rag
│   ├── Dockerfile.webapp
│   ├── Dockerfile.twin-registry
│   ├── Dockerfile.certificate-manager
│   └── Dockerfile.qi-analytics
└── framework/          # Framework-specific Dockerfiles (future use)
    └── (framework-specific files)
```

## 🎯 Manifest Categories

### 1. Independent Components (`manifests/independent/`)

These are standalone components that can run independently:

#### **ETL Pipeline** (`docker-compose.etl.yml`)
- **Purpose**: Process AASX files and extract structured data
- **Services**: 
  - `etl-pipeline`: Main ETL processing service
  - `neo4j`: Graph database (optional)
  - `qdrant`: Vector database (optional)
- **Usage**: `./scripts/run_etl_docker.sh --demo`

#### **Knowledge Graph** (`docker-compose.knowledge-graph.yml`)
- **Purpose**: Graph analysis and visualization
- **Services**:
  - `knowledge-graph`: Graph processing service
  - `neo4j`: Graph database
- **Usage**: `./scripts/run_knowledge_graph.sh --demo`

#### **AI/RAG System** (`docker-compose.ai-rag.yml`)
- **Purpose**: AI-powered querying and analysis
- **Services**:
  - `ai-rag`: AI/RAG processing service
  - `qdrant`: Vector database
  - `neo4j`: Graph database (optional)
- **Usage**: `./scripts/run_ai_rag_docker.sh --demo`

### 2. Framework Configurations (`manifests/framework/`)

These are full integrated system configurations:

#### **Main Framework** (`docker-compose.yml`)
- **Purpose**: Complete integrated system with all components
- **Services**: All components running together
- **Usage**: `docker-compose -f manifests/framework/docker-compose.yml up`

#### **Framework Core** (`docker-compose.framework.yml`)
- **Purpose**: Core framework without optional components
- **Services**: Essential services only
- **Usage**: `docker-compose -f manifests/framework/docker-compose.framework.yml up`

#### **Local Development** (`docker-compose.local.yml`)
- **Purpose**: Local development setup
- **Services**: Development-optimized configuration
- **Usage**: `docker-compose -f manifests/framework/docker-compose.local.yml up`

## 🔧 Dockerfile Organization

### Independent Dockerfiles (`docker/independent/`)

Each component has its own Dockerfile for standalone deployment:

#### **ETL Pipeline** (`Dockerfile.etl-pipeline`)
```dockerfile
# Features:
- .NET 6.0 SDK for AAS processor
- Python environment for ETL scripts
- AASX file processing capabilities
- Vector database integration
```

#### **Knowledge Graph** (`Dockerfile.knowledge-graph`)
```dockerfile
# Features:
- Python environment for graph processing
- Neo4j integration
- Graph analysis tools
- API endpoints
```

#### **AI/RAG System** (`Dockerfile.ai-rag`)
```dockerfile
# Features:
- Python environment for AI/RAG
- OpenAI integration
- Vector search capabilities
- Query processing
```

#### **Supporting Services**
- `Dockerfile.webapp`: Web application interface
- `Dockerfile.twin-registry`: Digital twin registry
- `Dockerfile.certificate-manager`: Certificate management
- `Dockerfile.qi-analytics`: Quality intelligence analytics

## 🚀 Usage Patterns

### Independent Component Deployment

```bash
# ETL Pipeline
./scripts/run_etl_docker.sh --build --start
./scripts/run_etl_docker.sh --demo

# Knowledge Graph
./scripts/run_knowledge_graph.sh --build --start
./scripts/run_knowledge_graph.sh --etl-output output/etl_results --demo

# AI/RAG System
./scripts/run_ai_rag_docker.sh --build --start
./scripts/run_ai_rag_docker.sh --demo
```

### Framework Deployment

```bash
# Full framework
docker-compose -f manifests/framework/docker-compose.yml up -d

# Core framework
docker-compose -f manifests/framework/docker-compose.framework.yml up -d

# Local development
docker-compose -f manifests/framework/docker-compose.local.yml up -d
```

### Complete Pipeline Workflow

```bash
# 1. Process AASX files
./scripts/run_etl_docker.sh --demo

# 2. Load into Knowledge Graph
./scripts/run_knowledge_graph.sh --etl-output output/etl_results --demo

# 3. Query with AI/RAG
./scripts/run_ai_rag_docker.sh --query-name quality_issues

# 4. Check status
./scripts/run_etl_docker.sh --status
./scripts/run_knowledge_graph.sh --status
./scripts/run_ai_rag_docker.sh --status
```

## 🔗 Integration Points

### Data Flow Between Components

```
AASX Files → ETL Pipeline → Structured Data → Knowledge Graph → Graph Analysis
                                    ↓
                              Vector Database → AI/RAG System → AI Queries
```

### Service Dependencies

- **ETL Pipeline**: Independent, can run standalone
- **Knowledge Graph**: Can use ETL output or standalone data
- **AI/RAG System**: Requires vector database, optional graph database

### Port Mappings

| Service | Port | Purpose |
|---------|------|---------|
| ETL Pipeline | 8001 | ETL API |
| Knowledge Graph | 8004 | Graph API |
| AI/RAG System | 8002 | AI/RAG API |
| Neo4j | 7474, 7687 | Graph Database |
| Qdrant | 6333 | Vector Database |
| Web App | 8000 | Web Interface |

## 🛠️ Configuration Management

### Environment Variables

Each component supports environment-specific configuration:

```bash
# ETL Configuration
ETL_INPUT_DIR=data/aasx-examples
ETL_OUTPUT_DIR=output/etl_results
ETL_CONFIG_FILE=scripts/config_etl.yaml

# Knowledge Graph Configuration
KG_DATA_DIR=data/graph_data
KG_API_PORT=8004
NEO4J_URI=neo4j://localhost:7687

# AI/RAG Configuration
RAG_QUERY_NAME=quality_issues
RAG_ANALYSIS_TYPE=quality
RAG_COLLECTION=aasx_assets
```

### Configuration Files

- **ETL**: `scripts/config_etl.yaml`
- **AI/RAG**: `config/ai_rag_queries.yaml`
- **Knowledge Graph**: `backend/kg_neo4j/config.py`

## 📊 Monitoring and Management

### Status Monitoring

```bash
# Check all independent components
./scripts/run_etl_docker.sh --status
./scripts/run_knowledge_graph.sh --status
./scripts/run_ai_rag_docker.sh --status

# Check framework
docker-compose -f manifests/framework/docker-compose.yml ps
```

### Log Management

```bash
# View logs for independent components
./scripts/run_etl_docker.sh --logs
./scripts/run_knowledge_graph.sh --logs
./scripts/run_ai_rag_docker.sh --logs

# View framework logs
docker-compose -f manifests/framework/docker-compose.yml logs -f
```

### Cleanup Operations

```bash
# Clean independent components
./scripts/run_etl_docker.sh --clean
./scripts/run_knowledge_graph.sh --clean
./scripts/run_ai_rag_docker.sh --clean

# Clean framework
docker-compose -f manifests/framework/docker-compose.yml down -v
```

## 🔐 Security Considerations

### Development vs Production

- **Development**: Default passwords, local access
- **Production**: Secure credentials, network isolation
- **Environment Variables**: Use `.env` files for sensitive data

### Access Control

- **Neo4j**: Username/password authentication
- **Qdrant**: API key authentication
- **AI/RAG**: OpenAI API key required
- **Web App**: Session-based authentication

## 📚 Best Practices

### Deployment Strategies

1. **Independent Deployment**: Start with individual components
2. **Integration Testing**: Test component interactions
3. **Full Framework**: Deploy complete system
4. **Production**: Use framework configurations

### Data Management

1. **Input Data**: Place AASX files in `data/aasx-examples/`
2. **Output Data**: Results stored in `output/etl_results/`
3. **Graph Data**: Processed data in `data/graph_data/`
4. **Backup**: Regular backups of databases and data

### Performance Optimization

1. **Resource Allocation**: Adjust memory/CPU limits
2. **Database Tuning**: Optimize Neo4j and Qdrant settings
3. **Caching**: Implement appropriate caching strategies
4. **Scaling**: Use Docker Swarm or Kubernetes for scaling

## 🆘 Troubleshooting

### Common Issues

1. **Port Conflicts**: Check port usage with `netstat`
2. **Memory Issues**: Increase Docker memory allocation
3. **Network Issues**: Verify Docker network connectivity
4. **Data Issues**: Check file permissions and paths

### Debug Commands

```bash
# Check Docker status
docker info
docker ps -a

# Check service logs
docker-compose -f manifests/independent/docker-compose.etl.yml logs

# Check resource usage
docker stats

# Check network connectivity
docker network ls
docker network inspect bridge
```

## 📈 Future Enhancements

### Planned Improvements

1. **Kubernetes Manifests**: K8s deployment configurations
2. **Helm Charts**: Package management for K8s
3. **Monitoring Stack**: Prometheus/Grafana integration
4. **CI/CD Pipelines**: Automated deployment workflows
5. **Multi-Environment**: Dev/Staging/Production configurations

### Extension Points

1. **Custom Components**: Add new independent components
2. **Plugin System**: Extensible architecture
3. **API Gateway**: Centralized API management
4. **Service Mesh**: Advanced networking features 