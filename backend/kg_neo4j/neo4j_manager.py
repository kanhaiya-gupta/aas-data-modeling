"""
Neo4j Manager for AASX Data Import and Management

This module provides the core Neo4j integration functionality for importing
AASX graph data and managing database operations.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from neo4j import GraphDatabase, Driver, Session
import pandas as pd

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, will use system environment variables

logger = logging.getLogger(__name__)

class Neo4jManager:
    """
    Manager class for Neo4j database operations.
    
    Handles connection management, data import, and basic query operations.
    """
    
    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Neo4j manager.
        
        Args:
            uri: Neo4j connection URI (e.g., 'bolt://localhost:7687')
            user: Neo4j username
            password: Neo4j password
            
        If not provided, will use environment variables:
        - NEO4J_URI
        - NEO4J_USER
        - NEO4J_PASSWORD
        """
        # Use environment variables if not provided
        self.uri = uri or os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        logger.info(f"Initializing Neo4j connection to {self.uri}")
        self.driver: Optional[Driver] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test Neo4j connection"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            logger.info("✓ Neo4j connection test successful")
            return True
        except Exception as e:
            logger.error(f"✗ Neo4j connection test failed: {e}")
            return False
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def import_graph_file(self, graph_file_path: Union[str, Path]):
        """
        Import a single graph file to Neo4j.
        
        Args:
            graph_file_path: Path to the graph JSON file
        """
        graph_file_path = Path(graph_file_path)
        
        if not graph_file_path.exists():
            raise FileNotFoundError(f"Graph file not found: {graph_file_path}")
        
        logger.info(f"Importing graph file: {graph_file_path.name}")
        
        # Load graph data
        with open(graph_file_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # Validate graph data structure
        if not self._validate_graph_data(graph_data):
            raise ValueError(f"Invalid graph data structure in {graph_file_path}")
        
        # Import to Neo4j
        with self.driver.session() as session:
            # Import nodes
            nodes_imported = self._import_nodes(session, graph_data['nodes'])
            logger.info(f"Imported {nodes_imported} nodes")
            
            # Import relationships
            if graph_data.get('edges'):
                rels_imported = self._import_relationships(session, graph_data['edges'])
                logger.info(f"Imported {rels_imported} relationships")
            else:
                logger.info("No relationships to import")
    
    def _validate_graph_data(self, graph_data: Dict[str, Any]) -> bool:
        """Validate graph data structure"""
        required_keys = ['format', 'version', 'nodes']
        
        if not all(key in graph_data for key in required_keys):
            logger.error(f"Missing required keys: {required_keys}")
            return False
        
        if graph_data['format'] != 'graph':
            logger.error(f"Invalid format: {graph_data['format']}, expected 'graph'")
            return False
        
        if not isinstance(graph_data['nodes'], list):
            logger.error("Nodes must be a list")
            return False
        
        return True
    
    def _import_nodes(self, session: Session, nodes: List[Dict[str, Any]]) -> int:
        """Import nodes to Neo4j"""
        imported_count = 0
        
        for node in nodes:
            try:
                # Create node with properties
                query = """
                MERGE (n:Node {id: $id})
                SET n += $properties
                SET n.type = $node_type
                """
                
                session.run(query, 
                           id=node['id'],
                           properties=node.get('properties', {}),
                           node_type=node.get('type', 'unknown'))
                
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Error importing node {node.get('id', 'unknown')}: {e}")
        
        return imported_count
    
    def _import_relationships(self, session: Session, edges: List[Dict[str, Any]]) -> int:
        """Import relationships to Neo4j"""
        imported_count = 0
        
        for edge in edges:
            try:
                # Create relationship
                query = """
                MATCH (source:Node {id: $source_id})
                MATCH (target:Node {id: $target_id})
                MERGE (source)-[r:RELATES_TO]->(target)
                SET r.type = $rel_type
                SET r += $properties
                """
                
                session.run(query,
                           source_id=edge['source'],
                           target_id=edge['target'],
                           rel_type=edge.get('type', 'unknown'),
                           properties=edge.get('properties', {}))
                
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Error importing relationship {edge.get('source', 'unknown')} -> {edge.get('target', 'unknown')}: {e}")
        
        return imported_count
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            
        Returns:
            List of result records as dictionaries
        """
        try:
            with self.driver.session() as session:
                result = session.run(query)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        try:
            with self.driver.session() as session:
                # Get node count
                node_count = session.run("MATCH (n:Node) RETURN count(n) as count").single()['count']
                
                # Get relationship count
                rel_count = session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count").single()['count']
                
                # Get node types
                node_types = session.run("""
                    MATCH (n:Node)
                    RETURN n.type as type, count(*) as count
                    ORDER BY count DESC
                """).data()
                
                # Get relationship types
                rel_types = session.run("""
                    MATCH ()-[r:RELATES_TO]->()
                    RETURN r.type as type, count(*) as count
                    ORDER BY count DESC
                """).data()
                
                return {
                    'total_nodes': node_count,
                    'total_relationships': rel_count,
                    'node_types': node_types,
                    'relationship_types': rel_types
                }
                
        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            return {}
    
    def clear_database(self):
        """Clear all data from the database"""
        try:
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            raise
    
    def create_indexes(self):
        """Create indexes for better performance"""
        try:
            with self.driver.session() as session:
                # Create indexes
                indexes = [
                    "CREATE INDEX node_id_index IF NOT EXISTS FOR (n:Node) ON (n.id)",
                    "CREATE INDEX node_type_index IF NOT EXISTS FOR (n:Node) ON (n.type)",
                    "CREATE INDEX node_quality_index IF NOT EXISTS FOR (n:Node) ON (n.quality_level)",
                    "CREATE INDEX rel_type_index IF NOT EXISTS FOR ()-[r:RELATES_TO]-() ON (r.type)"
                ]
                
                for index_query in indexes:
                    session.run(index_query)
                
            logger.info("Indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise 