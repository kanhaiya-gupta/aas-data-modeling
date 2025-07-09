# AAS Integration Guide

## Overview

The QI Digital Platform integrates with Asset Administrative Shell (AAS) for standardized digital twin representation and management. This guide covers AAS integration, data models, and implementation patterns.

## AAS Core Concepts

### Asset Administrative Shell (AAS)

AAS is a standardized digital representation of assets that provides:
- **Digital Identity**: Unique identification of assets
- **Semantic Description**: Machine-readable asset descriptions
- **Submodels**: Modular data structures for specific use cases
- **Interoperability**: Standardized communication between systems

### Key AAS Components

1. **Asset**: Physical or logical entity (e.g., manufacturing equipment)
2. **Asset Administrative Shell**: Digital representation of the asset
3. **Submodels**: Specific data models for different aspects
4. **Submodel Elements**: Individual data points within submodels

## AAS Integration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AASX Explorer │    │  QI Platform    │    │   External      │
│   (Windows)     │    │   Services      │    │   Systems       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      AAS Integration      │
                    │         Layer             │
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
┌───────▼────────┐    ┌───────────▼──────────┐    ┌────────▼────────┐
│ AAS Parser     │    │ AAS Validator        │    │ AAS Exporter    │
│ (Import)       │    │ (Validation)         │    │ (Export)        │
└───────┬────────┘    └───────────┬──────────┘    └────────┬────────┘
        │                         │                        │
        └─────────────────────────┼─────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │      Data Storage         │
                    │   (PostgreSQL/JSON)       │
                    └───────────────────────────┘
```

## AAS Data Models

### Core AAS Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AssetKind(str, Enum):
    TYPE = "Type"
    INSTANCE = "Instance"

class AASIdentifier(BaseModel):
    id_type: str
    value: str

class Asset(BaseModel):
    id_short: str
    description: Optional[str] = None
    id: AASIdentifier
    kind: AssetKind
    submodels: List["Submodel"] = []

class Submodel(BaseModel):
    id_short: str
    description: Optional[str] = None
    id: AASIdentifier
    submodel_elements: List["SubmodelElement"] = []

class SubmodelElement(BaseModel):
    id_short: str
    description: Optional[str] = None
    semantic_id: Optional[str] = None
    kind: str = "Instance"
```

### Quality Infrastructure Submodels

```python
class QualityCertificateSubmodel(Submodel):
    """Submodel for quality certificates and compliance"""
    
    certificate_type: str
    issuer: str
    issued_date: datetime
    expiry_date: datetime
    standards: List[str]
    scope: str
    status: str

class ManufacturingProcessSubmodel(Submodel):
    """Submodel for manufacturing process data"""
    
    process_type: str
    parameters: Dict[str, Any]
    quality_metrics: Dict[str, float]
    equipment_id: str
    operator_id: str

class SensorDataSubmodel(Submodel):
    """Submodel for IoT sensor data"""
    
    sensor_type: str
    measurements: List[Dict[str, Any]]
    calibration_date: datetime
    accuracy: float
    unit: str
```

## FastAPI AAS Implementation

### AAS Service Structure

```python
# backend/aas-service/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Optional
import aas_core3 as aas
from .models import AssetCreate, AssetResponse, SubmodelCreate
from .services import AASService

app = FastAPI(
    title="AAS Integration Service",
    description="Asset Administrative Shell integration for QI Platform",
    version="1.0.0"
)

aas_service = AASService()

@app.post("/aas/assets", response_model=AssetResponse)
async def create_asset(asset: AssetCreate):
    """Create a new AAS asset"""
    return await aas_service.create_asset(asset)

@app.get("/aas/assets", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """List all AAS assets with optional filtering"""
    return await aas_service.list_assets(asset_type, limit, offset)

@app.get("/aas/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: str):
    """Get a specific AAS asset by ID"""
    asset = await aas_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset

@app.post("/aas/assets/{asset_id}/submodels")
async def add_submodel(asset_id: str, submodel: SubmodelCreate):
    """Add a submodel to an existing asset"""
    return await aas_service.add_submodel(asset_id, submodel)

@app.post("/aas/import/aasx")
async def import_aasx(file: UploadFile = File(...)):
    """Import AASX package file"""
    if not file.filename.endswith('.aasx'):
        raise HTTPException(status_code=400, detail="File must be .aasx format")
    
    content = await file.read()
    return await aas_service.import_aasx(content)

@app.get("/aas/export/aasx/{asset_id}")
async def export_aasx(asset_id: str):
    """Export asset as AASX package"""
    aasx_content = await aas_service.export_aasx(asset_id)
    return FileResponse(
        content=aasx_content,
        filename=f"asset_{asset_id}.aasx",
        media_type="application/octet-stream"
    )
```

