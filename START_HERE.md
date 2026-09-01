# 🎉 START HERE - LTI Development

Welcome! This guide will get you testing in **under 5 minutes**.

---

## ⚡ Super Quick Start

### 1️⃣ Start Everything (One Command!)

```bash
./start-lti-dev.sh
```

That's it! The script will:
- [ DONE ]Check all prerequisites
- [ DONE ]Start all 4 services (Redis, Backend, ngrok, Frontend)
- [ DONE ]Show you all the URLs you need

**First time?** The script will prompt you for your ngrok domain.

---

## 2️⃣ What You'll See

```
═══════════════════════════════════════════════════════════
  🎉 All Services Started Successfully!
═══════════════════════════════════════════════════════════

Services Status:
  ✓ Redis:    Running
  ✓ Backend:  Running on http://localhost:8000
  ✓ ngrok:    Running
  ✓ Frontend: Running on http://localhost:3000

Access URLs:
  Frontend:     http://localhost:3000
  Backend:      http://localhost:8000
  Backend Docs: http://localhost:8000/docs
  ngrok Web UI: http://localhost:4040
  Public URL:   https://your-domain.ngrok-free.app
```

---

## 3️⃣ Test It

1. **Open your browser:** http://localhost:3000
2. You should see the landing page with "Access via Brightspace" message
3. **Check backend:** http://localhost:8000/docs

---

## 4️⃣ Next Steps

Now follow **TESTING_GUIDE.md** to:
1. Register your tool in Brightspace
2. Create an LTI link
3. Test the complete flow!

---

## 🛑 To Stop Everything

```bash
./stop-lti-dev.sh
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **SCRIPTS_README.md** | Detailed script documentation |
| **TESTING_GUIDE.md** | Complete testing instructions |
| **MIGRATION_COMPLETE.md** | What was built and delivered |
| **LTI_MIGRATION_PLAN.md** | Architecture and design |

---

## ⚠️ Prerequisites

Before running the start script, make sure you have:

- [ DONE ]**Docker Desktop** - Must be running
- [ DONE ]**Python 3.11+** - `python3 --version`
- [ DONE ]**Node.js 18+** - `node --version`
- [ DONE ]**ngrok** - `ngrok version`
  - Get free account at https://ngrok.com
  - Run: `ngrok config add-authtoken YOUR_TOKEN`

---

## 🔧 Quick Troubleshooting

### Script won't run?
```bash
chmod +x start-lti-dev.sh stop-lti-dev.sh
```

### Docker not running?
```bash
open -a Docker
# Wait for Docker to start, then try again
```

### Need ngrok?
```bash
# Install via homebrew
brew install ngrok

# Or download from https://ngrok.com/download
```

### Port already in use?
```bash
# Find what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill it
kill -9 <PID>
```

---

## 📊 Project Structure

```
virtuallab/
├── start-lti-dev.sh          ← START HERE!
├── stop-lti-dev.sh            ← Stop everything
├── SCRIPTS_README.md          ← Script docs
├── TESTING_GUIDE.md           ← Testing steps
├── MIGRATION_COMPLETE.md      ← What's included
├── backend-lti/               ← FastAPI LTI service
│   ├── app/
│   ├── .env.example
│   └── requirements.txt
├── src/                       ← React frontend
│   ├── contexts/LTIContext.js
│   └── ...
└── logs/                      ← Created by script
    ├── backend.log
    ├── frontend.log
    └── ngrok.log
```

---

## 🎯 Your Workflow

```bash
# Day 1: Setup
./start-lti-dev.sh
# Follow prompts, enter ngrok domain
# Open http://localhost:3000

# Day 2-N: Daily development
./start-lti-dev.sh
# Develop/test
./stop-lti-dev.sh

# View logs
tail -f logs/*.log

# Check services
docker ps | grep redis
curl http://localhost:8000/health
```

---

## [ DONE ]Success Checklist

After running `./start-lti-dev.sh`:

- [ ] Script completed without errors
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:8000
- [ ] Backend docs at http://localhost:8000/docs
- [ ] ngrok UI at http://localhost:4040
- [ ] ngrok public URL shown in output

If all checked [ DONE ]→ **You're ready to test with Brightspace!**

---

## 🚀 What's Next?

1. [ DONE ]**Start services** (you're here!)
2. 📋 **Follow TESTING_GUIDE.md** - Register tool in Brightspace
3. 🧪 **Test the LTI flow** - Click link in Brightspace
4. 🎉 **Celebrate** - You've migrated from Auth0 to LTI!

---

## 💡 Pro Tips

- **Keep terminal open** - Don't close it, services run in background
- **Check ngrok UI** - Great for debugging requests
- **Monitor logs** - Open another terminal: `tail -f logs/*.log`
- **Save your ngrok domain** - You'll use it every time

---

## 📞 Need Help?

- **Script issues?** → See SCRIPTS_README.md
- **Testing issues?** → See TESTING_GUIDE.md
- **Architecture questions?** → See LTI_MIGRATION_PLAN.md
- **Can't find something?** → See MIGRATION_COMPLETE.md

---

**Ready? Let's go! 🚀**

```bash
./start-lti-dev.sh
```

---

**Last Updated:** January 3, 2025  
**Status:** [ DONE ]Production Ready
