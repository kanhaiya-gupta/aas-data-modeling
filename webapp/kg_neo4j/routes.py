"""
Neo4j Knowledge Graph API Routes

Provides REST API endpoints for the Neo4j knowledge graph frontend.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import sys
import os
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

try:
    from kg_neo4j import Neo4jManager, AASXGraphAnalyzer, CypherQueries
except ImportError:
    print("Warning: kg_neo4j module not available")

router = APIRouter(prefix="/api/kg-neo4j", tags=["Knowledge Graph - Neo4j"])

# Global Neo4j manager instance
neo4j_manager = None
analyzer = None

def get_neo4j_manager():
    """Get or create Neo4j manager instance"""
    global neo4j_manager
    
    if neo4j_manager is None:
        try:
            # Load environment variables
            from dotenv import load_dotenv
            load_dotenv()
            
            uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
            user = os.getenv('NEO4J_USER', 'neo4j')
            password = os.getenv('NEO4J_PASSWORD', 'password')
            
            neo4j_manager = Neo4jManager(uri, user, password)
        except Exception as e:
            print(f"Error creating Neo4j manager: {e}")
            return None
    
    return neo4j_manager

def get_analyzer():
    """Get or create analyzer instance"""
    global analyzer
    
    if analyzer is None:
        manager = get_neo4j_manager()
        if manager:
            analyzer = AASXGraphAnalyzer(manager)
    
    return analyzer

@router.get("/status")
async def get_connection_status():
    """Get Neo4j connection status"""
    try:
        manager = get_neo4j_manager()
        if manager and manager.test_connection():
            return {
                "connected": True,
                "message": "Successfully connected to Neo4j"
            }
        else:
            return {
                "connected": False,
                "message": "Failed to connect to Neo4j"
            }
    except Exception as e:
        return {
            "connected": False,
            "message": f"Error checking connection: {str(e)}"
        }

@router.get("/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        manager = get_neo4j_manager()
        if not manager:
            raise HTTPException(status_code=500, detail="Neo4j manager not available")
        
        if not manager.test_connection():
            raise HTTPException(status_code=503, detail="Neo4j not connected")
        
        # Get basic stats
        info = manager.get_database_info()
        
        # Get specific counts
        asset_count = 0
        submodel_count = 0
        
        try:
            with manager.driver.session() as session:
                # Count assets
                result = session.run("MATCH (n:Asset) RETURN count(n) as count")
                asset_count = result.single()['count']
                
                # Count submodels
                result = session.run("MATCH (n:Submodel) RETURN count(n) as count")
                submodel_count = result.single()['count']
        except Exception as e:
            print(f"Warning: Error getting specific counts: {e}")
        
        return {
            "total_nodes": info.get('node_count', 0),
            "total_relationships": info.get('relationship_count', 0),
            "asset_count": asset_count,
            "submodel_count": submodel_count,
            "database_info": info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@router.get("/graph-data")
async def get_graph_data():
    """Get graph data for visualization"""
    try:
        manager = get_neo4j_manager()
        if not manager:
            raise HTTPException(status_code=500, detail="Neo4j manager not available")
        
        if not manager.test_connection():
            raise HTTPException(status_code=503, detail="Neo4j not connected")
        
        # Get graph data from Neo4j
        nodes = []
        links = []
        
        with manager.driver.session() as session:
            # Get all nodes with their properties
            result = session.run("""
                MATCH (n)
                RETURN n.id as id, 
                       labels(n) as labels,
                       n.id_short as id_short,
                       n.description as description,
                       n.quality_level as quality_level,
                       n.compliance_status as compliance_status
            """)
            
            for record in result:
                node_type = "unknown"
                if "Asset" in record["labels"]:
                    node_type = "asset"
                elif "Submodel" in record["labels"]:
                    node_type = "submodel"
                
                nodes.append({
                    "id": record["id"],
                    "type": node_type,
                    "id_short": record["id_short"],
                    "properties": {
                        "description": record["description"],
                        "quality_level": record["quality_level"],
                        "compliance_status": record["compliance_status"]
                    }
                })
            
            # Get relationships
            result = session.run("""
                MATCH (a)-[r]->(b)
                RETURN a.id as source, b.id as target, type(r) as type
            """)
            
            for record in result:
                links.append({
                    "source": record["source"],
                    "target": record["target"],
                    "type": record["type"]
                })
        
        return {
            "success": True,
            "data": {
                "nodes": nodes,
                "links": links
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting graph data: {str(e)}")

@router.post("/query")
async def execute_cypher_query(request: Dict[str, Any]):
    """Execute a Cypher query"""
    try:
        manager = get_neo4j_manager()
        if not manager:
            raise HTTPException(status_code=500, detail="Neo4j manager not available")
        
        if not manager.test_connection():
            raise HTTPException(status_code=503, detail="Neo4j not connected")
        
        query = request.get("query", "").strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Execute query
        with manager.driver.session() as session:
            result = session.run(query)
            records = []
            
            for record in result:
                # Convert Neo4j record to dict
                record_dict = {}
                for key, value in record.items():
                    if hasattr(value, '__dict__'):
                        # Handle Neo4j node/relationship objects
                        record_dict[key] = dict(value)
                    else:
                        record_dict[key] = value
                records.append(record_dict)
        
        return {
            "success": True,
            "results": records
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@router.get("/analytics")
async def get_analytics():
    """Get analytics data"""
    try:
        analyzer = get_analyzer()
        if not analyzer:
            raise HTTPException(status_code=500, detail="Analyzer not available")
        
        # Get analytics
        analytics_data = analyzer.get_comprehensive_analytics()
        
        return {
            "success": True,
            "analytics": analytics_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@router.post("/import")
async def import_graph_data(request: Dict[str, Any]):
    """Import graph data from ETL output"""
    try:
        manager = get_neo4j_manager()
        if not manager:
            raise HTTPException(status_code=500, detail="Neo4j manager not available")
        
        if not manager.test_connection():
            raise HTTPException(status_code=503, detail="Neo4j not connected")
        
        directory = request.get("directory", "output/etl_results")
        clear_database = request.get("clear_database", False)
        
        # Validate directory
        import_dir = Path(directory)
        if not import_dir.exists():
            raise HTTPException(status_code=400, detail=f"Directory not found: {directory}")
        
        # Clear database if requested
        if clear_database:
            with manager.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
        
        # Import graph files
        graph_files = list(import_dir.rglob("*_graph.json"))
        if not graph_files:
            raise HTTPException(status_code=400, detail="No graph files found in directory")
        
        imported_files = 0
        total_nodes = 0
        total_relationships = 0
        
        for graph_file in graph_files:
            try:
                manager.import_graph_file(graph_file)
                imported_files += 1
                
                # Get stats for this file
                with open(graph_file, 'r') as f:
                    import json
                    data = json.load(f)
                    if 'nodes' in data:
                        total_nodes += len(data['nodes'])
                    if 'edges' in data:
                        total_relationships += len(data['edges'])
                        
            except Exception as e:
                print(f"Warning: Error importing {graph_file}: {e}")
        
        return {
            "success": True,
            "imported_files": imported_files,
            "nodes_imported": total_nodes,
            "relationships_imported": total_relationships,
            "message": f"Successfully imported {imported_files} files"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing data: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        manager = get_neo4j_manager()
        if manager and manager.test_connection():
            return {
                "status": "healthy",
                "neo4j": "connected",
                "message": "Knowledge Graph service is running"
            }
        else:
            return {
                "status": "degraded",
                "neo4j": "disconnected",
                "message": "Neo4j connection failed"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "neo4j": "error",
            "message": f"Service error: {str(e)}"
        } 