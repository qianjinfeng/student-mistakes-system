#!/bin/bash

# Docker Network Fix - Frontend Connection Issues

echo "🔧 Fixing Docker networking issues between frontend and backend..."

# Stop all services
echo "📋 Stopping all services..."
docker compose down

# Remove orphaned containers and networks
echo "🧹 Cleaning up..."
docker compose down --remove-orphans
docker network prune -f

# Rebuild with networking fixes
echo "🏗️ Rebuilding services with network configuration..."
docker compose up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker compose ps

# Check backend health
echo "🏥 Checking backend health..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    else
        echo "⏳ Waiting for backend... ($i/10)"
        sleep 2
    fi
done

# Check frontend connection to backend
echo "🔗 Testing frontend-backend connectivity..."
for i in {1..5}; do
    if curl -f http://localhost:4173/api/health >/dev/null 2>&1; then
        echo "✅ Frontend can connect to backend!"
        break
    else
        echo "⏳ Waiting for frontend-backend connection... ($i/5)"
        sleep 3
    fi
done

echo ""
echo "🎉 Docker services should be running properly now!"
echo ""
echo "📋 Services:"
echo "   Frontend: http://localhost:4173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 To view logs:"
echo "   docker compose logs -f frontend"
echo "   docker compose logs -f backend"