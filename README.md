# AASX Digital Twin Analytics Framework

A comprehensive framework for processing AASX (Asset Administration Shell) files and building digital twin analytics with ETL, Knowledge Graph, and AI/RAG capabilities.

## 📚 Documentation

### 📖 **Complete Documentation**
- **[📋 Setup Guide](docs/SETUP_GUIDE.md)** - Complete environment setup and configuration
- **[🔧 AAS Processor](docs/AAS_PROCESSOR.md)** - .NET-based AASX file processing
- **[🧠 Knowledge Graph](docs/KNOWLEDGE_GRAPH.md)** - Neo4j integration and graph analytics
- **[📊 Data Examples](docs/DATA_EXAMPLES.md)** - Sample AASX files and data structures
- **[🔄 ETL Pipeline](docs/AASX_ETL_PIPELINE.md)** - Data extraction, transformation, and loading
- **[🤖 AI/RAG System](docs/AAS_INTEGRATION.md)** - AI-powered retrieval and analysis
- **[🏗️ Data Architecture](docs/AASX_DATA_ARCHITECTURE.md)** - Data model and schema documentation
- **[🔌 API Documentation](docs/API_DOCUMENTATION.md)** - REST API reference
- **[⚙️ Configuration](docs/CONFIGURATION.md)** - System configuration options
- **[🚀 Performance](docs/PERFORMANCE.md)** - Performance optimization and monitoring

### 🧪 **Testing & Quality**
- **[🧪 Testing Guide](test/README.md)** - Comprehensive testing procedures
- **[🐳 Docker Setup](docker/README.md)** - Containerized deployment

### 📋 **Documentation Index**
- **[📚 Documentation Overview](docs/README.md)** - Complete documentation index and navigation

## Overview

The AASX Digital Twin Analytics Framework provides a complete solution for:
- **ETL Processing** - Extract, Transform, Load AASX files into structured data
- **Knowledge Graph** - Build and query Neo4j-based relationship graphs
- **AI/RAG System** - Intelligent analysis and insights using AI
- **Digital Twin Registry** - Manage and monitor digital twin assets
- **Certificate Management** - Handle compliance and certification
- **Analytics Dashboard** - Visualize and analyze digital twin data

## Features

### 🚀 Core Components
- **AASX Package Explorer** - Process and explore AASX digital twin packages
- **AI/RAG System** - AI-powered analysis and insights for digital twins
- **Knowledge Graph** - Neo4j knowledge graph explorer and analytics
- **Digital Twin Registry** - Manage and monitor digital twin registrations
- **Certificate Manager** - Digital certificates and compliance management
- **Analytics Dashboard** - Digital twin analytics and visualization

### 🔧 Technical Capabilities
- **ETL Pipeline** - Automated processing of AASX files
- **Neo4j Integration** - Graph database for relationship analysis
- **Qdrant Vector Database** - Semantic search and similarity matching
- **OpenAI Integration** - AI-powered querying and analysis
- **RESTful APIs** - Complete API for integration
- **Web Interface** - Modern, responsive web application

## Quick Start

### Prerequisites
- Python 3.8+
- Neo4j Database
- Qdrant Vector Database
- OpenAI API Key (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aas-data-modeling
   ```

2. **Quick Setup (Recommended)**
   ```bash
   # Automatic setup with platform detection
   python scripts/setup_etl_auto.py
   ```

3. **Manual Setup (Alternative)**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the framework**
   ```bash
   python main_simple.py
   ```

5. **Access the web interface**
   - Open http://localhost:8000/ in your browser
   - Upload AASX files for processing
   - Explore the Knowledge Graph
   - Use AI/RAG for analysis

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AASX Files    │───▶│   ETL Pipeline  │───▶│  Knowledge Graph│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Vector Store   │    │   AI/RAG System │
                       │   (Qdrant)      │    │   (OpenAI)      │
                       └─────────────────┘    └─────────────────┘
                                │                        │
                                └──────────┬─────────────┘
                                           ▼
                                  ┌─────────────────┐
                                  │  Web Interface  │
                                  │   (FastAPI)     │
                                  └─────────────────┘
```

## Usage

### Processing AASX Files
1. Navigate to the AASX Package Explorer
2. Upload your AASX files
3. Monitor the ETL processing
4. View processed data and statistics

### Knowledge Graph Analysis
1. Access the Knowledge Graph module
2. Execute Cypher queries
3. Run graph analytics
4. Explore relationships and patterns

### AI-Powered Analysis
1. Use the AI/RAG System
2. Ask natural language questions
3. Get intelligent insights
4. Generate reports and recommendations

## API Documentation

The framework provides comprehensive REST APIs:
- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **Module-specific endpoints**: See [API Documentation](docs/API_DOCUMENTATION.md)

## Configuration

Key configuration options in `.env`:
```env
# Database Connections
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Framework Settings
FRAMEWORK_PORT=8000
FRAMEWORK_HOST=0.0.0.0
```

For detailed configuration options, see [Configuration Guide](docs/CONFIGURATION.md).

## Development

### Running Tests
```bash
# Run all tests
python test/run_all_tests.py

# Run specific test categories
python test/unit/test_basic.py
python test/kg_neo4j/run_all_neo4j_tests.py
```

For comprehensive testing information, see [Testing Guide](test/README.md).

### Building Docker Images
```bash
# Full framework
docker-compose -f manifests/framework/docker-compose.framework.yml build

# Individual components
docker-compose -f manifests/independent/docker-compose.etl-pipeline.yml build
docker-compose -f manifests/independent/docker-compose.knowledge-graph.yml build
docker-compose -f manifests/independent/docker-compose.ai-rag.yml build
```

For Docker setup details, see [Docker Documentation](docker/README.md).

### Development Mode
```bash
python main_simple.py --reload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (see [Testing Guide](test/README.md))
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the [Documentation Overview](docs/README.md)
- Review the [API Documentation](docs/API_DOCUMENTATION.md)
- Consult the [Setup Guide](docs/SETUP_GUIDE.md) for installation issues

---

**AASX Digital Twin Analytics Framework** - Transforming AASX data into actionable insights through advanced analytics and AI.
