#!/bin/zsh

###############################################################################
# LTI Development Environment Startup Script
# This script starts all required services for local LTI development
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$SCRIPT_DIR}"
BACKEND_DIR="$PROJECT_ROOT/backend-lti"
REDIS_CONTAINER_NAME="redis-lti-dev"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
PYTHON_BIN="${PYTHON_BIN:-}"

if [ -z "$PYTHON_BIN" ]; then
    # Prefer a stable Python version for backend dependencies (pydantic wheels may not exist yet for bleeding-edge Python).
    if command -v python3.11 &> /dev/null; then
        PYTHON_BIN="python3.11"
    elif command -v python3.12 &> /dev/null; then
        PYTHON_BIN="python3.12"
    elif command -v python3.13 &> /dev/null; then
        PYTHON_BIN="python3.13"
    else
        PYTHON_BIN="python3"
    fi
fi

# Log files
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"
REDIS_LOG="$LOG_DIR/redis.log"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_INSTALL_LOG="$LOG_DIR/backend-install.log"
FRONTEND_INSTALL_LOG="$LOG_DIR/frontend-install.log"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo "${BLUE}  $1${NC}"
    echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_success() {
    echo "${GREEN}✓${NC} $1"
}

print_error() {
    echo "${RED}✗${NC} $1"
}

print_warning() {
    echo "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo "${BLUE}ℹ${NC} $1"
}

