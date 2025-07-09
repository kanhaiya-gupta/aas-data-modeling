#!/usr/bin/env python3
"""
Neo4j Connection Test

This script tests the Neo4j connection with detailed error reporting.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def test_neo4j_connection():
    """Test Neo4j connection with detailed error reporting"""
    print("Testing Neo4j Connection...")
    print("=" * 50)
    
    # Get connection parameters
    uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"URI: {uri}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password)} ({len(password)} chars)")
    print()
    
    try:
        from neo4j import GraphDatabase
        
        print("Attempting to connect...")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()['test']
            
        print("SUCCESS: Connection successful!")
        print(f"   Test query returned: {value}")
        
        # Get Neo4j version
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            component = result.single()
            if component:
                print(f"   Neo4j Version: {component['versions'][0]}")
                print(f"   Edition: {component['edition']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print("FAILED: Connection failed!")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        
        # Provide specific troubleshooting advice
        if "authentication failure" in str(e).lower():
            print("\nAuthentication Troubleshooting:")
            print("   1. Check if Neo4j is running")
            print("   2. Verify username and password")
            print("   3. If this is a fresh install, try password: 'neo4j'")
            print("   4. You may need to change the default password on first login")
        elif "connection refused" in str(e).lower():
            print("\nConnection Troubleshooting:")
            print("   1. Make sure Neo4j is running")
            print("   2. Check if Neo4j is listening on port 7687")
            print("   3. Verify firewall settings")
        
        return False

if __name__ == "__main__":
    success = test_neo4j_connection()
    sys.exit(0 if success else 1) 