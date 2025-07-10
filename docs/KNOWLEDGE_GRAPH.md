# Knowledge Graph (Neo4j) Integration

## Overview

The Knowledge Graph module provides comprehensive Neo4j integration for the AASX Digital Twin Analytics Framework, enabling advanced graph analytics on Asset Administrative Shell (AAS) data. This includes both backend processing capabilities and frontend visualization interfaces.

## 🚀 Quick Start

### 1. Environment Setup

The system automatically uses your existing `.env` file. If you need to update it with complete Neo4j configuration:

```bash
python scripts/update_env.py
```

Your `.env` file should contain:
```env
# Neo4j Local Configuration
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_actual_password
NEO4J_DATABASE=neo4j
```

### 2. Install Dependencies

```bash
pip install -r requirements_aasx.txt
```

### 3. Test Integration

```bash
python test/kg_neo4j/run_all_neo4j_tests.py
```

### 4. Import ETL Data

```bash
python scripts/integrate_neo4j.py --import-dir data/outputs
```

### 5. Run Analytics

```bash
python scripts/integrate_neo4j.py --analyze --export-csv results.xlsx
```

## 🎯 What's Available

✅ **Environment Variable Support** - All components read from `.env`  
✅ **Automatic Configuration** - No need to pass connection params  
✅ **CLI Integration** - Easy command-line operations  
✅ **ETL Pipeline Integration** - Direct import from your ETL outputs  
✅ **Advanced Analytics** - Quality analysis, compliance checks, etc.  
✅ **Pre-built Queries** - Common operations ready to use  
✅ **Web Interface** - Interactive graph visualization and query interface  

## Backend Components

### Neo4jManager

Handles core Neo4j operations including:
- Connection management
- Graph data import from ETL pipeline output
- Basic query execution
- Database maintenance (indexes, cleanup)

```python
from backend.kg_neo4j import Neo4jManager

# Initialize manager (uses .env automatically)
manager = Neo4jManager()

# Import graph data
manager.import_graph_file("output/etl_results/file/aasx_data_graph.json")

# Execute custom query
results = manager.execute_query("MATCH (n:Node) RETURN count(n)")
```

### AASXGraphAnalyzer

Provides advanced analytics capabilities:
- Network statistics
- Quality distribution analysis
- Compliance analysis
- Relationship analysis
- Path finding
- Entity search

```python
from backend.kg_neo4j import AASXGraphAnalyzer

# Initialize analyzer (uses .env automatically)
analyzer = AASXGraphAnalyzer()

# Get quality distribution
quality_df = analyzer.get_quality_distribution()

# Find related entities
related_df = analyzer.find_related_entities("asset_001", max_depth=2)

# Analyze compliance
compliance_df = analyzer.analyze_compliance_network()
```

### CypherQueries

Collection of pre-built queries for common operations:
- Basic statistics
- Quality analysis
- Compliance analysis
- Relationship analysis
- Path analysis
- Search operations

```python
from backend.kg_neo4j import CypherQueries

# Use pre-built queries
query = CypherQueries.QUALITY_DISTRIBUTION
query = CypherQueries.find_related_entities("asset_001", max_depth=2)
query = CypherQueries.get_entities_by_quality("HIGH", "asset")
```

## Frontend Interface

### Graph Visualization
- Interactive D3.js-based graph visualization
- Zoom, pan, and drag functionality
- Node and relationship highlighting
- Tooltips with detailed information
- Color-coded nodes by type (assets, submodels)

### Cypher Query Interface
- Syntax-highlighted Cypher query editor
- Pre-built query templates
- Real-time query execution
- Tabular results display
- Query history and management

### Analytics Dashboard
- Quality distribution charts
- Entity type statistics
- Compliance metrics
- Interactive charts using Chart.js
- Real-time data updates

### Data Import
- ETL output directory import
- Batch processing capabilities
- Import status monitoring
- Database clearing options
- Progress tracking

### Connection Management
- Real-time connection status
- Connection health monitoring
- Automatic reconnection
- Error handling and notifications

## 🔧 Usage Examples

### Simple Import

```bash
# Import all graph files from ETL output
python scripts/integrate_neo4j.py --import-dir data/outputs

# Import specific file
python scripts/integrate_neo4j.py --import-file data/outputs/file/aasx_data_graph.json

# Dry run (see what would be imported)
python scripts/integrate_neo4j.py --import-dir data/outputs --dry-run
```

### Run Analysis

```bash
# Run comprehensive analysis
python scripts/integrate_neo4j.py --analyze

# Export analysis to Excel
python scripts/integrate_neo4j.py --analyze --export-csv results.xlsx

# Verbose output
python scripts/integrate_neo4j.py --analyze --verbose
```

### Custom Query

```bash
# Execute custom Cypher query
python scripts/integrate_neo4j.py --query "MATCH (n:Node) RETURN count(n)"

# Find high-quality assets
python scripts/integrate_neo4j.py --query "MATCH (n:Node {type: 'asset'}) WHERE n.quality_level = 'HIGH' RETURN n.id, n.description"

# Get relationship statistics
python scripts/integrate_neo4j.py --query "MATCH ()-[r:RELATES_TO]->() RETURN type(r), count(r)"
```

### Python API Examples

#### Basic Import and Analysis

```python
from backend.kg_neo4j import Neo4jManager, AASXGraphAnalyzer

# Import data (uses .env automatically)
manager = Neo4jManager()
manager.import_graph_file("aasx_data_graph.json")

# Analyze data
analyzer = AASXGraphAnalyzer()
stats = analyzer.get_network_statistics()
quality = analyzer.get_quality_distribution()
```

