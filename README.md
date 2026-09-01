# SIT Virtual Lab - LTI 1.3 Integration (Staging)

This private repository is the dedicated deployment source for
`https://hvlabonline-uat.singaporetech.edu.sg`. Start with
[STAGING_QUICKSTART.md](STAGING_QUICKSTART.md); the staging-safe deployment
command validates the environment, repairs the legacy PostgreSQL password
without deleting data, and waits for all five services to become healthy.

The populated `.env.uat` is intentionally excluded from Git.

A Virtual Lab application integrated with Singapore Institute of Technology's Brightspace LMS using LTI 1.3 protocol.

## Overview

This application provides a virtual laboratory environment that launches directly from SIT's Brightspace LMS. It uses LTI 1.3 (Learning Tools Interoperability) for secure single sign-on authentication and course context sharing.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Brightspace   │────▶│  Backend LTI     │────▶│  React Frontend │
│   (SIT LMS)     │     │  (FastAPI)       │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │    Redis     │
                        │  (Sessions)  │
                        └──────────────┘
```

## LTI Launch Flow

1. **User clicks Virtual Lab link** in Brightspace course
2. **Brightspace sends POST** to `/lti/login` with login_hint
3. **Backend generates state/nonce** and redirects to Brightspace authorization
4. **Brightspace authenticates** user and redirects to `/lti/launch` with signed JWT
5. **Backend validates JWT**, extracts user/course info, creates session
6. **User redirected to frontend** with session token

## Project Structure

```
virtuallab/
├── backend-lti/              # FastAPI LTI backend
│   ├── app/
│   │   ├── main.py           # API endpoints
│   │   ├── lti_handler.py    # LTI 1.3 protocol handler
│   │   ├── session_manager.py # Redis session management
│   │   ├── config.py         # Configuration settings
│   │   └── models.py         # Pydantic models
│   ├── Dockerfile
│   └── requirements.txt
├── src/                      # React frontend
│   ├── contexts/
│   │   └── LTIContext.js     # LTI session context provider
│   └── ...
├── lti_tool/                 # Alternative Python LTI tool
├── start-lti-dev.sh          # Development startup script
├── stop-lti-dev.sh           # Development shutdown script
└── docker-compose.yml
```

## Configuration

### SIT Brightspace Settings

| Setting | Staging | Production |
|---------|---------|------------|
| **Issuer** | `https://xsitestg.singaporetech.edu.sg` | `https://classaid.singaporetech.edu.sg` |
| **Authorization Endpoint** | `https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate` | - |
| **JWKS URL** | `https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks` | - |

### Environment Variables

Create a `.env` file in `backend-lti/`:

```env
# LTI 1.3 Configuration
LTI_CLIENT_ID=your-client-id
LTI_DEPLOYMENT_ID=your-deployment-id
LTI_ISSUER=https://xsitestg.singaporetech.edu.sg
LTI_AUTHORIZATION_ENDPOINT=https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate
LTI_KEY_SET_URL=https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks

# Tool Configuration
TOOL_URL=https://your-backend-url
FRONTEND_URL=https://your-frontend-url

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_SSL=false

# Session Configuration
SESSION_TTL=28800  # 8 hours in seconds
STATE_TTL=300      # 5 minutes for state/nonce

# Backend API
BACKEND_API_URL=http://backend-api:8080/api/v1
```

## Quick Start

### Development

1. **Start all services:**
   ```bash
   ./start-lti-dev.sh
   ```

2. **Stop all services:**
   ```bash
   ./stop-lti-dev.sh
   ```

### Manual Setup

1. **Start Redis:**
   ```bash
   redis-server
   ```

