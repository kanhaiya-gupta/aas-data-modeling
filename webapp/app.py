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
    title="QI Digital Platform",
    description="A comprehensive platform for Quality Infrastructure digital twins and analysis",
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
app.mount("/css", StaticFiles(directory=os.path.join(current_dir, "static", "css")), name="css")
app.mount("/js", StaticFiles(directory=os.path.join(current_dir, "static", "js")), name="js")
app.mount("/images", StaticFiles(directory=os.path.join(current_dir, "static", "images")), name="images")

# Setup templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Import routers from individual modules
from webapp.ai_rag.routes import router as ai_rag_router
from webapp.twin_registry.routes import router as twin_registry_router
from webapp.certificate_manager.routes import router as certificate_manager_router
from webapp.qi_analytics.routes import router as qi_analytics_router
from webapp.aasx.routes import router as aasx_router

# Include routers with proper prefixes
app.include_router(ai_rag_router, prefix="/ai-rag", tags=["ai-rag"])
app.include_router(twin_registry_router, prefix="/twin-registry", tags=["twin-registry"])
app.include_router(certificate_manager_router, prefix="/certificates", tags=["certificates"])
app.include_router(qi_analytics_router, prefix="/analytics", tags=["analytics"])
app.include_router(aasx_router, prefix="/aasx", tags=["aasx"])

# Main dashboard route
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "QI Digital Platform - Quality Infrastructure Digital Twins",
            "modules": [
                {
                    "id": "aasx",
                    "name": "AASX Package Explorer",
                    "description": "Manage and explore digital twin packages",
                    "url": "/aasx",
                    "icon": "📦"
                },
                {
                    "id": "ai-rag",
                    "name": "AI/RAG System",
                    "description": "AI-powered analysis and insights for digital twins",
                    "url": "/ai-rag",
                    "icon": "🤖"
                },
                {
                    "id": "twin-registry",
                    "name": "Digital Twin Registry",
                    "description": "Manage and monitor digital twin registrations",
                    "url": "/twin-registry",
                    "icon": "🔄"
                },
                {
                    "id": "certificates",
                    "name": "Certificate Manager",
                    "description": "Digital certificates and compliance management",
                    "url": "/certificates",
                    "icon": "📜"
                },
                {
                    "id": "analytics",
                    "name": "QI Analytics",
                    "description": "Quality Infrastructure analytics and dashboards",
                    "url": "/analytics",
                    "icon": "📊"
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
        "service": "qi-digital-platform",
        "version": "1.0.0",
        "timestamp": time.time()
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
                "title": "Page Not Found - QI Digital Platform"
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
                "title": "Internal Server Error - QI Digital Platform"
            },
            status_code=500
        )
    except Exception:
        # Fallback to simple JSON response if template fails
        return {"error": "Internal server error", "status_code": 500}

# Module-specific routes
@app.get("/ai-rag", response_class=HTMLResponse)
async def ai_rag_page(request: Request):
    """AI/RAG system page"""
    return templates.TemplateResponse(
        "ai_rag/index.html",
        {
            "request": request,
            "title": "AI/RAG System - QI Digital Platform"
        }
    )

@app.get("/twin-registry", response_class=HTMLResponse)
async def twin_registry_page(request: Request):
    """Twin registry page"""
    return templates.TemplateResponse(
        "twin_registry/index.html",
        {
            "request": request,
            "title": "Digital Twin Registry - QI Digital Platform"
        }
    )

@app.get("/certificates", response_class=HTMLResponse)
async def certificates_page(request: Request):
    """Certificate manager page"""
    return templates.TemplateResponse(
        "certificate_manager/index.html",
        {
            "request": request,
            "title": "Certificate Manager - QI Digital Platform"
        }
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    return templates.TemplateResponse(
        "qi_analytics/index.html",
        {
            "request": request,
            "title": "QI Analytics Dashboard - QI Digital Platform"
        }
    )

@app.get("/aasx", response_class=HTMLResponse)
async def aasx_page(request: Request):
    """AASX Package Explorer page"""
    # Import the function to get AASX files
    from webapp.aasx.routes import get_available_aasx_files
    from webapp.aasx.routes import AASX_EXPLORER_PATH
    import os
    
    # Get available AASX files
    aasx_files = get_available_aasx_files()
    
    return templates.TemplateResponse(
        "aasx/index.html",
        {
            "request": request,
            "title": "AASX Package Explorer - QI Digital Platform",
            "aasx_files": aasx_files,
            "explorer_available": os.path.exists(AASX_EXPLORER_PATH)
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
