# Setup Guide

## Quick Start

### Option 1: Smart Auto-Detection (Recommended)
```bash
python scripts/setup_etl_auto.py
```

This automatically detects your platform and runs the optimal setup.

### Option 2: Check Your Python Setup
```bash
python scripts/check_python.py
```

This helps verify your Python environment and recommends the correct commands.

## What the Setup Scripts Do

### `setup_etl_auto.py` (Main Setup Script)
This comprehensive script automatically detects your platform and sets up the entire ETL environment:

#### 🔧 **Platform Detection**
- Automatically detects Windows, Linux, or macOS
- Identifies Linux distribution (Ubuntu/Debian, CentOS/RHEL/Fedora)
- Checks macOS version compatibility
- Provides platform-specific optimizations

#### 📦 **Python Environment**
- Verifies Python 3.8+ is installed
- Installs all required packages from `requirements.txt`
- Uses platform-specific installation flags
- Handles dependencies automatically

#### 🔧 **System Dependencies**
- **Windows**: No system dependencies required
- **Linux**: Installs build tools and development packages
- **macOS**: Integrates with Homebrew for system packages

#### 🏗️ **.NET 6.0 SDK**
- **Windows**: Downloads and runs Windows installer
- **Linux**: Uses distribution-specific package managers
- **macOS**: Uses Homebrew or manual installation

#### ⚙️ **AAS Libraries**
- **AAS Core 3.0**: Industry 4.0 Asset Administration Shell core library
- **AASX Package**: AASX file format handling library
- These are .NET libraries, not Python packages

#### 🔨 **.NET Processor Build**
- Builds the `aas-processor` .NET project
- Creates platform-specific executables
- Sets up Python-.NET bridge
- Handles executable permissions

#### 🧪 **Environment Validation**
- Tests all Python package imports
- Verifies .NET processor build
- Validates AAS library availability
- Creates necessary directories

#### 📁 **Directory Setup**
- Creates project directories
- Sets up data and output folders
- Ensures proper structure

## Features

### 🌟 **Automatic Detection**
- Detects your operating system automatically
- Chooses appropriate installation methods
- Handles platform-specific requirements

### 🔄 **Error Recovery**
- Continues setup even if some steps fail
- Provides clear error messages
- Suggests manual alternatives

### 📊 **Progress Tracking**
- Clear step-by-step progress
- Detailed status reporting
- Success/failure indicators

### 🛡️ **Safety Features**
- Validates prerequisites
- Checks for existing installations
- Prevents conflicts

## Usage Examples

### Fresh Installation
```bash
# Complete setup from scratch
python scripts/setup_etl_auto.py
```

### Environment Check
```bash
# Check what's already installed
python scripts/run_etl.py --check
```

### Manual Package Installation
```bash
# Install missing packages only
python scripts/run_etl.py --build
```

### Python Command Check
```bash
# Check your Python setup
python scripts/check_python.py
```

## What Gets Installed

### Python Packages
- **Core**: yaml, pathlib, logging, json, xml, zipfile, datetime
- **Data Processing**: pandas, numpy, scikit-learn, scipy
- **AI/ML**: torch, transformers, sentence-transformers
- **Vector Databases**: qdrant-client, chromadb
- **Graph Database**: neo4j
- **AI APIs**: openai, anthropic, huggingface-hub

### .NET Components
- **.NET 6.0 SDK**: Required for AAS libraries
- **AAS Core 3.0**: Asset Administration Shell core library
- **AASX Package**: AASX file format library
- **AAS Processor**: Custom .NET application

### Directories Created
```
project/
├── data/aasx-examples/     # Sample AASX files
├── output/etl_results/     # ETL processing results
├── logs/                   # Application logs
└── temp/                   # Temporary files
```

## Platform-Specific Setup

### Windows Setup
```bash
# Automatic setup (recommended)
python scripts/setup_etl_auto.py

# Manual .NET installation
# Download from: https://dotnet.microsoft.com/download/dotnet/6.0
# Run installer and follow prompts
```

### Linux Setup (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y build-essential curl wget

# Run automatic setup
python scripts/setup_etl_auto.py
```

### Linux Setup (CentOS/RHEL/Fedora)
```bash
# Install system dependencies
sudo yum groupinstall "Development Tools"
sudo yum install curl wget

