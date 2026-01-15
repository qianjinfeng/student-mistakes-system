# Docker Networking Fix - Frontend/Backend Connection Issues

## 🚨 Problem Identified

Frontend logs showed repeated connection errors:
```
Error: connect ECONNREFUSED ::1:8000
```

**Root Cause**: Frontend container trying to connect to `localhost:8000`, but in Docker containers, `localhost` refers to the container itself, not the backend service.

## 🔧 Solution Implemented

### 1. **Fixed Vite Configuration** (`frontend/vite.config.ts`)
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // For local development
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://backend:8000',  // For Docker
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

### 2. **Updated Docker Compose** (`docker-compose.yml`)

#### Network Configuration
```yaml
networks:
  app-network:
    driver: bridge

services:
  backend:
    networks:
      - app-network
    
  frontend:
    networks:
      - app-network
    environment:
      - VITE_API_URL=http://backend:8000  # Use service name
```

#### Service Dependencies
```yaml
frontend:
  depends_on:
    backend:
      condition: service_healthy  # Wait for backend to be ready
```

#### Health Checks
```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### 3. **Enhanced Backend Dockerfile** (`backend/Dockerfile`)
```dockerfile
# Add curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

## 🚀 Quick Fix Commands

### Option 1: Use the Automated Script
```bash
./fix-docker-network.sh
```

### Option 2: Manual Commands
```bash
# Stop all services
docker-compose down

# Clean up networks
docker-compose down --remove-orphans
docker network prune -f

# Rebuild with networking fixes
docker-compose up -d --build

# Wait for services
sleep 10

# Check status
docker-compose ps
```

### Option 3: Quick Restart
```bash
# If services already exist, just restart with new config
docker-compose down
docker-compose up -d
```

## 📋 Service URLs After Fix

- **Frontend**: http://localhost:4173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Verification Steps

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "service": "student-mistakes-api"}
```

### 2. Check Frontend-Backend Connection
```bash
curl http://localhost:4173/api/health
# Expected: Same health response (proxied through frontend)
```

### 3. Check Docker Logs
```bash
# Frontend logs
docker-compose logs -f frontend

# Backend logs
docker-compose logs -f backend
```

### 4. Test Image Upload
```bash
# Test the specific endpoint that was failing
curl -X POST "http://localhost:4173/api/mistakes/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_image.jpg"
```

## 🎯 Key Changes Summary

| File | Change | Reason |
|------|---------|---------|
| `vite.config.ts` | Added `preview.proxy` config with service name | Fix Docker connectivity |
| `docker-compose.yml` | Added `networks` section | Ensure service discovery |
| `docker-compose.yml` | Updated `VITE_API_URL` to use `backend:8000` | Use Docker service names |
| `docker-compose.yml` | Added health checks | Ensure backend ready before frontend |
| `backend/Dockerfile` | Added `curl` installation | Enable health checks |
| `docker-compose.yml` | Added network dependencies | Ensure proper startup order |

## 🐛 Troubleshooting

### If Issues Persist:

1. **Check Network Names**
   ```bash
   docker network ls
   docker network inspect student-mistakes-system_app-network
   ```

2. **Verify Service Communication**
   ```bash
   # Exec into frontend container
   docker-compose exec frontend ping backend
   ```

3. **Check Environment Variables**
   ```bash
   docker-compose exec frontend env | grep VITE_API_URL
   docker-compose exec backend env | grep DATABASE_URL
   ```

4. **Reset Everything**
   ```bash
   # Complete reset
   docker-compose down -v --remove-orphans
   docker system prune -f
   docker-compose up -d --build
   ```

## ✅ Expected Result

After applying these fixes:

- ✅ **Frontend connects to backend** without ECONNREFUSED errors
- ✅ **API calls work** through the proxy
- ✅ **Image uploads succeed** with Qwen3-vl-plus analysis
- ✅ **Health checks pass** for all services
- ✅ **Docker networking** properly configured with service names

**The frontend should now successfully connect to the backend API!** 🎉