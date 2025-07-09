"""
Graph Analyzer for AASX Data Analytics

This module provides advanced graph analytics functionality for analyzing
AASX data in Neo4j, including quality analysis, compliance checking,
and relationship analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase
import pandas as pd

logger = logging.getLogger(__name__)

class AASXGraphAnalyzer:
    """
    Advanced graph analyzer for AASX data.
    
    Provides comprehensive analytics capabilities for AASX data in Neo4j,
    including quality analysis, compliance checking, and relationship analysis.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize graph analyzer.
        
        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def get_network_statistics(self) -> pd.DataFrame:
        """
        Get comprehensive network statistics.
        
        Returns:
            DataFrame with network statistics
        """
        try:
            with self.driver.session() as session:
                # Get basic counts
                node_count = session.run("MATCH (n:Node) RETURN count(n) as count").single()['count']
                rel_count = session.run("MATCH ()-[r:RELATES_TO]->() RETURN count(r) as count").single()['count']
                
                # Get isolated nodes count
                isolated_count = session.run("""
                    MATCH (n:Node)
                    WHERE NOT (n)-[:RELATES_TO]-()
                    RETURN count(n) as count
                """).single()['count']
                
                # Get connected components count
                components_count = session.run("""
                    CALL gds.alpha.scc.stream('aasx_graph')
                    YIELD componentId
                    RETURN count(DISTINCT componentId) as count
                """).single()['count']
                
                stats = pd.DataFrame([
                    {'metric': 'Total Nodes', 'value': node_count},
                    {'metric': 'Total Relationships', 'value': rel_count},
                    {'metric': 'Isolated Nodes', 'value': isolated_count},
                    {'metric': 'Connected Components', 'value': components_count},
                    {'metric': 'Average Degree', 'value': (2 * rel_count) / node_count if node_count > 0 else 0}
                ])
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting network statistics: {e}")
            return pd.DataFrame()
    
    def get_quality_distribution(self) -> pd.DataFrame:
        """
        Get quality level distribution across entities.
        
        Returns:
            DataFrame with quality distribution
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Node)
                    WHERE n.quality_level IS NOT NULL
                    RETURN n.type as entity_type, 
                           n.quality_level as quality_level, 
                           count(*) as count
                    ORDER BY entity_type, quality_level
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error getting quality distribution: {e}")
            return pd.DataFrame()
    
    def analyze_compliance_network(self) -> pd.DataFrame:
        """
        Analyze compliance status across the network.
        
        Returns:
            DataFrame with compliance analysis
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Node)
                    WHERE n.compliance_status IS NOT NULL
                    RETURN n.type as entity_type,
                           n.compliance_status as compliance_status,
                           count(*) as count
                    ORDER BY entity_type, compliance_status
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error analyzing compliance: {e}")
            return pd.DataFrame()
    
    def get_entity_type_distribution(self) -> pd.DataFrame:
        """
        Get distribution of entity types.
        
        Returns:
            DataFrame with entity type distribution
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Node)
                    RETURN n.type as entity_type, count(*) as count
                    ORDER BY count DESC
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error getting entity distribution: {e}")
            return pd.DataFrame()
    
    def analyze_relationships(self) -> pd.DataFrame:
        """
        Analyze relationship patterns in the graph.
        
        Returns:
            DataFrame with relationship analysis
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (source:Node)-[r:RELATES_TO]->(target:Node)
                    RETURN r.type as relationship_type,
                           source.type as source_type,
                           target.type as target_type,
                           count(*) as count
                    ORDER BY count DESC
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error analyzing relationships: {e}")
            return pd.DataFrame()
    
    def find_related_entities(self, entity_id: str, max_depth: int = 2) -> pd.DataFrame:
        """
        Find entities related to a specific entity within max_depth.
        
        Args:
            entity_id: ID of the entity to find relations for
            max_depth: Maximum path length to search
            
        Returns:
            DataFrame with related entities
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = (start:Node {id: $entity_id})-[*1..$max_depth]-(related:Node)
                    WHERE start <> related
                    RETURN DISTINCT related.id as id,
                           related.type as type,
                           related.description as description,
                           length(path) as distance
                    ORDER BY distance, related.type
                """, entity_id=entity_id, max_depth=max_depth)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error finding related entities: {e}")
            return pd.DataFrame()
    
    def get_high_quality_assets(self, min_quality: str = 'HIGH') -> pd.DataFrame:
        """
        Get assets with specified minimum quality level.
        
        Args:
            min_quality: Minimum quality level ('LOW', 'MEDIUM', 'HIGH')
            
        Returns:
            DataFrame with high-quality assets
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Node {type: 'asset'})
                    WHERE n.quality_level = $min_quality
                    RETURN n.id as id,
                           n.description as description,
                           n.quality_level as quality_level,
                           n.compliance_status as compliance_status
                    ORDER BY n.description
                """, min_quality=min_quality)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error getting high-quality assets: {e}")
            return pd.DataFrame()
    
    def get_compliance_summary(self) -> pd.DataFrame:
        """
        Get summary of compliance status across all entities.
        
        Returns:
            DataFrame with compliance summary
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Node)
                    WHERE n.compliance_status IS NOT NULL
                    RETURN n.compliance_status as status,
                           count(*) as count,
                           round(count(*) * 100.0 / size(collect(n)), 2) as percentage
                    ORDER BY count DESC
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error getting compliance summary: {e}")
            return pd.DataFrame()
    
    def find_isolated_nodes(self) -> pd.DataFrame:
        """
        Find nodes that have no relationships.
        
        Returns:
            DataFrame with isolated nodes
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (n:Node)
                    WHERE NOT (n)-[:RELATES_TO]-()
                    RETURN n.id as id,
                           n.type as type,
                           n.description as description,
                           n.quality_level as quality_level
                    ORDER BY n.type, n.description
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error finding isolated nodes: {e}")
            return pd.DataFrame()
    
    def get_connected_components(self) -> pd.DataFrame:
        """
        Get information about connected components in the graph.
        
        Returns:
            DataFrame with connected components info
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    CALL gds.alpha.scc.stream('aasx_graph')
                    YIELD nodeId, componentId
                    RETURN componentId,
                           count(*) as size
                    ORDER BY size DESC
                """)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error getting connected components: {e}")
            return pd.DataFrame()
    
    def search_entities(self, search_term: str, entity_type: Optional[str] = None) -> pd.DataFrame:
        """
        Search for entities by description or ID.
        
        Args:
            search_term: Search term to look for
            entity_type: Optional entity type filter
            
        Returns:
            DataFrame with matching entities
        """
        try:
            with self.driver.session() as session:
                if entity_type:
                    query = """
                        MATCH (n:Node {type: $entity_type})
                        WHERE toLower(n.description) CONTAINS toLower($search_term)
                           OR toLower(n.id) CONTAINS toLower($search_term)
                        RETURN n.id as id,
                               n.type as type,
                               n.description as description,
                               n.quality_level as quality_level
                        ORDER BY n.description
                    """
                    result = session.run(query, search_term=search_term, entity_type=entity_type)
                else:
                    query = """
                        MATCH (n:Node)
                        WHERE toLower(n.description) CONTAINS toLower($search_term)
                           OR toLower(n.id) CONTAINS toLower($search_term)
                        RETURN n.id as id,
                               n.type as type,
                               n.description as description,
                               n.quality_level as quality_level
                        ORDER BY n.type, n.description
                    """
                    result = session.run(query, search_term=search_term)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return pd.DataFrame()
    
    def get_path_between_entities(self, source_id: str, target_id: str) -> pd.DataFrame:
        """
        Find shortest path between two entities.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            
        Returns:
            DataFrame with path information
        """
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = shortestPath(
                        (source:Node {id: $source_id})-[*]-(target:Node {id: $target_id})
                    )
                    RETURN length(path) as path_length,
                           [node in nodes(path) | node.id] as node_ids,
                           [node in nodes(path) | node.type] as node_types
                """, source_id=source_id, target_id=target_id)
                
                data = [record.data() for record in result]
                return pd.DataFrame(data)
                
        except Exception as e:
            logger.error(f"Error finding path between entities: {e}")
            return pd.DataFrame() 