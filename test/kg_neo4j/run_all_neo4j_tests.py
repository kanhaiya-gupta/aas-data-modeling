#!/usr/bin/env python3
"""
Neo4j Test Runner

This script runs all Neo4j integration tests.
"""

import sys
import subprocess
from pathlib import Path

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"ERROR: Error running {test_file}: {e}")
        return False

def main():
    """Run all Neo4j tests"""
    print("Neo4j Test Suite Runner")
    print("=" * 60)
    
    # Define test files in order of execution
    test_files = [
        "test_neo4j_connection.py",
        "test_password_validation.py", 
        "test_data_import.py",
        "test_neo4j_integration.py"
    ]
    
    passed = 0
    total = len(test_files)
    
    for test_file in test_files:
        if Path(test_file).exists():
            if run_test(test_file):
                passed += 1
                print(f"SUCCESS: {test_file} PASSED")
            else:
                print(f"FAILED: {test_file} FAILED")
        else:
            print(f"WARNING: {test_file} not found, skipping")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed}/{total} test suites passed")
    print(f"{'='*60}")
    
    if passed == total:
        print("SUCCESS: All Neo4j tests passed!")
        print("\nSUCCESS: Neo4j integration is fully functional!")
        print("\nNext steps:")
        print("1. Import data: python scripts/integrate_neo4j.py --import-dir output/etl_results")
        print("2. Run analytics: python scripts/integrate_neo4j.py --analyze")
        print("3. Execute queries: python scripts/integrate_neo4j.py --query 'MATCH (n:Node) RETURN count(n)'")
    else:
        print("WARNING: Some tests failed. Check the output above for details.")
        print("\nTroubleshooting:")
        print("1. Ensure Neo4j is running")
        print("2. Check .env file configuration")
        print("3. Install dependencies: pip install neo4j pandas python-dotenv")
        print("4. Run ETL pipeline first: python scripts/run_etl.py")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 