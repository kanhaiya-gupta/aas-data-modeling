# Neo4j Integration Guide

This guide explains how to integrate the AASX ETL pipeline with Neo4j graph database for advanced graph analytics and relationship analysis.

## Overview

The AASX ETL pipeline generates graph-optimized JSON files that can be directly imported into Neo4j. This enables powerful graph analytics on Asset Administrative Shell (AAS) data, including:

- **Relationship Analysis**: Discover connections between assets, submodels, and documents
- **Quality Network Analysis**: Analyze quality levels and compliance across the network
- **Path Analysis**: Find paths between different entities
- **Community Detection**: Identify clusters of related assets
- **Graph Algorithms**: Apply Neo4j Graph Data Science (GDS) algorithms

## Prerequisites

1. **Neo4j Database**: Install and configure Neo4j (Community or Enterprise)
2. **Python Neo4j Driver**: Install the Python driver
   ```bash
   pip install neo4j
   ```
3. **AASX ETL Pipeline**: Ensure the pipeline is configured to generate graph format

## Graph Data Structure

The ETL pipeline generates graph files with the following structure:

```json
{
  "format": "graph",
  "version": "1.0",
  "nodes": [
    {
      "id": "asset_001",
      "type": "asset",
      "properties": {
        "id_short": "Motor_001",
        "description": "DC Servo Motor",
        "type": "Motor",
        "quality_level": "HIGH",
        "compliance_status": "COMPLIANT"
      }
    }
  ],
  "edges": [
    {
      "source": "asset_001",
      "target": "submodel_001",
      "type": "asset_has_submodel",
      "properties": {
        "extracted_at": "2025-07-09T12:36:45.020020"
      }
    }
  ],
  "metadata": {
    "created_at": "2025-07-09T12:36:45.020020",
    "total_nodes": 7,
    "total_edges": 1
  }
}
```

## Import Methods

### Method 1: Cypher Script Import

Create a Cypher script to import the graph data:

```cypher
// Load graph data from ETL output
LOAD JSON FROM 'file:///aasx_data_20250709_123645_graph.json' AS graph

// Create nodes with labels based on type
UNWIND graph.nodes AS node
CALL apoc.create.node([node.type], {
    id: node.id,
    id_short: node.properties.id_short,
    description: node.properties.description,
    type: node.properties.type,
    quality_level: node.properties.quality_level,
    compliance_status: node.properties.compliance_status
}) YIELD node as n
RETURN count(n)

// Create relationships
UNWIND graph.edges AS edge
MATCH (source {id: edge.source})
MATCH (target {id: edge.target})
CALL apoc.create.relationship(source, edge.type, {
    extracted_at: edge.properties.extracted_at
}, target) YIELD rel
RETURN count(rel)
```

### Method 2: Python Script Import

Use the Python Neo4j driver for programmatic import:

```python
from neo4j import GraphDatabase
import json
from pathlib import Path

class AASXNeo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def import_graph_file(self, graph_file_path):
        """Import a single graph file"""
        with open(graph_file_path, 'r') as f:
            graph_data = json.load(f)
        
        with self.driver.session() as session:
            # Clear existing data (optional)
            # session.run("MATCH (n) DETACH DELETE n")
            
            # Create nodes
            for node in graph_data['nodes']:
                session.run("""
                    MERGE (n:Node {id: $id})
                    SET n += $properties
                    SET n.type = $node_type
                """, id=node['id'], properties=node['properties'], node_type=node['type'])
            
            # Create relationships
            for edge in graph_data['edges']:
                session.run("""
                    MATCH (source:Node {id: $source_id})
                    MATCH (target:Node {id: $target_id})
                    MERGE (source)-[r:RELATES_TO]->(target)
                    SET r.type = $rel_type
                    SET r += $properties
                """, source_id=edge['source'], target_id=edge['target'],
                     rel_type=edge['type'], properties=edge['properties'])
    
    def import_directory(self, directory_path):
        """Import all graph files from a directory"""
        directory = Path(directory_path)
        graph_files = list(directory.glob("*_graph.json"))
        
        for graph_file in graph_files:
            print(f"Importing {graph_file.name}...")
            self.import_graph_file(graph_file)
            print(f"✓ Imported {graph_file.name}")

# Usage
importer = AASXNeo4jImporter("bolt://localhost:7687", "neo4j", "password")
importer.import_directory("output/etl_results/")
importer.close()
```

### Method 3: Neo4j Admin Import (Bulk Import)

