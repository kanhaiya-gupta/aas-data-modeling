# Test Suite

## Overview

This directory contains the comprehensive test suite for the AASX Digital Twin Analytics Framework. The tests are organized by type and functionality to ensure proper coverage and maintainability.

## Directory Structure

```
test/
├── README.md                    # This file
├── run_all_tests.py             # Main test runner
├── unit/                        # Unit tests
│   └── test_basic.py
├── data_quality/                # Data quality tests
│   └── test_aasx_data_quality.py
├── aasx/                        # AASX processing tests
│   ├── test_aasx_examples.py
│   ├── test_aasx_examples_simple.py
│   ├── test_aasx_integration.py
│   ├── test_aasx_processing.py
│   └── test_dotnet_bridge.py
├── webapp/                      # Web application tests
│   └── test_webapp_routes.py
├── performance/                 # Performance tests
│   └── test_aasx_performance.py
├── error_handling/              # Error handling tests
│   └── test_error_scenarios.py
├── integration/                 # Integration tests
│   └── test_hybrid_processing.py
└── kg_neo4j/                    # Knowledge Graph tests
    ├── test_neo4j_integration.py
    ├── test_neo4j_connection.py
    ├── test_password_validation.py
    ├── test_data_import.py
    └── run_all_neo4j_tests.py
```

## Test Categories

### Unit Tests (`unit/`)
Basic functionality and module import tests.

**Files:**
- `test_basic.py` - Basic imports, functionality, and directory structure

**Run Unit Tests:**
```bash
cd test/unit
python test_basic.py
```

### Data Quality Tests (`data_quality/`)
Tests for data integrity, completeness, and validation.

**Files:**
- `test_aasx_data_quality.py` - Data completeness, consistency, integrity, and validation

**Features Tested:**
- ✅ Data completeness (required fields present)
- ✅ Data consistency (no duplicates, valid types)
- ✅ Data integrity (structural validation)
- ✅ Data validation (format and content validation)

**Run Data Quality Tests:**
```bash
cd test/data_quality
python test_aasx_data_quality.py
```

### AASX Tests (`aasx/`)
Tests for AASX file processing and .NET bridge integration.

**Files:**
- `test_aasx_examples.py` - Comprehensive AASX example testing
- `test_aasx_examples_simple.py` - Simple AASX processing demonstration
- `test_aasx_integration.py` - AASX integration with platform
- `test_aasx_processing.py` - Core AASX processing functionality
- `test_dotnet_bridge.py` - .NET bridge integration testing

**Run AASX Tests:**
```bash
cd test/aasx
python test_dotnet_bridge.py
python test_aasx_examples_simple.py
```

### Web Application Tests (`webapp/`)
Tests for web application routes, templates, and static files.

**Files:**
- `test_webapp_routes.py` - Route registration, template availability, static files

**Features Tested:**
- ✅ Route imports and registration
- ✅ Template availability
- ✅ Static file availability
- ✅ App configuration

**Run Webapp Tests:**
```bash
cd test/webapp
python test_webapp_routes.py
```

### Performance Tests (`performance/`)
Tests for processing speed, memory usage, and scalability.

**Files:**
- `test_aasx_performance.py` - Processing speed, memory usage, concurrent processing

**Features Tested:**
- ✅ Processing speed (time thresholds)
- ✅ Memory usage (memory limits)
- ✅ Concurrent processing (threading)
- ✅ Large file handling (efficiency)

**Run Performance Tests:**
```bash
cd test/performance
python test_aasx_performance.py
```

### Error Handling Tests (`error_handling/`)
Tests for various failure scenarios and error recovery.

**Files:**
- `test_error_scenarios.py` - Invalid files, corrupted data, missing dependencies

**Features Tested:**
- ✅ Invalid file path handling
- ✅ Invalid file format handling
- ✅ Corrupted ZIP file handling
- ✅ Missing dependencies handling
- ✅ .NET bridge error handling
- ✅ Memory error handling

**Run Error Handling Tests:**
```bash
cd test/error_handling
python test_error_scenarios.py
```

### Integration Tests (`integration/`)
Tests for cross-module integration and end-to-end functionality.

**Files:**
- `test_hybrid_processing.py` - Python/.NET hybrid processing

**Run Integration Tests:**
```bash
cd test/integration
python test_hybrid_processing.py
```

### Knowledge Graph Tests (`kg_neo4j/`)
Tests for Neo4j integration and knowledge graph functionality.

**Files:**
- `test_neo4j_integration.py` - Comprehensive Neo4j integration testing
- `test_neo4j_connection.py` - Connection testing with detailed error reporting
- `test_password_validation.py` - Password testing utility
- `test_data_import.py` - Data import functionality testing
- `run_all_neo4j_tests.py` - Runs all Neo4j tests in sequence

