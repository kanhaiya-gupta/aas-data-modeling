# FastAPI Best Practices for QI Digital Platform

## Overview

This guide covers FastAPI best practices specifically tailored for the QI Digital Platform, including AAS integration, performance optimization, and production-ready patterns.

## FastAPI Service Structure

### Recommended Project Structure

```
backend/
├── ai-rag/
│   ├── main.py              # FastAPI application entry point
│   ├── api/                 # API route modules
│   │   ├── __init__.py
│   │   ├── v1/             # API versioning
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── query.py
│   │   │   │   ├── documents.py
│   │   │   │   └── health.py
│   │   │   └── api.py      # API router
│   │   └── dependencies.py # Shared dependencies
│   ├── core/               # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py       # Settings management
│   │   ├── security.py     # Authentication & authorization
│   │   └── exceptions.py   # Custom exceptions
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   ├── query.py        # Query request/response models
│   │   ├── document.py     # Document models
│   │   └── aas.py          # AAS-specific models
│   ├── services/           # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py   # AI/RAG logic
│   │   ├── vector_store.py # Vector database operations
│   │   └── aas_processor.py # AAS data processing
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py       # Logging configuration
│   │   └── validators.py   # Custom validators
│   └── tests/              # Test files
│       ├── __init__.py
│       ├── test_api.py
│       └── test_services.py
```

## FastAPI Application Setup

### Main Application Configuration

```python
# backend/ai-rag/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging

from core.config import settings
from core.exceptions import CustomException
from api.v1.api import api_router
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting AI/RAG Service...")
    # Initialize services, connections, etc.
    yield
    # Shutdown
    logger.info("Shutting down AI/RAG Service...")
    # Cleanup connections, etc.

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="QI Digital Platform - AI/RAG Service",
        description="AI-powered retrieval and analysis for quality infrastructure",
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    # Global exception handler
    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "code": exc.code}
        )
    
    # Request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    return app

app = create_application()
```

### Configuration Management

```python
# backend/ai-rag/core/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "QI Digital Platform - AI/RAG Service"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/qi_platform"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "qi_documents"
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # AAS Integration
    AAS_SERVICE_URL: str = "http://localhost:8002"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
```

## API Design Patterns

### Versioned API Routes

```python
# backend/ai-rag/api/v1/api.py
from fastapi import APIRouter
from .endpoints import query, documents, health, aas

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Core functionality
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# AAS integration
api_router.include_router(aas.router, prefix="/aas", tags=["aas"])
```

### Endpoint Implementation

```python
# backend/ai-rag/api/v1/endpoints/query.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Optional
import asyncio

from models.query import QueryRequest, QueryResponse, QueryStreamResponse
from services.ai_service import AIService
from services.vector_store import VectorStore
from core.security import get_current_user
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/", response_model=QueryResponse)
async def query_ai(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    ai_service: AIService = Depends(),
    vector_store: VectorStore = Depends()
):
    """Query the AI system with context"""
    
    try:
        # Log query for analytics
        background_tasks.add_task(
            log_query_analytics,
            user_id=current_user.id,
            query=request.query,
            context=request.context
        )
        
        # Retrieve relevant documents
        documents = await vector_store.search(
            query=request.query,
            context=request.context,
            limit=request.max_results or 5
        )
        
        # Generate AI response
        response = await ai_service.generate_response(
            query=request.query,
            context=request.context,
            documents=documents
        )
        
        return QueryResponse(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence,
            processing_time=response.processing_time
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/stream")
async def query_ai_stream(
    request: QueryRequest,
    current_user = Depends(get_current_user),
    ai_service: AIService = Depends()
):
    """Stream AI response"""
    
    async def generate_stream():
        try:
            async for chunk in ai_service.generate_stream_response(
                query=request.query,
                context=request.context
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Error in stream response: {str(e)}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )

@router.get("/suggestions")
async def get_query_suggestions(
    context: Optional[str] = None,
    limit: int = 5,
    vector_store: VectorStore = Depends()
):
    """Get query suggestions based on context"""
    
    suggestions = await vector_store.get_suggestions(
        context=context,
        limit=limit
    )
    
    return {"suggestions": suggestions}
```

### Pydantic Models

```python
# backend/ai-rag/models/query.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QueryType(str, Enum):
    GENERAL = "general"
    QUALITY = "quality"
    COMPLIANCE = "compliance"
    TECHNICAL = "technical"

class QueryRequest(BaseModel):
    """Query request model"""
    
    query: str = Field(..., min_length=1, max_length=1000, description="The query text")
    context: Optional[str] = Field(None, description="Query context or domain")
    query_type: QueryType = Field(QueryType.GENERAL, description="Type of query")
    max_results: Optional[int] = Field(5, ge=1, le=20, description="Maximum number of results")
    include_sources: bool = Field(True, description="Include source documents")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class DocumentSource(BaseModel):
    """Document source information"""
    
    id: str
    title: str
    content: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class QueryResponse(BaseModel):
    """Query response model"""
    
    answer: str
    sources: List[DocumentSource] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time: float
    query_type: QueryType
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class QueryStreamResponse(BaseModel):
    """Streaming query response model"""
    
    chunk: str
    is_complete: bool = False
    error: Optional[str] = None
```