For large datasets, use Neo4j's bulk import tool:

```python
import json
import csv
from pathlib import Path

def convert_graph_to_csv(graph_file_path, output_dir):
    """Convert graph JSON to CSV files for Neo4j admin import"""
    with open(graph_file_path, 'r') as f:
        graph_data = json.load(f)
    
    # Export nodes
    nodes_file = output_dir / "nodes.csv"
    with open(nodes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id:ID', 'type:LABEL', 'id_short', 'description', 'quality_level', 'compliance_status'])
        for node in graph_data['nodes']:
            writer.writerow([
                node['id'],
                node['type'],
                node['properties']['id_short'],
                node['properties']['description'],
                node['properties']['quality_level'],
                node['properties']['compliance_status']
            ])
    
    # Export relationships
    if graph_data['edges']:
        rels_file = output_dir / "relationships.csv"
        with open(rels_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([':START_ID', ':END_ID', ':TYPE', 'extracted_at'])
            for edge in graph_data['edges']:
                writer.writerow([
                    edge['source'],
                    edge['target'],
                    edge['type'],
                    edge['properties']['extracted_at']
                ])
    
    return nodes_file, rels_file

# Convert all graph files
output_dir = Path("neo4j_import")
output_dir.mkdir(exist_ok=True)

for graph_file in Path("output/etl_results/").rglob("*_graph.json"):
    print(f"Converting {graph_file.name}...")
    convert_graph_to_csv(graph_file, output_dir)

# Then use neo4j-admin import
# neo4j-admin import --database=aasx_data --nodes=neo4j_import/nodes.csv --relationships=neo4j_import/relationships.csv
```

## Graph Analytics Queries

### Basic Queries

```cypher
// Find all assets
MATCH (a:Node {type: 'asset'})
RETURN a.id, a.description, a.quality_level

// Find submodels for a specific asset
MATCH (asset:Node {id: 'asset_001'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
RETURN submodel.id, submodel.description, r.type

// Count entities by type
MATCH (n:Node)
RETURN n.type, count(*) as count
ORDER BY count DESC
```

### Quality Analysis

```cypher
// Quality distribution across assets
MATCH (a:Node {type: 'asset'})
RETURN a.quality_level, count(*) as count
ORDER BY count DESC

// Compliance status analysis
MATCH (n:Node)
RETURN n.type, n.compliance_status, count(*) as count
ORDER BY n.type, count DESC

// Find high-quality assets
MATCH (a:Node {type: 'asset', quality_level: 'HIGH'})
RETURN a.id, a.description, a.compliance_status
```

### Relationship Analysis

```cypher
// Find assets with most submodels
MATCH (asset:Node {type: 'asset'})-[r:RELATES_TO]->(submodel:Node {type: 'submodel'})
RETURN asset.id, asset.description, count(submodel) as submodel_count
ORDER BY submodel_count DESC

// Find isolated nodes (no relationships)
MATCH (n:Node)
WHERE NOT (n)-[:RELATES_TO]-()
RETURN n.id, n.type, n.description

// Find connected components
CALL gds.alpha.scc.stream('aasx_graph')
YIELD nodeId, componentId
RETURN componentId, count(*) as size
ORDER BY size DESC
```

### Advanced Analytics

```cypher
// Shortest path between two assets
MATCH path = shortestPath(
    (a1:Node {type: 'asset', id: 'asset_001'})-[*]-(a2:Node {type: 'asset', id: 'asset_002'})
)
RETURN path

// PageRank analysis (requires GDS library)
CALL gds.pageRank.stream('aasx_graph')
YIELD nodeId, score
MATCH (n:Node) WHERE id(n) = nodeId
RETURN n.id, n.type, score
ORDER BY score DESC

// Community detection
CALL gds.louvain.stream('aasx_graph')
YIELD nodeId, communityId
MATCH (n:Node) WHERE id(n) = nodeId
RETURN communityId, collect(n.id) as nodes
ORDER BY size(collect(n.id)) DESC
```

## Python Integration Examples

### Graph Analyzer Class

