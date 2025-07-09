"""
AASX Package Explorer Routes
FastAPI router for AASX Package Explorer integration and ETL pipeline management.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import subprocess
import json
import platform
import tempfile
import shutil
from pathlib import Path

# Import ETL pipeline components
from .aasx_etl_pipeline import AASXETLPipeline, ETLPipelineConfig
from .aasx_processor import AASXProcessor
from .aasx_transformer import AASXTransformer, TransformationConfig as TransformerConfig
from .aasx_loader import AASXLoader, LoaderConfig

# Create router
router = APIRouter(prefix="/aasx", tags=["aasx"])

# Setup templates
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# Pydantic models
class AasxFileInfo(BaseModel):
    filename: str
    filepath: str
    size: int
    modified_date: str
    description: Optional[str] = None

class AasxPackageInfo(BaseModel):
    package_id: str
    name: str
    version: str
    description: str
    assets: List[str]
    submodels: List[str]

class ETLConfigRequest(BaseModel):
    extract: Optional[Dict[str, Any]] = None
    transform: Optional[Dict[str, Any]] = None
    load: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None
    parallel_processing: bool = False
    max_workers: int = 4

class RAGSearchRequest(BaseModel):
    query: str
    entity_type: str = "all"
    top_k: int = 10

# Configuration
AASX_EXPLORER_PATH = os.path.join(os.getcwd(), "AasxPackageExplorer", "AasxPackageExplorer.exe")
AASX_CONTENT_PATH = os.path.join(os.getcwd(), "AasxPackageExplorer", "content-for-demo")

# Global ETL pipeline instance
etl_pipeline = None

def get_etl_pipeline():
    """Get or create ETL pipeline instance"""
    global etl_pipeline
    if etl_pipeline is None:
        config = ETLPipelineConfig(
            enable_validation=True,
            enable_logging=True,
            enable_backup=False,
            parallel_processing=False,
            max_workers=4
        )
        etl_pipeline = AASXETLPipeline(config)
    return etl_pipeline

@router.get("/", response_class=HTMLResponse)
async def aasx_dashboard(request: Request):
    """AASX ETL Pipeline dashboard"""
    # Get available AASX files
    aasx_files = get_available_aasx_files()
    
    return templates.TemplateResponse(
        "aasx/index.html",
        {
            "request": request,
            "title": "AASX ETL Pipeline - QI Digital Platform",
            "aasx_files": aasx_files,
            "explorer_available": os.path.exists(AASX_EXPLORER_PATH)
        }
    )

# ETL Pipeline API Endpoints

@router.post("/api/etl/run")
async def run_etl_pipeline(config: ETLConfigRequest):
    """Run complete ETL pipeline"""
    try:
        pipeline = get_etl_pipeline()
        
        # Update pipeline configuration if provided
        if config.extract:
            pipeline.config.extract_config = config.extract
        if config.transform:
            pipeline.config.transform_config = TransformerConfig(**config.transform)
        if config.load:
            pipeline.config.load_config = LoaderConfig(**config.load)
        
        pipeline.config.parallel_processing = config.parallel_processing
        pipeline.config.max_workers = config.max_workers
        
        # Process all files if no specific files provided
        if not config.files:
            aasx_files = get_available_aasx_files()
            config.files = [file['filename'] for file in aasx_files]
        
        # Run ETL pipeline
        results = []
        processed_files = {}
        
        for filename in config.files:
            file_path = find_aasx_file(filename)
            if file_path:
                result = pipeline.process_aasx_file(file_path)
                results.append(result)
                processed_files[filename] = result['status']
        
        # Calculate overall statistics
        successful = [r for r in results if r['status'] == 'completed']
        failed = [r for r in results if r['status'] == 'failed']
        
        overall_result = {
            'success': len(failed) == 0,
            'files_processed': len(successful),
            'files_failed': len(failed),
            'total_time': sum(r.get('processing_time', 0) for r in results),
            'processed_files': processed_files,
            'results': results,
            'pipeline_stats': pipeline.get_pipeline_stats()
        }
        
        return overall_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ETL pipeline error: {str(e)}")

@router.post("/api/etl/process-file")
async def process_single_file(config: ETLConfigRequest):
    """Process a single AASX file through ETL pipeline"""
    try:
        if not config.files or len(config.files) != 1:
            raise HTTPException(status_code=400, detail="Exactly one file must be specified")
        
        filename = config.files[0]
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        pipeline = get_etl_pipeline()
        
        # Update configuration
        if config.transform:
            pipeline.config.transform_config = TransformerConfig(**config.transform)
        if config.load:
            pipeline.config.load_config = LoaderConfig(**config.load)
        
        # Process file
        result = pipeline.process_aasx_file(file_path)
        
        return {
            'success': result['status'] == 'completed',
            'result': result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")

@router.post("/api/etl/process-batch")
async def process_batch_files(config: ETLConfigRequest):
    """Process multiple AASX files through ETL pipeline"""
    try:
        if not config.files:
            raise HTTPException(status_code=400, detail="No files specified")
        
        pipeline = get_etl_pipeline()
        
        # Update configuration
        if config.transform:
            pipeline.config.transform_config = TransformerConfig(**config.transform)
        if config.load:
            pipeline.config.load_config = LoaderConfig(**config.load)
        
        pipeline.config.parallel_processing = config.parallel_processing
        pipeline.config.max_workers = config.max_workers
        
        # Process files
        results = []
        processed_files = {}
        
        for filename in config.files:
            file_path = find_aasx_file(filename)
            if file_path:
                result = pipeline.process_aasx_file(file_path)
                results.append(result)
                processed_files[filename] = result['status']
        
        # Calculate statistics
        successful = [r for r in results if r['status'] == 'completed']
        failed = [r for r in results if r['status'] == 'failed']
        
        return {
            'success': len(failed) == 0,
            'files_processed': len(successful),
            'files_failed': len(failed),
            'total_time': sum(r.get('processing_time', 0) for r in results),
            'processed_files': processed_files,
            'results': results,
            'pipeline_stats': pipeline.get_pipeline_stats()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")

@router.get("/api/etl/stats")
async def get_etl_stats():
    """Get ETL pipeline statistics"""
    try:
        pipeline = get_etl_pipeline()
        stats = pipeline.get_pipeline_stats()
        
        # Add database statistics
        try:
            db_stats = pipeline.loader.get_database_stats()
            stats['database_stats'] = db_stats
        except Exception as e:
            stats['database_stats'] = {'error': str(e)}
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/api/etl/export-results")
async def export_etl_results():
    """Export ETL pipeline results"""
    try:
        pipeline = get_etl_pipeline()
        
        # Create export file
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'pipeline_stats': pipeline.get_pipeline_stats(),
            'validation_results': pipeline.validate_pipeline(),
            'component_configs': {
                'extract_config': pipeline.config.extract_config,
                'transform_config': {
                    'enable_quality_checks': pipeline.config.transform_config.enable_quality_checks,
                    'enable_enrichment': pipeline.config.transform_config.enable_enrichment,
                    'output_formats': pipeline.config.transform_config.output_formats,
                    'include_metadata': pipeline.config.transform_config.include_metadata
                },
                'load_config': {
                    'output_directory': pipeline.config.load_config.output_directory,
                    'database_path': pipeline.config.load_config.database_path,
                    'vector_db_path': pipeline.config.load_config.vector_db_path,
                    'vector_db_type': pipeline.config.load_config.vector_db_type,
                    'embedding_model': pipeline.config.load_config.embedding_model
                }
            }
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(export_data, f, indent=2)
            temp_file = f.name
        
        return FileResponse(
            temp_file,
            media_type='application/json',
            filename=f'etl_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# RAG System API Endpoints

@router.post("/api/rag/search")
async def search_rag(request: RAGSearchRequest):
    """Search RAG system using vector similarity"""
    try:
        pipeline = get_etl_pipeline()
        
        if not pipeline.loader.embedding_model:
            raise HTTPException(status_code=503, detail="Vector database not available")
        
        results = pipeline.loader.search_similar(
            query=request.query,
            entity_type=request.entity_type,
            top_k=request.top_k
        )
        
        return {
            'success': True,
            'query': request.query,
            'entity_type': request.entity_type,
            'results_count': len(results),
            'results': results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search error: {str(e)}")

@router.post("/api/rag/export")
async def export_rag_dataset():
    """Export RAG-ready dataset"""
    try:
        pipeline = get_etl_pipeline()
        
        # Create RAG dataset
        output_path = os.path.join(tempfile.gettempdir(), f'rag_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        rag_path = pipeline.create_rag_ready_dataset(output_path)
        
        return FileResponse(
            rag_path,
            media_type='application/json',
            filename=f'rag_dataset_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG export failed: {str(e)}")

# File Management API Endpoints

@router.get("/api/files")
async def get_aasx_files():
    """Get list of available AASX files"""
    try:
        files = get_available_aasx_files()
        return {
            "files": files,
            "total_count": len(files),
            "explorer_path": AASX_EXPLORER_PATH,
            "explorer_available": os.path.exists(AASX_EXPLORER_PATH)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/open/{filename}")
async def open_aasx_file(filename: str):
    """Open AASX file with AASX Package Explorer"""
    try:
        if not os.path.exists(AASX_EXPLORER_PATH):
            raise HTTPException(status_code=404, detail="AASX Package Explorer not found")
        
        # Find the file
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="AASX file not found")
        
        # Launch AASX Package Explorer with the file
        if platform.system() == "Windows":
            subprocess.Popen([AASX_EXPLORER_PATH, file_path])
        else:
            # For non-Windows systems, try to open with default application
            subprocess.Popen(["open", file_path] if platform.system() == "Darwin" else ["xdg-open", file_path])
        
        return {
            "success": True,
            "message": f"AASX Package Explorer launched with {filename}",
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/results/{filename}")
async def get_file_results(filename: str):
    """Get processing results for a specific file"""
    try:
        pipeline = get_etl_pipeline()
        
        # Get database stats to check if file was processed
        db_stats = pipeline.loader.get_database_stats()
        
        # Mock results (in real implementation, you'd query the database)
        results = {
            'filename': filename,
            'processed': True,
            'processing_time': 2.5,
            'extract_result': {
                'success': True,
                'assets_found': 3,
                'submodels_found': 2,
                'documents_found': 1
            },
            'transform_result': {
                'success': True,
                'transformations_applied': ['quality_enrichment', 'normalization'],
                'output_formats': ['json', 'csv']
            },
            'load_result': {
                'success': True,
                'database_records': 6,
                'vector_embeddings': 6,
                'files_exported': ['output.json', 'output.csv']
            }
        }
        
        return {
            'success': True,
            'data': results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")

@router.post("/api/refresh")
async def refresh_files():
    """Refresh the list of available AASX files"""
    try:
        # This would typically clear any cached file lists
        # For now, just return success
        return {
            "success": True,
            "message": "File list refreshed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/explorer/status")
async def get_explorer_status():
    """Get AASX Package Explorer status"""
    try:
        explorer_available = os.path.exists(AASX_EXPLORER_PATH)
        
        status = {
            "available": explorer_available,
            "path": AASX_EXPLORER_PATH,
            "platform": platform.system(),
            "content_path": AASX_CONTENT_PATH,
            "content_available": os.path.exists(AASX_CONTENT_PATH)
        }
        
        if explorer_available:
            # Get file size and modification time
            stat = os.stat(AASX_EXPLORER_PATH)
            status.update({
                "file_size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/explorer/launch")
async def launch_explorer():
    """Launch AASX Package Explorer without specific file"""
    try:
        if not os.path.exists(AASX_EXPLORER_PATH):
            raise HTTPException(status_code=404, detail="AASX Package Explorer not found")
        
        # Launch AASX Package Explorer
        if platform.system() == "Windows":
            subprocess.Popen([AASX_EXPLORER_PATH])
        else:
            # For non-Windows systems
            subprocess.Popen(["open", AASX_EXPLORER_PATH] if platform.system() == "Darwin" else ["xdg-open", AASX_EXPLORER_PATH])
        
        return {
            "success": True,
            "message": "AASX Package Explorer launched successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/explorer/launch-script")
async def launch_explorer_script():
    """Get launch script for AASX Package Explorer"""
    try:
        if not os.path.exists(AASX_EXPLORER_PATH):
            raise HTTPException(status_code=404, detail="AASX Package Explorer not found")
        
        # Create launch script
        script_content = f"""@echo off
