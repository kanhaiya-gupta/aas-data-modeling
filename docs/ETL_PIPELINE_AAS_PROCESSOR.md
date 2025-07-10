# 🚀 ETL Pipeline with AAS Processor Integration

This document describes the **ETL Pipeline** that integrates with the **AAS Processor** (.NET component) for comprehensive AASX file processing.

## 🎯 Overview

The ETL Pipeline is the **heart of the project** and consists of:

1. **AAS Processor** - .NET 6.0 component for advanced AASX processing
2. **Python ETL Pipeline** - Orchestrates extraction, transformation, and loading
3. **.NET Bridge** - Python interface to call the .NET processor
4. **Docker Integration** - Containerized deployment with .NET runtime

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AASX Files    │───▶│   ETL Pipeline   │───▶│  Knowledge      │
│   (Input)       │    │   (Python)       │    │  Graph          │
└─────────────────┘    │   Port 8003      │    │  (Neo4j)        │
                       └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  AAS Processor   │
                       │  (.NET 6.0)      │
                       │  - AAS Core 3.0  │
                       │  - AASX Package  │
                       └──────────────────┘
```

## 🔧 Components

### 1. AAS Processor (.NET 6.0)
**Location**: `aas-processor/`

**Features**:
- Advanced AASX file parsing using AAS Core 3.0
- Comprehensive asset and submodel extraction
- Document and metadata processing
- JSON output format

**Dependencies**:
- .NET 6.0 SDK
- AAS Core 3.0 libraries
- System.Text.Json

### 2. Python ETL Pipeline
**Location**: `backend/aasx/`

**Features**:
- Orchestrates the complete ETL process
- Integrates with .NET processor via bridge
- Handles data transformation and loading
- Provides REST API interface

**Dependencies**:
- Python 3.11+
- Neo4j driver
- XML/JSON processing libraries

### 3. .NET Bridge
**Location**: `backend/aasx/dotnet_bridge.py`

**Features**:
- Python interface to .NET processor
- Subprocess communication
- Error handling and fallback
- Environment variable configuration

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file with configuration
- AASX files for processing

### Option 1: Docker (Recommended)

```bash
# Build and start ETL pipeline
docker-compose -f docker-compose.core.yml up -d etl-pipeline

# Or build manually
docker build -f docker/Dockerfile.etl-pipeline -t aas-etl .
docker run -p 8003:8003 -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output aas-etl
```

### Option 2: Local Development

```bash
# Install .NET 6.0 SDK
# Download from: https://dotnet.microsoft.com/download/dotnet/6.0

# Build aas-processor
cd aas-processor
dotnet restore
dotnet build --configuration Release

# Test integration
python scripts/test_etl_with_processor.py
```

## 📊 Service Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/process` | POST | Process AASX file |
| `/batch` | POST | Process multiple files |
| `/status` | GET | Processing status |
| `/stats` | GET | Pipeline statistics |

## 🔧 Configuration

### Environment Variables

```env
# ETL Configuration
ETL_CONFIG_PATH=/app/scripts/config_etl.yaml
OUTPUT_DIR=/app/output/etl_results
LOG_LEVEL=INFO

# AAS Processor Configuration
AAS_PROCESSOR_PATH=/app/aas-processor/bin/Release/net6.0/AasProcessor
DOTNET_ROOT=/usr/share/dotnet

# Neo4j Configuration (for loading)
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123
```

### Data Directory Structure

```
project/
├── data/
│   └── aasx-examples/     # Input AASX files
├── output/
│   └── etl_results/       # Processed data
├── aas-processor/         # .NET processor
│   ├── AasProcessor.cs
│   ├── AasProcessor.csproj
│   └── bin/Release/net6.0/
└── backend/aasx/          # Python ETL pipeline
    ├── aasx_etl_pipeline.py
    ├── aasx_processor.py
    └── dotnet_bridge.py
```

## 📈 Usage Examples

### Process Single AASX File

```bash
# Via API
curl -X POST http://localhost:8003/process \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/aasx-examples/example.aasx"}'

# Via Python
from backend.aasx.aasx_etl_pipeline import AASXETLPipeline
pipeline = AASXETLPipeline()
result = pipeline.process_aasx_file("data/aasx-examples/example.aasx")
```

### Process Multiple Files

```bash
# Via API
curl -X POST http://localhost:8003/batch \
  -H "Content-Type: application/json" \
  -d '{"directory": "data/aasx-examples"}'

# Via Python
result = pipeline.process_aasx_directory("data/aasx-examples")
```

