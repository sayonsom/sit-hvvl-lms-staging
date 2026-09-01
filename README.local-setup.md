# Local Development Setup (No GCP Dependencies)

This branch (`local-no-gcp`) provides a fully local development environment without any Google Cloud Platform (GCP) dependencies.

## Changes from Main Branch

### Removed Dependencies
- ❌ Google Cloud Storage (GCS)
- ❌ Google Cloud Secret Manager
- ❌ Google Cloud SDK
- ❌ `google-cloud-storage` Python package
- ❌ `google-cloud-secret-manager` Python package

### Added Features
- [ DONE ]Local file storage system (replaces GCS)
- [ DONE ]Local PostgreSQL database via Docker
- [ DONE ]Simplified Docker configuration
- [ DONE ]Environment-based configuration

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────────┐
│   Browser/      │      │   FastAPI        │      │   PostgreSQL        │
│   Frontend      │─────▶│   Backend        │─────▶│   (Docker)          │
│                 │      │   (Docker)       │      │                     │
└─────────────────┘      └──────────────────┘      └─────────────────────┘
                                 │
                                 ▼
                         ┌──────────────────┐
                         │  Local Storage   │
                         │  (/local_storage)│
                         └──────────────────┘
```

## Prerequisites

- Docker & Docker Compose
- Git

## Quick Start

### 1. Checkout the Branch
```bash
git checkout local-no-gcp
```

### 2. Start the Services
```bash
docker-compose -f docker-compose.local.yml up --build
```

This will:
- Start a PostgreSQL database on port 5432
- Start the FastAPI application on port 8080
- Create persistent volumes for both database and file storage

### 3. Verify the Setup

Check if services are running:
```bash
# Check health endpoint
curl http://localhost:8080/health

# Check if database is accessible
docker-compose -f docker-compose.local.yml exec postgres psql -U alignuser -d aligndb -c "SELECT version();"
```

## Configuration Files

### 1. `docker-compose.local.yml`
Main Docker Compose configuration for local development.

**Services:**
- `postgres`: PostgreSQL 13 database
- `fastapi`: FastAPI application

### 2. `Dockerfile.local`
Dockerfile without GCP SDK and dependencies.

### 3. `.env.local.nogcp`
Environment variables for local development (no GCP credentials needed).

### 4. `app/storage/local_storage.py`
Local storage implementation that replaces Google Cloud Storage.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `local` | Environment mode |
| `DB_HOST` | `postgres` | Database host |
| `DB_PORT` | `5432` | Database port |
| `DB_NAME` | `aligndb` | Database name |
| `DB_USER` | `alignuser` | Database user |
| `DB_PASSWORD` | `local-dev-password-change-me` | Database password |
| `LOCAL_STORAGE_PATH` | `/code/local_storage` | Local file storage path |
| `STORAGE_BUCKET_NAME` | `align-hvl-2024-release1` | Bucket name (used as subdirectory) |

## API Endpoints

### Storage Endpoints

#### Generate Signed URL (Local)
```bash
GET /api/v1/generate-signed-url/?blob_name=path/to/file.glb
```

Returns a local URL to access the file:
```json
{
  "url": "/api/v1/local-storage/encoded_path"
}
```

#### Serve Local File
```bash
GET /api/v1/local-storage/{encoded_path}
```

Serves the actual file from local storage.

## File Storage Structure

Files are stored in the following structure:
```
/code/local_storage/
└── align-hvl-2024-release1/        # Bucket name
    └── exp3_ferranti_effect/       # Blob path
        └── ferranti_effect.glb     # File
```

## Adding Files to Local Storage

### Option 1: Using Docker Volume
Copy files directly to the volume:
```bash
docker cp /path/to/local/file.glb <container_id>:/code/local_storage/align-hvl-2024-release1/path/to/file.glb
```

### Option 2: Mount Local Directory
Update `docker-compose.local.yml` to mount a local directory:
```yaml
volumes:
  - ./my-local-files:/code/local_storage/align-hvl-2024-release1
```

## Database Management

### Access PostgreSQL
```bash
docker-compose -f docker-compose.local.yml exec postgres psql -U alignuser -d aligndb
```

### Run SQL Scripts
```bash
docker-compose -f docker-compose.local.yml exec postgres psql -U alignuser -d aligndb -f /docker-entrypoint-initdb.d/CreateInitialTables.sql
```

### Backup Database
```bash
docker-compose -f docker-compose.local.yml exec postgres pg_dump -U alignuser aligndb > backup.sql
```

### Restore Database
```bash
cat backup.sql | docker-compose -f docker-compose.local.yml exec -T postgres psql -U alignuser -d aligndb
```

## Troubleshooting

### Container Fails to Start
```bash
# View logs
docker-compose -f docker-compose.local.yml logs fastapi

# Rebuild from scratch
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up --build
```

### Database Connection Issues
```bash
# Check if PostgreSQL is ready
docker-compose -f docker-compose.local.yml exec postgres pg_isready -U alignuser

# Check environment variables
docker-compose -f docker-compose.local.yml exec fastapi env | grep DB_
```

### File Not Found Errors
```bash
# Check local storage structure
docker-compose -f docker-compose.local.yml exec fastapi ls -la /code/local_storage/

# Create bucket directory
docker-compose -f docker-compose.local.yml exec fastapi mkdir -p /code/local_storage/align-hvl-2024-release1
```

## Development Workflow

### 1. Make Code Changes
Edit files on your local machine. Changes are automatically synced to the container via volume mount.

### 2. Restart Services
```bash
docker-compose -f docker-compose.local.yml restart fastapi
```

### 3. View Logs
```bash
docker-compose -f docker-compose.local.yml logs -f fastapi
```

### 4. Stop Services
```bash
docker-compose -f docker-compose.local.yml down
```

## Migrating from GCP to Local

If you're migrating existing data from GCP:

### 1. Download Files from GCS
```bash
gsutil -m cp -r gs://align-hvl-2024-release1/* ./local_storage/align-hvl-2024-release1/
```

### 2. Copy to Docker Volume
```bash
docker cp ./local_storage/align-hvl-2024-release1 <container_id>:/code/local_storage/
```

### 3. Export Database from Cloud SQL
```bash
gcloud sql export sql INSTANCE_NAME gs://BUCKET/db-backup.sql --database=aligndb
gsutil cp gs://BUCKET/db-backup.sql ./
```

### 4. Import to Local PostgreSQL
```bash
cat db-backup.sql | docker-compose -f docker-compose.local.yml exec -T postgres psql -U alignuser -d aligndb
```

## Testing

### Run Health Check
```bash
curl http://localhost:8080/health
```

### Test Storage Endpoint
```bash
curl "http://localhost:8080/api/v1/generate-signed-url/?blob_name=test.txt"
```

### Test Database Connection
```bash
curl http://localhost:8080/api/v1/students/
```

## Production Considerations

⚠️ **This setup is for local development only!**

For production deployment:
- Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- Use cloud storage (S3, GCS, Azure Blob)
- Implement proper authentication and authorization
- Use environment-specific secrets management
- Enable SSL/TLS for all connections
- Set up proper monitoring and logging

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