## Service Layer Implementation

### AI Service

```python
# backend/ai-rag/services/ai_service.py
from typing import List, Optional, AsyncGenerator
import asyncio
import time
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from models.query import QueryRequest, QueryResponse, DocumentSource
from models.aas import AASAsset
from utils.logger import get_logger

logger = get_logger(__name__)

class AIService:
    """AI service for query processing and response generation"""
    
    def __init__(self):
        self.openai_client = AsyncOpenAI()
        self.anthropic_client = AsyncAnthropic()
        self.model_config = {
            "openai": "gpt-4-turbo-preview",
            "anthropic": "claude-3-sonnet-20240229"
        }
    
    async def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        documents: List[DocumentSource] = None
    ) -> QueryResponse:
        """Generate AI response with context"""
        
        start_time = time.time()
        
        try:
            # Prepare context from documents
            context_text = self._prepare_context(documents) if documents else ""
            
            # Generate response using OpenAI
            response = await self._generate_openai_response(
                query=query,
                context=context_text,
                domain_context=context
            )
            
            processing_time = time.time() - start_time
            
            return QueryResponse(
                answer=response["answer"],
                sources=documents or [],
                confidence=response["confidence"],
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise
    
    async def generate_stream_response(
        self,
        query: str,
        context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming AI response"""
        
        try:
            async for chunk in self._stream_openai_response(query, context):
                yield chunk
        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            yield f"Error: {str(e)}"
    
    async def process_aas_data(self, aas_asset: AASAsset) -> str:
        """Process AAS asset data for AI analysis"""
        
        # Extract relevant information from AAS asset
        asset_info = f"Asset: {aas_asset.id_short}\n"
        asset_info += f"Type: {aas_asset.kind}\n"
        asset_info += f"Description: {aas_asset.description or 'N/A'}\n"
        
        # Process submodels
        for submodel in aas_asset.submodels:
            asset_info += f"\nSubmodel: {submodel.id_short}\n"
            for element in submodel.submodel_elements:
                asset_info += f"  {element.id_short}: {element.value}\n"
        
        return asset_info
    
    def _prepare_context(self, documents: List[DocumentSource]) -> str:
        """Prepare context from documents"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i}: {doc.title}\n{doc.content}")
        return "\n\n".join(context_parts)
    
    async def _generate_openai_response(
        self,
        query: str,
        context: str,
        domain_context: Optional[str] = None
    ) -> dict:
        """Generate response using OpenAI"""
        
        system_prompt = self._build_system_prompt(domain_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}
        ]
        
        response = await self.openai_client.chat.completions.create(
            model=self.model_config["openai"],
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return {
            "answer": response.choices[0].message.content,
            "confidence": 0.85  # Placeholder confidence score
        }
    
    async def _stream_openai_response(
        self,
        query: str,
        context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI"""
        
        system_prompt = self._build_system_prompt(context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        stream = await self.openai_client.chat.completions.create(
            model=self.model_config["openai"],
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def _build_system_prompt(self, domain_context: Optional[str] = None) -> str:
        """Build system prompt based on domain context"""
        
        base_prompt = """You are an AI assistant specialized in quality infrastructure and digital twin management. 
        Provide accurate, helpful responses based on the provided context."""
        
        if domain_context == "additive_manufacturing":
            base_prompt += "\n\nFocus on additive manufacturing processes, quality standards, and best practices."
        elif domain_context == "hydrogen_filling":
            base_prompt += "\n\nFocus on hydrogen filling station operations, safety protocols, and compliance requirements."
        
        return base_prompt
```

## Error Handling and Validation

### Custom Exceptions

```python
# backend/ai-rag/core/exceptions.py
from fastapi import HTTPException
from typing import Optional

class CustomException(HTTPException):
    """Base custom exception"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.code = code

class AASValidationError(CustomException):
    """AAS validation error"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=400,
            detail=detail,
            code="AAS_VALIDATION_ERROR"
        )

class AIServiceError(CustomException):
    """AI service error"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=503,
            detail=detail,
            code="AI_SERVICE_ERROR"
        )

class VectorStoreError(CustomException):
    """Vector store error"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=503,
            detail=detail,
            code="VECTOR_STORE_ERROR"
        )
```

### Request Validation

