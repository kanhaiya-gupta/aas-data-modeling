#!/usr/bin/env python3
"""
Test script for Knowledge Graph System (Independent)
"""

import requests
import time
import json
import os
from pathlib import Path

def test_knowledge_graph_api():
    """Test Knowledge Graph API service"""
    print("🧪 Testing Knowledge Graph API...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8004/health", timeout=10)
        if response.status_code == 200:
            print("✅ Knowledge Graph API is healthy")
            return True
        else:
            print(f"❌ Knowledge Graph API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Knowledge Graph API not accessible: {e}")
        return False

def test_neo4j_database():
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
        "data/graph_data",
        "data/processed",
        "output",
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

def test_graph_data_loading():
    """Test if graph data can be loaded"""
    print("🧪 Testing Graph Data Loading...")
    
    graph_data_dir = Path("data/graph_data")
    if not graph_data_dir.exists():
        print("❌ No graph data directory found")
        return False
    
    # Check for common graph data formats
    graph_files = []
    graph_files.extend(graph_data_dir.glob("*.json"))
    graph_files.extend(graph_data_dir.glob("*.csv"))
    graph_files.extend(graph_data_dir.glob("*.cypher"))
    graph_files.extend(graph_data_dir.glob("*.graphml"))
    
    if not graph_files:
        print("❌ No graph data files found in graph_data directory")
        print("   Supported formats: .json, .csv, .cypher, .graphml")
        return False
    
    print(f"✅ Found {len(graph_files)} graph data files:")
    for file in graph_files:
        print(f"   - {file.name}")
    
    return True

def test_knowledge_graph_queries():
    """Test basic knowledge graph queries"""
    print("🧪 Testing Knowledge Graph Queries...")
    
    try:
        # Test basic query endpoint
        query_data = {
            "query": "MATCH (n) RETURN count(n) as node_count"
        }
        
        response = requests.post(
            "http://localhost:8004/query",
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Knowledge Graph query endpoint working")
            return True
        else:
            print(f"❌ Knowledge Graph query failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Knowledge Graph query not accessible: {e}")
        return False

def test_data_loading_api():
    """Test data loading API"""
    print("🧪 Testing Data Loading API...")
    
    try:
        # Test data loading endpoint
        response = requests.get("http://localhost:8004/load", timeout=10)
        
        if response.status_code in [200, 404]:  # 404 is OK if no data to load
            print("✅ Data loading API accessible")
            return True
        else:
            print(f"❌ Data loading API failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Data loading API not accessible: {e}")
        return False

def main():
    """Run all knowledge graph tests"""
    print("🧠 Testing Knowledge Graph System (Independent)")
    print("=" * 60)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    tests = [
        ("Knowledge Graph API", test_knowledge_graph_api),
        ("Neo4j Database", test_neo4j_database),
        ("Data Directories", test_data_directories),
        ("Graph Data Files", test_graph_data_loading),
        ("Graph Queries", test_knowledge_graph_queries),
        ("Data Loading API", test_data_loading_api),
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
        print("🎉 Knowledge Graph system is working correctly!")
        print("\n📚 Next Steps:")
        print("   1. Place graph data files in ./data/graph_data/")
        print("   2. Use Neo4j browser at http://localhost:7474")
        print("   3. Use Knowledge Graph API at http://localhost:8004")
        print("   4. Run graph queries and analysis")
    else:
        print("⚠️  Some components need attention. Check logs and configuration.")
    
    print("\n🔗 Available Endpoints:")
    print("   Knowledge Graph API:  http://localhost:8004")
    print("   Neo4j Browser:        http://localhost:7474")
    print("   Neo4j Bolt:           bolt://localhost:7687")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 