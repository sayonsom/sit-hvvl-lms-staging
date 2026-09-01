#!/bin/bash

# Migration Script: GCP to Local PostgreSQL
# This script migrates data from GCP Cloud SQL to local Docker PostgreSQL

set -e  # Exit on error

echo "=================================================="
echo "  GCP to Local PostgreSQL Migration Script"
echo "=================================================="
echo ""

# Configuration. Set these from a secure shell/session; do not commit real values.
GCP_HOST="${GCP_HOST:?Set GCP_HOST to the authorized Cloud SQL host}"
GCP_USER="${GCP_USER:-postgres}"
GCP_DB="${GCP_DB:-postgres}"
GCP_PASSWORD="${GCP_PASSWORD:?Set GCP_PASSWORD from the approved secret store}"

LOCAL_USER="alignuser"
LOCAL_DB="aligndb"
LOCAL_PASSWORD="${LOCAL_PASSWORD:-local-dev-password-change-me}"

BACKUP_FILE="gcp_backup_$(date +%Y%m%d_%H%M%S).sql"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Step 1: Start PostgreSQL container
echo "📦 Starting PostgreSQL container..."
docker-compose -f docker-compose.local.yml up -d postgres

echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose -f docker-compose.local.yml exec -T postgres pg_isready -U alignuser > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    echo "   Waiting... ($i/30)"
    sleep 2
done

# Check if PostgreSQL is ready
if ! docker-compose -f docker-compose.local.yml exec -T postgres pg_isready -U alignuser > /dev/null 2>&1; then
    echo "❌ Error: PostgreSQL failed to start"
    exit 1
fi

echo ""

# Step 2: Check if pg_dump is available
echo "🔍 Checking for pg_dump..."
if ! command -v pg_dump &> /dev/null; then
    echo "⚠️  Warning: pg_dump not found on your system"
    echo "   You can install it with: brew install libpq"
    echo ""
    echo "   Alternative: Export manually from GCP Console"
    echo "   Then run: cat your_export.sql | docker-compose -f docker-compose.local.yml exec -T postgres psql -U alignuser -d aligndb"
    exit 1
fi

echo "✅ pg_dump found: $(which pg_dump)"
echo ""

# Step 3: Export from GCP
echo "📤 Exporting data from GCP Cloud SQL..."
echo "   Host: $GCP_HOST"
echo "   Database: $GCP_DB"
echo ""

PGPASSWORD="$GCP_PASSWORD" pg_dump \
  -h "$GCP_HOST" \
  -U "$GCP_USER" \
  -d "$GCP_DB" \
  --no-owner \
  --no-acl \
  --verbose \
  -f "$BACKUP_FILE" 2>&1 | grep -E "^(pg_dump:|dumping|setting)"

if [ $? -eq 0 ]; then
    echo "✅ Export completed: $BACKUP_FILE"
    echo "   Size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    echo "❌ Error: Export failed"
    exit 1
fi

echo ""

# Step 4: Import to Local
echo "📥 Importing data to local PostgreSQL..."
echo "   Database: $LOCAL_DB"
echo ""

cat "$BACKUP_FILE" | docker-compose -f docker-compose.local.yml exec -T postgres \
  psql -U "$LOCAL_USER" -d "$LOCAL_DB" 2>&1 | grep -E "^(CREATE|ALTER|INSERT)"

if [ $? -eq 0 ] || [ ${PIPESTATUS[1]} -eq 0 ]; then
    echo "✅ Import completed successfully!"
else
    echo "⚠️  Import completed with warnings (this is often normal)"
fi

echo ""

# Step 5: Verify data
echo "🔍 Verifying migration..."
TABLE_COUNT=$(docker-compose -f docker-compose.local.yml exec -T postgres \
  psql -U "$LOCAL_USER" -d "$LOCAL_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

echo "   Tables found: $(echo $TABLE_COUNT | xargs)"

# List tables
echo ""
echo "📋 Tables in local database:"
docker-compose -f docker-compose.local.yml exec -T postgres \
  psql -U "$LOCAL_USER" -d "$LOCAL_DB" -c "\dt" | head -20

echo ""
echo "=================================================="
echo "✅ Migration completed!"
echo "=================================================="
echo ""
echo "📁 Backup file saved: $BACKUP_FILE"
echo ""
echo "🔗 Connection details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: $LOCAL_DB"
echo "   User: $LOCAL_USER"
echo "   Password: $LOCAL_PASSWORD"
echo ""
echo "🧪 Test the connection:"
echo "   psql -h localhost -p 5432 -U $LOCAL_USER -d $LOCAL_DB"
echo ""
echo "🚀 Start the full application:"
echo "   docker-compose -f docker-compose.local.yml up"
echo ""
