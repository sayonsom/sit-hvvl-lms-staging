#!/bin/zsh

###############################################################################
# Quick Start Script - Simplified LTI Development Startup
# For first-time setup without ngrok static domain
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "${BLUE}════════════════════════════════════════════════════${NC}"
echo "${BLUE}  LTI Development Environment - Quick Start${NC}"
echo "${BLUE}════════════════════════════════════════════════════${NC}"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$SCRIPT_DIR}"
BACKEND_DIR="$PROJECT_ROOT/backend-lti"
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

port_in_use() {
  local port="$1"
  if command -v lsof &> /dev/null; then
    lsof -tiTCP:"$port" -sTCP:LISTEN > /dev/null 2>&1
    return $?
  fi
  if command -v nc &> /dev/null; then
    nc -z localhost "$port" > /dev/null 2>&1
    return $?
  fi
  return 1
}

assert_port_available() {
  local port="$1"
  local name="$2"
  if port_in_use "$port"; then
    echo "${RED}✗ ${name} port ${port} is already in use.${NC}"
    if command -v lsof &> /dev/null; then
      lsof -nP -iTCP:"$port" -sTCP:LISTEN || true
    fi
    exit 1
  fi
}

###############################################################################
# Step 1: Check Prerequisites
###############################################################################

echo "${BLUE}[1/4] Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo "${RED}✗ Docker not found. Please install Docker Desktop.${NC}"
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo "${RED}✗ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "${RED}✗ Python3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "${RED}✗ npm not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo "${GREEN}✓ All prerequisites met${NC}"

# Choose Python interpreter (prefer 3.12 for compatibility)
PY_BIN=$(command -v python3.12 || command -v python3)
if [ -z "$PY_BIN" ]; then
    echo "${RED}✗ No suitable Python found (need python3.12 or python3)${NC}"
    exit 1
fi

###############################################################################
# Step 2: Start Services
###############################################################################

echo ""
echo "${BLUE}[2/4] Starting services...${NC}"

# Start Redis
echo "  Starting Redis..."
if ! docker ps | grep -q redis-lti-dev; then
    if docker ps -a | grep -q redis-lti-dev; then
        docker start redis-lti-dev > /dev/null 2>&1
    else
        docker run -d --name redis-lti-dev -p 6379:6379 redis:7-alpine > /dev/null 2>&1
    fi
fi
sleep 2
echo "${GREEN}  ✓ Redis started${NC}"

# Start Backend
echo "  Starting Backend..."
cd "$BACKEND_DIR"

if ! curl -s "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
  assert_port_available "$BACKEND_PORT" "Backend"
fi

if [ ! -d "venv" ]; then
    "$PY_BIN" -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip > /dev/null 2>&1
pip install -q -r requirements.txt > /dev/null 2>&1

# Start backend in background
nohup uvicorn app.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$LOG_DIR/backend.pid"

# Wait for backend
for i in {1..30}; do
    if curl -s "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
        echo "${GREEN}  ✓ Backend started (PID: $BACKEND_PID)${NC}"
        break
    fi
    sleep 1
done

# Prepare Frontend Environment
cd "$PROJECT_ROOT"
ENV_FILE="$PROJECT_ROOT/.env.local"

# Ensure .env.local exists
if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$PROJECT_ROOT/.env.local.example" ]; then
        cp "$PROJECT_ROOT/.env.local.example" "$ENV_FILE"
    else
        touch "$ENV_FILE"
    fi
fi

# Helper to upsert key=value in .env.local
upsert_env_var() {
    local key="$1"; shift
    local value="$1"
    if grep -q "^${key}=" "$ENV_FILE"; then
        sed -i.bak "s|^${key}=.*|${key}=${value}|g" "$ENV_FILE"
    else
        echo "${key}=${value}" >> "$ENV_FILE"
    fi
}

# Set API endpoints for local testing
upsert_env_var REACT_APP_API_URL "http://localhost:8080"
upsert_env_var REACT_APP_LTI_API_URL "http://localhost:$BACKEND_PORT"

echo "${GREEN}  ✓ Configured .env.local for frontend${NC}"

# Start Frontend
echo "  Starting Frontend..."
if ! curl -s "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
  assert_port_available "$FRONTEND_PORT" "Frontend"
fi
if [ ! -d "node_modules" ]; then
    npm ci > "$LOG_DIR/frontend-install.log" 2>&1
fi

nohup env PORT="$FRONTEND_PORT" BROWSER=none npm start > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"

# Wait for frontend
for i in {1..60}; do
    if curl -s "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
        echo "${GREEN}  ✓ Frontend started (PID: $FRONTEND_PID)${NC}"
        break
    fi
    sleep 1
done

###############################################################################
# Step 3: Setup ngrok
###############################################################################

