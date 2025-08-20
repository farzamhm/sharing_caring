#!/bin/bash

# Local development startup script

set -e

echo "🏠 Starting Neighborhood Food Sharing Platform Locally"
echo "=================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating default configuration...${NC}"
    cp .env.example .env 2>/dev/null || echo "Please create a .env file with your configuration"
fi

echo -e "${BLUE}📋 Starting services with Docker Compose...${NC}"

# Start the infrastructure services (PostgreSQL, Redis)
echo -e "${YELLOW}🗄️  Starting database and cache services...${NC}"
docker-compose up -d postgres redis

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
timeout 30 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 2; done'

echo -e "${GREEN}✅ Infrastructure services are ready!${NC}"

# Option to start services
echo ""
echo "Choose how to start the application:"
echo "1) Docker Compose (recommended for full stack)"
echo "2) Local Python (for development)"
echo "3) Just infrastructure (if you want to run app manually)"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo -e "${BLUE}🚀 Starting full application stack with Docker...${NC}"
        docker-compose up -d
        
        echo ""
        echo -e "${GREEN}🎉 Application is starting up!${NC}"
        echo ""
        echo "📍 Services available at:"
        echo "  • API: http://localhost:8000"
        echo "  • Admin Dashboard: http://localhost:8000/admin"
        echo "  • API Docs: http://localhost:8000/docs"
        echo "  • PostgreSQL: localhost:5432"
        echo "  • Redis: localhost:6379"
        echo ""
        echo "📝 Useful commands:"
        echo "  • View logs: docker-compose logs -f"
        echo "  • Stop services: docker-compose down"
        echo "  • Restart API: docker-compose restart api"
        echo ""
        echo "⏳ Waiting for API to be ready..."
        
        # Wait for API to respond
        timeout 60 bash -c '
        while true; do
            if curl -s http://localhost:8000/health >/dev/null 2>&1; then
                break
            fi
            echo "Waiting for API..."
            sleep 3
        done
        '
        
        echo -e "${GREEN}✅ API is ready at http://localhost:8000${NC}"
        
        # Show logs
        echo ""
        echo "📊 Recent logs:"
        docker-compose logs --tail=20 api
        ;;
        
    2)
        echo -e "${BLUE}🐍 Setting up for local Python development...${NC}"
        
        # Check Python version
        python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
        echo "Python version: $python_version"
        
        # Install dependencies if not installed
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        echo "Activating virtual environment..."
        source venv/bin/activate
        
        echo "Installing/updating dependencies..."
        pip install -r requirements.txt
        
        # Update .env for local development
        sed -i.bak 's/DATABASE_URL=.*/DATABASE_URL=postgresql+asyncpg:\/\/postgres:postgres@localhost:5432\/sharing_platform/' .env
        sed -i.bak 's/REDIS_URL=.*/REDIS_URL=redis:\/\/localhost:6379\/0/' .env
        
        echo -e "${GREEN}✅ Environment ready!${NC}"
        echo ""
        echo "🚀 To start the API server:"
        echo "  source venv/bin/activate"
        echo "  python run_dev.py"
        echo ""
        echo "🧪 To run tests:"
        echo "  source venv/bin/activate"
        echo "  ./scripts/test.sh"
        ;;
        
    3)
        echo -e "${BLUE}🔧 Infrastructure-only mode${NC}"
        echo ""
        echo -e "${GREEN}✅ PostgreSQL and Redis are running!${NC}"
        echo ""
        echo "📍 Services:"
        echo "  • PostgreSQL: localhost:5432"
        echo "  • Redis: localhost:6379"
        echo ""
        echo "🚀 To start the API manually:"
        echo "  python run_dev.py"
        ;;
        
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎯 Setup complete! Happy coding!${NC}"