### AAS Service Implementation

```python
# backend/aas-service/services.py
import aas_core3 as aas
from aas_core3 import Asset, Submodel, SubmodelElement
from typing import List, Optional, Dict, Any
import json
import zipfile
import io

class AASService:
    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        self.submodels: Dict[str, Submodel] = {}
    
    async def create_asset(self, asset_data: AssetCreate) -> AssetResponse:
        """Create a new AAS asset"""
        asset_id = f"asset_{len(self.assets) + 1}"
        
        asset = Asset(
            id_short=asset_data.name,
            description=asset_data.description,
            id=aas.Identifier(
                id_type="IRI",
                value=f"https://qi-platform.com/assets/{asset_id}"
            ),
            kind=aas.AssetKind.INSTANCE
        )
        
        self.assets[asset_id] = asset
        return AssetResponse(
            id=asset_id,
            asset=asset,
            created_at=datetime.utcnow()
        )
    
    async def import_aasx(self, content: bytes) -> Dict[str, Any]:
        """Import AASX package"""
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                # Extract AASX content
                aasx_data = {}
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith('.json'):
                        with zip_file.open(file_info.filename) as f:
                            aasx_data[file_info.filename] = json.load(f)
                
                # Parse AAS assets
                imported_assets = []
                for filename, data in aasx_data.items():
                    if 'assetAdministrationShells' in data:
                        for aas_data in data['assetAdministrationShells']:
                            asset = self._parse_aas_data(aas_data)
                            imported_assets.append(asset)
                
                return {
                    "message": f"Imported {len(imported_assets)} assets",
                    "assets": imported_assets
                }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid AASX file: {str(e)}")
    
    async def export_aasx(self, asset_id: str) -> bytes:
        """Export asset as AASX package"""
        if asset_id not in self.assets:
            raise HTTPException(status_code=404, detail="Asset not found")
        
        asset = self.assets[asset_id]
        
        # Create AASX package
        aasx_data = {
            "assetAdministrationShells": [self._asset_to_dict(asset)],
            "submodels": [self._submodel_to_dict(sm) for sm in asset.submodels]
        }
        
        # Create ZIP file
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            zip_file.writestr('AAS.json', json.dumps(aasx_data, indent=2))
        
        return buffer.getvalue()
    
    def _parse_aas_data(self, aas_data: Dict[str, Any]) -> Asset:
        """Parse AAS data from JSON"""
        # Implementation for parsing AAS JSON data
        pass
    
    def _asset_to_dict(self, asset: Asset) -> Dict[str, Any]:
        """Convert Asset to dictionary"""
        # Implementation for converting Asset to JSON
        pass
```

## AAS Submodel Templates

### Quality Certificate Submodel

```json
{
  "idShort": "QualityCertificate",
  "description": "Quality certificate and compliance information",
  "id": {
    "idType": "IRI",
    "value": "https://qi-platform.com/submodels/quality-certificate"
  },
  "submodelElements": [
    {
      "idShort": "certificateType",
      "description": "Type of quality certificate",
      "value": "ISO9001",
      "valueType": "string"
    },
    {
      "idShort": "issuer",
      "description": "Certificate issuing authority",
      "value": "QI Authority",
      "valueType": "string"
    },
    {
      "idShort": "issuedDate",
      "description": "Certificate issue date",
      "value": "2024-01-15",
      "valueType": "date"
    },
    {
      "idShort": "expiryDate",
      "description": "Certificate expiry date",
      "value": "2025-01-15",
      "valueType": "date"
    },
    {
      "idShort": "standards",
      "description": "Applicable standards",
      "value": ["ISO9001", "AS9100"],
      "valueType": "array"
    }
  ]
}
```

### Manufacturing Process Submodel

