#!/usr/bin/env python3
"""
Fix the Neo4j password in .env file
"""

import os
from pathlib import Path

def fix_password():
    """Fix the password in .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    content = env_file.read_text()
    
    # Replace the password line
    new_content = content.replace(
        'NEO4J_PASSWORD=password',
        'NEO4J_PASSWORD=Qidigital123'
    ).replace(
        'NEO4J_PASSWORD=QI_Digital123',
        'NEO4J_PASSWORD=Qidigital123'
    )
    
    # Write back to file
    env_file.write_text(new_content)
    
    print("✅ Fixed .env file with correct password: Qidigital123")
    print("\n📋 Updated .env content:")
    print("-" * 30)
    print(new_content)
    
    return True

if __name__ == "__main__":
    fix_password() 