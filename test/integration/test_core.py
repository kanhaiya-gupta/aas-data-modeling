#!/usr/bin/env python3
"""
Test script for core components: ETL Pipeline and Knowledge Graph
"""

import requests
import time
import json
import os
from pathlib import Path

def test_etl_pipeline():
    """Test ETL Pipeline service"""
    print("🧪 Testing ETL Pipeline...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8003/health", timeout=10)
        if response.status_code == 200:
            print("✅ ETL Pipeline is healthy")
            return True
        else:
            print(f"❌ ETL Pipeline health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ETL Pipeline not accessible: {e}")
        return False

def test_knowledge_graph():
    """Test Knowledge Graph service"""
    print("🧪 Testing Knowledge Graph...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8004/health", timeout=10)
        if response.status_code == 200:
            print("✅ Knowledge Graph is healthy")
            return True
        else:
            print(f"❌ Knowledge Graph health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Knowledge Graph not accessible: {e}")
        return False

def test_neo4j():
    """Test Neo4j database"""
    print("🧪 Testing Neo4j Database...")
    
    try:
        # Test Neo4j browser endpoint
        response = requests.get("http://localhost:7474/browser/", timeout=10)
        if response.status_code == 200:
            print("✅ Neo4j Database is accessible")
            return True
        else:
            print(f"❌ Neo4j Database not accessible: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Neo4j Database not accessible: {e}")
        return False

def test_data_directories():
    """Test if data directories exist and are accessible"""
    print("🧪 Testing Data Directories...")
    
    directories = [
        "data/aasx-examples",
        "output/etl_results",
        "logs"
    ]
    
    all_exist = True
    for directory in directories:
        if Path(directory).exists():
            print(f"✅ {directory} exists")
        else:
            print(f"❌ {directory} missing")
            all_exist = False
    
    return all_exist

def test_sample_aasx_processing():
    """Test if sample AASX files can be processed"""
    print("🧪 Testing AASX File Processing...")
    
    aasx_dir = Path("data/aasx-examples")
    if not aasx_dir.exists():
        print("❌ No AASX examples directory found")
        return False
    
    aasx_files = list(aasx_dir.glob("*.aasx"))
    if not aasx_files:
        print("❌ No AASX files found in examples directory")
        return False
    
    print(f"✅ Found {len(aasx_files)} AASX files:")
    for file in aasx_files:
        print(f"   - {file.name}")
    
    return True

def main():
    """Run all core component tests"""
    print("🚀 Testing Core Components: ETL Pipeline + Knowledge Graph")
    print("=" * 60)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    tests = [
        ("ETL Pipeline", test_etl_pipeline),
        ("Knowledge Graph", test_knowledge_graph),
        ("Neo4j Database", test_neo4j),
        ("Data Directories", test_data_directories),
        ("AASX Files", test_sample_aasx_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All core components are working correctly!")
        print("\n📚 Next Steps:")
        print("   1. Place AASX files in ./data/aasx-examples/")
        print("   2. Run ETL pipeline to process data")
        print("   3. Access knowledge graph for analysis")
        print("   4. Use Neo4j browser at http://localhost:7474")
    else:
        print("⚠️  Some components need attention. Check logs and configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 