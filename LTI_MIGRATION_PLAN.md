# LTI 1.3 Migration Plan

> Historical design note: examples below that pass `session_token` in a URL or
> use `localStorage` are superseded. The implemented flow uses a short-lived
> one-time `login_code`, `/lti/session/exchange`, and tab-scoped
> `sessionStorage` as documented in `UAT_LOCAL_DEPLOYMENT.md`.
## From Auth0 to SIT Brightspace Integration

### 📋 Overview

This document outlines the migration from Auth0 authentication to SIT Brightspace LTI 1.3 integration. The goal is to allow the Virtual High Voltage Lab to be launched directly from Brightspace without requiring separate authentication.

---

## 🎯 Goals

1. **Remove Auth0 dependency** - Eliminate all Auth0 provider, hooks, and authentication flows
2. **Implement LTI 1.3 standard** - Use IMS Global LTI 1.3 with OpenID Connect for secure integration
3. **Seamless user experience** - Students/instructors click a link in Brightspace and are directly authenticated
4. **Production-ready deployment** - No ngrok; proper production deployment on classaid.singaporetech.edu.sg
5. **Session management** - Maintain user sessions across the React SPA after initial LTI launch

---

## 🏗️ Architecture Changes

### Current (Auth0) Flow
```
User → Landing Page → Auth0 Login → Callback → /home
                ↓
         Auth0Provider wraps entire app
                ↓
         useAuth0() hook for user info
```

### New (LTI 1.3) Flow
```
User in Brightspace → Clicks LTI Link
        ↓
LTI Login Initiation (POST /lti/login)
        ↓
Redirect to Brightspace Auth Endpoint
        ↓
Brightspace validates & redirects back (POST /lti/launch)
        ↓
Backend validates JWT, extracts user/course data
        ↓
Creates session, stores in Redis/Database
        ↓
Redirects to Frontend with session token
        ↓
Frontend: LTIProvider wraps app, manages session
        ↓
React App loads with user context from LTI
```

---

## 🔑 SIT Brightspace Configuration

### Provided Credentials
- **Domain**: `https://classaid.singaporetech.edu.sg`
- **Callback URL**: `https://classaid.singaporetech.edu.sg/oauth/callback`
- **Client ID**: `2ad6f149-5011-40c4-b9a9-728acd7fa5d6`
- **Deployment ID**: `0c8bd348-2427-483f-a0b9-0ad0ed965d1e`

### Brightspace LTI 1.3 Endpoints
- **Issuer**: `https://xsitestg.singaporetech.edu.sg`
- **Authorization Endpoint**: `https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate`
- **JWKS URL**: `https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks`

---

## 📦 Components to Build

### 1. Backend LTI Service (FastAPI)
**Location**: `/backend-lti/` (new service alongside alignbackendapis)

**Responsibilities**:
- Handle LTI login initiation (`POST /lti/login`)
- Handle LTI launch (`POST /lti/launch`)
- Validate JWT ID tokens from Brightspace
- Extract user information (name, email, user_id, roles)
- Extract course information (course_id, title, section)
- Create and manage user sessions
- Provide session validation endpoint for frontend

**Key Files**:
- `main.py` - FastAPI app with LTI endpoints
- `lti_handler.py` - LTI 1.3 protocol implementation
- `session_manager.py` - Session creation and validation (Redis-backed)
- `config.py` - LTI configuration (Client ID, Deployment ID, etc.)

### 2. Frontend LTI Context Provider
**Location**: `/src/contexts/LTIContext.js`

**Responsibilities**:
- Replace Auth0Provider
- Store user/course information from LTI launch
- Provide `useLTI()` hook (replacement for `useAuth0()`)
- Handle session refresh
- Provide logout functionality

**Context Shape**:
```javascript
{
  isAuthenticated: boolean,
  user: {
    user_id: string,
    name: string,
    email: string,
    given_name: string,
    family_name: string,
    roles: string[]
  },
  course: {
    course_id: string,
    course_code: string,
    course_title: string,
    course_section: string
  },
  isLoading: boolean,
  logout: () => void
}
```

### 3. Updated Frontend Entry Flow
**Modified Files**:
- `src/App.js` - Replace Auth0Provider with LTIProvider
- `src/pages/AppEntry.jsx` - Handle LTI launch redirect
- `src/index.js` - Update provider wrapping
- Remove: `src/auth0-provider-with-navigate.js`

