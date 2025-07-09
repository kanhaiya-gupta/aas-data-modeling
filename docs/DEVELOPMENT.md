# Development Guide

## Overview

This guide is for developers contributing to the QI Digital Platform.

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git
- Conda (recommended)
- VS Code (recommended)

### Initial Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd aas-data-modeling
   ```

2. **Create Environment**
   ```bash
   conda create -n qi-digital-platform python=3.11 -y
   conda activate qi-digital-platform
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r webapp/requirements.txt
   ```

4. **Install Node.js Dependencies**
   ```bash
   cd backend/certificate-manager && npm install
   cd ../qi-analytics && npm install
   ```

## Project Structure

```
aas-data-modeling/
├── backend/                    # Backend services
│   ├── ai-rag/                # AI/RAG System (FastAPI)
│   ├── twin-registry/         # Digital Twin Registry (FastAPI)
│   ├── certificate-manager/   # Certificate Manager (Node.js)
│   ├── qi-analytics/          # Analytics Dashboard (Node.js)
│   └── shared/                # Shared utilities
├── webapp/                    # Frontend application (Flask)
│   ├── static/               # CSS, JS, images
│   ├── templates/            # HTML templates
│   ├── config/               # Configuration files
│   └── app.py               # Flask web application
├── docs/                     # Documentation
├── main.py                   # Main orchestrator
└── requirements.txt          # Backend dependencies
```

## Development Workflow

### 1. Starting Development

```bash
# Start all services
python main.py start

# Or start individual services
cd backend/ai-rag && uvicorn main:app --reload --port 8000
cd backend/twin-registry && uvicorn main:app --reload --port 8001
cd backend/certificate-manager && npm run dev
cd backend/qi-analytics && npm run dev
cd webapp && flask run --port 5000
```

### 2. Code Style

#### Python
- Use Black for formatting: `black .`
- Use Flake8 for linting: `flake8 .`
- Use MyPy for type checking: `mypy .`

#### JavaScript/Node.js
- Use Prettier for formatting: `npx prettier --write .`
- Use ESLint for linting: `npx eslint .`

### 3. Testing

#### Python Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest backend/ai-rag/tests/

# Run with coverage
pytest --cov=backend
```

#### Node.js Tests
```bash
# Certificate Manager tests
cd backend/certificate-manager && npm test

# Analytics tests
cd backend/qi-analytics && npm test
```

### 4. Database Development

```bash
# Create migrations
cd webapp && flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Reset database
flask db downgrade base
flask db upgrade
```

## Backend Development

### AI/RAG System (FastAPI)

**Location**: `backend/ai-rag/`

**Key Files**:
- `main.py` - FastAPI application
- `models.py` - Pydantic models
- `services/` - Business logic
- `api/` - API routes

**Development**:
```bash
cd backend/ai-rag
uvicorn main:app --reload --port 8000
```

**API Documentation**: http://localhost:8000/docs

### Digital Twin Registry (FastAPI)

**Location**: `backend/twin-registry/`

**Key Files**:
- `main.py` - FastAPI application
- `models.py` - Twin models
- `database.py` - Database operations
- `api/` - API routes

**Development**:
```bash
cd backend/twin-registry
uvicorn main:app --reload --port 8001
```

### Certificate Manager (Node.js)

**Location**: `backend/certificate-manager/`

**Key Files**:
- `src/server.js` - Express server
- `public/` - Static files
- `package.json` - Dependencies

**Development**:
```bash
cd backend/certificate-manager
npm run dev
```

### Analytics Dashboard (Node.js)

**Location**: `backend/qi-analytics/`

**Key Files**:
- `src/server.js` - Express server
- `public/` - Static files
- `package.json` - Dependencies

**Development**:
```bash
cd backend/qi-analytics
npm run dev
```

## Frontend Development

### Flask Webapp

**Location**: `webapp/`

**Key Files**:
- `app.py` - Flask application
- `templates/` - HTML templates
- `static/` - CSS, JS, images
- `config/` - Configuration

**Development**:
```bash
cd webapp
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port 5000
```

### Template Structure

- `base.html` - Base template with navigation
- `index.html` - Homepage
- `dashboard.html` - Analytics dashboard
- `certificates.html` - Certificate management
- `twins.html` - Digital twins view

### Static Assets

- `static/css/style.css` - Main stylesheet
- `static/js/main.js` - Main JavaScript
- `static/images/` - Images and icons

## API Development

### Adding New Endpoints

