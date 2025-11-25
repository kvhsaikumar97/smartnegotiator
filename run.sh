#!/bin/bash

# Smart Negotiator - Quick Start Script
# Run this script to start the application

echo "🤖 Smart Negotiator - Starting up..."
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Download from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Desktop."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please make sure it's in the project root."
    exit 1
fi

# Check if API key is configured
if grep -q "your-friend-should-get-their-own-key-here" .env; then
    echo "⚠️  API key not configured!"
    echo "   Please get a Gemini API key from: https://makersuite.google.com/app/apikey"
    echo "   Then edit the GEMINI_API_KEY in .env file"
    echo ""
    echo "   Do you want to continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "Aborted. Please configure your API key first."
        exit 1
    fi
fi

echo "🚀 Starting Docker containers..."
echo "   This may take 2-3 minutes on first run..."
echo ""

# Start the application
docker-compose up --build -d

# Wait a moment for startup
sleep 3

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Application started successfully!"
    echo "   🌐 Open your browser to: http://localhost:8501"
    echo ""
    echo "📝 To stop the app later, run: docker-compose down"
    echo "📊 To view logs, run: docker-compose logs app"
else
    echo ""
    echo "❌ Failed to start application. Check the logs:"
    echo "   docker-compose logs app"
    exit 1
fi</content>
<parameter name="filePath">/Users/saikumarkaparaju/Downloads/smartnegotiator/run.sh