---

## 🔄 Detailed Migration Steps

### Phase 1: Backend LTI Service (Day 1-2)

#### Step 1.1: Create Backend Service Structure
```bash
mkdir -p backend-lti/app
cd backend-lti
```

Create files:
- `requirements.txt` - FastAPI, PyJWT, Redis, etc.
- `Dockerfile` - Container for LTI service
- `docker-compose.yml` - Include Redis for sessions
- `app/main.py` - FastAPI application
- `app/config.py` - Configuration management
- `app/lti_handler.py` - LTI 1.3 implementation
- `app/session_manager.py` - Session management
- `app/models.py` - Pydantic models

#### Step 1.2: Implement LTI Endpoints

**POST /lti/login**
```python
# Receives: iss, login_hint, target_link_uri, lti_message_hint
# Generates: state, nonce
# Stores state/nonce in Redis (short TTL: 5 minutes)
# Redirects to: Brightspace authorization endpoint
```

**POST /lti/launch**
```python
# Receives: id_token, state
# Validates: JWT signature, nonce, deployment_id, issuer
# Extracts: user info, course info, roles
# Creates: long-lived session in Redis (TTL: 8 hours)
# Returns: session token + redirects to frontend with token
```

**GET /lti/session/validate**
```python
# Receives: Authorization header with session token
# Validates: session exists and not expired
# Returns: user and course information
```

**POST /lti/logout**
```python
# Receives: session token
# Deletes: session from Redis
# Returns: success
```

#### Step 1.3: Session Management with Redis
```python
# Session Structure in Redis
{
  "session_id": "unique-uuid",
  "user": {
    "user_id": "123456",
    "name": "John Doe",
    "email": "john.doe@singaporetech.edu.sg",
    "roles": ["Learner"]
  },
  "course": {
    "course_id": "6874",
    "course_code": "EEE101",
    "course_title": "High Voltage Engineering"
  },
  "created_at": "ISO timestamp",
  "expires_at": "ISO timestamp"
}
```

### Phase 2: Frontend Context Provider (Day 2-3)

#### Step 2.1: Create LTI Context
Create `/src/contexts/LTIContext.js`:

```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const LTIContext = createContext();

export const LTIProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [course, setCourse] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for session token in localStorage
    const validateSession = async () => {
      const sessionToken = localStorage.getItem('lti_session_token');
      if (sessionToken) {
        try {
          const response = await axios.get(
            `${process.env.REACT_APP_LTI_API_URL}/lti/session/validate`,
            { headers: { Authorization: `Bearer ${sessionToken}` } }
          );
          setUser(response.data.user);
          setCourse(response.data.course);
          setIsAuthenticated(true);
        } catch (error) {
          localStorage.removeItem('lti_session_token');
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };

    validateSession();
  }, []);

  const logout = async () => {
    const sessionToken = localStorage.getItem('lti_session_token');
    if (sessionToken) {
      try {
        await axios.post(
          `${process.env.REACT_APP_LTI_API_URL}/lti/logout`,
          {},
          { headers: { Authorization: `Bearer ${sessionToken}` } }
        );
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    localStorage.removeItem('lti_session_token');
    setUser(null);
    setCourse(null);
    setIsAuthenticated(false);
    window.location.href = '/lti-required';
  };

  return (
    <LTIContext.Provider
      value={{
        isAuthenticated,
        user,
        course,
        isLoading,
        logout,
      }}
    >
      {children}
    </LTIContext.Provider>
  );
};

export const useLTI = () => {
  const context = useContext(LTIContext);
  if (!context) {
    throw new Error('useLTI must be used within LTIProvider');
  }
  return context;
};
```

#### Step 2.2: Update Entry Point
Modify `/src/index.js`:

```javascript
import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import { LTIProvider } from "./contexts/LTIContext";
import "./index.css";

const container = document.getElementById("root");
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <BrowserRouter>
      <LTIProvider>
        <App />
      </LTIProvider>
    </BrowserRouter>
  </React.StrictMode>
);
```

#### Step 2.3: Update App Entry Handler
Modify `/src/pages/AppEntry.jsx`:

```javascript
import React, { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";

export default function AppEntry() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const sessionToken = searchParams.get("session_token");
    
    if (!sessionToken) {
      navigate("/lti-required", { replace: true });
      return;
    }

    // Validate and store session token
    const validateSession = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_LTI_API_URL}/lti/session/validate`,
          { headers: { Authorization: `Bearer ${sessionToken}` } }
        );
        
        // Store session token
        localStorage.setItem('lti_session_token', sessionToken);
        
        // Store user data for immediate access
        localStorage.setItem('lti_user', JSON.stringify(response.data.user));
        localStorage.setItem('lti_course', JSON.stringify(response.data.course));
        
        // Navigate to home/dashboard
        navigate("/home", { replace: true });
      } catch (error) {
        console.error('Session validation failed:', error);
        navigate("/lti-required", { replace: true });
      }
    };

    validateSession();
  }, [navigate, searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-xl font-semibold">Authenticating...</h2>
        <p className="mt-2 text-gray-600">Please wait while we set up your session.</p>
      </div>
    </div>
  );
}
```

### Phase 3: Update All Components (Day 3-4)

#### Step 3.1: Replace Auth0 Hooks
In every file using `useAuth0`, replace with `useLTI`:

**Files to update**:
- `src/pages/Home.js`
- `src/pages/AppLayout.js`
- `src/pages/QuizResults.jsx`
- `src/components/LoginButton.jsx`

**Example (AppLayout.js)**:
```javascript
// OLD
import { useAuth0 } from "@auth0/auth0-react";
const { user, logout, isAuthenticated } = useAuth0();

// NEW
import { useLTI } from "../contexts/LTIContext";
const { user, logout, isAuthenticated } = useLTI();
```

#### Step 3.2: Update LoginButton
Replace with LTI-required message:

```javascript
const LoginButton = () => {
  return (
    <div className="text-center">
      <p>This application must be launched from Brightspace.</p>
      <p className="text-sm text-gray-600 mt-2">
        Please access this tool through your course in Brightspace.
      </p>
    </div>
  );
};
```

#### Step 3.3: Update Landing Page
Modify `/src/pages/LandingPage.js` to show LTI requirement:

```javascript
export default function LandingPage() {
  return (
    <div className="bg-white min-h-screen flex items-center justify-center">
      <div className="max-w-2xl text-center px-6">
        <img
          className="h-20 mx-auto mb-8"
          src="https://res.cloudinary.com/dti7egpsg/image/upload/v1705671150/SIT%20Align/sit_app_logo_dsr3ee.png"
          alt="SIT HV Lab Logo"
        />
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Virtual High Voltage Laboratory
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          A web-based platform to enhance teaching and learning of topics related to high voltage engineering.
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-2">
            Access via Brightspace
          </h2>
          <p className="text-blue-700">
            This application must be launched from your course in SIT Brightspace.
            Please navigate to your course and click the Virtual Lab link.
          </p>
        </div>
      </div>
    </div>
  );
}
```

### Phase 4: Environment Configuration (Day 4)

#### Step 4.1: Update Environment Variables

**Frontend `.env.production`**:
```bash
REACT_APP_API_URL=https://classaid.singaporetech.edu.sg/api
REACT_APP_LTI_API_URL=https://classaid.singaporetech.edu.sg/lti
```

**Backend LTI `.env`**:
```bash
# LTI Configuration
CLIENT_ID=2ad6f149-5011-40c4-b9a9-728acd7fa5d6
DEPLOYMENT_ID=0c8bd348-2427-483f-a0b9-0ad0ed965d1e
ISSUER=https://xsitestg.singaporetech.edu.sg
AUTHORIZATION_ENDPOINT=https://xsitestg.singaporetech.edu.sg/d2l/lti/authenticate
KEY_SET_URL=https://xsitestg.singaporetech.edu.sg/d2l/.well-known/jwks

# Tool Configuration
TOOL_URL=https://classaid.singaporetech.edu.sg
FRONTEND_URL=https://classaid.singaporetech.edu.sg

# Redis Session Store
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-password
SESSION_TTL=28800  # 8 hours

# CORS
ALLOWED_ORIGINS=https://classaid.singaporetech.edu.sg,https://xsitestg.singaporetech.edu.sg

