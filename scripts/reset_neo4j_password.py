#!/usr/bin/env python3
"""
Neo4j Password Reset Helper

This script helps you reset your Neo4j password.
"""

import webbrowser
import time

def main():
    print("🔧 Neo4j Password Reset Helper")
    print("=" * 40)
    
    print("\n📋 Steps to reset your Neo4j password:")
    print("1. Open Neo4j Desktop")
    print("2. Find your database: QI_Digital_AASX")
    print("3. Click 'Start' if not running")
    print("4. Click 'Open with Neo4j Browser'")
    print("5. In the browser, run these commands:")
    
    print("\n🔑 Commands to run in Neo4j Browser:")
    print("-" * 30)
    print("// First, try to connect with default password")
    print(":server connect")
    print("// If that works, change the password:")
    print("ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'QI_Digital123'")
    print("// Or create a new user:")
    print("CREATE USER qi_user SET PASSWORD 'QI_Digital123'")
    print("GRANT ROLE admin TO qi_user")
    
    print("\n🌐 Opening Neo4j Browser...")
    print("   (If it doesn't open automatically, go to: http://localhost:7474)")
    
    # Try to open Neo4j Browser
    try:
        webbrowser.open('http://localhost:7474')
        print("✅ Neo4j Browser should open in your default browser")
    except:
        print("⚠️  Could not open browser automatically")
        print("   Please go to: http://localhost:7474")
    
    print("\n📝 After resetting the password:")
    print("1. Update your .env file with the new password")
    print("2. Run: python scripts/test_neo4j_connection.py")
    print("3. If successful, run: python scripts/test_neo4j_integration.py")

if __name__ == "__main__":
    main() 