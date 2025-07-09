# Neo4j Backend Module

This module provides comprehensive Neo4j integration for the AASX Data Modeling Platform, enabling advanced graph analytics on Asset Administrative Shell (AAS) data.

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
python scripts/test_neo4j_integration.py
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

## Overview

The Neo4j backend module consists of three main components:

1. **Neo4jManager**: Core database operations and data import
2. **AASXGraphAnalyzer**: Advanced graph analytics and query operations
3. **CypherQueries**: Pre-built Cypher queries for common operations

## Components

### Neo4jManager

Handles core Neo4j operations including:
- Connection management
- Graph data import from ETL pipeline output
- Basic query execution
- Database maintenance (indexes, cleanup)

```python
from kg_neo4j import Neo4jManager

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
from kg_neo4j import AASXGraphAnalyzer

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
from kg_neo4j import CypherQueries

# Use pre-built queries
query = CypherQueries.QUALITY_DISTRIBUTION
query = CypherQueries.find_related_entities("asset_001", max_depth=2)
query = CypherQueries.get_entities_by_quality("HIGH", "asset")
```

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
from kg_neo4j import Neo4jManager, AASXGraphAnalyzer

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

# Search for entities
results = analyzer.search_entities("motor", "asset")

# Get quality distribution
quality_dist = analyzer.get_quality_distribution()

# Analyze compliance network
compliance_analysis = analyzer.analyze_compliance_network()

# Get entity type distribution
entity_dist = analyzer.get_entity_type_distribution()

# Analyze relationships
relationship_analysis = analyzer.analyze_relationships()
```

#### Custom Queries

```python
# Execute custom Cypher query
custom_query = """
MATCH (n:Node {type: 'asset'})
WHERE n.quality_level = 'HIGH'
RETURN n.id, n.description
ORDER BY n.description
"""
results = manager.execute_query(custom_query)

# Use pre-built queries
from kg_neo4j import CypherQueries

# Basic statistics
stats_query = CypherQueries.BASIC_STATS
results = manager.execute_query(stats_query)

# Quality distribution
quality_query = CypherQueries.QUALITY_DISTRIBUTION
results = manager.execute_query(quality_query)

# Find related entities
related_query = CypherQueries.find_related_entities("asset_001", 2)
results = manager.execute_query(related_query)

# Get entities by quality
quality_assets = CypherQueries.get_entities_by_quality("HIGH", "asset")
results = manager.execute_query(quality_assets)
```

## Integration with ETL Pipeline

The Neo4j module integrates seamlessly with the AASX ETL pipeline:

1. **ETL Pipeline** generates graph format files (`*_graph.json`)
2. **Neo4jManager** imports these files to Neo4j
3. **AASXGraphAnalyzer** provides analytics on the imported data

### Complete Workflow

```python
# 1. Run ETL pipeline (generates graph files)
# python scripts/run_etl.py

# 2. Import to Neo4j (uses .env automatically)
from kg_neo4j import Neo4jManager
manager = Neo4jManager()

# Import all graph files
import glob
for graph_file in glob.glob("output/etl_results/**/*_graph.json"):
    manager.import_graph_file(graph_file)

# 3. Analyze data
from kg_neo4j import AASXGraphAnalyzer
analyzer = AASXGraphAnalyzer()

# Run comprehensive analysis
stats = analyzer.get_network_statistics()
quality = analyzer.get_quality_distribution()
compliance = analyzer.analyze_compliance_network()
```

### CLI Workflow

```bash
# 1. Run ETL pipeline
python scripts/run_etl.py

# 2. Import to Neo4j
python scripts/integrate_neo4j.py --import-dir data/outputs

# 3. Run analysis
python scripts/integrate_neo4j.py --analyze --export-csv analysis_results.xlsx

# 4. Execute custom queries
python scripts/integrate_neo4j.py --query "MATCH (n:Node {type: 'asset'}) RETURN n.id, n.description"
```

## 🧪 Testing

### Test Integration

```bash
# Run comprehensive test suite
python scripts/test_neo4j_integration.py
```

This will test:
- ✅ Module imports
- ✅ Graph file validation
- ✅ Cypher queries generation
- ✅ ETL integration
- ✅ Neo4j connection (if Neo4j is running)

### Test Individual Components

```python
# Test Neo4j connection
from kg_neo4j import Neo4jManager
manager = Neo4jManager()
if manager.test_connection():
    print("✓ Neo4j connection successful")
