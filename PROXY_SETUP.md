# Proxy Setup for External Access

## Problem
When accessing from Brightspace (external), both the backend AND frontend need to be publicly accessible via the same ngrok URL.

## Solution
We use a **reverse proxy** on port 4000 that routes requests to the appropriate service:
- `/lti/*` → Backend (port 8000)
- `/health` → Backend (port 8000)
- `/docs` → Backend (port 8000)
- `/api/v1/*` → local backend-api service
- `/*` (everything else) → Frontend (port 3000)

## Architecture

```
                                  ┌──────────────────┐
                                  │   Brightspace    │
                                  │   (External)     │
                                  └────────┬─────────┘
                                           │
                                           ▼
                    ┌──────────────────────────────────────┐
                    │  ngrok Tunnel (Port 4000)            │
                    │  https://elianna-evaporative...dev   │
                    └──────────────┬───────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────────────┐
                    │  Reverse Proxy (Port 4000)           │
                    │  proxy-server.js                     │
                    └──────┬───────────────────┬───────────┘
                           │                   │
                    /lti/* │                   │ /*
                           │                   │
                           ▼                   ▼
              ┌─────────────────┐    ┌─────────────────┐
              │  LTI Backend    │    │  React Frontend │
              │  Port 8000      │    │  Port 3000      │
              │  (FastAPI)      │    │  (npm start)    │
              └─────────────────┘    └─────────────────┘
```

## Running Services

### Start All Services (in order):

1. **Redis** (for sessions)
   ```bash
   docker run -d --name redis-lti-dev -p 6379:6379 redis:7-alpine
   ```

2. **Backend** (LTI service on port 8000)
   ```bash
   cd backend-lti
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend** (React on port 3000)
   ```bash
   npm start
   ```

4. **Proxy** (Reverse proxy on port 4000)
   ```bash
   # Optional: override the local backend API upstream base (no /api/v1)
   # export API_UPSTREAM_URL=http://localhost:8080
   
   node proxy-server.js
   ```

5. **ngrok** (Public tunnel to port 4000)
   ```bash
   ngrok http 4000 --domain=elianna-evaporative-ariane.ngrok-free.dev
   ```

### Check Status

```bash
# Check proxy
curl http://localhost:4000/proxy-health

# Check backend (through proxy)
curl https://elianna-evaporative-ariane.ngrok-free.dev/health

# Check frontend (through proxy)
curl https://elianna-evaporative-ariane.ngrok-free.dev/

# Check ngrok dashboard
open http://localhost:4040
```

### Stop Services

```bash
# Stop proxy
kill $(cat logs/proxy.pid)

# Stop ngrok
kill $(cat logs/ngrok.pid)

# Stop backend
kill $(cat logs/backend.pid)

# Stop frontend
# Press Ctrl+C in the npm start terminal

# Stop Redis
docker stop redis-lti-dev
```

## Configuration Files

### backend-lti/.env
```bash
TOOL_URL=https://elianna-evaporative-ariane.ngrok-free.dev
FRONTEND_URL=https://elianna-evaporative-ariane.ngrok-free.dev
ALLOWED_ORIGINS=http://localhost:3000,https://elianna-evaporative-ariane.ngrok-free.dev,https://xsitestg.singaporetech.edu.sg
```

### .env.local (frontend)
```bash
REACT_APP_API_URL=http://localhost:8080
REACT_APP_LTI_API_URL=https://elianna-evaporative-ariane.ngrok-free.dev
```

## URLs for Brightspace Registration

**OpenID Connect Login Initiation URL:**
```
https://elianna-evaporative-ariane.ngrok-free.dev/lti/login
```

**Redirect/Launch URL:**
```
https://elianna-evaporative-ariane.ngrok-free.dev/lti/launch
```

**Additional Redirect URI:**
```
https://elianna-evaporative-ariane.ngrok-free.dev/app
```

## Testing the Flow

1. Click LTI link in Brightspace
2. Brightspace POSTs to: `https://elianna-evaporative-ariane.ngrok-free.dev/lti/login`
3. Proxy forwards to: `http://localhost:8000/lti/login`
4. Backend redirects to Brightspace auth
5. Brightspace POSTs JWT to: `https://elianna-evaporative-ariane.ngrok-free.dev/lti/launch`
6. Backend validates JWT and redirects to: `https://elianna-evaporative-ariane.ngrok-free.dev/app?login_code=...`
7. Proxy forwards to: `http://localhost:3000/app?login_code=...`
8. Frontend exchanges the one-time code and loads the app

## Logs

- Proxy: `logs/proxy.log`
- Backend: `logs/backend.log`
- Frontend: Terminal where `npm start` is running
- ngrok: http://localhost:4040 (web interface)

## Notes

- The proxy server is needed because ngrok free tier only allows 1 tunnel
- All external requests go through the same ngrok URL
- The proxy intelligently routes to backend or frontend based on path
- WebSocket support is enabled for React hot reload
