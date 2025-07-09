# API Documentation

## Overview

The QI Digital Platform provides several REST APIs for managing digital twins, certificates, and analytics.

## Base URLs

- **AI/RAG System**: `http://localhost:8000`
- **Digital Twin Registry**: `http://localhost:8001`
- **Certificate Manager**: `http://localhost:3001`
- **Analytics Dashboard**: `http://localhost:3002`
- **Webapp**: `http://localhost:5000`

## AI/RAG System API

### Base URL: `http://localhost:8000`

#### Health Check
```http
GET /health
```

#### Query AI System
```http
POST /api/query
Content-Type: application/json

{
  "query": "What are the quality standards for additive manufacturing?",
  "context": "additive_manufacturing"
}
```

#### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: [document file]
metadata: {
  "title": "Quality Standards Document",
  "category": "additive_manufacturing",
  "tags": ["quality", "standards", "3d-printing"]
}
```

#### Search Documents
```http
GET /api/search?q=quality+standards&category=additive_manufacturing
```

## Digital Twin Registry API

### Base URL: `http://localhost:8001`

#### Health Check
```http
GET /health
```

#### List Digital Twins
```http
GET /api/twins
```

#### Get Digital Twin
```http
GET /api/twins/{twin_id}
```

#### Create Digital Twin
```http
POST /api/twins
Content-Type: application/json

{
  "name": "Additive Manufacturing Unit #1",
  "type": "additive_manufacturing",
  "description": "3D printing facility for aerospace components",
  "location": "Building A, Floor 2",
  "metadata": {
    "manufacturer": "Stratasys",
    "model": "F900",
    "serial_number": "AMU-001-2024"
  }
}
```

#### Update Digital Twin
```http
PUT /api/twins/{twin_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "status": "active"
}
```

#### Delete Digital Twin
```http
DELETE /api/twins/{twin_id}
```

## Certificate Manager API

### Base URL: `http://localhost:3001`

#### Health Check
```http
GET /health
```

#### List Certificates
```http
GET /api/certificates
```

#### Get Certificate
```http
GET /api/certificates/{certificate_id}
```

#### Create Certificate
```http
POST /api/certificates
Content-Type: application/json

{
  "name": "Quality Certificate - Additive Manufacturing",
  "type": "quality_certificate",
  "digitalTwinId": "dt-001",
  "issuer": "QI Authority",
  "issuedDate": "2024-01-15",
  "expiryDate": "2025-01-15",
  "metadata": {
    "standards": ["ISO 9001", "AS9100"],
    "scope": "Additive manufacturing processes"
  }
}
```

#### Update Certificate
```http
PUT /api/certificates/{certificate_id}
Content-Type: application/json

{
  "status": "active",
  "metadata": {
    "lastAudit": "2024-06-15"
  }
}
```

## Analytics Dashboard API

### Base URL: `http://localhost:3002`

#### Health Check
```http
GET /health
```

#### Get Overview
```http
GET /api/analytics/overview
```

#### Get Trends
```http
GET /api/analytics/trends
```

#### Get Alerts
```http
GET /api/analytics/alerts
```

## Authentication

Currently, the APIs are running in development mode without authentication. For production deployment, implement proper authentication using:

- JWT tokens
- API keys
- OAuth 2.0

## Error Handling

All APIs return consistent error responses:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

APIs implement rate limiting to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## CORS

All APIs support CORS for web application integration.

## Examples

### Python Client Example

```python
import requests

# Query AI system
response = requests.post('http://localhost:8000/api/query', json={
    'query': 'What are the quality standards?',
    'context': 'additive_manufacturing'
})
print(response.json())

# Create digital twin
response = requests.post('http://localhost:8001/api/twins', json={
    'name': 'Test Twin',
    'type': 'additive_manufacturing'
})
print(response.json())
```

### JavaScript Client Example

```javascript
// Query AI system
const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        query: 'What are the quality standards?',
        context: 'additive_manufacturing'
    })
});
const data = await response.json();
console.log(data);
```

## Interactive Documentation

Visit the interactive API documentation at:
- AI/RAG System: http://localhost:8000/docs
- Digital Twin Registry: http://localhost:8001/docs 