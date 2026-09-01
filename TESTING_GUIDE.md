# Testing Guide - LTI Integration

## Prerequisites

Before testing, ensure you have:
- [ DONE ]Python 3.11+ installed
- [ DONE ]Node.js 18+ and npm installed
- [ DONE ]Docker Desktop running
- [ DONE ]ngrok account with a static domain (free tier works)
- [ DONE ]Access to SIT Brightspace test/sandbox environment

---

## Step 1: Start Redis (Session Store)

```bash
# Start Redis container
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Verify it's running
docker ps | grep redis
```

---

## Step 2: Set Up LTI Backend

### 2.1 Install Dependencies

```bash
cd backend-lti

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2.2 Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your ngrok domain
nano .env  # or use your preferred editor
```

Update these values in `.env`:
```bash
# For local testing with ngrok
TOOL_URL=https://elianna-evaporative-ariane.ngrok-free.dev
FRONTEND_URL=http://localhost:3000

# Redis (local)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Enable debug mode
DEBUG=true
LOG_LEVEL=DEBUG

# CORS - allow both ngrok and localhost
ALLOWED_ORIGINS=https://elianna-evaporative-ariane.ngrok-free.dev,http://localhost:3000,https://xsitestg.singaporetech.edu.sg
```

### 2.3 Start the Backend

```bash
# Make sure you're in backend-lti with venv activated
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Successfully connected to Redis at localhost:6379
```

---

## Step 3: Expose Backend with ngrok

Open a **new terminal** (keep backend running):

```bash
# Using your static ngrok domain
ngrok http 8000 --domain=https://elianna-evaporative-ariane.ngrok-free.dev
```

You should see:
```
Session Status                online
Account                       NGrok Account
Forwarding                    https://blah-blah.ngrok-free.app -> http://localhost:8000
```

**Keep this terminal open!**

Test the backend:
```bash
# In another terminal
curl https://elianna-evaporative-ariane.ngrok-free.dev/health
# Should return: {"status":"healthy","service":"lti-backend"}
```

---

## Step 4: Configure Frontend

### 4.1 Create Local Environment File

```bash
cd /path/to/virtuallab  # repo root (where package.json lives)

# Copy example
cp .env.local.example .env.local

# Edit it
nano .env.local
```

Set these values:
```bash
REACT_APP_API_URL=http://localhost:8080
REACT_APP_LTI_API_URL=https://your-static-domain.ngrok-free.app
```

### 4.2 Start Frontend

```bash
npm start
```

Frontend should start at `http://localhost:3000`

---

## Step 5: Register Tool in Brightspace

Share this information with your SIT Brightspace administrator:

### Tool Registration Details

**Basic Information:**
- Tool Name: `Virtual High Voltage Laboratory`
- Tool Description: `Web-based platform for high voltage engineering education`

**LTI 1.3 Settings:**
- OpenID Connect Login Initiation URL: `https://your-static-domain.ngrok-free.app/lti/login`
- Target Link URI / Launch URL: `https://your-static-domain.ngrok-free.app/lti/launch`
- Redirect URIs: 
  - `https://your-static-domain.ngrok-free.app/lti/launch`
  - `http://localhost:3000/app`

**Provided by SIT (already configured in backend):**
- Client ID: `2ad6f149-5011-40c4-b9a9-728acd7fa5d6`
- Deployment ID: `0c8bd348-2427-483f-a0b9-0ad0ed965d1e`

**Permissions Needed:**
- [ DONE ]Send user's name
- [ DONE ]Send user's email
- [ DONE ]Send user ID
- [ DONE ]Send role information
- [ DONE ]Access to course information
- [ DONE ]Access to context information

**Launch Presentation:**
- Open in: New Window/Tab (recommended)
- Alternative: Embed in iframe

---

## Step 6: Create LTI Link in Brightspace

1. **Log into Brightspace** as instructor/admin
2. **Navigate to a test course**
3. **Go to Content**
4. **Click "Add External Learning Tool"**
5. **Select your registered tool** (Virtual High Voltage Laboratory)
6. **Configure the link:**
   - Title: "Virtual Lab"
   - Check "Open as External Resource"
   - Check "Open in new window"
7. **Save & Close**

---

## Step 7: Test the LTI Flow

### 7.1 Launch from Brightspace

1. In your test course, click the "Virtual Lab" link
2. **Watch the terminal logs** - you should see:

**Backend logs:**
```
INFO: LTI Login Initiation received from issuer: https://xsitestg.singaporetech.edu.sg
DEBUG: Generated state: abcd123... nonce: xyz789...
INFO: Redirecting to authorization URL
```

Then:
```
INFO: LTI launch received
DEBUG: Consumed one-time LTI state
DEBUG: Validating JWT token
DEBUG: Obtained signing key from JWKS
DEBUG: LTI token decoded successfully
INFO: Token validation successful
INFO: LTI session created
```

### 7.2 Check Browser Flow

You should be redirected through:
1. Brightspace → `/lti/login` (POST)
2. Brightspace auth → validates user
3. `/lti/launch` (POST) → validates JWT
4. Redirect to frontend → `/app?login_code=...`
5. Frontend atomically exchanges the short-lived code for the session
6. Redirect to `/home`

### 7.3 Verify Session

**In Browser Console:**
```javascript
// Check tab-scoped session storage after redirect to /home
sessionStorage.getItem('lti_session_token')
// Should show a long token

sessionStorage.getItem('lti_user')
// Should show user JSON

localStorage.getItem('lti_course')
// Should show course JSON
```