else:
    print("✗ Neo4j connection failed")
```

## Configuration

### Neo4j Connection

Configure Neo4j connection parameters using environment variables or direct parameters:

```python
# Using environment variables (recommended)
# Set in .env file: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
manager = Neo4jManager()  # Automatically reads from .env

# Direct parameters
manager = Neo4jManager(
    uri="bolt://your-neo4j-server:7687",
    user="your-username",
    password="your-password"
)

# Mixed approach (env vars with overrides)
manager = Neo4jManager(
    uri="bolt://custom-server:7687",  # Override URI
    # user and password from .env
)
```

### Performance Optimization

Create indexes for better performance:

```python
# Create indexes
manager.create_indexes()

# Get database info
info = manager.get_database_info()
print(f"Nodes: {info['total_nodes']}")
print(f"Relationships: {info['total_relationships']}")
```

## Error Handling

The module includes comprehensive error handling:

```python
try:
    manager = Neo4jManager("bolt://localhost:7687", "neo4j", "password")
    
    # Test connection
    if not manager.test_connection():
        print("Failed to connect to Neo4j")
        exit(1)
    
    # Import data
    manager.import_graph_file("data.json")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    manager.close()
```

## Dependencies

Required Python packages:
- `neo4j`: Neo4j Python driver
- `pandas`: Data analysis and manipulation
- `pathlib`: Path operations

Install dependencies:
```bash
pip install neo4j pandas
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check Neo4j is running
   - Verify connection URI and credentials
   - Check firewall settings

2. **Import Errors**
   - Validate graph file format
   - Check file permissions
   - Ensure Neo4j has sufficient memory

3. **Performance Issues**
   - Create appropriate indexes
   - Use graph projections for algorithms
   - Monitor Neo4j memory usage

### Debug Mode

Enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Operations will now show detailed logs
manager = Neo4jManager("bolt://localhost:7687", "neo4j", "password")
```

## Next Steps

1. **Explore Graph Algorithms**: Try Neo4j Graph Data Science (GDS) algorithms
2. **Build Dashboards**: Create visualizations with Neo4j Bloom
3. **Real-time Updates**: Set up streaming updates from the ETL pipeline
4. **Advanced Analytics**: Implement custom graph algorithms
5. **Integration**: Connect with other tools in the QI platform

## 🚀 Advanced Features

### Environment Variable Support
- **Automatic Configuration**: All components read from `.env` file
- **Flexible Setup**: Override any parameter via command line or code
- **Secure**: No hardcoded credentials in code

### CLI Integration
- **Simple Commands**: Easy-to-use command-line interface
- **Batch Operations**: Import multiple files at once
- **Dry Run Mode**: Preview operations without executing
- **Export Options**: Results to CSV, Excel, or console

### ETL Pipeline Integration
- **Direct Import**: Import from ETL pipeline outputs
- **Graph Format Support**: Native support for `*_graph.json` files
- **Quality Metrics**: Automatic quality assessment
- **Validation**: Built-in data validation and error handling

### Advanced Analytics
- **Network Statistics**: Comprehensive graph metrics
- **Quality Analysis**: Quality distribution and scoring
- **Compliance Analysis**: Compliance status and trends
- **Relationship Analysis**: Entity relationship patterns
- **Path Finding**: Find connections between entities
- **Search Capabilities**: Full-text and semantic search

### Pre-built Queries
- **Common Operations**: Ready-to-use Cypher queries
- **Dynamic Generation**: Parameterized query building
- **Performance Optimized**: Indexed and optimized queries
- **Extensible**: Easy to add custom queries

### Data Management
- **Index Management**: Automatic index creation
- **Database Maintenance**: Cleanup and optimization
- **Connection Pooling**: Efficient resource management
- **Error Handling**: Robust error recovery

## 📚 Additional Resources

For more information, see the main [Neo4j Integration Guide](../../docs/NEO4J_INTEGRATION.md). 