### Check Processing Status

```bash
# Get pipeline statistics
curl http://localhost:8003/stats

# Get processing status
curl http://localhost:8003/status
```

## 🧪 Testing

### Comprehensive Test Suite

```bash
# Test ETL pipeline with aas-processor integration
python scripts/test_etl_with_processor.py
```

This test suite verifies:
- ✅ .NET 6.0 installation
- ✅ AAS processor build
- ✅ .NET bridge functionality
- ✅ ETL pipeline integration
- ✅ Docker integration

### Individual Component Tests

```bash
# Test .NET bridge only
python -c "from backend.aasx.dotnet_bridge import DotNetAasBridge; bridge = DotNetAasBridge(); print('Available:', bridge.is_available())"

# Test aas-processor directly
cd aas-processor
dotnet run Example_AAS_ServoDCMotor_21.aasx output.json
```

## 🔍 Processing Workflow

### 1. File Validation
- Check file exists and has .aasx extension
- Validate file integrity

### 2. .NET Processing (Primary)
- Use AAS Core 3.0 libraries
- Extract assets, submodels, documents
- Generate structured JSON output

### 3. Python Processing (Fallback)
- Basic ZIP-based processing
- JSON/XML parsing
- Limited AAS structure extraction

### 4. Data Transformation
- Convert to graph format
- Apply business rules
- Validate data quality

### 5. Data Loading
- Load into Neo4j knowledge graph
- Create relationships
- Index for querying

## 🛠️ Development

### Building AAS Processor

```bash
# Navigate to processor directory
cd aas-processor

# Restore packages
dotnet restore

# Build in Release mode
dotnet build --configuration Release

# Run directly
dotnet run Example_AAS_ServoDCMotor_21.aasx output.json
```

### Debugging .NET Bridge

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Test bridge directly
python -c "
from backend.aasx.dotnet_bridge import DotNetAasBridge
bridge = DotNetAasBridge()
print('Available:', bridge.is_available())
result = bridge.process_aasx_file('data/aasx-examples/example.aasx')
print('Result:', result)
"
```

### Docker Development

```bash
# Build with no cache
docker build -f docker/Dockerfile.etl-pipeline --no-cache -t aas-etl .

# Run in interactive mode
docker run -it --rm -v $(pwd)/data:/app/data aas-etl bash

# View logs
docker logs etl-pipeline
```

## 🔒 Security

### Container Security
- Non-root user execution
- Minimal base image with .NET runtime
- No unnecessary packages

### Data Security
- Volume mounts for persistent data
- Environment variables for sensitive config
- Network isolation

## 📚 Integration

### With Knowledge Graph
The ETL pipeline automatically loads processed data into Neo4j:

```cypher
// Query processed assets
MATCH (a:Asset) RETURN a.name, a.type

// Query relationships
MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name
```

### With External Systems
- REST APIs for integration
- JSON data formats
- Docker containerization
- Standard Neo4j protocols

## 🚨 Troubleshooting

### Common Issues

**AAS Processor not building:**
```bash
# Check .NET installation
dotnet --version

# Check project dependencies
cd aas-processor
dotnet restore --verbosity detailed

# Check build errors
dotnet build --verbosity detailed
```

**ETL Pipeline not starting:**
```bash
# Check environment variables
echo $AAS_PROCESSOR_PATH
echo $DOTNET_ROOT

# Check .NET bridge
python -c "from backend.aasx.dotnet_bridge import DotNetAasBridge; print(DotNetAasBridge().is_available())"
```

**Docker build failing:**
```bash
# Check Dockerfile syntax
docker build -f docker/Dockerfile.etl-pipeline --no-cache .

# Check .NET installation in container
docker run --rm aas-etl dotnet --version
```

### Performance Issues

**Slow processing:**
- Check available memory
- Verify disk space
- Monitor CPU usage
- Consider parallel processing

**Large file handling:**
- Increase container memory limits
- Use streaming processing
- Implement chunking for large files

## 📖 Next Steps

1. **Process Data**: Add AASX files and run ETL pipeline
2. **Monitor Results**: Check processing statistics and logs
3. **Analyze Data**: Use knowledge graph for data exploration
4. **Optimize**: Tune processing parameters for your use case
5. **Scale**: Add more processing power as needed

## 🤝 Support

For issues and questions:
- Check the troubleshooting section
- Review service logs
- Test with the provided test script
- Consult the main project documentation

---

**🎉 You're now ready to process AASX files with advanced .NET integration!** 