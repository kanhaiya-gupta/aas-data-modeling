# Neo4j Integration Tests

This directory contains comprehensive tests for the Neo4j integration functionality in the AASX Data Modeling Platform.

## 🧪 Test Files

### Core Tests
- **`test_neo4j_integration.py`** - Comprehensive integration test suite
- **`test_neo4j_connection.py`** - Connection testing with detailed error reporting
- **`test_password_validation.py`** - Password testing utility
- **`test_data_import.py`** - Data import functionality testing

### Test Runner
- **`run_all_neo4j_tests.py`** - Runs all Neo4j tests in sequence

## 🚀 Quick Start

### Run All Tests
```bash
python test/kg_neo4j/run_all_neo4j_tests.py
```

### Run Individual Tests
```bash
# Test connection only
python test/kg_neo4j/test_neo4j_connection.py

# Test password validation
python test/kg_neo4j/test_password_validation.py

# Test data import
python test/kg_neo4j/test_data_import.py

# Run comprehensive integration test
python test/kg_neo4j/test_neo4j_integration.py
```

## 📋 Test Coverage

### 1. Environment Variables Test
- ✅ Load `.env` file
- ✅ Read Neo4j configuration
- ✅ Validate required variables

### 2. Module Imports Test
- ✅ Import Neo4jManager
- ✅ Import AASXGraphAnalyzer
- ✅ Import CypherQueries

### 3. Connection Test
- ✅ Neo4j database connection
- ✅ Authentication validation
- ✅ Version detection
- ✅ Error handling

### 4. Graph Validation Test
- ✅ Valid graph data structure
- ✅ Invalid data rejection
- ✅ Format validation

### 5. Cypher Queries Test
- ✅ Static query generation
- ✅ Dynamic query building
- ✅ Query validation

### 6. ETL Integration Test
- ✅ ETL output directory detection
- ✅ Graph file discovery
- ✅ File format validation
- ✅ Data structure validation

### 7. Data Import Test
- ✅ Graph data validation
- ✅ Import execution
- ✅ Database statistics

## 🔧 Prerequisites

### Required Dependencies
```bash
pip install neo4j pandas python-dotenv
```

### Environment Setup
Ensure your `.env` file contains:
```env
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Neo4j Database
- Neo4j must be running
- Database accessible on configured URI
- Valid credentials configured

### ETL Pipeline
- Run ETL pipeline first: `python scripts/run_etl.py`
- Ensure `output/etl_results/` contains graph files

## 📊 Expected Results

### Successful Test Run
```
============================================================
Test Results: 6/6 tests passed
============================================================
🎉 All tests passed! Neo4j integration is ready to use.
```

### Test Categories
- **Environment Variables**: 1 test
- **Module Imports**: 1 test
- **Graph Validation**: 1 test
- **Cypher Queries**: 1 test
- **ETL Integration**: 1 test
- **Neo4j Connection**: 1 test

## 🐛 Troubleshooting

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

## 📈 Test Results Interpretation

### All Tests Passed ✅
- Neo4j integration is fully functional
- Ready for data import and analytics
- All components working correctly

### Some Tests Failed ⚠️
- Check specific error messages
- Verify prerequisites are met
- Follow troubleshooting steps

### Connection Tests Failed ❌
- Verify Neo4j is running
- Check credentials in `.env` file
- Ensure network connectivity

## 🔄 Continuous Integration

### Automated Testing
These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Test Neo4j Integration
  run: |
    python test/kg_neo4j/run_all_neo4j_tests.py
```

### Test Dependencies
- Python 3.8+
- Neo4j database running
- ETL pipeline output available
- Required Python packages installed

## 📝 Adding New Tests

### Test Structure
```python
def test_new_functionality():
    """Test description"""
    print("Testing new functionality...")
    
    try:
        # Test implementation
        result = some_function()
        
        if expected_condition:
            print("✅ Test passed")
            return True
        else:
            print("❌ Test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
```

### Adding to Test Suite
1. Create test file: `test_new_feature.py`
2. Add to `run_all_neo4j_tests.py`:
   ```python
   test_files = [
       # ... existing tests
       "test_new_feature.py"
   ]
   ```

## 🎯 Success Criteria

A successful test run indicates:
- ✅ Neo4j connection established
- ✅ All modules imported correctly
- ✅ Graph data validation working
- ✅ Cypher queries functional
- ✅ ETL integration operational
- ✅ Data import capabilities verified

This confirms the Neo4j integration is ready for production use in the AASX Data Modeling Platform. 