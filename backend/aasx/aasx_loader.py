"""
AASX Data Loader Module

This module handles the loading of transformed AASX data into various storage systems
including file systems, databases, and vector databases for RAG applications.
"""

import json
import yaml
import csv
import sqlite3
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
from datetime import datetime
import hashlib
import uuid
from dataclasses import dataclass

# Vector database imports
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logging.warning("ChromaDB not available. Vector database features disabled.")

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available. Vector search features disabled.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers not available. Embedding features disabled.")

logger = logging.getLogger(__name__)

@dataclass
class LoaderConfig:
    """Configuration for AASX data loading"""
    output_directory: str = "output"
    database_path: str = "aasx_data.db"
    vector_db_path: str = "vector_db"
    vector_db_type: str = "chromadb"  # chromadb, faiss
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    overlap_size: int = 50
    include_metadata: bool = True
    create_indexes: bool = True
    backup_existing: bool = True
    separate_file_outputs: bool = False
    include_filename_in_output: bool = False

class AASXLoader:
    """
    Comprehensive AASX data loader for the QI Digital Platform.
    
    Supports multiple storage systems including vector databases for RAG.
    """
    
    def __init__(self, config: Optional[LoaderConfig] = None, source_file: Optional[str] = None):
        """
        Initialize AASX loader.
        
        Args:
            config: Loader configuration
            source_file: Source AASX file path (for file-specific outputs)
        """
        self.config = config or LoaderConfig()
        self.source_file = source_file
        
        # Create file-specific output directory if configured
        if self.config.separate_file_outputs and source_file:
            source_path = Path(source_file)
            if self.config.include_filename_in_output:
                file_name = source_path.stem
                self.output_dir = Path(self.config.output_directory) / file_name
            else:
                self.output_dir = Path(self.config.output_directory)
        else:
            self.output_dir = Path(self.config.output_directory)
        
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize storage systems
        self.vector_db = None
        self.embedding_model = None
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage systems"""
        logger.info("Initializing storage systems")
        
        # Initialize vector database
        if self.config.vector_db_type == "chromadb" and CHROMADB_AVAILABLE:
            self._initialize_chromadb()
        elif self.config.vector_db_type == "faiss" and FAISS_AVAILABLE:
            self._initialize_faiss()
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_embedding_model()
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB vector database"""
        try:
            vector_db_path = Path(self.config.vector_db_path)
            vector_db_path.mkdir(exist_ok=True)
            
            self.vector_db = chromadb.PersistentClient(
                path=str(vector_db_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create collections
            self.assets_collection = self.vector_db.get_or_create_collection(
                name="aasx_assets",
                metadata={"description": "AASX Assets for RAG"}
            )
            
            self.submodels_collection = self.vector_db.get_or_create_collection(
                name="aasx_submodels", 
                metadata={"description": "AASX Submodels for RAG"}
            )
            
            self.documents_collection = self.vector_db.get_or_create_collection(
                name="aasx_documents",
                metadata={"description": "AASX Documents for RAG"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.vector_db = None
    
    def _initialize_faiss(self):
        """Initialize FAISS vector database"""
        try:
            vector_db_path = Path(self.config.vector_db_path)
            vector_db_path.mkdir(exist_ok=True)
            
            # Initialize FAISS index (will be created when first data is loaded)
            self.faiss_index = None
            self.faiss_metadata = []
            
            logger.info("FAISS initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer model"""
        try:
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            logger.info(f"Embedding model {self.config.embedding_model} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def load_aasx_data(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load transformed AASX data into storage systems.
        
        Args:
            transformed_data: Transformed AASX data
            
        Returns:
            Dictionary with loading results
        """
        logger.info("Starting AASX data loading")
        
        results = {
            'files_exported': [],
            'database_records': 0,
            'vector_embeddings': 0,
            'errors': []
        }
        
        try:
            # Step 1: Export to files
            file_results = self._export_to_files(transformed_data)
            results['files_exported'] = file_results
            
            # Step 2: Load to database
            db_results = self._load_to_database(transformed_data)
            results['database_records'] = db_results
            
            # Step 3: Load to vector database
            vector_results = self._load_to_vector_db(transformed_data)
            results['vector_embeddings'] = vector_results
            
            logger.info("AASX data loading completed successfully")
            
        except Exception as e:
            error_msg = f"Error during AASX loading: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    def _export_to_files(self, data: Dict[str, Any]) -> List[str]:
        """Export data to various file formats"""
        exported_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # Export as JSON
            json_path = self.output_dir / f"aasx_data_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            exported_files.append(str(json_path))
            
            # Export as YAML
            yaml_path = self.output_dir / f"aasx_data_{timestamp}.yaml"
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            exported_files.append(str(yaml_path))
            
            # Export flattened data as CSV
            if 'data' in data and isinstance(data['data'], dict):
                csv_path = self.output_dir / f"aasx_data_{timestamp}.csv"
                self._export_to_csv(data['data'], csv_path)
                exported_files.append(str(csv_path))
            
            # Export as Graph format (for graph databases)
            graph_path = self.output_dir / f"aasx_data_{timestamp}_graph.json"
            graph_data = self._create_graph_format(data)
            with open(graph_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, indent=2, ensure_ascii=False)
            exported_files.append(str(graph_path))
            
            logger.info(f"Exported {len(exported_files)} files")
            
        except Exception as e:
            logger.error(f"Error exporting files: {e}")
        
        return exported_files
    
    def _export_to_csv(self, data: Dict[str, Any], csv_path: Path):
        """Export data to CSV format"""
        flattened_data = []
        
        # Flatten assets
        for asset in data.get('assets', []):
            flattened_data.append({
                'entity_type': 'asset',
                'id': asset.get('id', ''),
                'id_short': asset.get('id_short', ''),
                'description': asset.get('description', ''),
                'type': asset.get('type', ''),
                'quality_level': asset.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': asset.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        # Flatten submodels
        for submodel in data.get('submodels', []):
            flattened_data.append({
                'entity_type': 'submodel',
                'id': submodel.get('id', ''),
                'id_short': submodel.get('id_short', ''),
                'description': submodel.get('description', ''),
                'type': submodel.get('type', ''),
                'quality_level': submodel.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': submodel.get('qi_metadata', {}).get('compliance_status', '')
            })
        
        if flattened_data:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
    
    def _create_graph_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create graph format data for graph databases"""
        nodes = []
        edges = []
        
        # Add asset nodes
        for asset in data.get('data', {}).get('assets', []):
            nodes.append({
                'id': asset.get('id', ''),
                'type': 'asset',
                'properties': {
                    'id_short': asset.get('id_short', ''),
                    'description': asset.get('description', ''),
                    'type': asset.get('type', ''),
                    'quality_level': asset.get('qi_metadata', {}).get('quality_level', ''),
                    'compliance_status': asset.get('qi_metadata', {}).get('compliance_status', '')
                }
            })
        
        # Add submodel nodes
        for submodel in data.get('data', {}).get('submodels', []):
            nodes.append({
                'id': submodel.get('id', ''),
                'type': 'submodel',
                'properties': {
                    'id_short': submodel.get('id_short', ''),
                    'description': submodel.get('description', ''),
                    'type': submodel.get('type', ''),
                    'quality_level': submodel.get('qi_metadata', {}).get('quality_level', ''),
                    'compliance_status': submodel.get('qi_metadata', {}).get('compliance_status', '')
                }
            })
        
        # Add relationships as edges
        for relationship in data.get('data', {}).get('relationships', []):
            edges.append({
                'source': relationship.get('source_id', ''),
                'target': relationship.get('target_id', ''),
                'type': relationship.get('type', ''),
                'properties': relationship.get('metadata', {})
            })
        
        return {
            'format': 'graph',
            'version': '1.0',
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_nodes': len(nodes),
                'total_edges': len(edges)
            }
        }
    
    def _load_to_database(self, data: Dict[str, Any]) -> int:
        """Load data to SQLite database"""
        records_loaded = 0
        
        try:
            db_path = Path(self.config.database_path)
            
            # Create database directory if it doesn't exist
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Only backup on first file if configured
            if self.config.backup_existing and db_path.exists() and not hasattr(self, '_backup_created'):
                backup_path = db_path.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                import shutil
                shutil.copy2(db_path, backup_path)
                self._backup_created = True
                logger.info(f"Backed up existing database to {backup_path}")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            self._create_database_tables(cursor)
            
            # Load assets
            for asset in data.get('data', {}).get('assets', []):
                self._insert_asset(cursor, asset)
                records_loaded += 1
            
            # Load submodels
            for submodel in data.get('data', {}).get('submodels', []):
                self._insert_submodel(cursor, submodel)
                records_loaded += 1
            
            # Load documents
            for document in data.get('data', {}).get('documents', []):
                self._insert_document(cursor, document)
                records_loaded += 1
            
            # Load relationships
            for relationship in data.get('data', {}).get('relationships', []):
                self._insert_relationship(cursor, relationship)
                records_loaded += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Loaded {records_loaded} records to database")
            
        except Exception as e:
            logger.error(f"Error loading to database: {e}")
        
        return records_loaded
    
    def _create_database_tables(self, cursor):
        """Create database tables"""
        # Assets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY,
                id_short TEXT,
                description TEXT,
                type TEXT,
                quality_level TEXT,
                compliance_status TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Submodels table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submodels (
                id TEXT PRIMARY KEY,
                id_short TEXT,
                description TEXT,
                type TEXT,
                quality_level TEXT,
                compliance_status TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT,
                size INTEGER,
                type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Relationships table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id TEXT PRIMARY KEY,
                source_id TEXT,
                target_id TEXT,
                type TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes if configured
        if self.config.create_indexes:
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_submodels_type ON submodels(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)')
    
    def _insert_asset(self, cursor, asset: Dict[str, Any]):
        """Insert asset into database"""
        cursor.execute('''
            INSERT OR REPLACE INTO assets 
            (id, id_short, description, type, quality_level, compliance_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            asset.get('id', ''),
            asset.get('id_short', ''),
            asset.get('description', ''),
            asset.get('type', ''),
            asset.get('qi_metadata', {}).get('quality_level', ''),
            asset.get('qi_metadata', {}).get('compliance_status', ''),
            json.dumps(asset.get('metadata', {}))
        ))
    
    def _insert_submodel(self, cursor, submodel: Dict[str, Any]):
        """Insert submodel into database"""
        cursor.execute('''
            INSERT OR REPLACE INTO submodels 
            (id, id_short, description, type, quality_level, compliance_status, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            submodel.get('id', ''),
            submodel.get('id_short', ''),
            submodel.get('description', ''),
            submodel.get('type', ''),
            submodel.get('qi_metadata', {}).get('quality_level', ''),
            submodel.get('qi_metadata', {}).get('compliance_status', ''),
            json.dumps(submodel.get('metadata', {}))
        ))
    
    def _insert_document(self, cursor, document: Dict[str, Any]):
        """Insert document into database"""
        doc_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR REPLACE INTO documents 
            (id, filename, size, type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            doc_id,
            document.get('filename', ''),
            document.get('size', 0),
            document.get('type', ''),
            json.dumps(document.get('metadata', {}))
        ))
    
    def _insert_relationship(self, cursor, relationship: Dict[str, Any]):
        """Insert relationship into database"""
        rel_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT OR REPLACE INTO relationships 
            (id, source_id, target_id, type, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            rel_id,
            relationship.get('source_id', ''),
            relationship.get('target_id', ''),
            relationship.get('type', ''),
            json.dumps(relationship.get('metadata', {}))
        ))
    
    def _load_to_vector_db(self, data: Dict[str, Any]) -> int:
        """Load data to vector database for RAG"""
        embeddings_loaded = 0
        
        if not self.embedding_model:
            logger.warning("Embedding model not available, skipping vector database loading")
            return 0
        
        try:
            # Load assets to vector database
            for asset in data.get('data', {}).get('assets', []):
                self._add_to_vector_db(asset, 'asset')
                embeddings_loaded += 1
            
            # Load submodels to vector database
            for submodel in data.get('data', {}).get('submodels', []):
                self._add_to_vector_db(submodel, 'submodel')
                embeddings_loaded += 1
            
            # Load documents to vector database
            for document in data.get('data', {}).get('documents', []):
                self._add_to_vector_db(document, 'document')
                embeddings_loaded += 1
            
            logger.info(f"Loaded {embeddings_loaded} embeddings to vector database")
            
        except Exception as e:
            logger.error(f"Error loading to vector database: {e}")
        
        return embeddings_loaded
    
    def _add_to_vector_db(self, entity: Dict[str, Any], entity_type: str):
        """Add entity to vector database"""
        if not self.embedding_model:
            return
        
        try:
            # Create text for embedding
            text = self._create_embedding_text(entity, entity_type)
            
            # Generate embedding
            embedding = self.embedding_model.encode(text).tolist()
            
            # Create metadata
            metadata = {
                'entity_type': entity_type,
                'entity_id': entity.get('id', ''),
                'quality_level': entity.get('qi_metadata', {}).get('quality_level', ''),
                'compliance_status': entity.get('qi_metadata', {}).get('compliance_status', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to appropriate collection
            if self.vector_db and hasattr(self, 'assets_collection'):
                if entity_type == 'asset':
                    self.assets_collection.add(
                        embeddings=[embedding],
                        documents=[text],
                        metadatas=[metadata],
                        ids=[f"asset_{entity.get('id', str(uuid.uuid4()))}"]
                    )
                elif entity_type == 'submodel':
                    self.submodels_collection.add(
                        embeddings=[embedding],
                        documents=[text],
                        metadatas=[metadata],
                        ids=[f"submodel_{entity.get('id', str(uuid.uuid4()))}"]
                    )
                elif entity_type == 'document':
                    self.documents_collection.add(
                        embeddings=[embedding],
                        documents=[text],
                        metadatas=[metadata],
                        ids=[f"document_{entity.get('id', str(uuid.uuid4()))}"]
                    )
            
        except Exception as e:
            logger.error(f"Error adding {entity_type} to vector database: {e}")
    
    def _create_embedding_text(self, entity: Dict[str, Any], entity_type: str) -> str:
        """Create text for embedding from entity"""
        text_parts = []
        
        # Add basic information
        text_parts.append(f"Type: {entity_type}")
        text_parts.append(f"ID: {entity.get('id', '')}")
        text_parts.append(f"Short ID: {entity.get('id_short', '')}")
        text_parts.append(f"Description: {entity.get('description', '')}")
        
        # Add type-specific information
        if entity_type == 'asset':
            text_parts.append(f"Asset Type: {entity.get('type', '')}")
            asset_info = entity.get('asset_information', {})
            if asset_info:
                text_parts.append(f"Asset Information: {json.dumps(asset_info)}")
        
        elif entity_type == 'submodel':
            text_parts.append(f"Submodel Type: {entity.get('type', '')}")
            semantic_id = entity.get('semantic_id', {})
            if semantic_id:
                text_parts.append(f"Semantic ID: {json.dumps(semantic_id)}")
        
        elif entity_type == 'document':
            text_parts.append(f"Document Type: {entity.get('type', '')}")
            text_parts.append(f"Filename: {entity.get('filename', '')}")
            text_parts.append(f"Size: {entity.get('size', 0)} bytes")
        
        # Add quality information
        qi_metadata = entity.get('qi_metadata', {})
        if qi_metadata:
            text_parts.append(f"Quality Level: {qi_metadata.get('quality_level', '')}")
            text_parts.append(f"Compliance Status: {qi_metadata.get('compliance_status', '')}")
        
        return " | ".join(text_parts)
    
    def search_similar(self, query: str, entity_type: str = "all", top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar entities using vector similarity.
        
        Args:
            query: Search query
            entity_type: Type of entity to search (asset, submodel, document, all)
            top_k: Number of results to return
            
        Returns:
            List of similar entities
        """
        if not self.embedding_model or not self.vector_db:
            logger.warning("Vector search not available")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            results = []
            
            # Search in appropriate collections
            if entity_type in ["asset", "all"] and hasattr(self, 'assets_collection'):
                asset_results = self.assets_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                results.extend(self._format_search_results(asset_results, 'asset'))
            
            if entity_type in ["submodel", "all"] and hasattr(self, 'submodels_collection'):
                submodel_results = self.submodels_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                results.extend(self._format_search_results(submodel_results, 'submodel'))
            
            if entity_type in ["document", "all"] and hasattr(self, 'documents_collection'):
                document_results = self.documents_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                results.extend(self._format_search_results(document_results, 'document'))
            
            # Sort by similarity score
            results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    def _format_search_results(self, results, entity_type: str) -> List[Dict[str, Any]]:
        """Format search results"""
        formatted_results = []
        
        if not results or not results['ids']:
            return formatted_results
        
        for i, doc_id in enumerate(results['ids'][0]):
            formatted_results.append({
                'id': doc_id,
                'entity_type': entity_type,
                'document': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'similarity': results['distances'][0][i] if 'distances' in results else 0.0
            })
        
        return formatted_results
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats = {}
        
        try:
            conn = sqlite3.connect(self.config.database_path)
            cursor = conn.cursor()
            
            # Count records in each table
            tables = ['assets', 'submodels', 'documents', 'relationships']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
        
        return stats
    
    def export_for_rag(self, output_path: str) -> str:
        """
        Export data in RAG-ready format.
        
        Args:
            output_path: Path for RAG export file
            
        Returns:
            Path to exported file
        """
        try:
            rag_data = {
                'version': '1.0',
                'format': 'rag_ready',
                'timestamp': datetime.now().isoformat(),
                'entities': []
            }
            
            # Get all entities from database
            conn = sqlite3.connect(self.config.database_path)
            cursor = conn.cursor()
            
            # Get assets
            cursor.execute('SELECT * FROM assets')
            for row in cursor.fetchall():
                rag_data['entities'].append({
                    'type': 'asset',
                    'id': row[0],
                    'id_short': row[1],
                    'description': row[2],
                    'content': f"Asset: {row[1]} - {row[2]}",
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
            
            # Get submodels
            cursor.execute('SELECT * FROM submodels')
            for row in cursor.fetchall():
                rag_data['entities'].append({
                    'type': 'submodel',
                    'id': row[0],
                    'id_short': row[1],
                    'description': row[2],
                    'content': f"Submodel: {row[1]} - {row[2]}",
                    'metadata': json.loads(row[6]) if row[6] else {}
                })
            
            conn.close()
            
            # Export to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rag_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"RAG data exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting RAG data: {e}")
            raise 