```json
{
  "idShort": "ManufacturingProcess",
  "description": "Manufacturing process parameters and data",
  "id": {
    "idType": "IRI",
    "value": "https://qi-platform.com/submodels/manufacturing-process"
  },
  "submodelElements": [
    {
      "idShort": "processType",
      "description": "Type of manufacturing process",
      "value": "additive_manufacturing",
      "valueType": "string"
    },
    {
      "idShort": "parameters",
      "description": "Process parameters",
      "value": {
        "temperature": 200,
        "pressure": 1.2,
        "speed": 50
      },
      "valueType": "object"
    },
    {
      "idShort": "qualityMetrics",
      "description": "Quality measurement data",
      "value": {
        "tensile_strength": 450,
        "surface_roughness": 0.8,
        "dimensional_accuracy": 0.1
      },
      "valueType": "object"
    }
  ]
}
```

## AAS Integration Patterns

### 1. Asset Registration Pattern

```python
async def register_asset_with_aas(asset_data: Dict[str, Any]):
    """Register a new asset with AAS representation"""
    
    # Create AAS asset
    aas_asset = await aas_service.create_asset(asset_data)
    
    # Add quality certificate submodel
    certificate_submodel = QualityCertificateSubmodel(
        id_short="QualityCertificate",
        certificate_type="ISO9001",
        issuer="QI Authority",
        issued_date=datetime.utcnow(),
        expiry_date=datetime.utcnow() + timedelta(days=365),
        standards=["ISO9001", "AS9100"]
    )
    
    await aas_service.add_submodel(aas_asset.id, certificate_submodel)
    
    # Add manufacturing process submodel
    process_submodel = ManufacturingProcessSubmodel(
        id_short="ManufacturingProcess",
        process_type="additive_manufacturing",
        parameters=asset_data.get("parameters", {}),
        quality_metrics=asset_data.get("quality_metrics", {})
    )
    
    await aas_service.add_submodel(aas_asset.id, process_submodel)
    
    return aas_asset
```

### 2. AAS Validation Pattern

```python
async def validate_aas_asset(asset_id: str):
    """Validate AAS asset structure and data"""
    
    asset = await aas_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    validation_results = []
    
    # Validate required submodels
    required_submodels = ["QualityCertificate", "ManufacturingProcess"]
    for submodel_name in required_submodels:
        submodel = next(
            (sm for sm in asset.submodels if sm.id_short == submodel_name),
            None
        )
        if not submodel:
            validation_results.append({
                "type": "error",
                "message": f"Missing required submodel: {submodel_name}"
            })
    
    # Validate data quality
    for submodel in asset.submodels:
        for element in submodel.submodel_elements:
            if not element.value:
                validation_results.append({
                    "type": "warning",
                    "message": f"Empty value in {submodel.id_short}.{element.id_short}"
                })
    
    return {
        "asset_id": asset_id,
        "valid": len([r for r in validation_results if r["type"] == "error"]) == 0,
        "validation_results": validation_results
    }
```

### 3. AAS Export Pattern

```python
async def export_asset_for_analysis(asset_id: str):
    """Export AAS asset data for AI analysis"""
    
    asset = await aas_service.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Extract relevant data for AI analysis
    analysis_data = {
        "asset_id": asset_id,
        "asset_type": asset.id_short,
        "quality_data": {},
        "process_data": {},
        "sensor_data": {}
    }
    
    for submodel in asset.submodels:
        if submodel.id_short == "QualityCertificate":
            for element in submodel.submodel_elements:
                analysis_data["quality_data"][element.id_short] = element.value
        
        elif submodel.id_short == "ManufacturingProcess":
            for element in submodel.submodel_elements:
                analysis_data["process_data"][element.id_short] = element.value
        
        elif submodel.id_short == "SensorData":
            for element in submodel.submodel_elements:
                analysis_data["sensor_data"][element.id_short] = element.value
    
    return analysis_data
```

## AAS Integration with AI/RAG System

### AAS Document Processing