**Features Tested:**
- ✅ Environment Variables Test - Load `.env` file, read Neo4j configuration
- ✅ Module Imports Test - Import Neo4jManager, AASXGraphAnalyzer, CypherQueries
- ✅ Connection Test - Neo4j database connection, authentication validation
- ✅ Graph Validation Test - Valid graph data structure, invalid data rejection
- ✅ Cypher Queries Test - Static query generation, dynamic query building
- ✅ ETL Integration Test - ETL output directory detection, graph file discovery
- ✅ Data Import Test - Graph data validation, import execution

**Run Knowledge Graph Tests:**
```bash
# Run all Neo4j tests
python test/kg_neo4j/run_all_neo4j_tests.py

# Run individual tests
python test/kg_neo4j/test_neo4j_connection.py
python test/kg_neo4j/test_password_validation.py
python test/kg_neo4j/test_data_import.py
python test/kg_neo4j/test_neo4j_integration.py
```

## Running Tests

### Run All Tests
```bash
cd test
python run_all_tests.py
```

### Run Specific Test Categories
```bash
# Unit tests only
cd test/unit
python test_basic.py

# Data quality tests only
cd test/data_quality
python test_aasx_data_quality.py

# AASX tests only
cd test/aasx
python test_dotnet_bridge.py

# Web application tests only
cd test/webapp
python test_webapp_routes.py

# Performance tests only
cd test/performance
python test_aasx_performance.py

# Error handling tests only
cd test/error_handling
python test_error_scenarios.py

# Integration tests only
cd test/integration
python test_hybrid_processing.py

# Knowledge Graph tests only
python test/kg_neo4j/run_all_neo4j_tests.py
```

### Run Individual Tests
```bash
# Test data quality
python test/data_quality/test_aasx_data_quality.py

# Test performance
python test/performance/test_aasx_performance.py

# Test error handling
python test/error_handling/test_error_scenarios.py

# Test web application
python test/webapp/test_webapp_routes.py

# Test Neo4j integration
python test/kg_neo4j/test_neo4j_integration.py
```

## Test Prerequisites

### Environment Setup
1. **Python Environment**: Python 3.8+ with required packages
2. **.NET 6.0**: For AAS processor tests
3. **Neo4j Database**: For knowledge graph tests
4. **Qdrant**: For vector database tests
5. **Environment Variables**: Properly configured `.env` file

### Required Dependencies
```bash
# Install test dependencies
pip install -r requirements.txt

# Install additional test packages
pip install pytest pytest-cov pytest-mock
```

### Database Setup
```bash
# Start Neo4j (for knowledge graph tests)
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# Start Qdrant (for vector database tests)
docker run -d --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant:latest
```

## Test Results

### Expected Output
```
============================================================
Test Results: X/Y tests passed
============================================================
✅ Unit Tests: X/X passed
✅ Data Quality Tests: X/X passed
✅ AASX Tests: X/X passed
✅ Web Application Tests: X/X passed
✅ Performance Tests: X/X passed
✅ Error Handling Tests: X/X passed
✅ Integration Tests: X/X passed
✅ Knowledge Graph Tests: X/X passed
============================================================
🎉 All tests passed! Framework is ready to use.
```

### Test Categories
- **Unit Tests**: Basic functionality and imports
- **Data Quality Tests**: Data integrity and validation
- **AASX Tests**: File processing and .NET integration
- **Web Application Tests**: Routes and templates
- **Performance Tests**: Speed and memory usage
- **Error Handling Tests**: Failure scenarios
- **Integration Tests**: Cross-module functionality
- **Knowledge Graph Tests**: Neo4j integration

## Troubleshooting

### Common Test Issues

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing packages
pip install -r requirements.txt
```

#### Database Connection Errors
```bash
# Check Neo4j status
docker ps | grep neo4j

# Test connection
python test/kg_neo4j/test_neo4j_connection.py
```

#### .NET Processor Errors
```bash
# Check .NET installation
dotnet --version

# Rebuild processor
cd aas-processor
dotnet build --configuration Release
```

### Debug Commands

#### Verbose Test Output
```bash
# Run with verbose output
python -v test/unit/test_basic.py

# Run with coverage
python -m pytest test/ --cov=. --cov-report=html
```

#### Individual Component Testing
```bash
# Test .NET bridge only
python test/aasx/test_dotnet_bridge.py

# Test Neo4j connection only
python test/kg_neo4j/test_neo4j_connection.py

# Test web routes only
python test/webapp/test_webapp_routes.py
```

## Continuous Integration

### Automated Testing
These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    python test/run_all_tests.py
```

### Test Dependencies
- Python 3.8+
- .NET 6.0 SDK
- Neo4j database
- Qdrant vector database
- Required Python packages

## Contributing

### Adding New Tests
1. Create test file in appropriate directory
2. Follow existing naming conventions
3. Include comprehensive test coverage
4. Update this README with new test information
5. Ensure tests pass before submitting

### Test Standards
- Use descriptive test names
- Include setup and teardown
- Test both success and failure cases
- Provide clear error messages
- Maintain test isolation 