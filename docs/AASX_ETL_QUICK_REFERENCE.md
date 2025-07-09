# AASX ETL Pipeline - Quick Reference Guide

## Quick Start

### Basic Processing
```python
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline

# Process single file
pipeline = AASXETLPipeline()
result = pipeline.process_aasx_file("file.aasx")

# Process directory
result = pipeline.process_aasx_directory("aasx_files/")
```

### Batch Processing
```python
from webapp.aasx.aasx_etl_pipeline import process_aasx_batch

files = ["file1.aasx", "file2.aasx", "file3.aasx"]
result = process_aasx_batch(files)
```

## Configuration

### Default Configuration
```python
from webapp.aasx.aasx_etl_pipeline import ETLPipelineConfig

config = ETLPipelineConfig(
    enable_validation=True,
    enable_logging=True,
    parallel_processing=False,
    max_workers=4
)
```

### Custom Configuration
```python
from webapp.aasx.aasx_transformer import TransformerConfig
from webapp.aasx.aasx_loader import LoaderConfig

# Transform configuration
transform_config = TransformerConfig(
    enable_quality_checks=True,
    enable_enrichment=True,
    output_formats=['json', 'csv', 'graph'],
    include_metadata=True
)

# Load configuration
load_config = LoaderConfig(
    output_directory="output",
    database_path="aasx_data.db",
    vector_db_path="vector_db",
    vector_db_type="chromadb",
    embedding_model="all-MiniLM-L6-v2"
)

# Complete configuration
config = ETLPipelineConfig(
    transform_config=transform_config,
    load_config=load_config,
    parallel_processing=True,
    max_workers=8
)
```

## Common Operations

### 1. Extract Only
```python
from webapp.aasx.aasx_processor import AASXProcessor

processor = AASXProcessor()
result = processor.process_aasx_file("file.aasx")

if result['success']:
    data = result['data']
    print(f"Assets: {len(data.get('assets', []))}")
    print(f"Submodels: {len(data.get('submodels', []))}")
```

### 2. Transform Only
```python
from webapp.aasx.aasx_transformer import AASXTransformer

transformer = AASXTransformer()
result = transformer.transform_aasx_data(extracted_data)

if result['success']:
    transformed_data = result['data']
    print(f"Transformations applied: {result['transformations_applied']}")
```

### 3. Load Only
```python
from webapp.aasx.aasx_loader import AASXLoader

loader = AASXLoader()
result = loader.load_aasx_data(transformed_data)

print(f"Files exported: {len(result['files_exported'])}")
print(f"Database records: {result['database_records']}")
print(f"Vector embeddings: {result['vector_embeddings']}")
```

### 4. Vector Search
```python
# Search for similar entities
results = loader.search_similar(
    query="motor quality control",
    entity_type="asset",
    top_k=5
)

for result in results:
    print(f"ID: {result['id']}")
    print(f"Similarity: {result['similarity']}")
    print(f"Content: {result['document']}")
```

### 5. Database Statistics
```python
# Get database stats
stats = loader.get_database_stats()
print(f"Assets: {stats['assets_count']}")
print(f"Submodels: {stats['submodels_count']}")
print(f"Documents: {stats['documents_count']}")
print(f"Relationships: {stats['relationships_count']}")
```

### 6. RAG Dataset Export
```python
# Export RAG-ready dataset
rag_path = loader.export_for_rag("rag_dataset.json")
print(f"RAG dataset: {rag_path}")
```

### 7. Graph Database Integration
```python
# Import to Neo4j
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    # Load graph data from ETL output
    with open("aasx_data_20250709_123645_graph.json", "r") as f:
        graph_data = json.load(f)
    
    # Create nodes and relationships
    for node in graph_data['nodes']:
        session.run("CREATE (n:Node {id: $id, type: $type})", 
                   id=node['id'], type=node['type'])
```

## Output Formats

### JSON Export (General Purpose)
```python
# Export as JSON with full metadata
transformer = AASXTransformer(
    TransformerConfig(output_formats=['json'])
)
result = transformer.transform_aasx_data(data)
```
**Features**: Complete data with quality metrics and metadata

### YAML Export (Human-Readable)
```python
# Export as YAML for documentation
transformer = AASXTransformer(
    TransformerConfig(output_formats=['yaml'])
)
result = transformer.transform_aasx_data(data)
```
**Features**: Readable format with preserved structure

### CSV Export (Analytics-Ready)
```python
# Export as CSV for spreadsheet analysis
transformer = AASXTransformer(
    TransformerConfig(output_formats=['csv'])
)
result = transformer.transform_aasx_data(data)
```
**Features**: Flattened structure with one row per entity

### Graph Export (Neo4j/Graph Databases)
```python
# Export as graph format for Neo4j
transformer = AASXTransformer(
    TransformerConfig(output_formats=['graph'])
)
result = transformer.transform_aasx_data(data)
```
**Features**: Nodes and edges structure for graph analytics

### Analytics Export
```python
# Export as analytics format (BI tools)
transformer = AASXTransformer(
    TransformerConfig(output_formats=['analytics'])
)
result = transformer.transform_aasx_data(data)
```

## Performance Optimization

### Parallel Processing
```python
# Enable parallel processing
config = ETLPipelineConfig(
    parallel_processing=True,
    max_workers=8  # Adjust based on CPU cores
)
pipeline = AASXETLPipeline(config)
```

### Memory Optimization
```python
# Process in smaller chunks
config = ETLPipelineConfig(
    transform_config=TransformerConfig(chunk_size=256)
)
```

### Vector Database Optimization
```python
# Use GPU-accelerated FAISS
load_config = LoaderConfig(
    vector_db_type="faiss",
    embedding_model="all-mpnet-base-v2"
)
```

