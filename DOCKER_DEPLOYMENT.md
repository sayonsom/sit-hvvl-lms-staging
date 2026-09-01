# Virtual Lab - Docker Deployment Guide

This guide explains how to deploy the Virtual HV Lab application using Docker in your local environment.

## Prerequisites

- Docker (version 20.0 or higher)
- Docker Compose (version 2.0 or higher)
- Git (optional, for cloning the repository)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Extract the repository** (if you have a zip file) or clone it:
   ```bash
   # If using zip file
   unzip virtuallab.zip
   cd virtuallab
   
   # If cloning from repository
   git clone <repository-url>
   cd virtuallab
   ```

2. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env file with your specific configuration
   ```

3. **Build and run the application**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:3000`

### Option 2: Using Docker directly

1. **Build the Docker image**:
   ```bash
   docker build -t virtuallab .
   ```

2. **Run the container**:
   ```bash
   docker run -p 3000:80 \
     -e REACT_APP_API_URL=/api/v1 \
     -e REACT_APP_AUTH0_DOMAIN=your-auth0-domain \
     -e REACT_APP_AUTH0_CLIENT_ID=your-auth0-client-id \
     virtuallab
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:3000`

## Configuration

### Environment Variables

The application uses the following environment variables:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `REACT_APP_API_URL` | Backend API URL | `/api/v1` |
| `REACT_APP_AUTH0_DOMAIN` | Auth0 domain for authentication | `dev-o4fxv2xy7kvnxb0d.us.auth0.com` |
| `REACT_APP_AUTH0_CLIENT_ID` | Auth0 client ID | `R227TInzL2MGUwozJQiObpDauZ2yRTod` |
| `REACT_APP_MAPS_API` | Maps API key (optional) | (empty) |

### Customizing Configuration

1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your specific values:
   ```bash
   nano .env  # or use your preferred editor
   ```

3. Rebuild and restart the containers:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

## Application Architecture

The application is built with:
- **Frontend**: React 18 with Create React App
- **Styling**: Tailwind CSS with custom components
- **Authentication**: Auth0
- **3D Graphics**: Three.js with React Three Fiber
- **Maps**: Leaflet and Mapbox GL
- **Charts**: Highcharts
- **Server**: Nginx (in production container)

## Development vs Production

### Development Mode
For development, you can run the application in development mode:

```bash
# Install dependencies
npm install

# Start development server
npm start
```

This will start the development server on `http://localhost:3000` with hot reloading.

### Production Mode (Docker)
The Docker setup builds the application for production with:
- Optimized build bundle
- Nginx server for static file serving
- Gzip compression
- Security headers
- Health check endpoint

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Change the port in docker-compose.yml or stop the conflicting service
   docker-compose down
   # Edit docker-compose.yml to use a different port (e.g., 3001:80)
   docker-compose up
   ```

2. **Permission denied errors**:
   ```bash
   # Make sure Docker has appropriate permissions
   sudo chmod +x docker-entrypoint.sh
   ```

3. **Build failures**:
   ```bash
   # Clean Docker cache and rebuild
   docker system prune -f
   docker-compose build --no-cache
   ```

4. **Application not loading**:
   - Check if the container is running: `docker-compose ps`
   - Check logs: `docker-compose logs virtuallab`
   - Verify port mapping and firewall settings

### Checking Application Health

The application includes a health check endpoint:
```bash
curl http://localhost:3000/health
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs virtuallab

# Follow logs in real-time
docker-compose logs -f virtuallab
```

## Stopping the Application

```bash
# Stop and remove containers
docker-compose down

# Stop, remove containers, and remove volumes
docker-compose down -v

# Stop, remove everything including images
docker-compose down --rmi all -v
```

## Additional Notes

- The application uses CORS configuration for API access
- Auth0 is configured for authentication - you may need to update the configuration for your domain
- The application includes 3D visualization capabilities and may require WebGL support
- Maps functionality requires appropriate API keys for full functionality

For more detailed information about the application's features and API endpoints, refer to the main documentation.
