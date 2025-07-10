# 🚀 Core Components: ETL Pipeline + Knowledge Graph

This document describes the **heart of the AAS Data Modeling Framework** - the ETL Pipeline and Knowledge Graph components that form the foundation of the entire system.

## 🎯 Overview

The core components consist of:

1. **ETL Pipeline** - Processes AASX files and extracts structured data
2. **Knowledge Graph** - Neo4j-based graph database for data analysis
3. **Neo4j Database** - Graph database backend

These components can be run independently from the full framework, making them perfect for:
- Quick prototyping
- Data processing workflows
- Graph analysis tasks
- Integration with other systems

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AASX Files    │───▶│   ETL Pipeline   │───▶│  Knowledge      │
│   (Input)       │    │   (Port 8003)    │    │  Graph          │
└─────────────────┘    └──────────────────┘    │  (Port 8004)    │
                                               └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   Neo4j DB      │
                                               │   (Port 7474)   │
                                               └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file with configuration (see `.env.example`)

### Option 1: Automated Script (Recommended)

**Linux/Mac:**
```bash
chmod +x scripts/run_core.sh
./scripts/run_core.sh
```

**Windows:**
```cmd
scripts\run_core.bat
```

### Option 2: Manual Docker Compose

```bash
# Build and start core services
docker-compose -f docker-compose.core.yml up -d

# View logs
docker-compose -f docker-compose.core.yml logs -f

# Stop services
docker-compose -f docker-compose.core.yml down
```

### Option 3: Individual Containers

```bash
# Build individual images
docker build -f docker/Dockerfile.etl-pipeline -t aas-etl .
docker build -f docker/Dockerfile.knowledge-graph -t aas-kg .

# Run containers
docker run -p 8003:8003 -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output aas-etl
docker run -p 8004:8004 -v $(pwd)/output:/app/output aas-kg
```

## 📊 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| ETL Pipeline | http://localhost:8003 | Process AASX files |
| Knowledge Graph | http://localhost:8004 | Graph analysis API |
| Neo4j Browser | http://localhost:7474 | Database interface |
| Neo4j Bolt | bolt://localhost:7687 | Database connection |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123

# ETL Configuration
ETL_CONFIG_PATH=/app/scripts/config_etl.yaml
OUTPUT_DIR=/app/output/etl_results
LOG_LEVEL=INFO

# Optional: OpenAI for enhanced processing
OPENAI_API_KEY=your_openai_api_key_here
```

### Data Directories

```
project/
├── data/
│   └── aasx-examples/     # Place AASX files here
├── output/
│   └── etl_results/       # ETL processing results
└── logs/                  # Application logs
```

## 📁 Data Flow

### 1. Input Preparation
Place AASX files in `./data/aasx-examples/`:
```bash
cp your-file.aasx data/aasx-examples/
```

### 2. ETL Processing
The ETL pipeline will:
- Parse AASX files
- Extract structured data
- Transform to graph format
- Load into Neo4j

### 3. Knowledge Graph Analysis
Access the knowledge graph for:
- Graph queries
- Data analysis
- Relationship exploration

## 🧪 Testing

Run the core component test suite:

```bash
python scripts/test_core.py
```

This will test:
- ✅ ETL Pipeline health
- ✅ Knowledge Graph health
- ✅ Neo4j database connectivity
- ✅ Data directory structure
- ✅ AASX file availability

## 📈 Usage Examples

### ETL Pipeline API

```bash
# Health check
curl http://localhost:8003/health

# Process AASX file
curl -X POST http://localhost:8003/process \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/aasx-examples/example.aasx"}'

# Get processing status
curl http://localhost:8003/status
```

### Knowledge Graph API

```bash
# Health check
curl http://localhost:8004/health

# Run Cypher query
curl -X POST http://localhost:8004/query \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (n) RETURN count(n)"}'

# Get graph statistics
curl http://localhost:8004/stats
```

### Neo4j Browser

1. Open http://localhost:7474
2. Login with:
   - Username: `neo4j`
   - Password: `Neo4j123`
3. Run Cypher queries directly

## 🔍 Monitoring

### Health Checks
All services include built-in health checks:

```bash
# Check all services
docker-compose -f docker-compose.core.yml ps

# View service logs
docker-compose -f docker-compose.core.yml logs -f etl-pipeline
docker-compose -f docker-compose.core.yml logs -f knowledge-graph
docker-compose -f docker-compose.core.yml logs -f neo4j
```

### Performance Monitoring
- ETL processing time
- Graph query performance
- Database connection status
- Memory and CPU usage

## 🛠️ Development

### Building Images

```bash
# Build with no cache
docker-compose -f docker-compose.core.yml build --no-cache

# Build specific service
docker-compose -f docker-compose.core.yml build etl-pipeline
docker-compose -f docker-compose.core.yml build knowledge-graph
```

### Debugging

```bash
# Run in interactive mode
docker-compose -f docker-compose.core.yml run --rm etl-pipeline bash
docker-compose -f docker-compose.core.yml run --rm knowledge-graph bash

# View real-time logs
docker-compose -f docker-compose.core.yml logs -f --tail=100
```

## 🔒 Security

### Container Security
- All containers run as non-root users
- Minimal base images (python:3.11-slim)
- No unnecessary packages installed

### Data Security
- Volume mounts for persistent data
- Environment variables for sensitive config
- Network isolation between services

## 📚 Integration

### With Full Framework
The core components can be integrated with the full framework:

```bash
# Start core components first
docker-compose -f docker-compose.core.yml up -d

# Then start additional services
docker-compose -f docker-compose.framework.yml up -d
```

### With External Systems
- REST APIs for integration
- Standard Neo4j protocols
- JSON data formats
- Docker containerization

## 🚨 Troubleshooting

### Common Issues

**ETL Pipeline not starting:**
```bash
# Check logs
docker-compose -f docker-compose.core.yml logs etl-pipeline

# Verify data directory permissions
ls -la data/aasx-examples/
```

**Knowledge Graph connection failed:**
```bash
# Check Neo4j status
docker-compose -f docker-compose.core.yml logs neo4j

# Verify Neo4j credentials
curl -u neo4j:Neo4j123 http://localhost:7474/browser/
```

**Neo4j not accessible:**
```bash
# Restart Neo4j
docker-compose -f docker-compose.core.yml restart neo4j

# Check port conflicts
netstat -tulpn | grep 7474
```

### Performance Issues

**Slow ETL processing:**
- Check available memory
- Verify disk space
- Monitor CPU usage

**Graph query timeouts:**
- Optimize Cypher queries
- Add database indexes
- Consider query caching

## 📖 Next Steps

1. **Process Data**: Add AASX files and run ETL pipeline
2. **Explore Graph**: Use Neo4j browser for data exploration
3. **Build Queries**: Create custom Cypher queries
4. **Integrate**: Connect with other systems
5. **Scale**: Add more processing power as needed

## 🤝 Support

For issues and questions:
- Check the troubleshooting section
- Review service logs
- Test with the provided test script
- Consult the main project documentation

---

**🎉 You're now ready to process AASX data and build knowledge graphs!** 