## Error Handling

### Common Error Patterns
```python
try:
    result = pipeline.process_aasx_file("file.aasx")
    if result['status'] == 'completed':
        print("Processing successful")
    else:
        print(f"Processing failed: {result['error']}")
except Exception as e:
    print(f"Pipeline error: {e}")
```

### Validation
```python
# Validate pipeline configuration
validation = pipeline.validate_pipeline()
if validation['pipeline_valid']:
    print("Pipeline is valid")
else:
    print(f"Validation errors: {validation['errors']}")
```

## Monitoring and Statistics

### Pipeline Statistics
```python
# Get comprehensive statistics
stats = pipeline.get_pipeline_stats()
print(f"Files processed: {stats['files_processed']}")
print(f"Files failed: {stats['files_failed']}")
print(f"Total time: {stats['total_processing_time']:.2f}s")
print(f"Extract time: {stats['extract_time']:.2f}s")
print(f"Transform time: {stats['transform_time']:.2f}s")
print(f"Load time: {stats['load_time']:.2f}s")
```

### Reset Statistics
```python
# Reset pipeline statistics
pipeline.reset_stats()
```

### Export Report
```python
# Export processing report
report_path = pipeline.export_pipeline_report("pipeline_report.json")
print(f"Report exported: {report_path}")
```

## Testing

### Run Tests
```bash
# Run all ETL tests
python -m pytest test/aasx/ -v

# Run specific component tests
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

## Integration Examples

### Web Application Integration
```python
# FastAPI route
from fastapi import FastAPI, UploadFile
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline

app = FastAPI()

@app.post("/api/aasx/process")
async def process_aasx_file(file: UploadFile):
    pipeline = AASXETLPipeline()
    result = pipeline.process_aasx_file(file.filename)
    return result
```

### AI/RAG Integration
```python
# Create RAG dataset
pipeline = AASXETLPipeline()
pipeline.process_aasx_directory("aasx_files/")
rag_dataset = pipeline.create_rag_ready_dataset("ai_rag_dataset.json")

# Use in RAG system
from webapp.ai_rag.rag_system import RAGSystem
rag = RAGSystem(rag_dataset)
results = rag.query("quality control requirements")
```

### Analytics Integration
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

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/webapp"
   ```

2. **Vector Database Issues**
   ```bash
   pip install chromadb sentence-transformers
   ```

3. **.NET Processor Issues**
   ```bash
   cd aas-processor
   dotnet clean
   dotnet build
   ```

### Performance Issues

1. **Slow Processing**
   - Enable parallel processing
   - Use SSD storage
   - Increase chunk sizes

2. **Memory Issues**
   - Process in batches
   - Reduce chunk sizes
   - Use streaming processing

3. **Vector Database Performance**
   - Use GPU-accelerated FAISS
   - Optimize embedding model
   - Implement indexing

## Command Line Usage

### Process Single File
```bash
python -c "
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline
pipeline = AASXETLPipeline()
result = pipeline.process_aasx_file('file.aasx')
print(f'Status: {result[\"status\"]}')
"
```

### Process Directory
```bash
python -c "
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline
pipeline = AASXETLPipeline()
result = pipeline.process_aasx_directory('aasx_files/')
print(f'Processed: {result[\"files_processed\"]}')
print(f'Failed: {result[\"files_failed\"]}')
"
```

### Export RAG Dataset
```bash
python -c "
from webapp.aasx.aasx_etl_pipeline import AASXETLPipeline
pipeline = AASXETLPipeline()
pipeline.process_aasx_directory('aasx_files/')
rag_path = pipeline.create_rag_ready_dataset('rag_dataset.json')
print(f'RAG dataset: {rag_path}')
"
```

## Configuration Reference

### ETLPipelineConfig
```python
ETLPipelineConfig(
    extract_config={},                    # Extraction configuration
    transform_config=TransformerConfig(), # Transformation configuration
    load_config=LoaderConfig(),          # Loading configuration
    enable_validation=True,              # Enable validation
    enable_logging=True,                 # Enable logging
    enable_backup=True,                  # Enable backup
    parallel_processing=False,           # Enable parallel processing
    max_workers=4                        # Max parallel workers
)
```

### TransformerConfig
```python
TransformerConfig(
    enable_quality_checks=True,          # Enable quality checks
    enable_enrichment=True,              # Enable enrichment
    output_formats=['json'],             # Output formats
    include_metadata=True,               # Include metadata
    quality_threshold=0.8,               # Quality threshold
    enrichment_sources=[]                # Enrichment sources
)
```

### LoaderConfig
```python
LoaderConfig(
    output_directory="output",           # Output directory
    database_path="aasx_data.db",        # Database path
    vector_db_path="vector_db",          # Vector DB path
    vector_db_type="chromadb",           # Vector DB type
    embedding_model="all-MiniLM-L6-v2",  # Embedding model
    chunk_size=512,                      # Chunk size
    overlap_size=50,                     # Overlap size
    include_metadata=True,               # Include metadata
    create_indexes=True,                 # Create indexes
    backup_existing=True                 # Backup existing
)
```

## File Structure

```
webapp/aasx/
├── aasx_processor.py      # Extract phase
├── aasx_transformer.py    # Transform phase
├── aasx_loader.py         # Load phase
├── aasx_etl_pipeline.py   # Complete pipeline
└── dotnet_bridge.py       # .NET integration

test/aasx/
├── test_aasx_processor.py
├── test_aasx_transformer.py
├── test_aasx_loader.py
└── test_aasx_etl_pipeline.py

docs/
├── AASX_ETL_PIPELINE.md
└── AASX_ETL_QUICK_REFERENCE.md
``` 