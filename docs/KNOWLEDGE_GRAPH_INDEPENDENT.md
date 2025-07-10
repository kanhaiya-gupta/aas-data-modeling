# 🧠 Knowledge Graph System (Independent)

This document describes the **Knowledge Graph System** that can operate independently without requiring the ETL pipeline. Perfect for scenarios where you already have processed data in the desired format.

## 🎯 Overview

The Knowledge Graph System is designed to work with:
- **Pre-processed graph data** (JSON, CSV, Cypher, GraphML)
- **Existing Neo4j databases**
- **Direct data imports** via Neo4j browser
- **API-based data loading**

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Graph Data    │───▶│  Knowledge       │───▶│   Neo4j DB      │
│   (Pre-processed)│   │  Graph API       │    │   (Port 7474)   │
│   - JSON        │    │  (Port 8004)     │    │                 │
│   - CSV         │    │                  │    │                 │
│   - Cypher      │    │                  │    │                 │
│   - GraphML     │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file with configuration
- Graph data in supported formats

### Option 1: Automated Script (Recommended)

**Linux/Mac:**
```bash
chmod +x scripts/run_knowledge_graph.sh
./scripts/run_knowledge_graph.sh
```

**Windows:**
```cmd
scripts\run_knowledge_graph.bat
```

### Option 2: Manual Docker Compose

```bash
# Build and start knowledge graph services
docker-compose -f docker-compose.knowledge-graph.yml up -d

# View logs
docker-compose -f docker-compose.knowledge-graph.yml logs -f

# Stop services
docker-compose -f docker-compose.knowledge-graph.yml down
```

### Option 3: Individual Container

```bash
# Build knowledge graph image
docker build -f docker/Dockerfile.knowledge-graph -t aas-kg .

# Run container
docker run -p 8004:8004 -v $(pwd)/data:/app/data aas-kg
```

## 📊 Service Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Knowledge Graph API | http://localhost:8004 | Graph analysis and queries |
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

# Knowledge Graph Configuration
DATA_SOURCE=neo4j
GRAPH_DATA_DIR=/app/data/graph_data
PROCESSED_DATA_DIR=/app/data/processed
ENABLE_ETL_INTEGRATION=false

# Logging
LOG_LEVEL=INFO
```

### Data Directory Structure

```
project/
├── data/
│   ├── graph_data/        # Pre-processed graph data
│   │   ├── nodes.json     # Node data
│   │   ├── edges.csv      # Edge data
│   │   ├── schema.cypher  # Schema definitions
│   │   └── graph.graphml  # GraphML format
│   └── processed/         # Processed data cache
├── output/                # Analysis results
└── logs/                  # Application logs
```

## 📁 Supported Data Formats

### 1. JSON Format
```json
{
  "nodes": [
    {"id": "1", "label": "Asset", "properties": {"name": "Motor", "type": "Component"}},
    {"id": "2", "label": "Asset", "properties": {"name": "Sensor", "type": "Component"}}
  ],
  "relationships": [
    {"source": "1", "target": "2", "type": "MONITORS", "properties": {"since": "2024-01-01"}}
  ]
}
```

### 2. CSV Format
```csv
# nodes.csv
id,label,name,type
1,Asset,Motor,Component
2,Asset,Sensor,Component

# relationships.csv
source,target,type,since
1,2,MONITORS,2024-01-01
```

### 3. Cypher Scripts
```cypher
// Create nodes
CREATE (m:Asset {name: 'Motor', type: 'Component'})
CREATE (s:Asset {name: 'Sensor', type: 'Component'})

// Create relationships
CREATE (m)-[:MONITORS {since: '2024-01-01'}]->(s)
```

### 4. GraphML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <graph id="G" edgedefault="directed">
    <node id="1">
      <data key="name">Motor</data>
      <data key="type">Component</data>
    </node>
    <edge source="1" target="2">
      <data key="type">MONITORS</data>
    </edge>
  </graph>
</graphml>
```

## 📈 Usage Examples

### Knowledge Graph API

```bash
# Health check
curl http://localhost:8004/health

# Load data from files
curl -X POST http://localhost:8004/load \
  -H "Content-Type: application/json" \
  -d '{"source": "file", "path": "data/graph_data/nodes.json"}'

# Run Cypher query
curl -X POST http://localhost:8004/query \
  -H "Content-Type: application/json" \
  -d '{"query": "MATCH (n:Asset) RETURN n.name, n.type LIMIT 10"}'

# Get graph statistics
curl http://localhost:8004/stats

# Find shortest path
curl -X POST http://localhost:8004/path \
  -H "Content-Type: application/json" \
  -d '{"start": "Motor", "end": "Sensor", "max_depth": 3}'
```

