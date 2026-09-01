# Local Development Setup Guide

This guide explains how to run the Align Backend APIs in a local development environment with PostgreSQL.

## Prerequisites

- Docker
- Docker Compose

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Start the local environment:**
   ```bash
   docker-compose -f docker-compose.local.yml up --build
   ```

2. **Access the application:**
   - FastAPI: http://localhost:8080
   - FastAPI Docs: http://localhost:8080/docs
   - PostgreSQL: localhost:5432

3. **Stop the environment:**
   ```bash
   docker-compose -f docker-compose.local.yml down
   ```

4. **Clean up (removes volumes):**
   ```bash
   docker-compose -f docker-compose.local.yml down -v
   ```

### Option 2: Using Dockerfile.SITLocal directly

1. **Build the image:**
   ```bash
   docker build -f Dockerfile.SITLocal -t align-local .
   ```

2. **Run PostgreSQL separately:**
   ```bash
   docker run -d \
     --name postgres-local \
     -e POSTGRES_DB=aligndb \
     -e POSTGRES_USER=alignuser \
     -e POSTGRES_PASSWORD=local-dev-password-change-me \
     -p 5432:5432 \
     postgres:13
   ```

3. **Run the FastAPI application:**
   ```bash
   docker run -p 8080:8080 \
     --link postgres-local:postgres \
     -e DB_HOST=postgres \
     -e DB_USER=alignuser \
     -e DB_PASSWORD=local-dev-password-change-me \
     -e DB_NAME=aligndb \
     -e ENVIRONMENT=local \
     align-local
   ```

## Local Database Configuration

The local setup uses the following database configuration:

- **Host:** postgres (when using docker-compose) or localhost
- **Port:** 5432
- **Database:** aligndb
- **Username:** alignuser
- **Password:** local-dev-password-change-me

## Environment Variables

The following environment variables are set for local development:

- `ENVIRONMENT=local` - Tells the application to use local database settings
- `DB_HOST=postgres` - PostgreSQL host
- `DB_PORT=5432` - PostgreSQL port
- `DB_NAME=aligndb` - Database name
- `DB_USER=alignuser` - Database user
- `DB_PASSWORD=local-dev-password-change-me` - Database password

## Database Initialization

If you have a `sql/CreateInitialTables.sql` file, it will be automatically executed when the PostgreSQL container starts for the first time.

## Development Workflow

1. **Make code changes** in your local files
2. **Rebuild and restart** the containers:
   ```bash
   docker-compose -f docker-compose.local.yml up --build
   ```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Check if PostgreSQL is running:
   ```bash
   docker-compose -f docker-compose.local.yml ps
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose -f docker-compose.local.yml logs postgres
   ```

3. Check FastAPI logs:
   ```bash
   docker-compose -f docker-compose.local.yml logs fastapi
   ```

### Reset Database

To reset the database (removes all data):

```bash
docker-compose -f docker-compose.local.yml down -v
docker-compose -f docker-compose.local.yml up --build
```

## Production vs Local

The application automatically detects the environment based on the `ENVIRONMENT` variable:

- **Local (`ENVIRONMENT=local`):** Uses local PostgreSQL configuration
- **Production (default):** Uses the existing production database configuration

## File Structure

- `Dockerfile.SITLocal` - Docker configuration for local development
- `docker-compose.local.yml` - Docker Compose configuration for local development
- `.env.local` - Local environment variables template
- `app/db/connection.py` - Updated to support both local and production environments
