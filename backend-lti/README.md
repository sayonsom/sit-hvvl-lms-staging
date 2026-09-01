# LTI Backend Service

FastAPI-based LTI 1.3 authentication service for SIT Brightspace integration.

## Features

- LTI 1.3 login initiation and launch handling
- JWT validation with Brightspace JWKS
- Redis-backed session management
- User and course information extraction
- Session validation and refresh endpoints
- Production-ready with proper logging and error handling

## Quick Start

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start Redis

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 4. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### LTI Endpoints

- `POST /lti/login` - LTI login initiation (receives request from Brightspace)
- `POST /lti/launch` - LTI launch (validates JWT and creates session)
- `GET /lti/session/validate` - Validate session token
- `POST /lti/logout` - Destroy session
- `GET /lti/session/refresh` - Refresh session TTL

### Health Check

- `GET /health` - Application health status

## Docker Deployment

```bash
# Build image
docker build -t lti-backend .

# Run container
docker run -d \
  --name lti-backend \
  -p 8000:8000 \
  --env-file .env \
  lti-backend
```

## Environment Variables

See `.env.example` for all configuration options.

Key variables:
- `CLIENT_ID` - Brightspace client ID
- `DEPLOYMENT_ID` - Brightspace deployment ID
- `ISSUER` - Brightspace issuer URL
- `REDIS_HOST` - Redis host for session storage
- `TOOL_URL` - Your tool's public URL
- `FRONTEND_URL` - Frontend application URL

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
isort app/
```

### Linting

```bash
flake8 app/
mypy app/
```

## Architecture

```
┌─────────────┐
│ Brightspace │
└──────┬──────┘
       │ 1. POST /lti/login
       ▼
┌─────────────┐
│  LTI        │
│  Backend    │──────────┐
│  (FastAPI)  │          │
└──────┬──────┘          │
       │                 ▼
       │ 2. Redirect  ┌────────┐
       │    to Auth   │ Redis  │
       ▼              │Session │
┌─────────────┐       │ Store  │
│ Brightspace │       └────────┘
│ Auth        │
└──────┬──────┘
       │ 3. POST /lti/launch (JWT)
       ▼
┌─────────────┐
│  LTI        │
│  Backend    │
└──────┬──────┘
       │ 4. Redirect with one-time login_code
       ▼
┌─────────────┐
│  Frontend   │
│  (React)    │
└─────────────┘
```

## Logging

Logs are output to stdout/stderr. Configure log level with `LOG_LEVEL` environment variable.

Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Security

- All JWT tokens are validated against Brightspace JWKS
- State and nonce are cryptographically secure random values
- Sessions are stored in Redis with configurable TTL
- CORS is restricted to configured origins only
- All sensitive data is logged at DEBUG level only

## Support

For issues or questions, refer to:
- `../LTI_MIGRATION_PLAN.md` - Full migration guide
- `../IMPLEMENTATION_STATUS.md` - Implementation status
