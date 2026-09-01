# LTI 1.3 Implementation Status

## [ DONE ]Completed

### 1. Planning & Documentation
- [ DONE ]**LTI_MIGRATION_PLAN.md** - Complete migration strategy with flow diagrams
- [ DONE ]Architecture design for production deployment (no ngrok)
- [ DONE ]Security considerations documented
- [ DONE ]Brightspace configuration requirements

### 2. Backend LTI Service (FastAPI)
- [ DONE ]**backend-lti/app/main.py** - FastAPI application with all endpoints
  - POST /lti/login - Login initiation
  - POST /lti/launch - Launch handling  
  - GET /lti/session/validate - Session validation
  - POST /lti/logout - Logout
  - GET /lti/session/refresh - Session refresh
  - GET /health - Health check

- [ DONE ]**backend-lti/app/config.py** - Configuration management
  - Environment variable loading
  - Default values for SIT Brightspace
  - Redis configuration
  - CORS settings

- [ DONE ]**backend-lti/app/lti_handler.py** - LTI 1.3 protocol implementation
  - JWT validation with PyJWKClient
  - User info extraction
  - Course info extraction
  - Role mapping from LTI URIs

- [ DONE ]**backend-lti/app/session_manager.py** - Redis-backed session management
  - State storage (for login flow)
  - Session creation
  - Session validation
  - Session refresh
  - Logout handling

---

## 🔨 Next Steps (To Complete Migration)

### Step 1: Create Remaining Backend Files (15 minutes)

Create these files in `backend-lti/`:

**1. `backend-lti/app/models.py`**
```python
from pydantic import BaseModel
from typing import Dict, List, Any

class SessionResponse(BaseModel):
    user: Dict[str, Any]
    course: Dict[str, Any]

class LogoutRequest(BaseModel):
    pass  # Can be empty
```

**2. `backend-lti/app/__init__.py`**
```python
# Empty file to make app a package
```

**3. `backend-lti/requirements.txt`**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
PyJWT[crypto]==2.8.0
cryptography==42.0.0
redis==5.0.1
python-multipart==0.0.6
```

**4. `backend-lti/Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app /code/app

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**5. `backend-lti/.env.example`**
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

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-password-here
REDIS_DB=0
REDIS_SSL=false

# Session Configuration
SESSION_TTL=28800
STATE_TTL=300

# CORS Configuration
ALLOWED_ORIGINS=https://classaid.singaporetech.edu.sg,https://xsitestg.singaporetech.edu.sg

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### Step 2: Create Frontend LTI Context (30 minutes)

**1. Create `src/contexts/LTIContext.js`**
- Use the code from `LTI_MIGRATION_PLAN.md` Phase 2, Step 2.1
- This replaces Auth0Provider

**2. Update `src/index.js`**
- Replace `Auth0ProviderWithNavigate` with `LTIProvider`
- Use code from migration plan Phase 2, Step 2.2

**3. Update `src/App.js`**
- Remove Auth0 imports
- Routing stays the same

**4. Update `src/pages/AppEntry.jsx`**
- Exchange the one-time login_code from query params
- Validate and store in localStorage
- Redirect to /home
- Use code from migration plan Phase 2, Step 2.3

### Step 3: Replace Auth0 in Components (1-2 hours)

Replace `useAuth0` with `useLTI` in these files:

1. **src/pages/Home.js**
```javascript
// OLD
import { useAuth0 } from "@auth0/auth0-react";
const { isAuthenticated, user } = useAuth0();

// NEW
import { useLTI } from "../contexts/LTIContext";
const { isAuthenticated, user } = useLTI();
```

2. **src/pages/AppLayout.js**
```javascript
// Same replacement as above
import { useLTI } from "../contexts/LTIContext";
const { user, logout, isAuthenticated } = useLTI();
```

3. **src/pages/QuizResults.jsx**
```javascript
// Same replacement
```

