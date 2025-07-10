# Docker Configuration

This folder contains all Dockerfiles for the AAS Data Modeling Framework.

## 📁 File Structure

```
docker/
├── README.md                    # This file
├── Dockerfile.etl-pipeline     # 🚀 ETL Pipeline (Heart of Project)
├── Dockerfile.knowledge-graph  # 🧠 Knowledge Graph System
├── Dockerfile.webapp           # Main web application
├── Dockerfile.ai-rag           # AI/RAG system with GPT-4.1-mini
├── Dockerfile.twin-registry    # Digital twin registry
├── Dockerfile.certificate-manager # Certificate management
└── Dockerfile.qi-analytics     # Quality infrastructure analytics
```

## 🐳 Dockerfiles Overview

### 🚀 Core Components (Essential)

#### Dockerfile.etl-pipeline
- **Base Image**: `python:3.11-slim` + **.NET 6.0 SDK**
- **Purpose**: **ETL Pipeline - Heart of the Project**
- **Port**: 8003
- **Features**: AASX file processing, data extraction, transformation, loading
- **Dependencies**: 
  - XML processing, JSON handling, data validation
  - **.NET 6.0 SDK** for aas-processor integration
  - **AAS Core 3.0** libraries for advanced AASX processing

#### Dockerfile.knowledge-graph
- **Base Image**: `python:3.11-slim`
- **Purpose**: **Knowledge Graph System with Neo4j**
- **Port**: 8004
- **Features**: Graph database operations, Cypher queries, graph analysis
- **Dependencies**: Neo4j driver, graph algorithms, data visualization

### 🔧 Additional Services

#### Dockerfile.webapp
- **Base Image**: `python:3.11-slim`
- **Purpose**: Main web application interface
- **Port**: 5000
- **Features**: Flask web server, static file serving, API routing

#### Dockerfile.ai-rag
- **Base Image**: `python:3.11-slim`
- **Purpose**: AI/RAG system with OpenAI integration
- **Port**: 8000
- **Features**: GPT-4.1-mini model, vector search, graph analysis

### Dockerfile.twin-registry
- **Base Image**: `python:3.11-slim`
- **Purpose**: Digital twin management and registry
- **Port**: 8001
- **Features**: Twin registration, lifecycle management, synchronization

### Dockerfile.certificate-manager
- **Base Image**: `node:18-alpine`
- **Purpose**: Digital certificate management
- **Port**: 3001
- **Features**: Certificate storage, validation, lifecycle management

### Dockerfile.qi-analytics
- **Base Image**: `node:18-alpine`
- **Purpose**: Quality infrastructure analytics dashboard
- **Port**: 3002
- **Features**: Data visualization, reporting, analytics

## 🔧 Common Features

All Dockerfiles include:

- **Health Checks**: Built-in monitoring for container health
- **Environment Variables**: Configurable settings
- **Volume Mounts**: Persistent data storage
- **Security**: Non-root user execution (where applicable)
- **Optimization**: Multi-stage builds and caching

## 🚀 Usage

### Option 1: Core Components Only (Recommended for Start)
Run just the essential ETL pipeline and knowledge graph:

```bash
# Linux/Mac
./scripts/run_core.sh

# Windows
scripts\run_core.bat
```

Or manually:
```bash
# Build and start core services
docker-compose -f docker-compose.core.yml build
docker-compose -f docker-compose.core.yml up -d

# View logs
docker-compose -f docker-compose.core.yml logs -f

# Stop services
docker-compose -f docker-compose.core.yml down
```

### Option 1.5: Knowledge Graph Only (Independent)
Run just the knowledge graph system with pre-processed data:

```bash
# Linux/Mac
./scripts/run_knowledge_graph.sh

# Windows
scripts\run_knowledge_graph.bat
```

Or manually:
```bash
# Build and start knowledge graph services
docker-compose -f docker-compose.knowledge-graph.yml build
docker-compose -f docker-compose.knowledge-graph.yml up -d

# View logs
docker-compose -f docker-compose.knowledge-graph.yml logs -f

# Stop services
docker-compose -f docker-compose.knowledge-graph.yml down
```

### Option 2: Full Framework
These Dockerfiles are used by the main docker-compose configuration:

```bash
# Build all services
docker-compose -f docker-compose.framework.yml build

# Run the complete framework
docker-compose -f docker-compose.framework.yml up -d
```

### Individual Services
You can also run individual services:

```bash
# Build specific service
docker build -f docker/Dockerfile.etl-pipeline -t aas-etl .
docker build -f docker/Dockerfile.knowledge-graph -t aas-kg .

# Run specific service
docker run -p 8003:8003 aas-etl
docker run -p 8004:8004 aas-kg
```

### Testing
Test the systems:

```bash
# Test core components
python scripts/test_core.py

# Test knowledge graph only
python scripts/test_knowledge_graph.py

# Test ETL pipeline with aas-processor integration
python scripts/test_etl_with_processor.py
```

## 📝 Customization

To customize any service:

1. **Modify the Dockerfile** in this folder
2. **Update environment variables** in docker-compose.framework.yml
3. **Rebuild the specific service**:
   ```bash
   docker-compose -f docker-compose.framework.yml build [service-name]
   ```

## 🔍 Troubleshooting

### Build Issues
- Check base image availability
- Verify file paths in COPY commands
- Ensure all dependencies are included

### Runtime Issues
- Check health check endpoints
- Verify port mappings
- Review environment variable configuration

### Performance Issues
- Optimize layer caching
- Use multi-stage builds where appropriate
- Consider resource limits in docker-compose 