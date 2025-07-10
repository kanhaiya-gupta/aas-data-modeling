"""
Knowledge Graph API Routes
Provides REST API endpoints for the Neo4j knowledge graph system
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'backend'))

from kg_neo4j.neo4j_manager import Neo4jManager
from kg_neo4j.cypher_queries import CypherQueries
from kg_neo4j.graph_analyzer import AASXGraphAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    execution_time: Optional[float] = None
    error: Optional[str] = None

class GraphStats(BaseModel):
    node_count: int
    relationship_count: int
    node_labels: List[str]
    relationship_types: List[str]
    database_size: Optional[str] = None
    last_updated: Optional[str] = None

class SystemStatus(BaseModel):
    status: str
    neo4j_version: Optional[str] = None
    graph_available: bool
    gds_available: bool
    last_updated: Optional[str] = None
    error: Optional[str] = None

class LoadDataRequest(BaseModel):
    data_path: str
    clear_existing: bool = False

# Initialize Neo4j manager
neo4j_manager = None
cypher_queries = None
graph_analyzer = None

def get_neo4j_manager():
    """Get or initialize Neo4j manager instance"""
    global neo4j_manager, cypher_queries, graph_analyzer
    
    if neo4j_manager is None:
        try:
            # Initialize from environment variables
            neo4j_uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
            neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
            neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
            
            neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
            cypher_queries = CypherQueries(neo4j_manager)
            graph_analyzer = AASXGraphAnalyzer(neo4j_uri, neo4j_user, neo4j_password)
            
            logger.info("Neo4j manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j manager: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize Neo4j connection")
    
    return neo4j_manager, cypher_queries, graph_analyzer

@router.get("/", response_class=HTMLResponse)
async def kg_page(request: Request):
    """Knowledge Graph main page"""
    templates = Jinja2Templates(directory="webapp/templates")
    return templates.TemplateResponse(
        "kg_neo4j/index.html",
        {
            "request": request,
            "title": "Knowledge Graph - QI Digital Platform"
        }
    )

@router.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """
    Execute a Cypher query
    
    Args:
        request: Query request with Cypher query string
        
    Returns:
        Query results with execution details
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Execute query
        results = neo4j_mgr.execute_query(request.query)
        
        return QueryResponse(
            query=request.query,
            results=results,
            execution_time=None  # Could add timing if needed
        )
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return QueryResponse(
            query=request.query,
            results=[],
            error=str(e)
        )

