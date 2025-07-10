# Docker Framework Setup

This document explains how to run the complete AAS Data Modeling Framework using Docker.

## 🐳 Overview

The framework consists of multiple services, with Dockerfiles organized in the `docker/` folder:

- **Web Application** (Port 5000) - Main user interface
- **AI/RAG System** (Port 8000) - AI-powered analysis with GPT-4.1-mini
- **Twin Registry** (Port 8001) - Digital twin management
- **Certificate Manager** (Port 3001) - Certificate management
- **Analytics Dashboard** (Port 3002) - Quality infrastructure analytics
- **Neo4j** (Port 7474/7687) - Graph database
- **Qdrant** (Port 6333) - Vector database
- **PostgreSQL** (Port 5432) - Relational database
- **Redis** (Port 6379) - Caching

## 🚀 Quick Start

### Prerequisites

1. **Docker and Docker Compose** installed
2. **Environment file** (.env) configured

### Step 1: Configure Environment

Create a `.env` file in the project root:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Neo4j Configuration
NEO4J_URI=neo4j://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=Neo4j123

# Qdrant Configuration
QDRANT_URL=http://qdrant:6333

# Database Configuration
DATABASE_URL=postgresql://aasx_user:aasx_password@postgres:5432/aasx_data
REDIS_URL=redis://redis:6379

# Application Configuration
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here
```

### Step 2: Build and Run

```bash
# Make the script executable
chmod +x scripts/build_framework.sh

# Build and run the complete framework
./scripts/build_framework.sh
```

Or manually:

```bash
# Build all images (Dockerfiles are in docker/ folder)
docker-compose -f docker-compose.framework.yml build

# Start all services
docker-compose -f docker-compose.framework.yml up -d
```

### Step 3: Access Services

Once running, access the services at:

- **Web Application**: http://localhost:5000
- **AI/RAG API**: http://localhost:8000
- **Twin Registry**: http://localhost:8001
- **Certificate Manager**: http://localhost:3001
- **Analytics Dashboard**: http://localhost:3002
- **Neo4j Browser**: http://localhost:7474
- **Qdrant Dashboard**: http://localhost:6333

## 🔧 Management Commands

### View Service Status
```bash
docker-compose -f docker-compose.framework.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.framework.yml logs -f

# Specific service
docker-compose -f docker-compose.framework.yml logs -f ai-rag-system
```

### Stop Services
```bash
docker-compose -f docker-compose.framework.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.framework.yml restart
```

### Update and Rebuild
```bash
# Pull latest changes and rebuild
git pull
docker-compose -f docker-compose.framework.yml down
docker-compose -f docker-compose.framework.yml build --no-cache
docker-compose -f docker-compose.framework.yml up -d
```

## 📁 Volume Persistence

The following data is persisted in Docker volumes:

- **Neo4j Data**: `neo4j-data`
- **Qdrant Data**: `qdrant-data`
- **PostgreSQL Data**: `postgres-data`
- **Redis Data**: `redis-data`

## 🔍 Troubleshooting

### Service Not Starting
```bash
# Check logs
docker-compose -f docker-compose.framework.yml logs [service-name]

# Check resource usage
docker stats
```

### Port Conflicts
If ports are already in use, modify the port mappings in `docker-compose.framework.yml`.

### Memory Issues
Increase Docker memory allocation in Docker Desktop settings.

### Database Connection Issues
```bash
# Check database connectivity
docker-compose -f docker-compose.framework.yml exec postgres psql -U aasx_user -d aasx_data
```

## 🧪 Testing

After deployment, test the framework:

```bash
# Test AI/RAG system
curl http://localhost:8000/health

# Test web application
curl http://localhost:5000/health

# Test Neo4j connection
curl -u neo4j:Neo4j123 http://localhost:7474/db/data/
```

## 📊 Monitoring

### Health Checks
All services include health checks that can be monitored via:

```bash
docker-compose -f docker-compose.framework.yml ps
```

### Resource Monitoring
```bash
# Monitor resource usage
docker stats

# Monitor logs
docker-compose -f docker-compose.framework.yml logs -f --tail=100
```

## 🔒 Security Notes

1. **Change default passwords** in production
2. **Use secrets management** for sensitive data
3. **Enable SSL/TLS** for production deployments
4. **Restrict network access** as needed
5. **Regular security updates** for base images

## 🚀 Production Deployment

For production deployment:

1. **Use production images** (remove `--reload` flags)
2. **Configure proper logging** (JSON format, log rotation)
3. **Set up monitoring** (Prometheus, Grafana)
4. **Configure backups** for persistent data
5. **Use reverse proxy** (nginx, traefik)
6. **Enable SSL/TLS** certificates
7. **Set resource limits** for containers 