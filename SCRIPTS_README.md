# 🚀 LTI Development Scripts

Quick start/stop scripts for running the entire LTI development environment with one command.

---

## 📋 Files

- **`start-lti-dev.sh`** - Starts all services (Redis, Backend, ngrok, Frontend)
- **`stop-lti-dev.sh`** - Stops all services cleanly
- **`logs/`** - Log files directory (created automatically)

---

## ⚡ Quick Start

### Start Everything

```bash
./start-lti-dev.sh
```

This will:
1. [ DONE ]Check prerequisites (Docker, Python, npm, ngrok)
2. [ DONE ]Verify/create configuration files (.env, .env.local)
3. [ DONE ]Start Redis container
4. [ DONE ]Create Python venv and install dependencies
5. [ DONE ]Start FastAPI backend on port 8000
6. [ DONE ]Start ngrok tunnel
7. [ DONE ]Install npm packages and start React frontend on port 3000
8. [ DONE ]Display all URLs and access information

### Stop Everything

```bash
./stop-lti-dev.sh
```

This will:
1. Stop Frontend (React dev server)
2. Stop ngrok tunnel
3. Stop Backend (FastAPI/uvicorn)
4. Optionally stop/remove Redis container
5. Optionally clear log files

---

## 📝 First Time Setup

### 1. Make scripts executable (already done)

```bash
chmod +x start-lti-dev.sh stop-lti-dev.sh
```

### 2. Get ngrok static domain

Sign up at [ngrok.com](https://ngrok.com) (free tier works):
1. Create account
2. Get your auth token
3. Get a free static domain
4. Configure ngrok: `ngrok config add-authtoken YOUR_TOKEN`

### 3. Run the start script

```bash
./start-lti-dev.sh
```

The script will prompt you to enter your ngrok domain if not configured.

---

## 🎯 What the Start Script Does

### Pre-flight Checks
- [ DONE ]Verifies Docker, Python, npm, ngrok are installed
- [ DONE ]Checks Docker is running
- [ DONE ]Verifies project directories exist

### Configuration
- 📝 Creates `.env` from `.env.example` if missing
- 📝 Creates `.env.local` from `.env.local.example` if missing
- 🔧 Prompts for ngrok domain if not configured
- ✏️ Updates configuration files automatically

### Service Startup (in order)
1. **Redis** (Docker container)
   - Creates/starts `redis-lti-dev` container
   - Exposes port 6379
   - Waits until Redis is ready

2. **Backend** (FastAPI)
   - Creates Python venv if needed
   - Installs dependencies from requirements.txt
   - Starts uvicorn on port 8000 with auto-reload
   - Waits until /health endpoint responds

3. **ngrok**
   - Starts tunnel to localhost:8000
   - Uses your static domain if configured
   - Retrieves and displays public URL

4. **Frontend** (React)
   - Installs npm packages if needed
   - Starts React dev server on port 3000
   - Waits until server is ready

---

## 📊 Output Example

```
═══════════════════════════════════════════════════════════
  🎉 All Services Started Successfully!
═══════════════════════════════════════════════════════════

Services Status:
  ✓ Redis:    Running (container: redis-lti-dev)
  ✓ Backend:  Running on http://localhost:8000 (PID: 12345)
  ✓ ngrok:    Running (PID: 12346)
  ✓ Frontend: Running on http://localhost:3000 (PID: 12347)

Access URLs:
  Frontend:     http://localhost:3000
  Backend:      http://localhost:8000
  Backend Docs: http://localhost:8000/docs
  ngrok Web UI: http://localhost:4040
  Public URL:   https://your-domain.ngrok-free.app

Log Files:
  Backend:  /Users/sayon/.../logs/backend.log
  Frontend: /Users/sayon/.../logs/frontend.log
  ngrok:    /Users/sayon/.../logs/ngrok.log

Next Steps:
  1. Register tool in Brightspace with ngrok URL
  2. Create LTI link in test course
  3. Test the flow!
  
  See TESTING_GUIDE.md for detailed instructions

To stop all services, run:
  ./stop-lti-dev.sh
```

---

## 📂 Log Files

All logs are stored in `logs/` directory:

- **`backend.log`** - FastAPI/uvicorn output
- **`frontend.log`** - React dev server output
- **`ngrok.log`** - ngrok tunnel logs
- **`*.pid`** - Process ID files

### View logs in real-time

```bash
# All logs
tail -f logs/*.log

# Backend only
tail -f logs/backend.log

# Frontend only
tail -f logs/frontend.log
```

---

## 🔧 Manual Control

If you need to control services individually:

### Redis
```bash
# Start
docker start redis-lti-dev

# Stop
docker stop redis-lti-dev

# Remove
docker rm redis-lti-dev

# Check status
docker ps | grep redis-lti-dev
```

### Backend
```bash
# Start
cd backend-lti
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Check
curl http://localhost:8000/health
```

### Frontend
```bash
# Start
npm start

# Check
curl http://localhost:3000
```

### ngrok
```bash
# Start
ngrok http 8000 --domain=your-domain.ngrok-free.app

# Check web UI
open http://localhost:4040
```

---

## ⚠️ Troubleshooting

### "Docker is not running"
```bash
# Start Docker Desktop application
open -a Docker
# Wait for Docker to start, then run script again
```

### "Port already in use"
```bash
# Check what's using the port
lsof -i :8000   # Backend
lsof -i :3000   # Frontend
lsof -i :6379   # Redis

# Kill the process
kill -9 <PID>
```

### "ngrok authentication required"
```bash
# Add your auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### "Backend failed to start"
```bash
# Check the log
cat logs/backend.log

# Common issues:
# - Redis not running
# - Port 8000 in use
# - Missing dependencies
```

### "Frontend failed to start"
```bash
# Check the log
cat logs/frontend.log

# Common issues:
# - Port 3000 in use
# - Missing node_modules (run: npm install)
# - Syntax errors in code
```

### Start from scratch
```bash
# Stop everything
./stop-lti-dev.sh

# Remove containers and logs
docker rm -f redis-lti-dev
rm -rf logs/

# Clean Python venv
rm -rf backend-lti/venv

# Clean node_modules (optional)
rm -rf node_modules

# Start again
./start-lti-dev.sh
```

---

## 🎓 Tips

1. **Keep scripts running** - Don't close the terminal, open new tabs for other work
2. **Check ngrok UI** - Visit http://localhost:4040 to see requests
3. **Monitor logs** - Use `tail -f logs/*.log` in another terminal
4. **Save ngrok domain** - Static domains don't change, save it in your config

---

## 🚀 Next Steps After Starting

1. **Verify all services** - Check all URLs are accessible
2. **Register in Brightspace** - Use ngrok URL from output
3. **Follow TESTING_GUIDE.md** - Complete step-by-step testing
4. **Test LTI flow** - Click LTI link in Brightspace

---

## 📞 Need Help?

- **Start fails?** - Check logs in `logs/` directory
- **Service won't stop?** - Use `ps aux | grep uvicorn` (or npm, ngrok) and kill manually
- **Config issues?** - Delete `.env` and `.env.local`, script will recreate them

---

**Quick Commands:**

```bash
# Start everything
./start-lti-dev.sh

# Stop everything
./stop-lti-dev.sh

# View logs
tail -f logs/*.log

# Check status
docker ps | grep redis
curl http://localhost:8000/health
curl http://localhost:3000

# Access UIs
open http://localhost:3000        # Frontend
open http://localhost:8000/docs   # Backend API docs
open http://localhost:4040        # ngrok inspect UI
```

---

**Created:** January 3, 2025  
**Status:** [ DONE ]Ready to use
