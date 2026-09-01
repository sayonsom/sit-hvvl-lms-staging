# Local Setup FAQ

## ❓ Common Questions About Local Development Setup

### Q: What's the local database? Will PostgreSQL be installed on my Mac?

**A:** No installation on your Mac! PostgreSQL runs **inside a Docker container**. 

**How it works:**
- When you run `docker-compose -f docker-compose.local.yml up`, Docker automatically:
  - Downloads PostgreSQL 13 image (first time only)
  - Creates an isolated container with PostgreSQL running inside
  - Exposes it on port 5432 so your Mac can access it
  - Stores data in a persistent Docker volume (survives container restarts)

**Benefits:**
- ✅ No system-wide PostgreSQL installation needed
- ✅ Clean and isolated from your Mac
- ✅ Easy to reset: `docker-compose down -v` removes everything
- ✅ Same setup works for everyone on your team

**Connection details:**
```
Host: localhost (from your Mac) or postgres (from FastAPI container)
Port: 5432
Database: aligndb
User: alignuser
Password: local-dev-password-change-me
```

### Q: How do I migrate data from GCP to local?

**A:** You have 3 options:

#### Option 1: Automated Script (Easiest) ⚡

I've created a script that does everything:

```bash
# Just run this:
./migrate_gcp_to_local.sh
```

It will:
1. Start PostgreSQL container
2. Export all data from the approved GCP host in `GCP_HOST`
3. Import to local PostgreSQL
4. Verify the migration
5. Show you a summary

**You already have `pg_dump` installed**, so this should work perfectly!

#### Option 2: Manual Step-by-Step

```bash
# 1. Start local PostgreSQL
docker-compose -f docker-compose.local.yml up -d postgres

# 2. Export from GCP (load values from your approved secret store)
PGPASSWORD="$GCP_PASSWORD" pg_dump \
  -h "$GCP_HOST" \
  -U "$GCP_USER" \
  -d "$GCP_DB" \
  --no-owner \
  --no-acl \
  -f backup.sql

# 3. Import to local
cat backup.sql | docker-compose -f docker-compose.local.yml exec -T postgres \
  psql -U alignuser -d aligndb

# 4. Verify
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb -c "\dt"
```

#### Option 3: Using GCP Console

If direct connection doesn't work:
1. Go to GCP Console → Cloud SQL
2. Export database to Cloud Storage
3. Download the `.sql` file
4. Import: `cat downloaded.sql | docker-compose -f docker-compose.local.yml exec -T postgres psql -U alignuser -d aligndb`

### Q: How do I migrate files from Google Cloud Storage?

**A:** Files need to be downloaded from GCS and copied to local storage.

#### Step 1: Download from GCS

```bash
# Using gsutil (if you have gcloud CLI)
gsutil -m cp -r gs://align-hvl-2024-release1/* ./local_files/

# Or download manually from GCP Console
```

#### Step 2: Copy to Docker volume

```bash
# Start containers
docker-compose -f docker-compose.local.yml up -d

# Copy files
CONTAINER_ID=$(docker-compose -f docker-compose.local.yml ps -q fastapi)
docker cp ./local_files/. $CONTAINER_ID:/code/local_storage/align-hvl-2024-release1/

# Verify
docker-compose -f docker-compose.local.yml exec fastapi \
  ls /code/local_storage/align-hvl-2024-release1/
```

#### Alternative: Mount local directory

Edit `docker-compose.local.yml`:
```yaml
fastapi:
  volumes:
    - .:/code
    - ./local_files:/code/local_storage/align-hvl-2024-release1  # Add this
```

### Q: Where is the data stored?

**Docker volumes** store your data:

```bash
# View volumes
docker volume ls | grep alignbackendapis

# You'll see:
# alignbackendapis_postgres_data      (database files)
# alignbackendapis_local_storage_data (uploaded files)
```

**Data persistence:**
- ✅ Survives container restarts
- ✅ Survives `docker-compose down`
- ❌ Deleted by `docker-compose down -v` (the -v flag removes volumes)