#### Advanced Analytics

```python
# Find high-quality assets
high_quality = analyzer.get_high_quality_assets("HIGH")

# Get compliance summary
compliance = analyzer.get_compliance_summary()

# Find isolated nodes
isolated = analyzer.find_isolated_nodes()

# Analyze relationships
relationships = analyzer.analyze_relationships()
```

## Web Interface Usage

### Accessing the Interface
1. Start the web application: `python main.py`
2. Navigate to `/kg-neo4j` in your browser
3. Check connection status
4. Import data from ETL output
5. Explore graph visualization
6. Execute Cypher queries
7. View analytics dashboard

### Interactive Features
- **Graph Navigation**: Zoom, pan, and explore the knowledge graph
- **Node Selection**: Click nodes to view detailed information
- **Query Execution**: Write and run custom Cypher queries
- **Analytics**: View charts and statistics
- **Data Import**: Upload and process new data

## API Endpoints

### Backend APIs
- `/api/kg-neo4j/status` - Connection status
- `/api/kg-neo4j/stats` - Database statistics
- `/api/kg-neo4j/graph-data` - Graph visualization data
- `/api/kg-neo4j/query` - Cypher query execution
- `/api/kg-neo4j/analytics` - Analytics data
- `/api/kg-neo4j/import` - Data import functionality

## Testing

### Test Coverage

#### 1. Environment Variables Test
- ✅ Load `.env` file
- ✅ Read Neo4j configuration
- ✅ Validate required variables

#### 2. Module Imports Test
- ✅ Import Neo4jManager
- ✅ Import AASXGraphAnalyzer
- ✅ Import CypherQueries

#### 3. Connection Test
- ✅ Neo4j database connection
- ✅ Authentication validation
- ✅ Version detection
- ✅ Error handling

#### 4. Graph Validation Test
- ✅ Valid graph data structure
- ✅ Invalid data rejection
- ✅ Format validation

#### 5. Cypher Queries Test
- ✅ Static query generation
- ✅ Dynamic query building
- ✅ Query validation

#### 6. ETL Integration Test
- ✅ ETL output directory detection
- ✅ Graph file discovery
- ✅ File format validation
- ✅ Data structure validation

#### 7. Data Import Test
- ✅ Graph data validation
- ✅ Import execution
- ✅ Database statistics

### Running Tests

```bash
# Run all Neo4j tests
python test/kg_neo4j/run_all_neo4j_tests.py

# Run individual tests
python test/kg_neo4j/test_neo4j_connection.py
python test/kg_neo4j/test_password_validation.py
python test/kg_neo4j/test_data_import.py
python test/kg_neo4j/test_neo4j_integration.py
```

## Docker Integration

### Running in Docker

```bash
# Build and run knowledge graph container
docker-compose -f manifests/independent/docker-compose.knowledge-graph.yml up --build

# Run with custom configuration
docker run -e NEO4J_URI=neo4j://host.docker.internal:7687 \
           -e NEO4J_USER=neo4j \
           -e NEO4J_PASSWORD=your_password \
           aasx-knowledge-graph
```

### Docker Compose Configuration
```yaml
version: '3.8'
services:
  knowledge-graph:
    build:
      context: .
      dockerfile: docker/Dockerfile.knowledge-graph
    environment:
      - NEO4J_URI=neo4j://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=your_password
    volumes:
      - ./output:/app/output
      - ./data:/app/data
    depends_on:
      - neo4j
```

## Troubleshooting

### Common Issues

#### 1. Connection Failed
```
❌ Neo4j connection error: Authentication failure
```
**Solution**: Check Neo4j credentials in `.env` file

#### 2. Module Import Error
```
✗ Import error: No module named 'kg_neo4j'
```
**Solution**: Ensure backend directory is in Python path

#### 3. ETL Output Not Found
```
✗ ETL output directory not found
```
**Solution**: Run ETL pipeline first: `python scripts/run_etl.py`

#### 4. Graph Files Missing
```
✗ No graph files found in ETL output
```
**Solution**: Ensure ETL pipeline generates `*_graph.json` files

### Debug Commands

#### Test Connection Only
```bash
python test/kg_neo4j/test_neo4j_connection.py
```

#### Test Password
```bash
python test/kg_neo4j/test_password_validation.py
```

#### Check Environment
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('NEO4J_URI:', os.getenv('NEO4J_URI')); print('NEO4J_USER:', os.getenv('NEO4J_USER')); print('NEO4J_PASSWORD:', '*' * len(os.getenv('NEO4J_PASSWORD', '')))"
```

## Performance Optimization

### Large Dataset Handling
```python
# Batch processing for large datasets
manager.import_graph_file_batch("large_dataset.json", batch_size=1000)

# Memory optimization
analyzer.set_memory_limit("2GB")
```

### Query Optimization
```python
# Use indexed properties
query = "MATCH (n:Asset {id: $asset_id}) RETURN n"

# Limit result sets
query = "MATCH (n:Node) RETURN n LIMIT 1000"

# Use parameterized queries
params = {"asset_id": "asset_001"}
results = manager.execute_query(query, params)
```

## Future Enhancements

### Planned Features
- Advanced graph algorithms
- Machine learning integration
- Real-time collaboration
- Enhanced visualization options
- Automated graph optimization
- Integration with additional graph databases 