### Neo4j Browser

1. Open http://localhost:7474
2. Login with:
   - Username: `neo4j`
   - Password: `Neo4j123`
3. Run Cypher queries directly

**Example Queries:**
```cypher
// Count all nodes
MATCH (n) RETURN count(n) as total_nodes

// Find all assets
MATCH (a:Asset) RETURN a.name, a.type

// Find relationships
MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name

// Graph visualization
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50
```

## 🧪 Testing

Run the knowledge graph test suite:

```bash
python scripts/test_knowledge_graph.py
```

This will test:
- ✅ Knowledge Graph API health
- ✅ Neo4j database connectivity
- ✅ Data directory structure
- ✅ Graph data file availability
- ✅ Query functionality
- ✅ Data loading API

## 🔍 Monitoring

### Health Checks
```bash
# Check service status
docker-compose -f docker-compose.knowledge-graph.yml ps

# View service logs
docker-compose -f docker-compose.knowledge-graph.yml logs -f knowledge-graph
docker-compose -f docker-compose.knowledge-graph.yml logs -f neo4j
```

### Performance Monitoring
- Graph query response times
- Database connection status
- Memory and CPU usage
- Data loading performance

## 🛠️ Development

### Building Images
```bash
# Build with no cache
docker-compose -f docker-compose.knowledge-graph.yml build --no-cache

# Build specific service
docker-compose -f docker-compose.knowledge-graph.yml build knowledge-graph
```

### Debugging
```bash
# Run in interactive mode
docker-compose -f docker-compose.knowledge-graph.yml run --rm knowledge-graph bash

# View real-time logs
docker-compose -f docker-compose.knowledge-graph.yml logs -f --tail=100
```

## 🔒 Security

### Container Security
- Non-root user execution
- Minimal base image (python:3.11-slim)
- No unnecessary packages

### Data Security
- Volume mounts for persistent data
- Environment variables for sensitive config
- Network isolation

## 📚 Integration

### With External Data Sources
```bash
# Load from external API
curl -X POST http://localhost:8004/load \
  -H "Content-Type: application/json" \
  -d '{"source": "api", "url": "https://api.example.com/graph-data"}'

# Load from database
curl -X POST http://localhost:8004/load \
  -H "Content-Type: application/json" \
  -d '{"source": "database", "connection": "postgresql://..."}'
```

### With Other Systems
- REST APIs for integration
- Standard Neo4j protocols
- JSON data formats
- Docker containerization

## 🚨 Troubleshooting

### Common Issues

**Knowledge Graph API not starting:**
```bash
# Check logs
docker-compose -f docker-compose.knowledge-graph.yml logs knowledge-graph

# Verify environment variables
docker-compose -f docker-compose.knowledge-graph.yml config
```

**Neo4j connection failed:**
```bash
# Check Neo4j status
docker-compose -f docker-compose.knowledge-graph.yml logs neo4j

# Verify Neo4j credentials
curl -u neo4j:Neo4j123 http://localhost:7474/browser/
```

**Data loading issues:**
```bash
# Check data directory permissions
ls -la data/graph_data/

# Verify file formats
file data/graph_data/*.json
```

### Performance Issues

**Slow queries:**
- Add database indexes
- Optimize Cypher queries
- Consider query caching
- Monitor query execution plans

**Memory issues:**
- Increase container memory limits
- Optimize data loading
- Use pagination for large results

## 📖 Data Loading Workflows

### 1. File-Based Loading
```bash
# Place data files
cp your-graph-data.json data/graph_data/

# Load via API
curl -X POST http://localhost:8004/load \
  -d '{"source": "file", "path": "data/graph_data/your-graph-data.json"}'
```

### 2. Direct Neo4j Import
```bash
# Copy files to Neo4j import directory
cp your-data.csv data/graph_data/

# Use Neo4j browser to import
LOAD CSV WITH HEADERS FROM 'file:///your-data.csv' AS row
CREATE (:Node {name: row.name, type: row.type})
```

### 3. API-Based Loading
```bash
# Load from external source
curl -X POST http://localhost:8004/load \
  -d '{"source": "api", "url": "https://your-api.com/graph-data"}'
```

## 📖 Next Steps

1. **Prepare Data**: Format your data in supported formats
2. **Load Data**: Use the provided loading methods
3. **Explore Graph**: Use Neo4j browser for visualization
4. **Build Queries**: Create custom Cypher queries
5. **Integrate**: Connect with other systems
6. **Scale**: Add more processing power as needed

## 🤝 Support

For issues and questions:
- Check the troubleshooting section
- Review service logs
- Test with the provided test script
- Consult the main project documentation

---

**🎉 You're now ready to work with pre-processed graph data independently!** 