#!/usr/bin/env python3
"""
Wait for Neo4j to be ready before running knowledge graph operations
"""

import time
import os
import sys
import logging
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def wait_for_neo4j(uri, user, password, max_attempts=60, delay=5):
    """Wait for Neo4j to be ready"""
    logger.info(f"Waiting for Neo4j at {uri} to be ready...")
    
    for attempt in range(max_attempts):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_attempts}: Testing Neo4j connection...")
            driver = GraphDatabase.driver(uri, auth=(user, password))
            
            # Test connection with timeout
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            driver.close()
            logger.info("✓ Neo4j is ready!")
            return True
            
        except Exception as e:
            logger.info(f"Attempt {attempt + 1}/{max_attempts}: Neo4j not ready yet ({str(e)[:100]}...)")
            if attempt < max_attempts - 1:
                logger.info(f"Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
            else:
                logger.error(f"✗ Neo4j failed to become ready after {max_attempts} attempts")
                return False
    
    return False

if __name__ == "__main__":
    # Get environment variables
    uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "Neo4j123")
    
    logger.info(f"Neo4j connection parameters:")
    logger.info(f"  URI: {uri}")
    logger.info(f"  User: {user}")
    logger.info(f"  Password: {'*' * len(password)}")
    
    if wait_for_neo4j(uri, user, password):
        sys.exit(0)
    else:
        sys.exit(1) 