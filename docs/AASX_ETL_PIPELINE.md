# AASX ETL Pipeline Documentation

## Overview

The AASX ETL (Extract, Transform, Load) Pipeline is a comprehensive data processing system designed for the Quality Infrastructure Digital Platform. It provides end-to-end processing of Asset Administration Shell (AAS) data from AASX packages, enabling advanced analytics, RAG (Retrieval-Augmented Generation) applications, and quality management workflows.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AASX Files    │───▶│  Extract Phase   │───▶│ Transform Phase │
│   (.aasx)       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Vector DB      │◀───│   Load Phase     │◀───│  Transformed    │
│  (ChromaDB)     │    │                  │    │     Data        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌──────────────────┐
│  RAG System     │    │  SQLite DB       │
│  (Semantic      │    │  (Structured     │
│   Search)       │    │   Storage)       │
└─────────────────┘    └──────────────────┘
```

## Components

### 1. Extract Phase (`aasx_processor.py`)

**Purpose**: Extract data from AASX packages (ZIP-based AAS containers)

**Features**:
- ZIP archive extraction
- JSON and XML parsing
- Asset and submodel extraction
- Document extraction
- Metadata extraction
- Hybrid Python/.NET processing

**Key Classes**:
- `AASXProcessor`: Main processor with fallback mechanisms
- `DotNetBridge`: Bridge to .NET AAS Core libraries

### 2. Transform Phase (`aasx_transformer.py`)

**Purpose**: Transform extracted data into standardized formats

**Features**:
- Data cleaning and normalization
- Quality checks and validation
- Data enrichment with QI metadata
- Multiple output formats (JSON, XML, CSV, YAML)
- Graph database format (Neo4j compatible)
- Analytics format (flattened for BI tools)
- API-ready format (for web services)

**Key Classes**:
- `AASXTransformer`: Main transformation engine
- `TransformerConfig`: Configuration for transformation options

### 3. Load Phase (`aasx_loader.py`)

**Purpose**: Load transformed data into various storage systems

**Features**:
- File export (JSON, YAML, CSV)
- SQLite database storage
- Vector database integration (ChromaDB, FAISS)
- Embedding generation for RAG
- Semantic search capabilities
- RAG-ready dataset export

**Key Classes**:
- `AASXLoader`: Main loader with multiple storage backends
- `LoaderConfig`: Configuration for loading options

### 4. ETL Pipeline (`aasx_etl_pipeline.py`)

**Purpose**: Orchestrate the complete ETL process

**Features**:
- End-to-end pipeline orchestration
- Batch processing capabilities
- Parallel processing support
- Error handling and recovery
- Comprehensive logging and statistics
- Pipeline validation
- Performance monitoring

**Key Classes**:
- `AASXETLPipeline`: Main pipeline orchestrator
- `ETLPipelineConfig`: Complete pipeline configuration

## Installation

### Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt

# Vector database dependencies (optional)
pip install chromadb sentence-transformers

# FAISS for vector search (optional)
pip install faiss-cpu  # or faiss-gpu for GPU support

# .NET 6.0 SDK (for advanced AAS processing)
# Download from: https://dotnet.microsoft.com/download
```

### .NET AAS Processor Setup

```bash
# Navigate to .NET processor directory
cd aas-processor

# Restore NuGet packages
dotnet restore

# Build the project
dotnet build

# Test the processor
dotnet run --project AasProcessor
```

## Usage

### Basic Usage

```python
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig

# Create pipeline configuration
config = ETLPipelineConfig(
    enable_validation=True,
    enable_logging=True,
    parallel_processing=False
)

# Create pipeline
pipeline = AASXETLPipeline(config)

# Process single file
result = pipeline.process_aasx_file("path/to/file.aasx")

# Process directory
batch_result = pipeline.process_aasx_directory("path/to/aasx/files")
```

### Advanced Configuration

