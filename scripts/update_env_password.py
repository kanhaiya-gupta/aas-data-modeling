#!/usr/bin/env python3
"""
Update .env file with the correct Neo4j password
"""

import os
from pathlib import Path

def update_env_password():
    """Update .env file with correct Neo4j password"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    content = env_file.read_text()
    
    # Update the password line
    lines = content.split('\n')
    updated_lines = []
    
    for line in lines:
        if line.startswith('NEO4J_PASSWORD='):
            updated_lines.append('NEO4J_PASSWORD=Qidigital123')
        else:
            updated_lines.append(line)
    
    # Write back to file
    new_content = '\n'.join(updated_lines)
    env_file.write_text(new_content)
    
    print("✅ Updated .env file with correct password: Qidigital123")
    print("\n📋 Current .env content:")
    print("-" * 30)
    print(new_content)
    
    return True

if __name__ == "__main__":
    update_env_password() 