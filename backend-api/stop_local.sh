#!/bin/bash

echo "=================================================="
echo "  Stopping Align Backend (Local Environment)"
echo "=================================================="
echo ""

# Stop the services
echo "🛑 Stopping PostgreSQL and FastAPI services..."
docker-compose -f docker-compose.local.yml down

echo ""
echo "✅ Services stopped!"
echo ""
echo "💡 Tip: Data is preserved in Docker volumes."
echo "   To remove data volumes, run:"
echo "   docker-compose -f docker-compose.local.yml down -v"
echo ""