```python
from webapp.aasx.aasx_etl_pipeline import ETLPipelineConfig
from webapp.aasx.aasx_transformer import TransformerConfig
from webapp.aasx.aasx_loader import LoaderConfig

# Configure transformation
transform_config = TransformerConfig(
    enable_quality_checks=True,
    enable_enrichment=True,
    output_formats=['json', 'csv', 'graph'],
    include_metadata=True
)

# Configure loading
load_config = LoaderConfig(
    output_directory="output",
    database_path="aasx_data.db",
    vector_db_path="vector_db",
    vector_db_type="chromadb",
    embedding_model="all-MiniLM-L6-v2"
)

# Create complete pipeline configuration
config = ETLPipelineConfig(
    transform_config=transform_config,
    load_config=load_config,
    parallel_processing=True,
    max_workers=4
)
```

### Batch Processing

```python
# Process multiple files in parallel
config = ETLPipelineConfig(parallel_processing=True, max_workers=4)
pipeline = AASXETLPipeline(config)

# Process entire directory
result = pipeline.process_aasx_directory("aasx_files/")

print(f"Processed: {result['files_processed']}")
print(f"Failed: {result['files_failed']}")
print(f"Total time: {result['total_time']:.2f}s")
```

### Vector Database Integration

```python
# Initialize pipeline with vector database
config = ETLPipelineConfig()
pipeline = AASXETLPipeline(config)

# Process files (automatically creates embeddings)
pipeline.process_aasx_file("file.aasx")

# Search for similar entities
results = pipeline.loader.search_similar(
    query="motor quality control",
    entity_type="asset",
    top_k=5
)

for result in results:
    print(f"ID: {result['id']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Content: {result['document']}")
```

### RAG Dataset Creation

```python
# Create RAG-ready dataset
pipeline = AASXETLPipeline()

# Process some files first
pipeline.process_aasx_directory("aasx_files/")

# Export RAG dataset
rag_path = pipeline.create_rag_ready_dataset("rag_dataset.json")
print(f"RAG dataset created: {rag_path}")
```

## Configuration Options

### ETLPipelineConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `extract_config` | dict | `{}` | Extraction phase configuration |
| `transform_config` | TransformerConfig | Default | Transformation configuration |
| `load_config` | LoaderConfig | Default | Loading configuration |
| `enable_validation` | bool | `True` | Enable data validation |
| `enable_logging` | bool | `True` | Enable detailed logging |
| `enable_backup` | bool | `True` | Enable backup of processed files |
| `parallel_processing` | bool | `False` | Enable parallel processing |
| `max_workers` | int | `4` | Maximum parallel workers |

### TransformerConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_quality_checks` | bool | `True` | Enable data quality validation |
| `enable_enrichment` | bool | `True` | Enable data enrichment |
| `output_formats` | list | `['json']` | Output formats to generate |
| `include_metadata` | bool | `True` | Include metadata in output |
| `quality_threshold` | float | `0.8` | Minimum quality score |
| `enrichment_sources` | list | `[]` | External enrichment sources |

### LoaderConfig

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_directory` | str | `"output"` | Output directory for files |
| `database_path` | str | `"aasx_data.db"` | SQLite database path |
| `vector_db_path` | str | `"vector_db"` | Vector database path |
| `vector_db_type` | str | `"chromadb"` | Vector database type |
| `embedding_model` | str | `"all-MiniLM-L6-v2"` | Embedding model name |
| `chunk_size` | int | `512` | Text chunk size for embeddings |
| `overlap_size` | int | `50` | Chunk overlap size |
| `include_metadata` | bool | `True` | Include metadata in vector DB |
| `create_indexes` | bool | `True` | Create database indexes |
| `backup_existing` | bool | `True` | Backup existing databases |

## Output Formats

The ETL pipeline generates multiple output formats, each optimized for specific use cases:

### 1. JSON Format (General Purpose)
```json
{
  "format": "json",
  "version": "1.0",
  "data": {
    "assets": [...],
    "submodels": [...],
    "documents": [...],
    "relationships": [...]
  },
  "quality_metrics": {
    "total_assets": 2,
    "total_submodels": 5,
    "quality_score": 1.0
  },
  "metadata": {
    "transformation_timestamp": "2025-07-09T12:36:45.011634",
    "transformer_version": "1.0.0"
  }
}
```
**Use case**: Web APIs, data exchange, general processing  
**Features**: Complete data with metadata, quality metrics, configuration info

### 2. YAML Format (Human-Readable)
```yaml
format: yaml
version: "1.0"
data:
  assets:
    - id: "asset_001"
      id_short: "Motor_001"
      description: "DC Servo Motor"
      type: "Motor"
      quality_level: "HIGH"
      compliance_status: "COMPLIANT"