is_interactive() {
    [ -t 0 ] && [ -t 1 ]
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

get_listen_pids() {
    local port="$1"
    if command -v lsof &> /dev/null; then
        lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null || true
        return 0
    fi
    if command -v nc &> /dev/null; then
        if nc -z localhost "$port" > /dev/null 2>&1; then
            echo "unknown"
        fi
        return 0
    fi
    return 0
}

assert_port_available() {
    local port="$1"
    local name="$2"
    local var_name="$3"

    local listen_pids
    listen_pids="$(get_listen_pids "$port")"
    if [ -n "$listen_pids" ]; then
        print_error "$name port $port is already in use."
        if command -v lsof &> /dev/null; then
            lsof -nP -iTCP:"$port" -sTCP:LISTEN || true
        fi
        print_info "Stop the existing process (or run ./stop-lti-dev.sh), then retry."
        if [ -n "$var_name" ]; then
            local next_port=$((port + 1))
            print_info "Or override the port: ${var_name}=${next_port} ./start-lti-dev.sh"
        fi
        exit 1
    fi
}

###############################################################################
# Pre-flight Checks
###############################################################################

print_header "Pre-flight Checks"

# Check required commands
print_info "Checking required tools..."
check_command docker
check_command "$PYTHON_BIN"
check_command npm
check_command ngrok
print_success "All required tools are installed"
print_info "Using Python for backend venv: $PYTHON_BIN"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop."
    exit 1
fi
print_success "Docker is running"

# Check if project directories exist
if [ ! -d "$PROJECT_ROOT" ]; then
    print_error "Project root not found: $PROJECT_ROOT"
    exit 1
fi

if [ ! -d "$BACKEND_DIR" ]; then
    print_error "Backend directory not found: $BACKEND_DIR"
    exit 1
fi
print_success "Project directories verified"

###############################################################################
# Configuration Check
###############################################################################

print_header "Configuration Check"

# Check backend .env
if [ ! -f "$BACKEND_DIR/.env" ]; then
    print_warning "Backend .env not found. Creating from template..."
    if [ -f "$BACKEND_DIR/.env.example" ]; then
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        if is_interactive; then
            print_error "Please edit $BACKEND_DIR/.env with your ngrok domain and press Enter to continue..."
            read
        else
            print_warning "Created $BACKEND_DIR/.env from template (non-interactive mode: skipping prompt)."
        fi
    else
        print_error "No .env.example found in backend directory"
        exit 1
    fi
else
    print_success "Backend .env exists"
fi

# Check frontend .env.local
if [ ! -f "$PROJECT_ROOT/.env.local" ]; then
    print_warning "Frontend .env.local not found. Creating from template..."
    if [ -f "$PROJECT_ROOT/.env.local.example" ]; then
        cp "$PROJECT_ROOT/.env.local.example" "$PROJECT_ROOT/.env.local"
        if is_interactive; then
            print_error "Please edit $PROJECT_ROOT/.env.local with your configuration and press Enter to continue..."
            read
        else
            print_warning "Created $PROJECT_ROOT/.env.local from template (non-interactive mode: skipping prompt)."
        fi
    else
        print_error "No .env.local.example found"
        exit 1
    fi
else
    print_success "Frontend .env.local exists"
fi

# Extract ngrok domain from backend .env
NGROK_DOMAIN=$(grep "^TOOL_URL=" "$BACKEND_DIR/.env" | cut -d '=' -f2 | sed 's/https:\/\///' | sed 's/http:\/\///')
if [ -z "$NGROK_DOMAIN" ] || [[ "$NGROK_DOMAIN" == *"your-"* ]] || [[ "$NGROK_DOMAIN" == *"example"* ]]; then
    print_warning "Ngrok domain not properly configured in $BACKEND_DIR/.env"
    print_info "Current value: $NGROK_DOMAIN"
    if is_interactive; then
        echo -n "Enter your ngrok static domain (e.g., your-domain.ngrok-free.app): "
        read USER_NGROK_DOMAIN
        if [ -n "$USER_NGROK_DOMAIN" ]; then
            NGROK_DOMAIN="$USER_NGROK_DOMAIN"
            # Update .env file
            sed -i.bak "s|^TOOL_URL=.*|TOOL_URL=https://$NGROK_DOMAIN|g" "$BACKEND_DIR/.env"
            print_success "Updated TOOL_URL in .env"
        fi
    else
        print_warning "Non-interactive mode: starting ngrok without a static domain."
    fi
fi

print_info "Ngrok domain: $NGROK_DOMAIN"

# Ensure backend redirects back to the correct local frontend port (only if configured for localhost).
DESIRED_FRONTEND_URL="http://localhost:$FRONTEND_PORT"
CURRENT_FRONTEND_URL="$(grep "^FRONTEND_URL=" "$BACKEND_DIR/.env" 2>/dev/null | head -n 1 | cut -d '=' -f2- || true)"
if [ -z "$CURRENT_FRONTEND_URL" ] || [[ "$CURRENT_FRONTEND_URL" == http://localhost:* ]] || [[ "$CURRENT_FRONTEND_URL" == http://127.0.0.1:* ]]; then
    if grep -q "^FRONTEND_URL=" "$BACKEND_DIR/.env"; then
        sed -i.bak "s|^FRONTEND_URL=.*|FRONTEND_URL=$DESIRED_FRONTEND_URL|g" "$BACKEND_DIR/.env"
    else
        echo "FRONTEND_URL=$DESIRED_FRONTEND_URL" >> "$BACKEND_DIR/.env"
    fi
    print_info "Backend FRONTEND_URL set to: $DESIRED_FRONTEND_URL"
else
    print_info "Backend FRONTEND_URL preserved: $CURRENT_FRONTEND_URL"
fi

# Ensure CORS allows the local frontend origin when frontend and backend are on different ports.
DESIRED_FRONTEND_ORIGIN="http://localhost:$FRONTEND_PORT"
CURRENT_ALLOWED_ORIGINS="$(grep "^ALLOWED_ORIGINS=" "$BACKEND_DIR/.env" 2>/dev/null | head -n 1 | cut -d '=' -f2- || true)"
if [ -z "$CURRENT_ALLOWED_ORIGINS" ]; then
    echo "ALLOWED_ORIGINS=$DESIRED_FRONTEND_ORIGIN" >> "$BACKEND_DIR/.env"
    print_info "Backend ALLOWED_ORIGINS set to: $DESIRED_FRONTEND_ORIGIN"
elif [[ ",$CURRENT_ALLOWED_ORIGINS," != *",$DESIRED_FRONTEND_ORIGIN,"* ]]; then
    NEW_ALLOWED_ORIGINS="${CURRENT_ALLOWED_ORIGINS},${DESIRED_FRONTEND_ORIGIN}"
    sed -i.bak "s|^ALLOWED_ORIGINS=.*|ALLOWED_ORIGINS=${NEW_ALLOWED_ORIGINS}|g" "$BACKEND_DIR/.env"
    print_info "Added $DESIRED_FRONTEND_ORIGIN to backend ALLOWED_ORIGINS"
fi

###############################################################################
# Start Redis
###############################################################################

print_header "Starting Redis"

# Check if Redis container already exists
if docker ps -a --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER_NAME}$"; then
    if docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER_NAME}$"; then
        print_info "Redis container already running"
    else
        print_info "Starting existing Redis container..."
        docker start $REDIS_CONTAINER_NAME > /dev/null 2>&1
        print_success "Redis container started"
    fi
else
    print_info "Creating and starting Redis container..."
    docker run -d \
        --name $REDIS_CONTAINER_NAME \
        -p 6379:6379 \
        redis:7-alpine \
        > /dev/null 2>&1
    print_success "Redis container created and started"
fi

# Wait for Redis to be ready
print_info "Waiting for Redis to be ready..."
sleep 2
if docker exec $REDIS_CONTAINER_NAME redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is ready"
else
    print_error "Redis failed to start"
    exit 1
fi

###############################################################################
# Start Backend
###############################################################################

print_header "Starting Backend (FastAPI)"

cd "$BACKEND_DIR"

BACKEND_ALREADY_RUNNING=false
if curl -fsS --connect-timeout 1 --max-time 2 "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
    BACKEND_ALREADY_RUNNING=true
    BACKEND_PID="$(cat "$LOG_DIR/backend.pid" 2>/dev/null || true)"
    if [ -z "$BACKEND_PID" ]; then
        BACKEND_PID="$(get_listen_pids "$BACKEND_PORT" | head -n 1)"
    fi
    print_info "Backend already running on http://localhost:$BACKEND_PORT"
fi

# Check if venv exists
if [ -d "venv" ]; then
    VENV_PY="$(pwd)/venv/bin/python"
    if [ -x "$VENV_PY" ]; then
        VENV_VERSION="$("$VENV_PY" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
        DESIRED_VERSION="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)"
        if [ -n "$VENV_VERSION" ] && [ -n "$DESIRED_VERSION" ] && [ "$VENV_VERSION" != "$DESIRED_VERSION" ]; then
            print_warning "Backend venv uses Python $VENV_VERSION but $PYTHON_BIN is $DESIRED_VERSION; recreating venv..."
            rm -rf venv
        fi
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    "$PYTHON_BIN" -m venv venv
    print_success "Virtual environment created"
fi

# Activate venv and install dependencies
print_info "Installing backend dependencies..."
source venv/bin/activate
pip install -q --upgrade pip > "$BACKEND_INSTALL_LOG" 2>&1
pip install -q -r requirements.txt >> "$BACKEND_INSTALL_LOG" 2>&1
print_success "Backend dependencies installed"

if [ "$BACKEND_ALREADY_RUNNING" = false ]; then
    assert_port_available "$BACKEND_PORT" "Backend" "BACKEND_PORT"

    # Start backend in background
    print_info "Starting backend server on port $BACKEND_PORT..."
    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT \
        > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$LOG_DIR/backend.pid"

    # Wait for backend to start
    print_info "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -fsS --connect-timeout 1 --max-time 2 "http://localhost:$BACKEND_PORT/health" > /dev/null 2>&1; then
            print_success "Backend is ready (PID: $BACKEND_PID)"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start. Check logs: $BACKEND_LOG"
            exit 1
        fi
        sleep 1
    done
fi

###############################################################################
# Start ngrok
###############################################################################

print_header "Starting ngrok"

# Check if ngrok is already running
if pgrep -f "ngrok http $BACKEND_PORT" > /dev/null; then
    print_warning "ngrok appears to be already running"
    NGROK_PID=$(pgrep -f "ngrok http $BACKEND_PORT")
    print_info "ngrok PID: $NGROK_PID"
else
    print_info "Starting ngrok tunnel to localhost:$BACKEND_PORT..."
    
    if [ -n "$NGROK_DOMAIN" ] && [[ ! "$NGROK_DOMAIN" == *"your-"* ]] && [[ ! "$NGROK_DOMAIN" == *"example"* ]]; then
        # Start with static domain
        nohup ngrok http $BACKEND_PORT --domain=$NGROK_DOMAIN \
            > "$LOG_DIR/ngrok.log" 2>&1 &
        NGROK_PID=$!
    else
        # Start without static domain
        print_warning "No static domain configured, starting ngrok without domain..."
        nohup ngrok http $BACKEND_PORT \
            > "$LOG_DIR/ngrok.log" 2>&1 &
        NGROK_PID=$!
    fi
    
    echo $NGROK_PID > "$LOG_DIR/ngrok.pid"
    
    # Wait for ngrok to start
    print_info "Waiting for ngrok to establish tunnel..."
    sleep 3
    
    # Get ngrok URL
    NGROK_URL=$(curl -fsS --connect-timeout 1 --max-time 2 http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)
    
    if [ -n "$NGROK_URL" ]; then
        print_success "ngrok tunnel established (PID: $NGROK_PID)"
        print_info "Public URL: $NGROK_URL"
    else
        print_warning "Could not retrieve ngrok URL (check if ngrok is authenticated)"
        print_info "ngrok PID: $NGROK_PID"
    fi
fi

###############################################################################
# Start Frontend
###############################################################################

print_header "Starting Frontend (React)"

cd "$PROJECT_ROOT"

FRONTEND_ALREADY_RUNNING=false
LISTEN_PIDS="$(get_listen_pids "$FRONTEND_PORT")"
if [ -n "$LISTEN_PIDS" ]; then
    FRONTEND_PID_FILE="$LOG_DIR/frontend.pid"
    FRONTEND_PID="$(cat "$FRONTEND_PID_FILE" 2>/dev/null || true)"
    if [ -n "$FRONTEND_PID" ] && echo "$LISTEN_PIDS" | grep -qx "$FRONTEND_PID"; then
        FRONTEND_ALREADY_RUNNING=true
        print_info "Frontend already running on http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
    else
        print_error "Frontend port $FRONTEND_PORT is already in use by another process."
        if command -v lsof &> /dev/null; then
            lsof -nP -iTCP:"$FRONTEND_PORT" -sTCP:LISTEN || true
        fi
        print_info "Stop the existing process, or run with a different port: FRONTEND_PORT=$((FRONTEND_PORT + 1)) ./start-lti-dev.sh"
        exit 1
    fi
fi

if [ "$FRONTEND_ALREADY_RUNNING" = false ]; then
    assert_port_available "$FRONTEND_PORT" "Frontend" "FRONTEND_PORT"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing frontend dependencies (npm ci)..."
        npm ci > "$FRONTEND_INSTALL_LOG" 2>&1
        print_success "Frontend dependencies installed"
    fi

    # Start frontend
    print_info "Starting frontend on port $FRONTEND_PORT..."
    nohup env PORT="$FRONTEND_PORT" BROWSER=none npm start > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"

    # Wait for frontend to start
    print_info "Waiting for frontend to be ready..."
    for i in {1..60}; do
        if curl -fsS --connect-timeout 1 --max-time 2 "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
            print_success "Frontend is ready (PID: $FRONTEND_PID)"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "Frontend failed to start. Check logs: $FRONTEND_LOG"
            exit 1
        fi
        sleep 1
    done
fi

###############################################################################
# Summary
###############################################################################

print_header "🎉 All Services Started Successfully!"

echo ""
echo "${GREEN}Services Status:${NC}"
echo "  ${GREEN}✓${NC} Redis:    Running (container: $REDIS_CONTAINER_NAME)"
echo "  ${GREEN}✓${NC} Backend:  Running on http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
echo "  ${GREEN}✓${NC} ngrok:    Running (PID: $NGROK_PID)"
echo "  ${GREEN}✓${NC} Frontend: Running on http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
echo ""

echo "${BLUE}Access URLs:${NC}"
echo "  Frontend:     ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo "  Backend:      ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo "  Backend Docs: ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
echo "  ngrok Web UI: ${GREEN}http://localhost:4040${NC}"
if [ -n "$NGROK_URL" ]; then
    echo "  Public URL:   ${GREEN}$NGROK_URL${NC}"
fi
echo ""

echo "${BLUE}Log Files:${NC}"
echo "  Backend:  $BACKEND_LOG"
echo "  Frontend: $FRONTEND_LOG"
echo "  ngrok:    $LOG_DIR/ngrok.log"
echo ""

echo "${YELLOW}Next Steps:${NC}"
echo "  1. Register tool in Brightspace with ngrok URL"
echo "  2. Create LTI link in test course"
echo "  3. Test the flow!"
echo ""
echo "  See TESTING_GUIDE.md for detailed instructions"
echo ""

echo "${YELLOW}To stop all services, run:${NC}"
echo "  ./stop-lti-dev.sh"
echo ""

echo "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Keep script running and show logs
echo "${GREEN}Press Ctrl+C to view logs, or run 'tail -f $LOG_DIR/*.log' in another terminal${NC}"
echo ""

# Optional: tail logs
# tail -f "$BACKEND_LOG" "$FRONTEND_LOG"
