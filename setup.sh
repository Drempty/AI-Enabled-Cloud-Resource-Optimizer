#!/bin/bash

# Cloud Optimizer Setup Script
# This script initializes the project and creates sample data

set -e

echo "🚀 Cloud Resource Optimizer - Setup Script"
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please update with your configurations if needed."
else
    echo "✅ .env file already exists"
fi

# Build and start containers
echo ""
echo "🏗️  Building Docker containers..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if backend is running
echo "🔍 Checking backend health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend might not be ready yet. Please check with: docker-compose logs backend"
fi

# Check if frontend is accessible
echo "🔍 Checking frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend might not be ready yet. Please check with: docker-compose logs frontend"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart: docker-compose restart"
echo ""
echo "💡 To generate sample data, run:"
echo "   docker exec -it cloud-optimizer-backend python -c \""
echo "   from app.core.database import AsyncSessionLocal"
echo "   from app.utils.data_generator import DataGenerator"
echo "   import asyncio"
echo "   async def setup():"
echo "       async with AsyncSessionLocal() as db:"
echo "           resources = await DataGenerator.create_sample_resources(db)"
echo "           for r in resources:"
echo "               await DataGenerator.populate_sample_metrics(db, r.id, 168, 'normal')"
echo "   asyncio.run(setup())"
echo "   \""
echo ""
echo "🎉 Happy optimizing!"
