# AASX Data Modeling Platform

A comprehensive **Asset Administrative Shell (AAS)** data modeling and digital twin management platform for Quality Infrastructure (QI) systems. This platform enables standardized digital representation, processing, and analytics of industrial assets using AASX packages.

## 🌟 Overview

The AASX Data Modeling Platform is a modern, scalable solution for managing digital twins in industrial and quality infrastructure environments. It provides:

- **AASX Package Processing**: Import, validate, and transform AASX files
- **Digital Twin Registry**: Centralized management of asset digital twins
- **AI-Powered Analytics**: Intelligent analysis using RAG (Retrieval-Augmented Generation)
- **Quality Infrastructure Integration**: Specialized tools for QI compliance and certification
- **Graph Neural Networks**: Advanced analytics for anomaly detection and community analysis
- **Multi-Format Export**: Support for JSON, XML, CSV, YAML, and graph formats

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AASX Data Modeling Platform              │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Frontend (Routes & Templates)                     │
├─────────────────────────────────────────────────────────────┤
│  Backend Business Logic (AASX, AI/RAG, Twin Registry)      │
├─────────────────────────────────────────────────────────────┤
│  AASX Explorer │  Data Pipeline │  Quality Checks │  Export │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features

### 🔧 AASX Processing
- **Import/Export**: Handle AASX package files with validation
- **Data Transformation**: Convert between multiple formats (JSON, XML, CSV, YAML, Graph)
- **Quality Validation**: Built-in data quality checks and compliance validation
- **Metadata Enrichment**: Automatic enhancement with quality infrastructure data

### 🤖 AI & Analytics
- **RAG System**: Intelligent document retrieval and question answering
- **Graph Neural Networks**: Anomaly detection and community analysis
- **Dynamic Graph Learning**: Real-time graph structure adaptation
- **Embedding Visualization**: Interactive graph embedding exploration

### 🏭 Digital Twin Management
- **Asset Registry**: Centralized digital twin storage and management
- **Relationship Mapping**: Automatic extraction of asset-submodel relationships
- **Compliance Tracking**: Quality infrastructure compliance monitoring
- **Certificate Management**: Digital certificate and product passport handling

### 📊 Quality Infrastructure
- **QI Analytics**: Specialized analytics for quality infrastructure
- **Compliance Monitoring**: Real-time compliance status tracking
- **Certificate Validation**: Automated certificate verification
- **Quality Metrics**: Comprehensive quality scoring and reporting

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.11+
- **Frontend**: FastAPI with Jinja2 templates, Bootstrap, JavaScript
- **AI/ML**: PyTorch, Transformers, Sentence-Transformers
- **Database**: PostgreSQL, Redis, Qdrant (vector database)
- **Graph Analytics**: NetworkX, PyTorch Geometric
- **AAS Processing**: Custom AASX parser with XML/JSON support
- **Containerization**: Docker, Docker Compose

## 📦 Project Structure

```
aas-data-modeling/
├── webapp/                    # FastAPI frontend application
│   ├── aasx/                 # AASX API routes and templates
│   ├── ai_rag/               # AI/RAG API routes
│   ├── twin_registry/        # Digital twin registry API
│   └── qi_analytics/         # Quality infrastructure analytics API
├── backend/                  # Backend business logic
│   ├── aasx/                 # AASX processing core modules
│   ├── ai-rag/               # AI/RAG system backend
│   ├── twin-registry/        # Digital twin registry backend
│   └── qi-analytics/         # QI analytics backend
├── graph-neural-network/     # GNN analytics platform
├── AasxPackageExplorer/      # Windows AASX explorer
├── data/                     # Sample AASX files
├── docs/                     # Comprehensive documentation
└── test/                     # Test suites
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/your-username/aas-data-modeling.git
   cd aas-data-modeling
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   python main.py setup
   ```

4. **Start the platform:**
   ```bash
   python main.py start
   ```

5. **Access the application:**
   - Web Interface: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

## 📚 Documentation

- [AAS Integration Guide](docs/AAS_INTEGRATION.md) - Asset Administrative Shell integration
- [AASX ETL Pipeline](docs/AASX_ETL_PIPELINE.md) - Data processing pipeline
- [Neo4j Integration](docs/NEO4J_INTEGRATION.md) - Neo4j graph database integration
- [Neo4j Success Story](docs/NEO4J_INTEGRATION_SUCCESS_STORY.md) - Complete integration journey and results
- [Graph Neural Networks](graph-neural-network/docs/) - GNN analytics documentation
- [API Reference](docs/API.md) - Complete API documentation
- [Architecture Guide](docs/ARCHITECTURE.md) - System architecture

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python test/run_all_tests.py

# Run specific test categories
python test/run_etl_tests.py
python test/aasx/test_aasx_examples.py
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-username/aas-data-modeling/issues)
- 💬 [Discussions](https://github.com/your-username/aas-data-modeling/discussions)

## 🙏 Acknowledgments

- Asset Administrative Shell (AAS) community
- Quality Infrastructure (QI) standards organizations
- Open source contributors and maintainers

---

**Built with ❤️ for the Quality Infrastructure community**