**In Backend Terminal:**
Check Redis:
```bash
# In another terminal
docker exec -it redis redis-cli

# List all LTI sessions
KEYS lti_*

# Check a session (copy key from above)
GET lti_session:your-token-here
```

### 7.4 Test Features

- [ DONE ]User name appears in top bar
- [ DONE ]User profile photo (if provided)
- [ DONE ]Navigation works (Home, My Submissions, etc.)
- [ DONE ]Logout works (clears session, redirects to /lti-required)
- [ DONE ]Session persists on page refresh
- [ DONE ]Can access existing features (experiments, courses, etc.)

---

## Step 8: Common Issues & Debugging

### Issue: "Invalid or expired state parameter"

**Cause:** State/nonce expired (5 min TTL) or already used

**Solution:** 
- Try the launch again
- Check Redis is running: `docker ps | grep redis`
- Check backend logs for state storage

### Issue: "Token validation failed"

**Possible causes:**
1. **Client ID mismatch** - Check `CLIENT_ID` in `.env` matches Brightspace
2. **Deployment ID mismatch** - Check `DEPLOYMENT_ID` in `.env`
3. **JWKS URL wrong** - Verify `KEY_SET_URL` in `.env`
4. **Issuer mismatch** - Verify `ISSUER` in `.env`

**Debug:**
```bash
# In backend terminal, look for:
ERROR: Token validation error: ...
ERROR: Deployment ID mismatch. Expected: ..., Got: ...
ERROR: Nonce mismatch...
```

### Issue: Frontend shows "Session validation failed"

**Cause:** Backend not reachable or session expired

**Check:**
1. Is backend running? `curl http://localhost:8000/health`
2. Is ngrok running? `curl https://your-domain.ngrok-free.app/health`
3. Check browser console for network errors
4. Check `REACT_APP_LTI_API_URL` in `.env.local`

### Issue: CORS errors

**Cause:** Origin not in ALLOWED_ORIGINS

**Solution:** Update backend `.env`:
```bash
ALLOWED_ORIGINS=https://your-ngrok.ngrok-free.app,http://localhost:3000,https://xsitestg.singaporetech.edu.sg
```

Then restart backend.

### Issue: User data not showing

**Check:**
1. Browser console for LTI user object
2. Backend logs for extracted user info
3. Brightspace permissions - ensure all user data fields are enabled

---

## Step 9: Testing Different Scenarios

### Test as Student
1. Log into Brightspace as a student
2. Launch tool from course
3. Verify role is "Learner" or "Student"

### Test as Instructor
1. Log into Brightspace as instructor
2. Launch tool from same course
3. Verify role is "Instructor"

### Test Session Expiry
1. Launch tool successfully
2. Wait or manually delete session in Redis:
   ```bash
   docker exec -it redis redis-cli
   DEL lti_session:your-token
   ```
3. Refresh page - should redirect to /lti-required

### Test Logout
1. Click user menu → Log Out
2. Confirm logout
3. Should redirect to /lti-required page
4. Session should be deleted from Redis

---

## Step 10: Stop Services

When done testing:

```bash
# Stop frontend (Ctrl+C in terminal)

# Stop backend (Ctrl+C in terminal)
# Deactivate venv
deactivate

# Stop ngrok (Ctrl+C in terminal)

# Stop Redis
docker stop redis
docker rm redis

# Or keep Redis running for next session
```

---

## Production Deployment Notes

When moving to production:

1. **No ngrok** - Deploy backend to actual server
2. **Update URLs** in backend `.env`:
   ```bash
   TOOL_URL=https://classaid.singaporetech.edu.sg
   FRONTEND_URL=https://classaid.singaporetech.edu.sg
   ```
3. **Update Brightspace registration** - Change URLs from ngrok to production
4. **Use managed Redis** - AWS ElastiCache, Redis Cloud, etc.
5. **Enable SSL** - All communication over HTTPS
6. **Production secrets** - Use secure secret management
7. **Monitoring** - Set up logging and alerting

---

## Useful Commands

```bash
# Check backend health
curl http://localhost:8000/health

# Check Redis connections
docker exec -it redis redis-cli INFO clients

# View all sessions in Redis
docker exec -it redis redis-cli KEYS "lti_*"

# Clear all sessions (for testing)
docker exec -it redis redis-cli FLUSHDB

# Backend logs with colors
uvicorn app.main:app --reload --log-level debug

# Frontend build (for production testing)
npm run build

# Check environment variables in frontend
# In browser console:
console.log(process.env)
```

---

## Success Checklist

[ DONE ]Redis running and accessible
[ DONE ]Backend starts without errors
[ DONE ]ngrok tunnel established
[ DONE ]Frontend starts and shows landing page
[ DONE ]Tool registered in Brightspace
[ DONE ]LTI link created in test course
[ DONE ]Can launch from Brightspace
[ DONE ]User authenticated and redirected to /home
[ DONE ]User name/photo displays correctly
[ DONE ]Session persists on refresh
[ DONE ]Logout works properly
[ DONE ]Can access all application features

---

## Need Help?

- Check `LTI_MIGRATION_PLAN.md` for architecture details
- Review backend logs for detailed error messages
- Check browser console for frontend errors
- Verify all environment variables are set correctly
- Ensure all services are running (Redis, backend, frontend, ngrok)

---

**Last Updated:** January 3, 2025
**Status:** Ready for Testing
