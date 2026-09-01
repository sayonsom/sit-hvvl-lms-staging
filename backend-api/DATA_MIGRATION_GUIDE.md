# Data Migration Guide: GCP to Local PostgreSQL

This guide explains how to migrate your data from Google Cloud SQL to a local Docker PostgreSQL database.

## 📋 Overview

### Current Setup (GCP)
- **Host**: set `GCP_HOST` from the approved secret store
- **Database**: set `GCP_DB`
- **User**: set `GCP_USER`
- **Port**: `5432`

### New Setup (Local Docker)
- **Host**: `localhost` (Docker container)
- **Database**: `aligndb`
- **User**: `alignuser`
- **Password**: `local-dev-password-change-me`
- **Port**: `5432`
- **Container**: Runs PostgreSQL 13 in Docker

## 🎯 Migration Options

You have **3 options** for migrating data:

### Option 1: Automated Script (Recommended) ⚡

I've created a script that does everything automatically:

```bash
./migrate_gcp_to_local.sh
```

**What it does:**
1. ✅ Starts local PostgreSQL container
2. ✅ Exports data from GCP using `pg_dump`
3. ✅ Imports data to local PostgreSQL
4. ✅ Verifies the migration
5. ✅ Creates a backup file for safety

**Prerequisites:**
```bash
# Install PostgreSQL client tools (for pg_dump)
brew install libpq

# Add to PATH (add to ~/.zshrc for permanent)
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
```

### Option 2: Manual Export/Import 📦

If you prefer manual control:

#### Step 1: Start Local PostgreSQL
```bash
docker-compose -f docker-compose.local.yml up -d postgres

# Wait for it to be ready
docker-compose -f docker-compose.local.yml exec postgres pg_isready -U alignuser
```

#### Step 2: Export from GCP
```bash
# Using pg_dump (if installed)
PGPASSWORD="$GCP_PASSWORD" pg_dump \
  -h "$GCP_HOST" \
  -U "$GCP_USER" \
  -d "$GCP_DB" \
  --no-owner \
  --no-acl \
  -f gcp_backup.sql
```

#### Step 3: Import to Local
```bash
cat gcp_backup.sql | docker-compose -f docker-compose.local.yml exec -T postgres \
  psql -U alignuser -d aligndb
```

### Option 3: Using GCP Console 🌐

If you can't connect directly to GCP database:

#### Step 1: Export from GCP Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/sql/instances)
2. Select your Cloud SQL instance
3. Click **"Export"** → **"SQL"**
4. Choose destination (Cloud Storage bucket)
5. Download the exported `.sql` file

#### Step 2: Import to Local

```bash
# Start PostgreSQL
docker-compose -f docker-compose.local.yml up -d postgres

# Import the downloaded file
cat ~/Downloads/your_export.sql | docker-compose -f docker-compose.local.yml exec -T postgres \
  psql -U alignuser -d aligndb
```

## 🔍 Verification Steps

After migration, verify your data:

### 1. Check Tables
```bash
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb -c "\dt"
```

### 2. Count Records
```bash
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb -c "SELECT COUNT(*) FROM students;"
```

### 3. Test API Connection
```bash
# Start full application
docker-compose -f docker-compose.local.yml up

# Test in another terminal
curl http://localhost:8080/api/v1/students/
```

## 🗂️ Migrating Files from Google Cloud Storage

If you also have files in GCS that need to be migrated:

### Step 1: Download from GCS

```bash
# Install gcloud CLI if not installed
# brew install google-cloud-sdk

# Authenticate
gcloud auth login

# Download files
gsutil -m cp -r gs://align-hvl-2024-release1/* ./local_storage_backup/
```

### Step 2: Copy to Docker Volume

```bash
# Start the containers
docker-compose -f docker-compose.local.yml up -d

# Get the FastAPI container ID
CONTAINER_ID=$(docker-compose -f docker-compose.local.yml ps -q fastapi)

# Copy files to container
docker cp ./local_storage_backup/. $CONTAINER_ID:/code/local_storage/align-hvl-2024-release1/

# Verify
docker-compose -f docker-compose.local.yml exec fastapi \
  ls -la /code/local_storage/align-hvl-2024-release1/
```

### Alternative: Mount Local Directory

Edit `docker-compose.local.yml` and add a bind mount:

```yaml
fastapi:
  volumes:
    - .:/code
    - ./local_storage_backup:/code/local_storage/align-hvl-2024-release1
```

## 🛠️ Troubleshooting

### Problem: pg_dump not found

**Solution:**
```bash
# Install PostgreSQL client tools
brew install libpq

# Add to PATH
export PATH="/opt/homebrew/opt/libpq/bin:$PATH"

# Make permanent (add to ~/.zshrc)
echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc
```

### Problem: Can't connect to GCP database

**Possible causes:**
1. IP not whitelisted in GCP Cloud SQL
2. VPN or firewall blocking connection
3. Cloud SQL Proxy needed

**Solutions:**

#### Option A: Whitelist Your IP
1. Go to Cloud SQL instance in GCP Console
2. Click "Connections" → "Networking"
3. Add your IP to "Authorized networks"

