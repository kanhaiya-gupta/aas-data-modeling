#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QI Digital Platform Web Application
Main FastAPI application for the Quality Infrastructure Digital Platform.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import time
from pathlib import Path

# Create FastAPI app
app = FastAPI(
    title="AASX Digital Twin Analytics Framework",
    description="A comprehensive framework for processing AASX files and building digital twin analytics with ETL, Knowledge Graph, and AI/RAG capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Import routers from individual modules (with error handling)
ai_rag_router = None
twin_registry_router = None
certificate_manager_router = None
qi_analytics_router = None
aasx_router = None
kg_neo4j_router = None

try:
    from webapp.ai_rag.routes import router as ai_rag_router
    app.include_router(ai_rag_router, prefix="/ai-rag", tags=["ai-rag"])
    print("✅ AI/RAG router loaded successfully")
except Exception as e:
    print(f"⚠️  AI/RAG router failed to load: {e}")

try:
    from webapp.kg_neo4j.routes import router as kg_neo4j_router
    app.include_router(kg_neo4j_router, prefix="/kg-neo4j", tags=["kg-neo4j"])
    print("✅ Knowledge Graph router loaded successfully")
except Exception as e:
    print(f"⚠️  Knowledge Graph router failed to load: {e}")

try:
    from webapp.twin_registry.routes import router as twin_registry_router
    app.include_router(twin_registry_router, prefix="/twin-registry", tags=["twin-registry"])
    print("✅ Twin Registry router loaded successfully")
except Exception as e:
    print(f"⚠️  Twin Registry router failed to load: {e}")

try:
    from webapp.certificate_manager.routes import router as certificate_manager_router
    app.include_router(certificate_manager_router, prefix="/certificates", tags=["certificates"])
    print("✅ Certificate Manager router loaded successfully")
except Exception as e:
    print(f"⚠️  Certificate Manager router failed to load: {e}")

try:
    from webapp.qi_analytics.routes import router as qi_analytics_router
    app.include_router(qi_analytics_router, prefix="/analytics", tags=["analytics"])
    print("✅ QI Analytics router loaded successfully")
except Exception as e:
    print(f"⚠️  QI Analytics router failed to load: {e}")

try:
    from webapp.aasx.routes import router as aasx_router
    app.include_router(aasx_router, prefix="/aasx", tags=["aasx"])
    print("✅ AASX router loaded successfully")
except Exception as e:
    print(f"⚠️  AASX router failed to load: {e}")

# Main dashboard route
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "AASX Digital Twin Analytics Framework",
            "modules": [
                {
                    "id": "aasx-etl",
                    "name": "AASX ETL Pipeline",
                    "description": "Extract, Transform, Load AASX files into structured data",
                    "url": "/aasx",
                    "icon": "⚙️",
                    "available": aasx_router is not None
                },
                {
                    "id": "kg-neo4j",
                    "name": "Knowledge Graph",
                    "description": "Neo4j knowledge graph explorer and analytics",
                    "url": "/kg-neo4j",
                    "icon": "🕸️",
                    "available": kg_neo4j_router is not None
                },
                {
                    "id": "ai-rag",
                    "name": "AI/RAG System",
                    "description": "AI-powered analysis and insights for digital twins",
                    "url": "/ai-rag",
                    "icon": "🤖",
                    "available": ai_rag_router is not None
                },
                {
                    "id": "twin-registry",
                    "name": "Digital Twin Registry",
                    "description": "Manage and monitor digital twin registrations",
                    "url": "/twin-registry",
                    "icon": "🔄",
                    "available": twin_registry_router is not None
                },
                {
                    "id": "certificates",
                    "name": "Certificate Manager",
                    "description": "Digital certificates and compliance management",
                    "url": "/certificates",
                    "icon": "📜",
                    "available": certificate_manager_router is not None
                },
                {
                    "id": "analytics",
                    "name": "Analytics Dashboard",
                    "description": "Digital twin analytics and visualization",
                    "url": "/analytics",
                    "icon": "📊",
                    "available": qi_analytics_router is not None
                }
            ]
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "aasx-digital-twin-analytics-framework",
        "version": "1.0.0",
        "timestamp": time.time(),
        "modules": {
            "ai_rag": ai_rag_router is not None,
            "kg_neo4j": kg_neo4j_router is not None,
            "twin_registry": twin_registry_router is not None,
            "certificate_manager": certificate_manager_router is not None,
            "qi_analytics": qi_analytics_router is not None,
            "aasx": aasx_router is not None
        }
    }

# API documentation redirect
@app.get("/docs")
async def api_docs():
    """Redirect to API documentation"""
    return {"message": "API documentation available at /docs"}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    try:
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "title": "Page Not Found - AASX Digital Twin Analytics Framework"
            },
            status_code=404
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Page not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    """Handle 500 errors"""
    try:
        return templates.TemplateResponse(
            "500.html",
            {
                "request": request,
                "title": "Internal Server Error - AASX Digital Twin Analytics Framework"
            },
            status_code=500
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Internal server error", "status_code": 500}

# Module-specific routes (with availability checks)
@app.get("/ai-rag", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG system page"""
    if ai_rag_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "AI/RAG System - AASX Digital Twin Analytics Framework",
                "error": "AI/RAG module is not available. Please check the backend services."
            }
        )
    
    return templates.TemplateResponse(
        "ai_rag/index.html",
        {
            "request": request,
            "title": "AI/RAG System - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/twin-registry", response_class=HTMLResponse)
async def twin_registry_page(request: Request):
    """Twin registry page"""
    if twin_registry_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework",
                "error": "Twin Registry module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "twin_registry/index.html",
        {
            "request": request,
            "title": "Digital Twin Registry - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/certificates", response_class=HTMLResponse)
async def certificates_page(request: Request):
    """Certificate manager page"""
    if certificate_manager_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Certificate Manager - AASX Digital Twin Analytics Framework",
                "error": "Certificate Manager module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "certificate_manager/index.html",
        {
            "request": request,
            "title": "Certificate Manager - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    if qi_analytics_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Analytics Dashboard - AASX Digital Twin Analytics Framework",
                "error": "Analytics module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "qi_analytics/index.html",
        {
            "request": request,
            "title": "Analytics Dashboard - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/kg-neo4j", response_class=HTMLResponse)
async def kg_neo4j_page(request: Request):
    """Knowledge Graph page"""
    if kg_neo4j_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "Knowledge Graph - AASX Digital Twin Analytics Framework",
                "error": "Knowledge Graph module is not available. Please check Neo4j connection."
            }
        )
    
    return templates.TemplateResponse(
        "kg_neo4j/index.html",
        {
            "request": request,
            "title": "Knowledge Graph - AASX Digital Twin Analytics Framework"
        }
    )

@app.get("/aasx", response_class=HTMLResponse)
async def aasx_page(request: Request):
    """AASX Package Explorer page"""
    if aasx_router is None:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "title": "AASX Package Explorer - AASX Digital Twin Analytics Framework",
                "error": "AASX module is not available."
            }
        )
    
    return templates.TemplateResponse(
        "aasx/index.html",
        {
            "request": request,
            "title": "AASX Package Explorer - AASX Digital Twin Analytics Framework",
            "aasx_files": [],
            "explorer_available": False
        }
    )

@app.get("/flowchart", response_class=HTMLResponse)
async def flowchart_page(request: Request):
    """Flowchart page showing the complete framework processing flow"""
    return templates.TemplateResponse(
        "flowchart.html",
        {
            "request": request,
            "title": "Processing Flow - AASX Digital Twin Analytics Framework"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
