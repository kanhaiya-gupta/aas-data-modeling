#!/usr/bin/env python3
"""
Environment Configuration Updater

This script helps update the .env file with complete Neo4j configuration
and other necessary environment variables.
"""

import os
from pathlib import Path

def update_env_file():
    """Update .env file with complete configuration"""
    env_file = Path('.env')
    
    # Current content
    current_content = ""
    if env_file.exists():
        current_content = env_file.read_text()
        print(f"Current .env content:\n{current_content}")
    
    # New content with complete configuration
    new_content = """# Neo4j Local Configuration
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=QI_Digital123
NEO4J_DATABASE=neo4j

# Database Configuration
DATABASE_URL=postgresql://aasx_user:aasx_password@localhost:5432/aasx_data
REDIS_URL=redis://localhost:6379

# AI Services (Optional)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Application Settings
JWT_SECRET=your_jwt_secret_key_here
NODE_ENV=development
"""
    
    # Write new content
    env_file.write_text(new_content)
    print(f"\nUpdated .env file with complete configuration")
    print(f"Please update the Neo4j password and other sensitive values as needed")

if __name__ == "__main__":
    update_env_file() 