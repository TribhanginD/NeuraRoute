#!/bin/bash

# NeuraRoute Startup Script
# AI-Native Hyperlocal Logistics System

echo "🚀 Starting NeuraRoute - AI-Native Logistics System"
echo "=================================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your API keys before continuing"
    echo "   Required: OPENAI_API_KEY, ANTHROPIC_API_KEY, MAPBOX_TOKEN"
    read -p "Press Enter after updating .env file..."
fi

# Start database and Redis
echo "🗄️  Starting database and Redis..."
docker-compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Start backend
echo "🔧 Starting backend API..."
docker-compose up -d backend

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 15

# Start frontend
echo "🎨 Starting frontend..."
docker-compose up -d frontend

echo ""
echo "✅ NeuraRoute is starting up!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔌 API Docs: http://localhost:8000/docs"
echo "📈 Health Check: http://localhost:8000/health"
echo ""
echo "🔄 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "🎯 The system will take a few minutes to fully initialize."
echo "   Check the health endpoint to confirm all services are running." 