```python
from neo4j import GraphDatabase
import pandas as pd

class AASXGraphAnalyzer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def get_quality_distribution(self):
        """Get quality level distribution"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Node {type: 'asset'})
                RETURN n.quality_level, count(*) as count
                ORDER BY count DESC
            """)
            return pd.DataFrame([record.data() for record in result])
    
    def find_related_entities(self, entity_id, max_depth=2):
        """Find entities related to a specific entity within max_depth"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (start:Node {id: $entity_id})-[*1..$max_depth]-(related:Node)
                RETURN DISTINCT related.id, related.type, related.description,
                       length(path) as distance
                ORDER BY distance
            """, entity_id=entity_id, max_depth=max_depth)
            return pd.DataFrame([record.data() for record in result])
    
    def analyze_compliance_network(self):
        """Analyze compliance across the network"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Node)
                RETURN n.type, n.compliance_status, count(*) as count
                ORDER BY n.type, count DESC
            """)
            return pd.DataFrame([record.data() for record in result])
    
    def get_network_statistics(self):
        """Get overall network statistics"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:Node)
                WITH n.type as type, count(*) as count
                RETURN type, count
                UNION
                MATCH ()-[r:RELATES_TO]->()
                RETURN 'relationships' as type, count(r) as count
            """)
            return pd.DataFrame([record.data() for record in result])

# Usage
analyzer = AASXGraphAnalyzer("bolt://localhost:7687", "neo4j", "password")

# Get quality distribution
quality_df = analyzer.get_quality_distribution()
print("Quality Distribution:")
print(quality_df)

# Find related entities
related_df = analyzer.find_related_entities("asset_001", max_depth=2)
print("\nRelated Entities:")
print(related_df)

# Analyze compliance
compliance_df = analyzer.analyze_compliance_network()
print("\nCompliance Analysis:")
print(compliance_df)

analyzer.close()
```

### Visualization Integration

```python
import networkx as nx
import matplotlib.pyplot as plt
from neo4j import GraphDatabase

def create_network_graph(uri, user, password):
    """Create NetworkX graph from Neo4j data"""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    G = nx.Graph()
    
    with driver.session() as session:
        # Get nodes
        result = session.run("MATCH (n:Node) RETURN n.id, n.type, n.quality_level")
        for record in result:
            G.add_node(record['n.id'], 
                      type=record['n.type'], 
                      quality_level=record['n.quality_level'])
        
        # Get relationships
        result = session.run("MATCH (a:Node)-[r:RELATES_TO]->(b:Node) RETURN a.id, b.id, r.type")
        for record in result:
            G.add_edge(record['a.id'], record['b.id'], 
                      type=record['r.type'])
    
    driver.close()
    return G

# Create and visualize graph
G = create_network_graph("bolt://localhost:7687", "neo4j", "password")

# Draw the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', 
        node_size=1000, font_size=8)
plt.title("AASX Data Network")
plt.show()
```

## Performance Optimization

### Indexing

```cypher
// Create indexes for better performance
CREATE INDEX node_id_index FOR (n:Node) ON (n.id);
CREATE INDEX node_type_index FOR (n:Node) ON (n.type);
CREATE INDEX node_quality_index FOR (n:Node) ON (n.quality_level);
```

### Graph Projection (GDS)

```cypher
// Create a graph projection for algorithms
CALL gds.graph.project(
    'aasx_graph',
    'Node',
    'RELATES_TO',
    {
        nodeProperties: ['type', 'quality_level', 'compliance_status']
    }
);
```

### Query Optimization

```cypher
// Use parameterized queries
MATCH (n:Node {type: $entity_type, quality_level: $quality})
RETURN n.id, n.description

// Use LIMIT for large result sets
MATCH (n:Node)
RETURN n.id, n.description
LIMIT 1000
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Check file paths and permissions
   - Verify JSON format is valid
   - Ensure Neo4j is running and accessible

2. **Performance Issues**
   - Create appropriate indexes
   - Use graph projections for algorithms
   - Limit result set sizes

3. **Memory Issues**
   - Use streaming algorithms for large graphs
   - Process data in batches
   - Monitor Neo4j memory usage

### Debugging Queries

```cypher
// Check if data was imported correctly
MATCH (n:Node)
RETURN count(n) as total_nodes;

// Check relationships
MATCH ()-[r:RELATES_TO]->()
RETURN count(r) as total_relationships;

// Sample data
MATCH (n:Node)
RETURN n LIMIT 5;
```

## Next Steps

1. **Explore Graph Algorithms**: Try different GDS algorithms
2. **Build Dashboards**: Create visualizations with Neo4j Bloom
3. **Real-time Updates**: Set up streaming updates from the ETL pipeline
4. **Advanced Analytics**: Implement custom graph algorithms
5. **Integration**: Connect with other tools in the QI platform

For more information, see the main [AASX ETL Pipeline documentation](AASX_ETL_PIPELINE.md). 