2. **Start Backend:**
   ```bash
   cd backend-lti
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **Start Frontend:**
   ```bash
   npm install
   npm start
   ```

### Docker Deployment

```bash
docker-compose up -d
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/lti/login` | POST | LTI login initiation (receives from Brightspace) |
| `/lti/launch` | POST | LTI launch with JWT validation |
| `/lti/session/validate` | GET | Validate session token |
| `/lti/session/refresh` | GET | Refresh session TTL |
| `/lti/logout` | POST | Destroy session |

## Session Management

Sessions are stored in Redis with the following structure:

```json
{
  "session_id": "uuid",
  "user": {
    "user_id": "from LTI",
    "name": "Full Name",
    "email": "user@example.com",
    "roles": ["Learner", "Instructor"],
    "given_name": "First",
    "family_name": "Last",
    "picture": "URL or gravatar"
  },
  "course": {
    "course_id": "from LTI context",
    "course_code": "EEE101",
    "course_title": "Course Name",
    "course_section": "Section identifier"
  },
  "created_at": "ISO timestamp",
  "expires_at": "ISO timestamp",
  "last_accessed": "ISO timestamp"
}
```

## LTI Role Mappings

The application maps IMS Global LTI roles to application roles:

| LTI Role | Application Role |
|----------|------------------|
| `Instructor`, `http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor` | Instructor |
| `Learner`, `http://purl.imsglobal.org/vocab/lis/v2/membership#Learner` | Learner |
| `Administrator`, `http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator` | Administrator |
| `TeachingAssistant` | Teaching Assistant |

## Security Features

- **JWT Validation**: Signature verification using Brightspace JWKS
- **Issuer Verification**: Validates token issuer matches configured LMS
- **Audience Verification**: Validates client_id
- **Nonce Verification**: Prevents replay attacks (one-time use)
- **Deployment ID Verification**: Ensures correct tool deployment
- **Session Security**: Cryptographically secure tokens (48-byte urlsafe)
- **Server-side Storage**: Sessions stored in Redis, not client-side
- **Configurable TTL**: 8-hour session lifetime with auto-refresh

## Testing with ngrok

For local development testing with Brightspace:

1. **Start ngrok tunnels:**
   ```bash
   ngrok http 3000  # Frontend
   ngrok http 8001  # Backend (in separate terminal)
   ```

2. **Update configuration** with ngrok URLs:
   ```env
   TOOL_URL=https://your-backend.ngrok-free.app
   FRONTEND_URL=https://your-frontend.ngrok-free.app
   ```

3. **Register tool in Brightspace** with the ngrok URLs

## Brightspace Admin Setup

To register this tool in Brightspace, an LMS administrator needs to:

1. **Navigate to**: Admin Tools > Manage Extensibility > LTI Advantage
2. **Register new tool** with:
   - **Name**: SIT Virtual Lab
   - **Domain**: Your deployment domain
   - **Redirect URLs**: `{backend-url}/lti/launch`
   - **Login URL**: `{backend-url}/lti/login`
   - **Target Link URI**: `{frontend-url}`
   - **Keyset URL**: (if implementing tool-side keys)

3. **Create deployment** and note:
   - Client ID
   - Deployment ID

4. **Add to course** as External Learning Tool link

## Frontend Integration

The React frontend uses `LTIContext` for session management:

```jsx
import { useLTI } from './contexts/LTIContext';

function MyComponent() {
  const { user, course, isAuthenticated, logout } = useLTI();

  if (!isAuthenticated) {
    return <div>Please launch from Brightspace</div>;
  }

  return (
    <div>
      <p>Welcome, {user.name}!</p>
      <p>Course: {course.course_title}</p>
    </div>
  );
}
```

## Troubleshooting

### Common Issues

1. **"Invalid state" error**
   - State expired (>5 minutes) - restart the launch
   - Clear browser cookies and retry

2. **"JWT validation failed"**
   - Check JWKS URL is accessible
   - Verify client_id matches Brightspace configuration

3. **Session not persisting**
   - Check Redis is running: `redis-cli ping`
   - Verify CORS settings allow your frontend domain

4. **"Deployment ID mismatch"**
   - Verify deployment_id in config matches Brightspace

### Logs

Backend logs are available at:
```bash
# Development
uvicorn logs in terminal

# Docker
docker logs virtuallab-backend-lti
```

## Additional Documentation

- [LTI Migration Plan](./LTI_MIGRATION_PLAN.md) - Detailed migration guide from Auth0
- [Implementation Status](./IMPLEMENTATION_STATUS.md) - Current implementation status
- [Testing Guide](./TESTING_GUIDE.md) - Step-by-step testing procedures
- [Backend README](./backend-lti/README.md) - Backend-specific documentation

## License

Proprietary - Singapore Institute of Technology
