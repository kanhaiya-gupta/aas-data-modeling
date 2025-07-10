#!/usr/bin/env python3
"""
Frontend-Backend Integration Test
Tests the integration between frontend webapp and backend services
"""

import os
import sys
import time
import json
import requests
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from backend.ai_rag.ai_rag import get_rag_system
from backend.kg_neo4j.neo4j_manager import Neo4jManager
from backend.kg_neo4j.cypher_queries import CypherQueries

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendBackendIntegrationTest:
    """Test class for frontend-backend integration"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        
        if details:
            logger.info(f"  Details: {json.dumps(details, indent=2)}")
    
    def test_webapp_health(self) -> bool:
        """Test webapp health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Webapp Health Check",
                    True,
                    f"Webapp is healthy: {data.get('status', 'unknown')}",
                    data
                )
                return True
            else:
                self.log_test(
                    "Webapp Health Check",
                    False,
                    f"Health check failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test(
                "Webapp Health Check",
                False,
                f"Health check error: {str(e)}"
            )
            return False
    
    def test_ai_rag_api(self) -> bool:
        """Test AI/RAG API endpoints"""
        try:
            # Test AI/RAG stats endpoint
            response = self.session.get(f"{self.base_url}/ai-rag/stats")
            if response.status_code == 200:
                stats = response.json()
                self.log_test(
                    "AI/RAG Stats API",
                    True,
                    f"AI/RAG stats retrieved: {stats.get('collections_count', 0)} collections",
                    stats
                )
            else:
                self.log_test(
                    "AI/RAG Stats API",
                    False,
                    f"Stats endpoint failed with status {response.status_code}"
                )
                return False
            
            # Test AI/RAG query endpoint
            query_data = {
                "query": "What are the main assets in the system?",
                "analysis_type": "general"
            }
            response = self.session.post(f"{self.base_url}/ai-rag/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "AI/RAG Query API",
                    True,
                    f"Query executed successfully",
                    {"query": query_data["query"], "response_length": len(result.get("analysis", ""))}
                )
            else:
                self.log_test(
                    "AI/RAG Query API",
                    False,
                    f"Query endpoint failed with status {response.status_code}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test(
                "AI/RAG API",
                False,
                f"AI/RAG API error: {str(e)}"
            )
            return False
    
    def test_knowledge_graph_api(self) -> bool:
        """Test Knowledge Graph API endpoints"""
        try:
            # Test KG status endpoint
            response = self.session.get(f"{self.base_url}/kg-neo4j/status")
            if response.status_code == 200:
                status = response.json()
                self.log_test(
                    "Knowledge Graph Status API",
                    True,
                    f"KG status: {status.get('status', 'unknown')}",
                    status
                )
            else:
                self.log_test(
                    "Knowledge Graph Status API",
                    False,
                    f"Status endpoint failed with status {response.status_code}"
                )
                return False
            
            # Test KG stats endpoint
            response = self.session.get(f"{self.base_url}/kg-neo4j/stats")
            if response.status_code == 200:
                stats = response.json()
                self.log_test(
                    "Knowledge Graph Stats API",
                    True,
                    f"KG stats: {stats.get('node_count', 0)} nodes, {stats.get('relationship_count', 0)} relationships",
                    stats
                )
            else:
                self.log_test(
                    "Knowledge Graph Stats API",
                    False,
                    f"Stats endpoint failed with status {response.status_code}"
                )
                return False
            
            # Test KG query endpoint
            query_data = {"query": "MATCH (n) RETURN count(n) as node_count"}
            response = self.session.post(f"{self.base_url}/kg-neo4j/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "Knowledge Graph Query API",
                    True,
                    f"Query executed successfully",
                    {"query": query_data["query"], "results_count": len(result.get("results", []))}
                )
            else:
                self.log_test(
                    "Knowledge Graph Query API",
                    False,
                    f"Query endpoint failed with status {response.status_code}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test(
                "Knowledge Graph API",
                False,
                f"Knowledge Graph API error: {str(e)}"
            )
            return False
    
    def test_frontend_pages(self) -> bool:
        """Test frontend page accessibility"""
        pages = [
            ("/", "Home Page"),
            ("/ai-rag", "AI/RAG Page"),
            ("/kg-neo4j", "Knowledge Graph Page"),
            ("/twin-registry", "Twin Registry Page"),
            ("/certificates", "Certificates Page"),
            ("/analytics", "Analytics Page")
        ]
        
        all_success = True
        for path, name in pages:
            try:
                response = self.session.get(f"{self.base_url}{path}")
                if response.status_code == 200:
                    self.log_test(
                        f"Frontend Page: {name}",
                        True,
                        f"Page accessible: {path}"
                    )
                else:
                    self.log_test(
                        f"Frontend Page: {name}",
                        False,
                        f"Page failed with status {response.status_code}: {path}"
                    )
                    all_success = False
            except Exception as e:
                self.log_test(
                    f"Frontend Page: {name}",
                    False,
                    f"Page error: {str(e)}"
                )
                all_success = False
        
        return all_success
    
    def test_api_documentation(self) -> bool:
        """Test API documentation accessibility"""
        try:
            response = self.session.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.log_test(
                    "API Documentation",
                    True,
                    "API documentation accessible"
                )
                return True
            else:
                self.log_test(
                    "API Documentation",
                    False,
                    f"API docs failed with status {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test(
                "API Documentation",
                False,
                f"API docs error: {str(e)}"
            )
            return False
    
    def test_backend_services(self) -> bool:
        """Test backend services directly"""
        try:
            # Test AI/RAG system
            try:
                rag_system = get_rag_system()
                self.log_test(
                    "Backend AI/RAG System",
                    True,
                    "AI/RAG system initialized successfully"
                )
            except Exception as e:
                self.log_test(
                    "Backend AI/RAG System",
                    False,
                    f"AI/RAG system error: {str(e)}"
                )
                return False
            
            # Test Neo4j connection
            try:
                neo4j_uri = os.getenv('NEO4J_URI', 'neo4j://127.0.0.1:7687')
                neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
                neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
                
                neo4j_manager = Neo4jManager(neo4j_uri, neo4j_user, neo4j_password)
                if neo4j_manager.test_connection():
                    self.log_test(
                        "Backend Neo4j Connection",
                        True,
                        "Neo4j connection successful"
                    )
                else:
                    self.log_test(
                        "Backend Neo4j Connection",
                        False,
                        "Neo4j connection failed"
                    )
                    return False
            except Exception as e:
                self.log_test(
                    "Backend Neo4j Connection",
                    False,
                    f"Neo4j connection error: {str(e)}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test(
                "Backend Services",
                False,
                f"Backend services error: {str(e)}"
            )
            return False
    
    def test_data_flow(self) -> bool:
        """Test complete data flow from frontend to backend"""
        try:
            # Test AI/RAG query flow
            query_data = {
                "query": "What are the quality issues in manufacturing assets?",
                "analysis_type": "quality"
            }
            
            response = self.session.post(f"{self.base_url}/ai-rag/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                if result.get("analysis"):
                    self.log_test(
                        "AI/RAG Data Flow",
                        True,
                        "AI/RAG query flow successful",
                        {"query": query_data["query"], "response_length": len(result["analysis"])}
                    )
                else:
                    self.log_test(
                        "AI/RAG Data Flow",
                        False,
                        "AI/RAG query returned empty response"
                    )
                    return False
            else:
                self.log_test(
                    "AI/RAG Data Flow",
                    False,
                    f"AI/RAG query flow failed with status {response.status_code}"
                )
                return False
            
            # Test Knowledge Graph query flow
            kg_query_data = {"query": "MATCH (n:Asset) RETURN n LIMIT 5"}
            
            response = self.session.post(f"{self.base_url}/kg-neo4j/query", json=kg_query_data)
            if response.status_code == 200:
                result = response.json()
                self.log_test(
                    "Knowledge Graph Data Flow",
                    True,
                    "Knowledge Graph query flow successful",
                    {"query": kg_query_data["query"], "results_count": len(result.get("results", []))}
                )
            else:
                self.log_test(
                    "Knowledge Graph Data Flow",
                    False,
                    f"Knowledge Graph query flow failed with status {response.status_code}"
                )
                return False
            
            return True
            
        except Exception as e:
            self.log_test(
                "Data Flow",
                False,
                f"Data flow error: {str(e)}"
            )
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        logger.info("🚀 Starting Frontend-Backend Integration Tests")
        logger.info(f"Testing against: {self.base_url}")
        
        test_functions = [
            ("Webapp Health", self.test_webapp_health),
            ("Backend Services", self.test_backend_services),
            ("AI/RAG API", self.test_ai_rag_api),
            ("Knowledge Graph API", self.test_knowledge_graph_api),
            ("Frontend Pages", self.test_frontend_pages),
            ("API Documentation", self.test_api_documentation),
            ("Data Flow", self.test_data_flow)
        ]
        
        results = {}
        for test_name, test_func in test_functions:
            logger.info(f"\n📋 Running {test_name} tests...")
            try:
                success = test_func()
                results[test_name] = success
            except Exception as e:
                logger.error(f"❌ {test_name} test failed with exception: {e}")
                results[test_name] = False
        
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "component_results": results
        }
        
        logger.info(f"\n📊 Integration Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        # Log component results
        logger.info(f"\n🔧 Component Results:")
        for component, success in results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"   {component}: {status}")
        
        return summary

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frontend-Backend Integration Test")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL for testing")
    parser.add_argument("--output", help="Output file for test results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run tests
    tester = FrontendBackendIntegrationTest(args.url)
    results = tester.run_all_tests()
    
    # Save results if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"📄 Test results saved to: {args.output}")
    
    # Exit with appropriate code
    if results["failed_tests"] > 0:
        logger.error("❌ Some tests failed!")
        sys.exit(1)
    else:
        logger.info("✅ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main() 