**Backup your data:**
```bash
# Backup database
docker-compose -f docker-compose.local.yml exec postgres \
  pg_dump -U alignuser aligndb > backup_$(date +%Y%m%d).sql

# Backup files
docker cp $(docker-compose -f docker-compose.local.yml ps -q fastapi):/code/local_storage ./backup_files
```

### Q: How do I access the local database?

**Option 1: Using Docker exec (recommended)**
```bash
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb
```

**Option 2: From your Mac (if you have psql)**
```bash
psql -h localhost -p 5432 -U alignuser -d aligndb
# Password: local-dev-password-change-me
```

**Option 3: Using GUI tools**
- **pgAdmin**: http://localhost:5432
- **DBeaver**: Connect to localhost:5432
- **TablePlus**: Connect to localhost:5432

**Credentials:**
- Host: localhost
- Port: 5432
- Database: aligndb
- Username: alignuser
- Password: local-dev-password-change-me

### Q: How do I verify the migration worked?

**1. Check if containers are running:**
```bash
docker-compose -f docker-compose.local.yml ps
```
Should show both `postgres` and `fastapi` as "running"

**2. Check tables exist:**
```bash
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb -c "\dt"
```

**3. Count records:**
```bash
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb -c "SELECT COUNT(*) FROM students;"
```

**4. Test API:**
```bash
# Start full app
docker-compose -f docker-compose.local.yml up

# In another terminal:
curl http://localhost:8080/health
curl http://localhost:8080/api/v1/students/
```

### Q: What if port 5432 is already in use?

**Solution 1: Stop existing PostgreSQL**
```bash
# If you have PostgreSQL installed via Homebrew
brew services stop postgresql
# or
brew services stop postgresql@14  # or your version

# Check what's using the port
lsof -i :5432
```

**Solution 2: Change the port**

Edit `docker-compose.local.yml`:
```yaml
postgres:
  ports:
    - "5433:5432"  # Change from 5432 to 5433
```

Then connect to `localhost:5433` instead.

### Q: How do I reset everything and start fresh?

**Complete reset:**
```bash
# Stop and remove everything (including data!)
docker-compose -f docker-compose.local.yml down -v

# Start fresh
docker-compose -f docker-compose.local.yml up --build
```

**Keep data, rebuild containers:**
```bash
# Stop containers
docker-compose -f docker-compose.local.yml down

# Rebuild and restart
docker-compose -f docker-compose.local.yml up --build
```

### Q: Can I still use the GCP database?

**Yes!** The code supports both:

```bash
# To use LOCAL database:
export ENVIRONMENT=local
docker-compose -f docker-compose.local.yml up

# To use GCP database (switch back to main branch):
git checkout main
# or set environment to production
export ENVIRONMENT=production
```

The `app/db/connection.py` automatically switches based on `ENVIRONMENT` variable.

### Q: Is this setup secure?

**For local development: Yes, it's fine.**

⚠️ **Security notes:**
- ✅ Good for local development
- ✅ Data isolated in Docker
- ✅ Not exposed to internet
- ❌ Don't use in production (simple passwords)
- ❌ Don't commit sensitive data to git

### Q: How much disk space does this use?

Typical usage:
- PostgreSQL 13 image: ~150 MB
- Python 3.9 image: ~120 MB
- Your database data: depends on your data
- Application code: minimal

**Check Docker disk usage:**
```bash
docker system df
```

**Clean up unused Docker resources:**
```bash
# Remove old images and containers
docker system prune

# Remove all volumes (DANGER: deletes data!)
docker system prune -a --volumes
```

### Q: What files should I back up?

**Essential backups:**

1. **Database:**
   ```bash
   docker-compose -f docker-compose.local.yml exec postgres \
     pg_dump -U alignuser aligndb > backup.sql
   ```

2. **Local storage files:**
   ```bash
   docker cp $(docker-compose -f docker-compose.local.yml ps -q fastapi):/code/local_storage ./backup_storage
   ```

3. **Your code (already in git):**
   ```bash
   git status
   git push origin local-no-gcp
   ```

### Q: Can I develop on this branch and still have production use GCP?

**Yes! That's the whole point!**

