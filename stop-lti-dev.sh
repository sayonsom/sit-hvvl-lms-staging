#!/bin/zsh

###############################################################################
# LTI Development Environment Stop Script
# This script stops all services started by start-lti-dev.sh
###############################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$SCRIPT_DIR}"
LOG_DIR="$PROJECT_ROOT/logs"
REDIS_CONTAINER_NAME="redis-lti-dev"

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

print_info() {
    echo "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo "${YELLOW}⚠${NC} $1"
}

print_header "Stopping LTI Development Environment"

###############################################################################
# Stop Frontend
###############################################################################

print_info "Stopping Frontend..."
if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
    if kill -0 "$FRONTEND_PID" > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        print_success "Frontend stopped (PID: $FRONTEND_PID)"
    else
        print_warning "Frontend process not found"
    fi
    rm "$LOG_DIR/frontend.pid"
else
    # Try to find and kill any npm start process
    if pgrep -f "react-scripts start" > /dev/null; then
        pkill -f "react-scripts start"
        print_success "Frontend stopped"
    else
        print_warning "Frontend not running"
    fi
fi

###############################################################################
# Stop ngrok
###############################################################################

print_info "Stopping ngrok..."
if [ -f "$LOG_DIR/ngrok.pid" ]; then
    NGROK_PID=$(cat "$LOG_DIR/ngrok.pid")
    if kill -0 "$NGROK_PID" > /dev/null 2>&1; then
        kill $NGROK_PID 2>/dev/null
        print_success "ngrok stopped (PID: $NGROK_PID)"
    else
        print_warning "ngrok process not found"
    fi
    rm "$LOG_DIR/ngrok.pid"
else
    # Try to find and kill any ngrok process
    if pgrep -f "ngrok http" > /dev/null; then
        pkill -f "ngrok http"
        print_success "ngrok stopped"
    else
        print_warning "ngrok not running"
    fi
fi

###############################################################################
# Stop Backend
###############################################################################

print_info "Stopping Backend..."
if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
    if kill -0 "$BACKEND_PID" > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        print_success "Backend stopped (PID: $BACKEND_PID)"
    else
        print_warning "Backend process not found"
    fi
    rm "$LOG_DIR/backend.pid"
else
    # Try to find and kill any uvicorn process on port 8000
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        pkill -f "uvicorn app.main:app"
        print_success "Backend stopped"
    else
        print_warning "Backend not running"
    fi
fi

###############################################################################
# Stop Redis (Optional)
###############################################################################

echo ""
STOP_REDIS="N"
if [ -t 0 ]; then
    echo -n "${YELLOW}Stop Redis container? (y/N):${NC} "
    read -r STOP_REDIS
fi

if [[ "$STOP_REDIS" =~ ^[Yy]$ ]]; then
    print_info "Stopping Redis container..."
    if docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER_NAME}$"; then
        docker stop $REDIS_CONTAINER_NAME > /dev/null 2>&1
        print_success "Redis container stopped"
        
        REMOVE_REDIS="N"
        if [ -t 0 ]; then
            echo -n "${YELLOW}Remove Redis container? (y/N):${NC} "
            read -r REMOVE_REDIS
        fi
        if [[ "$REMOVE_REDIS" =~ ^[Yy]$ ]]; then
            docker rm $REDIS_CONTAINER_NAME > /dev/null 2>&1
            print_success "Redis container removed"
        fi
    else
        print_warning "Redis container not running"
    fi
else
    print_info "Redis container left running"
fi

###############################################################################
# Clean up
###############################################################################

print_info "Cleaning up..."

# Optional: clear log files
CLEAR_LOGS="N"
if [ -t 0 ]; then
    echo -n "${YELLOW}Clear log files? (y/N):${NC} "
    read -r CLEAR_LOGS
fi
if [[ "$CLEAR_LOGS" =~ ^[Yy]$ ]]; then
    rm -f "$LOG_DIR"/*.log
    print_success "Log files cleared"
fi

###############################################################################
# Summary
###############################################################################

print_header "✓ Services Stopped"

echo ""
echo "${GREEN}All services have been stopped.${NC}"
echo ""
echo "${BLUE}To start again, run:${NC}"
echo "  ./start-lti-dev.sh"
echo ""
