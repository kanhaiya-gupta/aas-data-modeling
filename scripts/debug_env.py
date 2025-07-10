#!/usr/bin/env python3
"""
Debug environment variables
"""

import os

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded successfully")
except ImportError:
    print("⚠️  dotenv not available")
except Exception as e:
    print(f"❌ Error loading dotenv: {e}")

print("\n🔍 Environment Variables:")
print("=" * 30)
print(f"NEO4J_URI: {os.getenv('NEO4J_URI', 'NOT SET')}")
print(f"NEO4J_USER: {os.getenv('NEO4J_USER', 'NOT SET')}")
print(f"NEO4J_PASSWORD: {os.getenv('NEO4J_PASSWORD', 'NOT SET')}")

# Test the actual connection
print("\n🔍 Testing Connection...")
print("=" * 30)

try:
    from neo4j import GraphDatabase
    
    uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"Connecting with:")
    print(f"  URI: {uri}")
    print(f"  User: {user}")
    print(f"  Password: {'*' * len(password)} ({len(password)} chars)")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        value = result.single()['test']
    
    print("✅ Connection successful!")
    driver.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}") 