# Run automatic setup
python scripts/setup_etl_auto.py
```

### macOS Setup
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Run automatic setup
python scripts/setup_etl_auto.py
```

## Environment Configuration

### .env File Setup
Create a `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini-2025-04-14

# Neo4j Configuration
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# Qdrant Configuration
QDRANT_HOST=127.0.0.1
QDRANT_PORT=6333

# Application Configuration
LOG_LEVEL=INFO
DEBUG_MODE=false
```

### Environment Variables
The setup script will help you configure these automatically, but you can also set them manually:

```bash
# Set environment variables
export OPENAI_API_KEY="your_key_here"
export NEO4J_PASSWORD="your_password_here"

# Or use the update script
python scripts/update_env.py
```

## Verification Steps

### 1. Python Environment
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Test imports
python -c "import pandas, torch, transformers, neo4j; print('All packages available')"
```

### 2. .NET Environment
```bash
# Check .NET version
dotnet --version

# Test AAS processor
cd aas-processor
dotnet build --configuration Release
dotnet run --configuration Release "../data/aasx-examples/additive-manufacturing-3d-printer.aasx"
```

### 3. Database Connections
```bash
# Test Neo4j connection
python test/kg_neo4j/test_neo4j_connection.py

# Test Qdrant connection
python -c "from qdrant_client import QdrantClient; client = QdrantClient('localhost', port=6333); print('Qdrant connected')"
```

## Troubleshooting

### Common Issues

#### .NET Installation Fails
```bash
# Manual .NET installation
# Windows: Download from https://dotnet.microsoft.com/download/dotnet/6.0
# Linux: sudo apt-get install dotnet-sdk-6.0
# macOS: brew install dotnet
```

#### Python Package Installation Fails
```bash
# Try upgrading pip first
pip install --upgrade pip

# Install packages individually
pip install pandas numpy torch transformers
```

#### AAS Libraries Not Found
```bash
# Rebuild the .NET processor
cd aas-processor
dotnet restore
dotnet build --configuration Release
```

#### Permission Errors
```bash
# Fix directory permissions
chmod -R 755 data/
chmod -R 755 output/
chmod -R 755 logs/

# Fix executable permissions
chmod +x aas-processor/bin/Release/net6.0/AasProcessor.exe
```

### Getting Help

1. **Check the logs**: Look for error messages in the output
2. **Run with --verbose**: Add verbose logging for more details
3. **Manual installation**: Follow the manual steps in the error messages
4. **Check prerequisites**: Ensure Python 3.8+ and .NET 6.0 are available

## Integration with Framework

Once setup is complete, you can run the full framework:

```bash
# Check environment
python main.py --check-only

# Start the web application
python main.py

# Run ETL pipeline
python scripts/run_etl.py

# Run AI/RAG system
python scripts/run_ai_rag.py

# Run Knowledge Graph
python scripts/run_knowledge_graph.py
```

## Docker Setup

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for containers

### Quick Docker Setup
```bash
# Start all services
docker-compose -f manifests/framework/docker-compose.framework.yml up -d

# Check service status
docker-compose -f manifests/framework/docker-compose.framework.yml ps

# View logs
docker-compose -f manifests/framework/docker-compose.framework.yml logs
```

### Individual Components
```bash
# ETL Pipeline only
docker-compose -f manifests/independent/docker-compose.etl-pipeline.yml up --build

# Knowledge Graph only
docker-compose -f manifests/independent/docker-compose.knowledge-graph.yml up --build

# AI/RAG System only
docker-compose -f manifests/independent/docker-compose.ai-rag.yml up --build
```

## Next Steps

After successful setup:

1. **Explore the Data**: Check out the sample AASX files in `data/aasx-examples/`
2. **Run ETL Pipeline**: Process the sample data with `python scripts/run_etl.py`
3. **Start Web Interface**: Launch the application with `python main.py`
4. **Try AI/RAG**: Test the AI system with `python scripts/run_ai_rag.py`
5. **Explore Knowledge Graph**: Use the Neo4j interface at `/kg-neo4j`

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in the `logs/` directory
3. Run the verification steps
4. Check the project documentation
5. Open an issue with detailed error information 