```
**Use case**: Configuration files, documentation, human review  
**Features**: Readable format with preserved structure

### 3. CSV Format (Analytics-Ready)
```csv
entity_type,id,id_short,description,type,quality_level,compliance_status
asset,asset_001,Motor_001,DC Servo Motor,Motor,HIGH,COMPLIANT
submodel,submodel_001,TechData_001,Technical Data,TechnicalData,MEDIUM,COMPLIANT
```
**Use case**: Spreadsheet analysis, data visualization, business intelligence  
**Features**: Flattened structure with one row per entity

### 4. Graph Format (Neo4j/Graph Databases)
```json
{
  "format": "graph",
  "version": "1.0",
  "nodes": [
    {
      "id": "asset_001",
      "type": "asset",
      "properties": {
        "id_short": "Motor_001",
        "description": "DC Servo Motor",
        "type": "Motor",
        "quality_level": "HIGH",
        "compliance_status": "COMPLIANT"
      }
    }
  ],
  "edges": [
    {
      "source": "asset_001",
      "target": "submodel_001",
      "type": "asset_has_submodel",
      "properties": {
        "extracted_at": "2025-07-09T12:36:45.020020"
      }
    }
  ],
  "metadata": {
    "created_at": "2025-07-09T12:36:45.020020",
    "total_nodes": 7,
    "total_edges": 1
  }
}
```
**Use case**: Graph databases (Neo4j, ArangoDB), relationship analysis, network visualization  
**Features**: Nodes and edges structure optimized for graph operations

### 5. Vector Database Format
```python
{
  'id': 'asset_001',
  'embedding': [0.1, 0.2, 0.3, ...],
  'document': 'Asset: Motor_001 - DC Servo Motor for Quality Control',
  'metadata': {
    'entity_type': 'asset',
    'quality_level': 'high',
    'compliance_status': 'certified'
  }
}
```
**Use case**: Semantic search, AI/RAG systems, similarity analysis  
**Features**: Text embeddings for semantic search capabilities

## Performance Optimization

### Parallel Processing
```python
# Enable parallel processing for large datasets
config = ETLPipelineConfig(
    parallel_processing=True,
    max_workers=8  # Adjust based on CPU cores
)
```

### Vector Database Optimization
```python
# Use GPU-accelerated FAISS for large vector databases
load_config = LoaderConfig(
    vector_db_type="faiss",
    embedding_model="all-mpnet-base-v2"  # Better quality embeddings
)
```

### Memory Management
```python
# Process files in batches for large datasets
files = list(Path("aasx_files/").glob("*.aasx"))
batch_size = 100

for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    result = process_aasx_batch(batch, config)
    print(f"Processed batch {i//batch_size + 1}")
```

## Error Handling

### Common Errors and Solutions

1. **AASX File Format Error**
   ```python
   # Use hybrid processing with .NET fallback
   processor = AASXProcessor()
   result = processor.process_aasx_file("file.aasx")
   ```

2. **Vector Database Connection Error**
   ```python
   # Check ChromaDB installation
   pip install chromadb
   # Or use FAISS instead
   load_config = LoaderConfig(vector_db_type="faiss")
   ```

3. **Memory Issues with Large Files**
   ```python
   # Process in smaller chunks
   config = ETLPipelineConfig(
       transform_config=TransformerConfig(chunk_size=256)
   )
   ```

### Logging and Monitoring

```python
import logging

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

# Get pipeline statistics
stats = pipeline.get_pipeline_stats()
print(f"Files processed: {stats['files_processed']}")
print(f"Processing time: {stats['total_processing_time']:.2f}s")
```

## Integration with QI Platform

### Web Application Integration
```python
# In FastAPI route
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline

@app.post("/api/aasx/process")
async def process_aasx_file(file: UploadFile):
    pipeline = AASXETLPipeline()
    result = pipeline.process_aasx_file(file.filename)
    return result