4. **src/components/LoginButton.jsx**
- Replace entire component with LTI-required message
- See migration plan Phase 3, Step 3.2

5. **src/pages/LandingPage.js**
- Update to show "Must launch from Brightspace"
- See migration plan Phase 3, Step 3.3

6. **Remove `src/auth0-provider-with-navigate.js`**
- No longer needed

###Step 4: Local Testing with ngrok (1-2 hours)

1. **Start Redis locally:**
```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

2. **Start backend-lti:**
```bash
cd backend-lti
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DEBUG=true
export REDIS_HOST=localhost
export TOOL_URL=https://your-ngrok-domain.ngrok-free.app
export FRONTEND_URL=http://localhost:3000
python -m uvicorn app.main:app --reload --port 8000
```

3. **Start ngrok:**
```bash
ngrok http 8000 --domain=your-static-ngrok-domain
```

4. **Update frontend .env.local:**
```bash
REACT_APP_API_URL=http://localhost:8080
REACT_APP_LTI_API_URL=https://your-ngrok-domain.ngrok-free.app
```

5. **Start frontend:**
```bash
npm start
```

6. **Register in Brightspace:**
- Share `LTI_MIGRATION_PLAN.md` "Brightspace Admin Configuration" section with SIT admin
- Use your ngrok URL as TOOL_URL

7. **Test the flow:**
- Click LTI link in Brightspace course
- Should redirect through /lti/login → Brightspace → /lti/launch → /app → /home
- Verify user info appears correctly

### Step 5: Production Deployment (varies)

1. **Deploy to classaid.singaporetech.edu.sg**
- Set up Redis instance
- Deploy backend-lti service
- Update nginx configuration (see migration plan Phase 5)
- Configure SSL certificates

2. **Update Brightspace registration**
- Change URLs from ngrok to production
- Test with real course

3. **Monitor and verify**
- Check logs
- Test with multiple users
- Verify session persistence

---

## 📝 Key Files to Create

### Minimum Viable Implementation:
1. [ DONE ]backend-lti/app/main.py (DONE)
2. [ DONE ]backend-lti/app/config.py (DONE)
3. [ DONE ]backend-lti/app/lti_handler.py (DONE)
4. [ DONE ]backend-lti/app/session_manager.py (DONE)
5. ⏳ backend-lti/app/models.py (5 min)
6. ⏳ backend-lti/app/__init__.py (1 min)
7. ⏳ backend-lti/requirements.txt (2 min)
8. ⏳ backend-lti/Dockerfile (5 min)
9. ⏳ backend-lti/.env (2 min)
10. ⏳ src/contexts/LTIContext.js (15 min)
11. ⏳ Update src/index.js (2 min)
12. ⏳ Update src/pages/AppEntry.jsx (10 min)
13. ⏳ Update src/pages/Home.js (5 min)
14. ⏳ Update src/pages/AppLayout.js (5 min)
15. ⏳ Update src/pages/QuizResults.jsx (5 min)
16. ⏳ Update src/components/LoginButton.jsx (5 min)
17. ⏳ Update src/pages/LandingPage.js (10 min)

**Total estimated time to complete**: 3-4 hours

---

## 🚀 Quick Start Commands

### For Local Development:

```bash
# 1. Start Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 2. Setup backend-lti
cd backend-lti
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
uvicorn app.main:app --reload

# 3. Start ngrok (in another terminal)
ngrok http 8000 --domain=YOUR_STATIC_DOMAIN

# 4. Start frontend (in another terminal)
cd ../
npm start
```

---

## 📞 Need Help?

- Review `LTI_MIGRATION_PLAN.md` for detailed explanations
- Check backend logs: backend shows all LTI flow steps
- Check Redis: `redis-cli` → `KEYS lti_*` to see sessions
- Check frontend console for session token issues

---

**Status**: Backend 90% complete, Frontend 0% complete  
**Next Action**: Create frontend LTI Context Provider  
**Estimated Completion**: 3-4 hours of focused work
