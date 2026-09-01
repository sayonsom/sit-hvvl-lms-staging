#!/bin/bash

echo "=================================================="
echo "  Starting Align Backend (Local Environment)"
echo "=================================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start the services using docker-compose
echo "🚀 Starting PostgreSQL and FastAPI services..."
docker-compose -f docker-compose.local.yml up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
echo ""

# Wait for PostgreSQL
POSTGRES_READY=false
for i in {1..30}; do
    if docker exec alignbackendapis-postgres-1 pg_isready -U alignuser -d aligndb > /dev/null 2>&1; then
        POSTGRES_READY=true
        break
    fi
    echo "   Waiting for PostgreSQL... ($i/30)"
    sleep 2
done

if [ "$POSTGRES_READY" = true ]; then
    echo "✅ PostgreSQL is ready!"
else
    echo "❌ PostgreSQL failed to start within 60 seconds"
    exit 1
fi

# Wait for FastAPI
echo ""
FASTAPI_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1 || curl -s http://localhost:8080/docs > /dev/null 2>&1; then
        FASTAPI_READY=true
        break
    fi
    echo "   Waiting for FastAPI... ($i/30)"
    sleep 2
done

if [ "$FASTAPI_READY" = true ]; then
    echo "✅ FastAPI is ready!"
else
    echo "⚠️  FastAPI might still be starting up..."
fi

echo ""
echo "=================================================="
echo "✅ Services are running!"
echo "=================================================="
echo ""
echo "📊 Database:"
echo "   PostgreSQL: postgresql://alignuser:local-dev-password-change-me@localhost:5432/aligndb"
echo ""
echo "🌐 API:"
echo "   FastAPI Docs: http://localhost:8080/docs"
echo "   API Base URL: http://localhost:8080"
echo ""
echo "📋 Useful commands:"
echo "   View logs:        docker-compose -f docker-compose.local.yml logs -f"
echo "   Stop services:    docker-compose -f docker-compose.local.yml down"
echo "   Restart services: docker-compose -f docker-compose.local.yml restart"
echo ""