```

### AI/RAG System Integration
```python
# Create RAG dataset for AI system
pipeline = AASXETLPipeline()
pipeline.process_aasx_directory("aasx_files/")
rag_dataset = pipeline.create_rag_ready_dataset("ai_rag_dataset.json")

# Use in RAG system
from webapp.ai_rag.rag_system import RAGSystem
rag = RAGSystem(rag_dataset)
results = rag.query("quality control requirements")
```

### Analytics Dashboard Integration
```python
# Export analytics-ready data
config = ETLPipelineConfig(
    transform_config=TransformerConfig(
        output_formats=['csv', 'analytics']
    )
)
pipeline = AASXETLPipeline(config)
pipeline.process_aasx_file("file.aasx")
```

## Neo4j Graph Database Integration

### Importing Graph Data to Neo4j

The ETL pipeline generates graph-optimized JSON files that can be directly imported into Neo4j:

#### 1. Using Neo4j Cypher Scripts
```cypher
// Load graph data from ETL output
LOAD JSON FROM 'file:///aasx_data_20250709_123645_graph.json' AS graph

// Create nodes
UNWIND graph.nodes AS node
CREATE (n:Node {
    id: node.id,
    type: node.type,
    id_short: node.properties.id_short,
    description: node.properties.description,
    quality_level: node.properties.quality_level,
    compliance_status: node.properties.compliance_status
})

// Create relationships
UNWIND graph.edges AS edge
MATCH (source:Node {id: edge.source})
MATCH (target:Node {id: edge.target})
CREATE (source)-[r:RELATES_TO {
    type: edge.type,
    extracted_at: edge.properties.extracted_at
}]->(target)
```

#### 2. Using Neo4j Import Tool
```bash
# Convert graph JSON to CSV for Neo4j import
python -c "
import json
import csv

# Load graph data
with open('aasx_data_20250709_123645_graph.json', 'r') as f:
    graph_data = json.load(f)

# Export nodes
with open('nodes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id:ID', 'type:LABEL', 'id_short', 'description', 'quality_level', 'compliance_status'])
    for node in graph_data['nodes']:
        writer.writerow([
            node['id'],
            node['type'],
            node['properties']['id_short'],
            node['properties']['description'],
            node['properties']['quality_level'],
            node['properties']['compliance_status']
        ])