```python
# backend/ai-rag/services/aas_processor.py
from typing import List, Dict, Any
import json

class AASProcessor:
    """Process AAS data for AI/RAG system"""
    
    def process_aas_asset(self, asset_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert AAS asset to documents for vector storage"""
        
        documents = []
        
        # Create document from asset metadata
        asset_doc = {
            "content": f"Asset {asset_data['id_short']}: {asset_data.get('description', '')}",
            "metadata": {
                "type": "asset",
                "asset_id": asset_data.get('id', {}).get('value', ''),
                "asset_type": asset_data.get('kind', ''),
                "source": "aas"
            }
        }
        documents.append(asset_doc)
        
        # Process submodels
        for submodel in asset_data.get('submodels', []):
            submodel_doc = {
                "content": f"Submodel {submodel['id_short']}: {submodel.get('description', '')}",
                "metadata": {
                    "type": "submodel",
                    "submodel_type": submodel['id_short'],
                    "asset_id": asset_data.get('id', {}).get('value', ''),
                    "source": "aas"
                }
            }
            documents.append(submodel_doc)
            
            # Process submodel elements
            for element in submodel.get('submodel_elements', []):
                element_doc = {
                    "content": f"{element['id_short']}: {element.get('value', '')}",
                    "metadata": {
                        "type": "submodel_element",
                        "element_type": element['id_short'],
                        "submodel_type": submodel['id_short'],
                        "asset_id": asset_data.get('id', {}).get('value', ''),
                        "source": "aas"
                    }
                }
                documents.append(element_doc)
        
        return documents
```

## Testing AAS Integration

### Unit Tests

```python
# tests/test_aas_integration.py
import pytest
from fastapi.testclient import TestClient
from backend.aas_service.main import app

client = TestClient(app)

def test_create_aas_asset():
    """Test creating a new AAS asset"""
    asset_data = {
        "name": "Test Manufacturing Unit",
        "description": "Test asset for AAS integration",
        "type": "additive_manufacturing"
    }
    
    response = client.post("/aas/assets", json=asset_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["asset"]["id_short"] == "Test Manufacturing Unit"
    assert data["asset"]["kind"] == "Instance"

def test_import_aasx_file():
    """Test importing AASX file"""
    # Create test AASX file
    test_aasx_content = create_test_aasx()
    
    response = client.post(
        "/aas/import/aasx",
        files={"file": ("test.aasx", test_aasx_content, "application/octet-stream")}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "Imported" in data["message"]

def test_export_aasx_file():
    """Test exporting asset as AASX"""
    # First create an asset
    asset_data = {"name": "Export Test Asset", "description": "Test"}
    create_response = client.post("/aas/assets", json=asset_data)
    asset_id = create_response.json()["id"]
    
    # Export as AASX
    response = client.get(f"/aas/export/aasx/{asset_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
```

## Best Practices

### 1. AAS Design Principles

- **Modularity**: Use submodels for different aspects of the asset
- **Semantic Consistency**: Use standardized semantic IDs
- **Extensibility**: Design for future submodel additions
- **Validation**: Implement comprehensive validation rules

### 2. Performance Considerations

- **Caching**: Cache frequently accessed AAS data
- **Lazy Loading**: Load submodels on demand
- **Indexing**: Index AAS data for fast queries
- **Compression**: Compress AASX files for storage

### 3. Security

- **Access Control**: Implement role-based access to AAS data
- **Validation**: Validate all AAS input data
- **Audit Trail**: Log all AAS operations
- **Encryption**: Encrypt sensitive AAS data

## Integration with External Systems

### AASX Explorer Integration

```python
async def sync_with_aasx_explorer(asset_id: str):
    """Sync asset data with AASX Explorer"""
    
    # Export asset as AASX
    aasx_content = await aas_service.export_aasx(asset_id)
    
    # Save to shared directory for AASX Explorer
    explorer_path = "AasxPackageExplorer/content-for-demo/"
    filename = f"asset_{asset_id}.aasx"
    
    with open(f"{explorer_path}/{filename}", "wb") as f:
        f.write(aasx_content)
    
    return {"message": f"Asset exported to {filename}"}
```

### External AAS Systems

```python
async def integrate_external_aas(external_aas_url: str):
    """Integrate with external AAS systems"""
    
    # Fetch external AAS data
    async with httpx.AsyncClient() as client:
        response = await client.get(external_aas_url)
        external_aas_data = response.json()
    
    # Import external AAS assets
    imported_assets = []
    for asset_data in external_aas_data.get('assets', []):
        asset = await aas_service.import_external_asset(asset_data)
        imported_assets.append(asset)
    
    return {
        "message": f"Imported {len(imported_assets)} external assets",
        "assets": imported_assets
    }
```

This comprehensive AAS integration guide provides the foundation for implementing Asset Administrative Shell standards in your QI Digital Platform, ensuring interoperability and standardized digital twin representation. 