#### Option B: Use Cloud SQL Proxy
```bash
# Download Cloud SQL Proxy
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.0/cloud-sql-proxy.darwin.amd64

chmod +x cloud-sql-proxy

# Run proxy (replace CONNECTION_NAME)
./cloud-sql-proxy PROJECT:REGION:INSTANCE

# Then connect through localhost:5432
```

#### Option C: Export via GCP Console
Use Option 3 above (GCP Console export)

### Problem: Import fails with errors

**Common errors and fixes:**

#### "role 'postgres' does not exist"
```bash
# This is normal - the script uses --no-owner to avoid this
# Data is still imported correctly
```

#### "permission denied"
```bash
# Edit the SQL file and remove these lines:
sed -i '' '/ALTER.*OWNER/d' gcp_backup.sql
sed -i '' '/GRANT/d' gcp_backup.sql
```

#### "database 'aligndb' does not exist"
```bash
# Create database first
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -c "CREATE DATABASE aligndb;"
```

### Problem: Docker container won't start

```bash
# Check logs
docker-compose -f docker-compose.local.yml logs postgres

# Reset everything
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up
```

### Problem: Port 5432 already in use

**If you have PostgreSQL installed locally:**

```bash
# Stop local PostgreSQL
brew services stop postgresql@14  # or your version

# Or change the port in docker-compose.local.yml
# Change: "5432:5432" to "5433:5432"
# Then connect to localhost:5433
```

## 📊 Data Comparison

To verify data integrity, compare record counts:

### On GCP:
```bash
PGPASSWORD="$GCP_PASSWORD" psql \
  -h "$GCP_HOST" \
  -U "$GCP_USER" \
  -d "$GCP_DB" \
  -c "SELECT 'students', COUNT(*) FROM students UNION ALL
      SELECT 'courses', COUNT(*) FROM courses UNION ALL
      SELECT 'instructors', COUNT(*) FROM instructors;"
```

### On Local:
```bash
docker-compose -f docker-compose.local.yml exec postgres \
  psql -U alignuser -d aligndb \
  -c "SELECT 'students', COUNT(*) FROM students UNION ALL
      SELECT 'courses', COUNT(*) FROM courses UNION ALL
      SELECT 'instructors', COUNT(*) FROM instructors;"
```

Compare the counts to ensure all data migrated successfully.

## 🔐 Security Notes

1. **Password Security**: The local database uses simple passwords (`local-dev-password-change-me`) - this is OK for local development but **never use in production**

2. **Backup the GCP Export**: Keep the exported `.sql` file as a backup:
   ```bash
   cp gcp_backup_*.sql ~/Desktop/backups/
   ```

3. **Data Sensitivity**: If your data contains sensitive information, delete the backup file after successful migration:
   ```bash
   rm gcp_backup_*.sql
   ```

## 📝 Post-Migration Checklist

- [ ] Local PostgreSQL is running in Docker
- [ ] Data imported successfully (no critical errors)
- [ ] Table counts match GCP database
- [ ] API endpoints return data correctly
- [ ] Files migrated from GCS (if applicable)
- [ ] Application runs without errors
- [ ] GCP backup file saved securely

## 🎉 Success Indicators

Your migration is successful when:

1. ✅ `docker-compose -f docker-compose.local.yml ps` shows both containers running
2. ✅ `curl http://localhost:8080/health` returns `{"status":"200 ok"}`
3. ✅ API endpoints return your actual data
4. ✅ No database connection errors in logs

## 💡 Tips

1. **Keep GCP Running**: Don't delete GCP database immediately - keep it as backup for a few days

2. **Regular Backups**: Create local backups:
   ```bash
   docker-compose -f docker-compose.local.yml exec postgres \
     pg_dump -U alignuser aligndb > backup_$(date +%Y%m%d).sql
   ```

3. **Test Thoroughly**: Test all features before relying fully on local setup

4. **Performance**: Local PostgreSQL on Docker is usually faster than remote GCP for development

## 🔄 Switching Between Environments

The code already supports this via the `ENVIRONMENT` variable:

```bash
# Use local database
export ENVIRONMENT=local

# Use GCP database
export ENVIRONMENT=production

# Or in docker-compose, it's already set to 'local'
```

## 📞 Need Help?

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.local.yml logs`
2. Verify containers are running: `docker-compose -f docker-compose.local.yml ps`
3. Check database connection: `docker-compose -f docker-compose.local.yml exec postgres psql -U alignuser -d aligndb -c "SELECT version();"`

## 🎯 Quick Commands Reference

```bash
# Start everything
docker-compose -f docker-compose.local.yml up

# Stop everything
docker-compose -f docker-compose.local.yml down

# Reset everything (deletes data!)
docker-compose -f docker-compose.local.yml down -v

# View logs
docker-compose -f docker-compose.local.yml logs -f

# Access PostgreSQL
docker-compose -f docker-compose.local.yml exec postgres psql -U alignuser -d aligndb

# Backup database
docker-compose -f docker-compose.local.yml exec postgres pg_dump -U alignuser aligndb > backup.sql

# Restore database
cat backup.sql | docker-compose -f docker-compose.local.yml exec -T postgres psql -U alignuser -d aligndb
```
