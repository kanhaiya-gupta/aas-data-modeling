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

### 1. JSON Format
```json
{
  "metadata": {
    "source_file": "example.aasx",
    "processed_at": "2024-01-01T00:00:00Z",
    "version": "1.0"
  },
  "data": {
    "assets": [...],
    "submodels": [...],
    "documents": [...],
    "relationships": [...]
  }
}
```

### 2. CSV Format (Flattened)
```csv
entity_type,id,id_short,description,type,quality_level,compliance_status
asset,asset_001,Motor_001,DC Servo Motor,Motor,high,certified
submodel,submodel_001,TechData_001,Technical Data,TechnicalData,medium,pending
```

### 3. Graph Format (Neo4j)
```cypher
CREATE (a:Asset {id: 'asset_001', type: 'Motor', quality_level: 'high'})
CREATE (s:Submodel {id: 'submodel_001', type: 'TechnicalData'})
CREATE (a)-[:HAS_SUBMODEL]->(s)
```

### 4. Vector Database Format
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