# Export relationships
with open('relationships.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([':START_ID', ':END_ID', ':TYPE', 'extracted_at'])
    for edge in graph_data['edges']:
        writer.writerow([
            edge['source'],
            edge['target'],
            edge['type'],
            edge['properties']['extracted_at']
        ])
"

# Import to Neo4j
neo4j-admin import --database=aasx_data --nodes=nodes.csv --relationships=relationships.csv
```

#### 3. Graph Analytics Queries

Once imported, you can run powerful graph analytics:

```cypher
// Find all assets with high quality levels
MATCH (a:Node {type: 'asset', quality_level: 'HIGH'})
RETURN a.id, a.description, a.compliance_status

// Find submodels related to specific assets
MATCH (asset:Node {type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
WHERE asset.id CONTAINS 'motor'
RETURN asset.description, submodel.description, r.type

// Analyze compliance across the network
MATCH (n:Node)
RETURN n.type, n.quality_level, n.compliance_status, count(*) as count
ORDER BY count DESC

// Find connected components
CALL gds.alpha.scc.stream('aasx_graph')
YIELD nodeId, componentId
RETURN componentId, count(*) as size
ORDER BY size DESC
```

#### 4. Python Integration with Neo4j
```python
from neo4j import GraphDatabase
import json

class AASXGraphAnalyzer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def import_graph_data(self, graph_file_path):
        """Import graph data from ETL output"""
        with open(graph_file_path, 'r') as f:
            graph_data = json.load(f)
        
        with self.driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create nodes
            for node in graph_data['nodes']:
                session.run("""
                    CREATE (n:Node {
                        id: $id,
                        type: $type,
                        id_short: $id_short,
                        description: $description,
                        quality_level: $quality_level,
                        compliance_status: $compliance_status
                    })
                """, **node['properties'], id=node['id'], type=node['type'])
            
            # Create relationships
            for edge in graph_data['edges']:
                session.run("""
                    MATCH (source:Node {id: $source_id})
                    MATCH (target:Node {id: $target_id})
                    CREATE (source)-[r:RELATES_TO {
                        type: $rel_type,
                        extracted_at: $extracted_at
                    }]->(target)
                """, source_id=edge['source'], target_id=edge['target'],
                     rel_type=edge['type'], extracted_at=edge['properties']['extracted_at'])
    
    def analyze_quality_distribution(self):
        """Analyze quality distribution across assets"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Node {type: 'asset'})
                RETURN n.quality_level, count(*) as count
                ORDER BY count DESC
            """)
            return [record.data() for record in result]
    
    def find_related_submodels(self, asset_id):
        """Find all submodels related to a specific asset"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (asset:Node {id: $asset_id, type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
                RETURN submodel.id, submodel.description, r.type
            """, asset_id=asset_id)
            return [record.data() for record in result]

# Usage
analyzer = AASXGraphAnalyzer("bolt://localhost:7687", "neo4j", "password")
analyzer.import_graph_data("output/etl_results/additive-manufacturing-3d-printer_converted/aasx_data_20250709_123645_graph.json")

# Run analytics
quality_stats = analyzer.analyze_quality_distribution()
print("Quality distribution:", quality_stats)

related_submodels = analyzer.find_related_submodels("http://manufacturing.com/assets/3d_printer_am5000_001")
print("Related submodels:", related_submodels)
```

## Testing

### Run All Tests
```bash
# Run complete test suite
python -m pytest test/aasx/ -v

# Run specific test categories
python -m pytest test/aasx/test_aasx_processor.py -v
python -m pytest test/aasx/test_aasx_transformer.py -v
python -m pytest test/aasx/test_aasx_loader.py -v
python -m pytest test/aasx/test_aasx_etl_pipeline.py -v
```

### Test Individual Components
```python
# Test extraction
from test.aasx.test_aasx_processor import TestAASXProcessor
unittest.main(TestAASXProcessor)

# Test transformation
from test.aasx.test_aasx_transformer import TestAASXTransformer
unittest.main(TestAASXTransformer)

# Test loading
from test.aasx.test_aasx_loader import TestAASXLoader
unittest.main(TestAASXLoader)
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure webapp directory is in Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/webapp"
   ```

2. **Vector Database Issues**
   ```bash
   # Reinstall vector database dependencies
   pip uninstall chromadb sentence-transformers
   pip install chromadb sentence-transformers
   ```

3. **.NET Processor Issues**
   ```bash
   # Rebuild .NET processor
   cd aas-processor
   dotnet clean
   dotnet build
   ```

### Performance Issues

1. **Slow Processing**
   - Enable parallel processing
   - Use SSD storage for databases
   - Increase chunk sizes for large files

2. **Memory Issues**
   - Process files in batches
   - Reduce chunk sizes
   - Use streaming processing for large files

3. **Vector Database Performance**
   - Use GPU-accelerated FAISS
   - Optimize embedding model selection
   - Implement vector database indexing

## Future Enhancements

### Planned Features

1. **Advanced Processing**
   - Real-time streaming processing
   - Incremental updates
   - Delta processing for changed files

2. **Enhanced Vector Search**
   - Multi-modal embeddings
   - Hierarchical search
   - Semantic similarity clustering

3. **Quality Management**
   - Automated quality scoring
   - Compliance checking
   - Quality trend analysis

4. **Integration Capabilities**
   - REST API endpoints
   - GraphQL interface
   - WebSocket real-time updates

### Contributing

1. **Code Standards**
   - Follow PEP 8 style guide
   - Add comprehensive tests
   - Update documentation

2. **Testing Requirements**
   - Unit tests for all functions
   - Integration tests for pipeline
   - Performance benchmarks

3. **Documentation**
   - Update README files
   - Add code examples
   - Create user guides

## Support

For issues and questions:

1. **Documentation**: Check this README and inline code documentation
2. **Tests**: Review test files for usage examples
3. **Issues**: Create GitHub issues with detailed error information
4. **Community**: Join the QI Digital Platform community discussions

## License

This ETL pipeline is part of the Quality Infrastructure Digital Platform and follows the same licensing terms as the main project. 