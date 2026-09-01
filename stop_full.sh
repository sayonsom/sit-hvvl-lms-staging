#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────
# SIT Virtual HV Laboratory — Stop All Services
# ─────────────────────────────────────────────────────────

cd "$(dirname "$0")"

COMPOSE_FILE="docker-compose.local.yml"

# Detect compose command
if docker compose version > /dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
  COMPOSE_CMD="docker-compose"
else
  echo "❌ Docker Compose not found."
  exit 1
fi

echo ""
echo "Stopping all services..."
$COMPOSE_CMD -f "$COMPOSE_FILE" down
echo ""
echo "✅ All services stopped."
echo ""
echo "Note: Database and Redis data are preserved in Docker volumes."
echo "To remove all data and start fresh:"
echo "  $COMPOSE_CMD -f $COMPOSE_FILE down -v"
echo ""
