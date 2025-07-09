#!/usr/bin/env python3
"""
Neo4j Password Validation Test

This script tests different Neo4j passwords to find the correct one.
"""

import os
from neo4j import GraphDatabase

def test_password(password):
    """Test a specific password"""
    uri = "neo4j://127.0.0.1:7687"
    user = "neo4j"
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()['test']
        driver.close()
        return True
    except Exception as e:
        return False

def main():
    print("Testing Neo4j Passwords...")
    print("=" * 40)
    
    # Common passwords to try
    passwords_to_test = [
        "neo4j",  # Default password
        "Qidigital123",  # Working password
        "QI_Digital123",  # Previous password
        "password",
        "admin",
        "123456",
        "neo4j123"
    ]
    
    for password in passwords_to_test:
        print(f"Testing password: {password}")
        if test_password(password):
            print(f"SUCCESS! Password is: {password}")
            print(f"   Update your .env file with: NEO4J_PASSWORD={password}")
            return password
        else:
            print(f"Failed")
    
    print("\nFAILED: None of the common passwords worked.")
    print("   You may need to:")
    print("   1. Reset your Neo4j password")
    print("   2. Check if you changed it during setup")
    print("   3. Look in your Neo4j Desktop settings")
    
    return None

if __name__ == "__main__":
    main() 