echo Launching AASX Package Explorer...
"{AASX_EXPLORER_PATH}"
pause
"""
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
            f.write(script_content)
            temp_file = f.name
        
        return FileResponse(
            temp_file,
            media_type='application/x-bat',
            filename='launch_aasx_explorer.bat'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/packages/{filename}")
async def get_package_info(filename: str):
    """Get information about an AASX package"""
    try:
        # Find the file
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="AASX file not found")
        
        # Mock package information (in real implementation, you'd parse the AASX file)
        package_info = {
            "package_id": f"pkg_{filename.replace('.aasx', '')}",
            "name": filename.replace('.aasx', '').replace('_', ' ').title(),
            "version": "1.0.0",
            "description": f"Digital twin package for {filename.replace('.aasx', '').replace('_', ' ').title()}",
            "assets": [
                "3D_Model.step",
                "Technical_Documentation.pdf",
                "Quality_Certificate.pdf"
            ],
            "submodels": [
                "TechnicalData",
                "Documentation",
                "QualityAssurance",
                "Maintenance"
            ],
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "modified_date": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        return package_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/packages/{filename}/download")
async def download_aasx_file(filename: str):
    """Download an AASX file"""
    try:
        # Find the file
        file_path = find_aasx_file(filename)
        
        if not file_path:
            raise HTTPException(status_code=404, detail="AASX file not found")
        
        return FileResponse(
            file_path,
            media_type='application/octet-stream',
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions

def find_aasx_file(filename: str) -> Optional[str]:
    """Find AASX file in content directory"""
    for root, dirs, files in os.walk(AASX_CONTENT_PATH):
        if filename in files:
            return os.path.join(root, filename)
    return None

def get_available_aasx_files():
    """Get list of available AASX files"""
    files = []
    
    if not os.path.exists(AASX_CONTENT_PATH):
        return files
    
    for root, dirs, filenames in os.walk(AASX_CONTENT_PATH):
        for filename in filenames:
            if filename.lower().endswith('.aasx'):
                file_path = os.path.join(root, filename)
                stat = os.stat(file_path)
                
                # Create description based on filename
                description = filename.replace('.aasx', '').replace('_', ' ').title()
                
                files.append({
                    'filename': filename,
                    'filepath': file_path,
                    'size': stat.st_size,
                    'modified_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'description': description
                })
    
    # Sort by modification date (newest first)
    files.sort(key=lambda x: x['modified_date'], reverse=True)
    
    return files

@router.get("/api/integration/status")
async def get_integration_status():
    """Get integration status for all components"""
    try:
        pipeline = get_etl_pipeline()
        
        status = {
            "aasx_explorer": {
                "available": os.path.exists(AASX_EXPLORER_PATH),
                "path": AASX_EXPLORER_PATH
            },
            "etl_pipeline": {
                "available": True,
                "validation": pipeline.validate_pipeline(),
                "stats": pipeline.get_pipeline_stats()
            },
            "vector_database": {
                "available": pipeline.loader.embedding_model is not None,
                "type": pipeline.config.load_config.vector_db_type,
                "model": pipeline.config.load_config.embedding_model
            },
            "rag_system": {
                "available": pipeline.loader.embedding_model is not None and pipeline.vector_db is not None,
                "ready": True
            }
        }
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 