echo ""
echo "${BLUE}[3/4] Setting up ngrok...${NC}"
echo ""
echo "${YELLOW}You need an ngrok account to expose your local server.${NC}"
echo ""
echo "Options:"
echo "  1. I have ngrok configured with a static domain"
echo "  2. I have ngrok but no static domain (will use random URL)"
echo "  3. I don't have ngrok yet (skip for now)"
echo ""
echo -n "Choose option (1/2/3): "
read NGROK_OPTION

if [ "$NGROK_OPTION" = "1" ]; then
    echo ""
    echo -n "Enter your ngrok static domain (e.g., my-app.ngrok-free.app): "
    read NGROK_DOMAIN
    
    nohup ngrok http "$BACKEND_PORT" --domain=$NGROK_DOMAIN > "$LOG_DIR/ngrok.log" 2>&1 &
    NGROK_PID=$!
    echo $NGROK_PID > "$LOG_DIR/ngrok.pid"
    sleep 3
    
    NGROK_URL="https://$NGROK_DOMAIN"
    
elif [ "$NGROK_OPTION" = "2" ]; then
    nohup ngrok http "$BACKEND_PORT" > "$LOG_DIR/ngrok.log" 2>&1 &
    NGROK_PID=$!
    echo $NGROK_PID > "$LOG_DIR/ngrok.pid"
    sleep 3
    
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)
    
else
    echo "${YELLOW}Skipping ngrok. You can start it manually later.${NC}"
    NGROK_URL="(not started)"
fi

if [ "$NGROK_URL" != "(not started)" ] && [ -n "$NGROK_URL" ]; then
    echo "${GREEN}✓ ngrok started${NC}"
    echo "  Public URL: ${GREEN}$NGROK_URL${NC}"
    
    # Update .env.local with ngrok URL
    if [ -f "$PROJECT_ROOT/.env.local" ]; then
        sed -i.bak "s|REACT_APP_LTI_API_URL=.*|REACT_APP_LTI_API_URL=$NGROK_URL|g" "$PROJECT_ROOT/.env.local"
        echo "${GREEN}✓ Updated .env.local with ngrok URL${NC}"
        echo "${YELLOW}  Note: Restart frontend for changes to take effect${NC}"
    fi
fi

###############################################################################
# Step 4: Summary
###############################################################################

echo ""
echo "${BLUE}[4/4] Summary${NC}"
echo ""
echo "${GREEN}════════════════════════════════════════════════════${NC}"
echo "${GREEN}  ✓ All Services Running!${NC}"
echo "${GREEN}════════════════════════════════════════════════════${NC}"
echo ""
echo "Access your app:"
echo "  Frontend:     ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo "  LTI Backend:  ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo "  Backend Docs: ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"

# Show configured frontend API endpoints
ENV_FILE="$PROJECT_ROOT/.env.local"
API_URL=$(grep -E '^REACT_APP_API_URL=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
LTI_URL=$(grep -E '^REACT_APP_LTI_API_URL=' "$ENV_FILE" 2>/dev/null | cut -d'=' -f2-)
if [ -n "$API_URL" ]; then
  echo "  Frontend API URL:    ${GREEN}$API_URL${NC}"
fi
if [ -n "$LTI_URL" ]; then
  echo "  Frontend LTI API URL: ${GREEN}$LTI_URL${NC}"
fi

if [ "$NGROK_URL" != "(not started)" ] && [ -n "$NGROK_URL" ]; then
    echo "  ngrok URL:    ${GREEN}$NGROK_URL${NC}"
    echo "  ngrok UI:     ${GREEN}http://localhost:4040${NC}"
fi

echo ""
echo "View logs:"
echo "  Backend:  tail -f logs/backend.log"
echo "  Frontend: tail -f logs/frontend.log"
if [ "$NGROK_URL" != "(not started)" ]; then
    echo "  ngrok:    tail -f logs/ngrok.log"
fi

echo ""
echo "${YELLOW}Next Steps:${NC}"
if [ "$NGROK_URL" != "(not started)" ] && [ -n "$NGROK_URL" ]; then
    echo "  1. ${GREEN}Restart frontend${NC} to use ngrok URL:"
    echo "     ${BLUE}kill $FRONTEND_PID && npm start${NC}"
    echo "  2. Register tool in Brightspace with: ${GREEN}$NGROK_URL${NC}"
    echo "  3. Follow TESTING_GUIDE.md"
else
    echo "  1. Get ngrok account at: https://ngrok.com"
    echo "  2. Run: ngrok http $BACKEND_PORT"
    echo "  3. Update .env.local with ngrok URL"
    echo "  4. Follow TESTING_GUIDE.md"
fi

echo ""
echo "${YELLOW}To stop all services:${NC}"
echo "  ./stop-lti-dev.sh"
echo ""
echo "${BLUE}PIDs saved to logs/ directory for clean shutdown${NC}"
echo ""
