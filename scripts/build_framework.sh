#!/bin/bash

# Build and Run Complete AAS Framework
echo "🚀 Building and Running Complete AAS Framework..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your configuration."
    exit 1
fi

# Build all Docker images
echo "📦 Building Docker images..."
docker-compose -f docker-compose.framework.yml build

# Start all services
echo "🚀 Starting all services..."
docker-compose -f docker-compose.framework.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "📊 Service Status:"
docker-compose -f docker-compose.framework.yml ps

# Show access URLs
echo ""
echo "🌐 Access URLs:"
echo "   Web Application:     http://localhost:5000"
echo "   AI/RAG API:          http://localhost:8000"
echo "   Twin Registry:       http://localhost:8001"
echo "   Certificate Manager: http://localhost:3001"
echo "   Analytics Dashboard: http://localhost:3002"
echo "   Neo4j Browser:       http://localhost:7474"
echo "   Qdrant Dashboard:    http://localhost:6333"

echo ""
echo "✅ Framework is ready!"
echo "Use 'docker-compose -f docker-compose.framework.yml logs -f' to view logs"
echo "Use 'docker-compose -f docker-compose.framework.yml down' to stop services" 