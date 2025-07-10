"""
AASX Digital Twin Analytics Framework - AI/RAG System
Provides AI-powered analysis and insights for digital twin data
"""

import os
import json
import logging
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from neo4j import GraphDatabase
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AASXDigitalTwinRAG:
    """AI/RAG system for AASX Digital Twin Analytics Framework"""
    
    def __init__(self, config_path: str = "config_enhanced_rag.yaml"):
        """Initialize the RAG system"""
        self.config = self._load_config(config_path)
        self._setup_clients()
        self._setup_collection()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"✅ Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            raise
    
    def _setup_clients(self):
        """Setup database and AI clients"""
        # OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("⚠️  OpenAI API key not found")
        else:
            openai.api_key = api_key
            logger.info("✅ OpenAI client configured")
        
        # Qdrant client
        try:
            self.qdrant_client = QdrantClient(
                host=self.config['qdrant']['host'],
                port=self.config['qdrant']['port']
            )
            logger.info("✅ Qdrant client connected")
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
            raise
        
        # Neo4j client
        try:
            self.neo4j_driver = GraphDatabase.driver(
                self.config['neo4j']['uri'],
                auth=(self.config['neo4j']['username'], self.config['neo4j']['password'])
            )
            logger.info("✅ Neo4j client connected")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise
    
    def _setup_collection(self):
        """Setup Qdrant collection for vector storage"""
        collection_name = self.config['qdrant']['collection_name']
        
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [c.name for c in collections.collections]
            
            if collection_name not in collection_names:
                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=self.config['qdrant']['vector_size'],
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created Qdrant collection: {collection_name}")
            else:
                logger.info(f"✅ Using existing Qdrant collection: {collection_name}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to setup Qdrant collection: {e}")
            raise
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the vector database"""
        try:
            # Generate embedding
            embedding = self._get_embedding(content)
            
            # Create point
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "content": content,
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            # Add to collection
            self.qdrant_client.upsert(
                collection_name=self.config['qdrant']['collection_name'],
                points=[point]
            )
            
            logger.info(f"✅ Added document with ID: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"❌ Failed to add document: {e}")
            raise
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"❌ Failed to get embedding: {e}")
            raise
    
    def search_similar(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for similar documents"""
        try:
            # Get query embedding
            query_embedding = self._get_embedding(query)
            
            # Search in Qdrant
            top_k = top_k or self.config['rag']['top_k']
            results = self.qdrant_client.search(
                collection_name=self.config['qdrant']['collection_name'],
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=self.config['rag']['similarity_threshold']
            )
            
            # Format results
            documents = []
            for result in results:
                documents.append({
                    'id': result.id,
                    'score': result.score,
                    'content': result.payload['content'],
                    'metadata': result.payload['metadata']
                })
            
            logger.info(f"✅ Found {len(documents)} similar documents")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            raise
    
    def query_ai(self, question: str, context_docs: List[Dict] = None) -> Dict:
        """Query AI with context from vector search"""
        try:
            # Get relevant context
            if not context_docs:
                context_docs = self.search_similar(question)
            
            # Build context
            context = "\n\n".join([doc['content'] for doc in context_docs])
            
            # Build prompt
            system_prompt = self.config['rag']['system_prompt']
            user_prompt = f"""
Question: {question}

Context from digital twin data:
{context}

Please provide a comprehensive analysis based on the available digital twin data.
"""
            
            # Query OpenAI
            response = openai.ChatCompletion.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config['openai']['temperature'],
                max_tokens=self.config['openai']['max_tokens'],
                top_p=self.config['openai']['top_p'],
                frequency_penalty=self.config['openai']['frequency_penalty'],
                presence_penalty=self.config['openai']['presence_penalty']
            )
            
            # Format response
            result = {
                'answer': response.choices[0].message.content,
                'model': self.config['openai']['model'],
                'usage': response.usage,
                'sources': [doc['metadata'] for doc in context_docs],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ AI query completed using {result['model']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ AI query failed: {e}")
            raise
    
    def analyze_category(self, category: str, query: str) -> Dict:
        """Analyze data for a specific category"""
        try:
            # Get category info
            categories = self.config['analysis_categories']
            if category not in categories:
                raise ValueError(f"Unknown category: {category}")
            
            category_info = categories[category]
            
            # Build category-specific query
            enhanced_query = f"{category_info['description']}: {query}"
            
            # Get AI response
            result = self.query_ai(enhanced_query)
            
            # Add category metadata
            result['category'] = category
            result['category_name'] = category_info['name']
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Category analysis failed: {e}")
            raise
    
    def get_graph_insights(self, query: str) -> Dict:
        """Get insights from Neo4j knowledge graph"""
        try:
            with self.neo4j_driver.session() as session:
                # Run Cypher query
                result = session.run(query)
                
                # Process results
                records = []
                for record in result:
                    records.append(dict(record))
                
                # Get AI analysis of graph data
                graph_context = f"Knowledge Graph Query Results: {json.dumps(records, indent=2)}"
                ai_result = self.query_ai(f"Analyze this knowledge graph data: {graph_context}")
            
            return {
                    'graph_data': records,
                    'ai_analysis': ai_result,
                    'query': query
            }
            
        except Exception as e:
            logger.error(f"❌ Graph insights failed: {e}")
            raise
    
    def health_check(self) -> Dict:
        """Check system health"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {}
        }
        
        # Check OpenAI
        try:
            if openai.api_key:
                health_status['services']['openai'] = 'connected'
            else:
                health_status['services']['openai'] = 'not_configured'
        except:
            health_status['services']['openai'] = 'error'
        
        # Check Qdrant
        try:
            self.qdrant_client.get_collections()
            health_status['services']['qdrant'] = 'connected'
        except:
            health_status['services']['qdrant'] = 'error'
        
        # Check Neo4j
        try:
            with self.neo4j_driver.session() as session:
                session.run("RETURN 1")
            health_status['services']['neo4j'] = 'connected'
        except:
            health_status['services']['neo4j'] = 'error'
        
        # Overall status
        if 'error' in health_status['services'].values():
            health_status['status'] = 'degraded'
        
        return health_status
    
    def close(self):
        """Close connections"""
        try:
            self.neo4j_driver.close()
            logger.info("✅ Connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize RAG system
    rag = AASXDigitalTwinRAG()
    
    # Example queries
    queries = [
        "What are the quality metrics for the additive manufacturing facility?",
        "What are the main risks in the hydrogen filling station?",
        "How can we optimize the performance of the 3D printer?",
        "Provide a general overview of the digital twin assets"
    ]
    
    # Run queries
    for query in queries:
        print(f"\n🔍 Query: {query}")
        try:
            result = rag.query_ai(query)
            print(f"🤖 Answer: {result['answer'][:200]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Health check
    health = rag.health_check()
    print(f"\n🏥 Health Status: {health}")
    
    rag.close() 