**Workflow:**
1. **Local development** (this branch):
   ```bash
   git checkout local-no-gcp
   docker-compose -f docker-compose.local.yml up
   # Develop locally, no GCP costs
   ```

2. **Production** (main branch):
   ```bash
   git checkout main
   # Deploy to GCP Cloud Run
   # Uses GCP Cloud SQL and GCS
   ```

3. **Merge features** when ready:
   ```bash
   git checkout main
   git merge local-no-gcp
   # Test, then deploy
   ```

### Q: What's the difference between docker-compose.local.yml and other Docker files?

**In this repo:**

- `Dockerfile` - Original for GCP Cloud Run (has GCP SDK)
- `Dockerfile.local` - New! No GCP dependencies, for local dev
- `Dockerfile.SITLocal` - Old local dockerfile (still has GCP SDK)
- `docker-compose.local.yml` - Uses `Dockerfile.local`, runs PostgreSQL + FastAPI

**Use `docker-compose.local.yml` for the cleanest local setup!**

### Q: How do I see what's happening?

**View logs:**
```bash
# All logs
docker-compose -f docker-compose.local.yml logs

# Follow logs (live updates)
docker-compose -f docker-compose.local.yml logs -f

# Just FastAPI logs
docker-compose -f docker-compose.local.yml logs -f fastapi

# Just PostgreSQL logs
docker-compose -f docker-compose.local.yml logs -f postgres
```

### Q: How do I update my code without rebuilding?

Code is mounted as a volume, so changes are **automatically reflected**:

1. Edit your Python files
2. Restart just the FastAPI service:
   ```bash
   docker-compose -f docker-compose.local.yml restart fastapi
   ```

No rebuild needed! 🎉

**If you change `requirements.txt`, then rebuild:**
```bash
docker-compose -f docker-compose.local.yml up --build
```

## 📚 Quick Reference

### Essential Commands

```bash
# Start everything
docker-compose -f docker-compose.local.yml up

# Start in background
docker-compose -f docker-compose.local.yml up -d

# Stop everything
docker-compose -f docker-compose.local.yml down

# View status
docker-compose -f docker-compose.local.yml ps

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Restart after code changes
docker-compose -f docker-compose.local.yml restart fastapi

# Access database
docker-compose -f docker-compose.local.yml exec postgres psql -U alignuser -d aligndb

# Reset everything
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up --build
```

### Migration Commands

```bash
# Automated migration
./migrate_gcp_to_local.sh

# Manual export from GCP
PGPASSWORD="$GCP_PASSWORD" pg_dump -h "$GCP_HOST" -U "$GCP_USER" -d "$GCP_DB" -f backup.sql

# Manual import to local
cat backup.sql | docker-compose -f docker-compose.local.yml exec -T postgres psql -U alignuser -d aligndb
```

### Testing Commands

```bash
# Health check
curl http://localhost:8080/health

# Test API
curl http://localhost:8080/api/v1/students/

# Test storage endpoint
curl "http://localhost:8080/api/v1/generate-signed-url/?blob_name=test.txt"
```

## 🎯 Next Steps

1. **Start PostgreSQL**: `docker-compose -f docker-compose.local.yml up -d postgres`
2. **Migrate data**: `./migrate_gcp_to_local.sh`
3. **Verify**: Check tables and data
4. **Start app**: `docker-compose -f docker-compose.local.yml up`
5. **Test**: Access http://localhost:8080

## 📖 Documentation Files

- `README.local-setup.md` - Complete setup guide
- `DATA_MIGRATION_GUIDE.md` - Detailed migration instructions
- `MIGRATION_SUMMARY.md` - What changed in this branch
- `LOCAL_SETUP_FAQ.md` - This file
- `migrate_gcp_to_local.sh` - Automated migration script

## 🆘 Getting Help

If something doesn't work:

1. Check logs: `docker-compose -f docker-compose.local.yml logs`
2. Check containers: `docker-compose -f docker-compose.local.yml ps`
3. Reset: `docker-compose -f docker-compose.local.yml down -v && docker-compose -f docker-compose.local.yml up --build`
4. Check documentation files above