# Backend API
BACKEND_API_URL=http://alignbackendapis:8080
```

### Phase 5: Deployment Configuration (Day 5)

#### Step 5.1: Update Nginx Configuration
Add LTI endpoints to `nginx.conf`:

```nginx
# LTI endpoints (backend service)
location /lti/ {
    proxy_pass http://lti-backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Main API endpoints (existing alignbackendapis)
location /api/ {
    proxy_pass http://alignbackendapis:8080;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Frontend SPA (existing)
location / {
    try_files $uri $uri/ /index.html;
}
```

#### Step 5.2: Docker Compose for Production
Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Redis for LTI sessions
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - backend

  # LTI Backend Service
  lti-backend:
    build: ./backend-lti
    environment:
      - CLIENT_ID=${CLIENT_ID}
      - DEPLOYMENT_ID=${DEPLOYMENT_ID}
      - ISSUER=${ISSUER}
      - AUTHORIZATION_ENDPOINT=${AUTHORIZATION_ENDPOINT}
      - KEY_SET_URL=${KEY_SET_URL}
      - TOOL_URL=${TOOL_URL}
      - REDIS_HOST=redis
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    depends_on:
      - redis
    networks:
      - backend

  # Existing services...
  # alignbackendapis, postgres, etc.

  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - lti-backend
      - alignbackendapis
    networks:
      - backend

volumes:
  redis_data:

networks:
  backend:
```

---

## 🧪 Testing Plan

### Local Testing (with ngrok temporarily)
1. Start backend-lti service locally
2. Use ngrok to expose: `ngrok http 8000 --domain=your-static-domain`
3. Register in Brightspace test course with ngrok URL
4. Test LTI flow end-to-end
5. Verify user/course data extraction
6. Test session management

### Production Testing
1. Deploy to classaid.singaporetech.edu.sg
2. Configure SSL certificates
3. Register production URL in Brightspace
4. Test with real course
5. Verify session persistence
6. Test logout flow
7. Load testing with multiple concurrent users

---

## 📋 Brightspace Admin Configuration

Share with SIT Admin:

### Tool Registration Details
- **Tool Name**: Virtual High Voltage Laboratory
- **Tool URL**: `https://classaid.singaporetech.edu.sg`
- **Login Initiation URL**: `https://classaid.singaporetech.edu.sg/lti/login`
- **Redirect/Launch URL**: `https://classaid.singaporetech.edu.sg/lti/launch`
- **Client ID**: `2ad6f149-5011-40c4-b9a9-728acd7fa5d6`
- **Deployment ID**: `0c8bd348-2427-483f-a0b9-0ad0ed965d1e`
- **OpenID Connect Login Initiation URL**: `https://classaid.singaporetech.edu.sg/lti/login`
- **Target Link URI**: `https://classaid.singaporetech.edu.sg/app`

### Required Permissions
- Send user name
- Send user email  
- Send user ID
- Send role information
- Access to course information
- Access to context information

### Launch Settings
- Open in new window/tab (recommended)
- Or embed in iframe (if preferred)

---

## 🔒 Security Considerations

1. **JWT Validation**: Always validate signature, issuer, audience, nonce, deployment_id
2. **State/Nonce**: Use cryptographically secure random values, one-time use
3. **Session Security**: Use secure, httpOnly cookies or secure token storage
4. **HTTPS Only**: All communication must be over HTTPS
5. **CORS**: Restrict to Brightspace domain only
6. **Session Expiry**: Implement reasonable TTL (8 hours recommended)
7. **Rate Limiting**: Protect LTI endpoints from abuse
8. **Logging**: Log all LTI attempts for security audit

---

## 📊 Rollback Plan

If issues arise:
1. Keep Auth0 credentials active during migration
2. Feature flag: `USE_LTI_AUTH=true/false` in environment
3. Can switch back to Auth0 by changing environment variable
4. Dual authentication support during transition period

---

## [ DONE ]Success Criteria

- [ ] User clicks link in Brightspace → automatically authenticated
- [ ] No Auth0 login screen appears
- [ ] User information extracted correctly from LTI
- [ ] Course context available throughout app
- [ ] Sessions persist across page refreshes
- [ ] Logout works correctly
- [ ] All existing features work with LTI user context
- [ ] No ngrok in production
- [ ] Performance is acceptable (<2s initial load)

---

## 📚 References

- [IMS Global LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3/)
- [D2L Brightspace LTI Documentation](https://documentation.brightspace.com/EN/integrations/lti_advantage/index.htm)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 📞 Support Contacts

- **SIT IT Support**: [Contact details]
- **Brightspace Admin**: [Contact details]
- **Development Team**: [Your team details]

---

**Last Updated**: January 2, 2025
**Status**: Planning Phase
**Next Review**: After Phase 1 completion