```python
# backend/ai-rag/utils/validators.py
from typing import Any, Dict
from pydantic import ValidationError
import re

def validate_aas_identifier(identifier: str) -> bool:
    """Validate AAS identifier format"""
    # Basic IRI validation
    iri_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(iri_pattern, identifier))

def validate_query_content(query: str) -> Dict[str, Any]:
    """Validate query content and return analysis"""
    
    analysis = {
        "is_valid": True,
        "warnings": [],
        "suggestions": []
    }
    
    # Check length
    if len(query) < 10:
        analysis["warnings"].append("Query is very short")
        analysis["suggestions"].append("Consider providing more context")
    
    if len(query) > 500:
        analysis["warnings"].append("Query is very long")
        analysis["suggestions"].append("Consider breaking into multiple queries")
    
    # Check for technical terms
    technical_terms = ["quality", "standard", "certificate", "compliance", "manufacturing"]
    found_terms = [term for term in technical_terms if term.lower() in query.lower()]
    
    if not found_terms:
        analysis["suggestions"].append("Consider using quality infrastructure terminology")
    
    return analysis
```

## Performance Optimization

### Caching Strategy

```python
# backend/ai-rag/services/cache_service.py
import redis.asyncio as redis
import json
import hashlib
from typing import Optional, Any
from functools import wraps

class CacheService:
    """Redis-based caching service"""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            await self.redis.setex(key, ttl, json.dumps(value))
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False
    
    def generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()

def cache_result(ttl: int = 3600):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_service = CacheService("redis://localhost:6379")
            cache_key = cache_service.generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### Database Connection Pooling

```python
# backend/ai-rag/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from core.config import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

## Testing Strategies

### API Testing

```python
# backend/ai-rag/tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)

@pytest.fixture
def mock_ai_service():
    with patch('api.v1.endpoints.query.AIService') as mock:
        service = AsyncMock()
        mock.return_value = service
        yield service

@pytest.fixture
def mock_vector_store():
    with patch('api.v1.endpoints.query.VectorStore') as mock:
        store = AsyncMock()
        mock.return_value = store
        yield store

def test_query_ai_success(mock_ai_service, mock_vector_store):
    """Test successful AI query"""
    
    # Mock responses
    mock_vector_store.search.return_value = [
        {"id": "1", "title": "Test Doc", "content": "Test content"}
    ]
    
    mock_ai_service.generate_response.return_value = {
        "answer": "Test answer",
        "confidence": 0.9,
        "processing_time": 1.5
    }
    
    # Make request
    response = client.post(
        "/api/v1/query/",
        json={
            "query": "What are quality standards?",
            "context": "additive_manufacturing"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "confidence" in data

def test_query_ai_validation_error():
    """Test query validation error"""
    
    response = client.post(
        "/api/v1/query/",
        json={
            "query": "",  # Empty query
            "context": "additive_manufacturing"
        }
    )
    
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_aas_integration():
    """Test AAS integration"""
    
    # Test AAS asset creation
    aas_data = {
        "id_short": "TestAsset",
        "description": "Test AAS asset",
        "kind": "Instance"
    }
    
    response = client.post("/api/v1/aas/assets", json=aas_data)
    assert response.status_code == 200
    
    # Test AAS asset retrieval
    asset_id = response.json()["id"]
    response = client.get(f"/api/v1/aas/assets/{asset_id}")
    assert response.status_code == 200
```

### Service Testing

```python
# backend/ai-rag/tests/test_services.py
import pytest
from unittest.mock import AsyncMock, patch

from services.ai_service import AIService
from services.vector_store import VectorStore

@pytest.fixture
def ai_service():
    return AIService()

@pytest.fixture
def vector_store():
    return VectorStore()

@pytest.mark.asyncio
async def test_ai_service_generate_response(ai_service):
    """Test AI service response generation"""
    
    with patch.object(ai_service, '_generate_openai_response') as mock_generate:
        mock_generate.return_value = {
            "answer": "Test response",
            "confidence": 0.85
        }
        
        response = await ai_service.generate_response(
            query="Test query",
            context="additive_manufacturing"
        )
        
        assert response.answer == "Test response"
        assert response.confidence == 0.85
        assert response.processing_time > 0

@pytest.mark.asyncio
async def test_vector_store_search(vector_store):
    """Test vector store search functionality"""
    
    with patch.object(vector_store, '_search_vectors') as mock_search:
        mock_search.return_value = [
            {"id": "1", "score": 0.9, "content": "Test document"}
        ]
        
        results = await vector_store.search(
            query="test query",
            limit=5
        )
        
        assert len(results) == 1
        assert results[0]["id"] == "1"
```

## Production Deployment

### Docker Configuration

```dockerfile
# backend/ai-rag/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Environment Configuration

```bash
# backend/ai-rag/.env.production
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Security
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=["your-domain.com"]

# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/qi_platform

# Redis
REDIS_URL=redis://prod-redis:6379

# AI Services
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Vector Database
QDRANT_URL=http://prod-qdrant:6333

# Logging
LOG_LEVEL=INFO
```

This comprehensive FastAPI best practices guide provides the foundation for building robust, scalable, and maintainable FastAPI services for the QI Digital Platform, with specific focus on AAS integration and quality infrastructure requirements. 