@router.get("/stats", response_model=GraphStats)
async def get_graph_stats():
    """
    Get knowledge graph statistics
    
    Returns:
        Graph statistics including node counts, labels, and relationship types
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Get basic stats
        node_count = neo4j_mgr.get_node_count()
        relationship_count = neo4j_mgr.get_relationship_count()
        node_labels = neo4j_mgr.get_node_labels()
        relationship_types = neo4j_mgr.get_relationship_types()
        
        return GraphStats(
            node_count=node_count,
            relationship_count=relationship_count,
            node_labels=node_labels,
            relationship_types=relationship_types,
            database_size=None,  # Could add if needed
            last_updated=None    # Could add if needed
        )
        
    except Exception as e:
        logger.error(f"Failed to get graph stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph stats: {str(e)}")

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    Get Neo4j system status
    
    Returns:
        System status including connection and feature availability
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Test connection
        connection_ok = neo4j_mgr.test_connection()
        
        # Check GDS availability
        gds_available = False
        try:
            gds_available = neo4j_mgr.check_gds_availability()
        except Exception:
            pass
        
        # Get Neo4j version
        neo4j_version = None
        try:
            version_result = neo4j_mgr.execute_query("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition")
            if version_result:
                neo4j_version = version_result[0].get('version', 'Unknown')
        except Exception:
            pass
        
        return SystemStatus(
            status="connected" if connection_ok else "disconnected",
            neo4j_version=neo4j_version,
            graph_available=connection_ok,
            gds_available=gds_available,
            last_updated=None
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return SystemStatus(
            status="error",
            graph_available=False,
            gds_available=False,
            error=str(e)
        )

@router.post("/load-data")
async def load_graph_data(request: LoadDataRequest):
    """
    Load graph data from ETL output
    
    Args:
        request: Load data request with path and options
        
    Returns:
        Loading status and statistics
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Load data from ETL output
        stats = neo4j_mgr.load_etl_data(
            etl_output_dir=request.data_path,
            clear_existing=request.clear_existing
        )
        
        return {
            "message": "Graph data loaded successfully",
            "stats": stats,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Failed to load graph data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load graph data: {str(e)}")

@router.get("/analysis")
async def run_graph_analysis():
    """
    Run comprehensive graph analysis
    
    Returns:
        Analysis results including network statistics and distributions
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Run various analyses
        analysis_results = {
            "network_statistics": analyzer.get_network_statistics().to_dict('records'),
            "quality_distribution": analyzer.get_quality_distribution().to_dict('records'),
            "compliance_analysis": analyzer.analyze_compliance_network().to_dict('records'),
            "entity_distribution": analyzer.get_entity_type_distribution().to_dict('records'),
            "relationship_analysis": analyzer.analyze_relationships().to_dict('records'),
            "isolated_nodes": analyzer.find_isolated_nodes().to_dict('records'),
            "connected_components": analyzer.get_connected_components().to_dict('records')
        }
        
        return {
            "analysis": analysis_results,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Graph analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Graph analysis failed: {str(e)}")

@router.get("/graph")
async def get_graph_data(limit: int = 100):
    """
    Get graph data for visualization
    
    Args:
        limit: Maximum number of nodes to return
        
    Returns:
        Graph data in format suitable for visualization
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Get graph data
        graph_data = neo4j_mgr.get_graph_for_visualization(limit=limit)
        
        return {
            "nodes": graph_data.get('nodes', []),
            "relationships": graph_data.get('relationships', []),
            "total_nodes": len(graph_data.get('nodes', [])),
            "total_relationships": len(graph_data.get('relationships', []))
        }
        
    except Exception as e:
        logger.error(f"Failed to get graph data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get graph data: {str(e)}")

@router.get("/labels")
async def get_node_labels():
    """
    Get all node labels in the graph
    
    Returns:
        List of node labels with counts
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        labels = neo4j_mgr.get_node_labels_with_counts()
        
        return {
            "labels": labels,
            "total_labels": len(labels)
        }
        
    except Exception as e:
        logger.error(f"Failed to get node labels: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get node labels: {str(e)}")

@router.get("/relationship-types")
async def get_relationship_types():
    """
    Get all relationship types in the graph
    
    Returns:
        List of relationship types with counts
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        types = neo4j_mgr.get_relationship_types_with_counts()
        
        return {
            "relationship_types": types,
            "total_types": len(types)
        }
        
    except Exception as e:
        logger.error(f"Failed to get relationship types: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get relationship types: {str(e)}")

@router.get("/sample-queries")
async def get_sample_queries():
    """
    Get sample Cypher queries for common operations
    
    Returns:
        List of sample queries organized by category
    """
    sample_queries = {
        "basic": [
            {
                "name": "All Nodes",
                "query": "MATCH (n) RETURN n LIMIT 10",
                "description": "Get all nodes in the graph"
            },
            {
                "name": "All Relationships",
                "query": "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10",
                "description": "Get all relationships in the graph"
            },
            {
                "name": "Node Labels",
                "query": "CALL db.labels() YIELD label RETURN label",
                "description": "Get all node labels"
            },
            {
                "name": "Relationship Types",
                "query": "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType",
                "description": "Get all relationship types"
            }
        ],
        "assets": [
            {
                "name": "All Assets",
                "query": "MATCH (n:Asset) RETURN n LIMIT 10",
                "description": "Get all asset nodes"
            },
            {
                "name": "Asset Properties",
                "query": "MATCH (n:Asset) RETURN n.id, n.id_short, n.description LIMIT 10",
                "description": "Get asset properties"
            },
            {
                "name": "Assets with Submodels",
                "query": "MATCH (a:Asset)-[:HAS_SUBMODEL]->(s:Submodel) RETURN a, s LIMIT 10",
                "description": "Get assets and their submodels"
            }
        ],
        "submodels": [
            {
                "name": "All Submodels",
                "query": "MATCH (n:Submodel) RETURN n LIMIT 10",
                "description": "Get all submodel nodes"
            },
            {
                "name": "Submodel Types",
                "query": "MATCH (n:Submodel) RETURN DISTINCT n.submodel_type",
                "description": "Get distinct submodel types"
            },
            {
                "name": "Submodel Properties",
                "query": "MATCH (n:Submodel) RETURN n.id, n.id_short, n.submodel_type LIMIT 10",
                "description": "Get submodel properties"
            }
        ],
        "analysis": [
            {
                "name": "Node Count by Label",
                "query": "CALL db.labels() YIELD label CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) YIELD value RETURN label, value.count as count",
                "description": "Count nodes by label"
            },
            {
                "name": "Relationship Count by Type",
                "query": "CALL db.relationshipTypes() YIELD relationshipType CALL apoc.cypher.run('MATCH ()-[r:' + relationshipType + ']->() RETURN count(r) as count', {}) YIELD value RETURN relationshipType, value.count as count",
                "description": "Count relationships by type"
            },
            {
                "name": "Isolated Nodes",
                "query": "MATCH (n) WHERE NOT (n)--() RETURN n LIMIT 10",
                "description": "Find nodes with no relationships"
            }
        ]
    }
    
    return {
        "sample_queries": sample_queries,
        "categories": list(sample_queries.keys())
    }

@router.get("/health")
async def health_check():
    """
    Health check for knowledge graph system
    
    Returns:
        System health status
    """
    try:
        neo4j_mgr, cypher, analyzer = get_neo4j_manager()
        
        # Test connection
        connection_ok = neo4j_mgr.test_connection()
        
        health_status = {
            "status": "healthy" if connection_ok else "unhealthy",
            "neo4j_connected": connection_ok,
            "database_accessible": connection_ok,
            "timestamp": None  # Could add current timestamp
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "neo4j_connected": False,
            "database_accessible": False,
            "error": str(e)
        } 