1. **FastAPI (Python)**
   ```python
   from fastapi import APIRouter, HTTPException
   from pydantic import BaseModel
   
   router = APIRouter()
   
   class NewModel(BaseModel):
       name: str
       description: str
   
   @router.post("/new-endpoint")
   async def create_item(item: NewModel):
       # Implementation
       return {"message": "Created", "item": item}
   ```

2. **Express (Node.js)**
   ```javascript
   const express = require('express');
   const router = express.Router();
   
   router.post('/new-endpoint', async (req, res) => {
       try {
           // Implementation
           res.json({ message: 'Created', item: req.body });
       } catch (error) {
           res.status(500).json({ error: error.message });
       }
   });
   ```

### Error Handling

```python
# FastAPI
from fastapi import HTTPException

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]
```

```javascript
// Express
app.use((error, req, res, next) => {
    console.error(error.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});
```

## Database Development

### Models

**SQLAlchemy Models**:
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DigitalTwin(Base):
    __tablename__ = "digital_twins"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    created_at = Column(DateTime)
```

**Pydantic Models**:
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DigitalTwinCreate(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class DigitalTwin(DigitalTwinCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Migrations

```bash
# Create migration
flask db migrate -m "Add digital twins table"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## Testing

### Unit Tests

**Python Tests**:
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_digital_twin():
    response = client.post(
        "/api/twins",
        json={"name": "Test Twin", "type": "additive_manufacturing"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Twin"
```

**Node.js Tests**:
```javascript
const request = require('supertest');
const app = require('../src/server');

describe('Certificate API', () => {
    test('GET /api/certificates', async () => {
        const response = await request(app)
            .get('/api/certificates')
            .expect(200);
        
        expect(Array.isArray(response.body)).toBe(true);
    });
});
```

### Integration Tests

```python
# Test database integration
def test_database_connection():
    from database import get_db
    db = next(get_db())
    assert db is not None
```

## Debugging

### Python Debugging

```python
import logging
import pdb

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Add breakpoint
pdb.set_trace()

# Or use breakpoint() (Python 3.7+)
breakpoint()
```

### Node.js Debugging

```javascript
// Add debug logging
console.log('Debug:', variable);

// Use debugger
debugger;

// Use Node.js inspector
// node --inspect src/server.js
```

### VS Code Debugging

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": ["main:app", "--reload", "--port", "8000"],
            "cwd": "${workspaceFolder}/backend/ai-rag"
        },
        {
            "name": "Node.js: Certificate Manager",
            "type": "node",
            "request": "launch",
            "program": "${workspaceFolder}/backend/certificate-manager/src/server.js",
            "cwd": "${workspaceFolder}/backend/certificate-manager"
        }
    ]
}
```

## Performance Optimization

### Python Optimization

1. **Async/Await**
   ```python
   async def get_items():
       return await db.fetch_all("SELECT * FROM items")
   ```

2. **Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def expensive_operation(data):
       # Expensive computation
       pass
   ```

3. **Database Optimization**
   ```python
   # Use indexes
   # Optimize queries
   # Use connection pooling
   ```

### Node.js Optimization

1. **Async Operations**
   ```javascript
   async function getItems() {
       return await db.query('SELECT * FROM items');
   }
   ```

2. **Caching**
   ```javascript
   const NodeCache = require('node-cache');
   const cache = new NodeCache({ stdTTL: 600 });
   
   function getCachedData(key) {
       let data = cache.get(key);
       if (!data) {
           data = fetchData();
           cache.set(key, data);
       }
       return data;
   }
   ```

## Security Best Practices

### Input Validation

```python
# FastAPI with Pydantic
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    name: str
    email: str
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email')
        return v
```

### Authentication

```python
# JWT Authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    # Validate JWT token
    pass
```

### Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/query")
@limiter.limit("10/minute")
async def query_ai(request: Request):
    # Implementation
    pass
```

## Deployment Preparation

### Environment Variables

```bash
# Development
export FLASK_ENV=development
export DATABASE_URL=postgresql://localhost/qi_dev

# Production
export FLASK_ENV=production
export DATABASE_URL=postgresql://prod-host/qi_prod
```

### Docker Development

```dockerfile
# Development Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py", "start"]
```

## Contributing Guidelines

### Code Review Process

1. Create feature branch
2. Make changes
3. Add tests
4. Update documentation
5. Submit pull request
6. Code review
7. Merge to main

### Commit Messages

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Express.js Documentation](https://expressjs.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/) 