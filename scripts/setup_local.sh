#!/bin/bash

# Quick setup script for local development without Docker

set -e

echo "🏠 Setting up Neighborhood Food Sharing Platform (Local Mode)"
echo "=========================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python version
echo -e "${BLUE}🐍 Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+ first.${NC}"
    exit 1
fi

python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [[ $major_version -lt 3 ]] || [[ $major_version -eq 3 && $minor_version -lt 11 ]]; then
    echo -e "${RED}❌ Python 3.11+ required. Found: $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $python_version found${NC}"

# Check for PostgreSQL
echo -e "${BLUE}🗄️  Checking PostgreSQL...${NC}"
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL client found${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL client not found. You may need to install it.${NC}"
    echo "On macOS: brew install postgresql"
    echo "On Ubuntu: sudo apt-get install postgresql-client"
fi

# Check for Redis
echo -e "${BLUE}🔄 Checking Redis...${NC}"
if command -v redis-cli &> /dev/null; then
    echo -e "${GREEN}✅ Redis client found${NC}"
else
    echo -e "${YELLOW}⚠️  Redis client not found. You may need to install it.${NC}"
    echo "On macOS: brew install redis"
    echo "On Ubuntu: sudo apt-get install redis-tools"
fi

# Create virtual environment
echo -e "${BLUE}🌐 Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Create uploads directory
mkdir -p uploads
echo -e "${GREEN}✅ Uploads directory created${NC}"

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}⚙️  Creating environment configuration...${NC}"
    cat > .env << 'EOF'
# Environment Configuration for Local Development

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database Configuration (update these for your local setup)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sharing_platform

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=local-development-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# File Storage
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
EOF
    echo -e "${GREEN}✅ Environment file created${NC}"
else
    echo -e "${YELLOW}⚠️  Environment file already exists${NC}"
fi

# Database setup instructions
echo ""
echo -e "${BLUE}🗄️  Database Setup Instructions:${NC}"
echo "1. Make sure PostgreSQL is running locally"
echo "2. Create the database:"
echo "   createdb sharing_platform"
echo "3. The application will create tables automatically on first run"
echo ""

echo -e "${BLUE}🔄 Redis Setup Instructions:${NC}"
echo "1. Make sure Redis is running locally:"
echo "   redis-server"
echo "2. Test connection:"
echo "   redis-cli ping"
echo ""

echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "🚀 To start the application:"
echo "   source venv/bin/activate"
echo "   python run_dev.py"
echo ""
echo "🧪 To run tests:"
echo "   source venv/bin/activate"
echo "   ./scripts/test.sh"
echo ""
echo "📊 The application will be available at:"
echo "   • API: http://localhost:8000"
echo "   • Admin Dashboard: http://localhost:8000/admin"
echo "   • API Docs: http://localhost:8000/docs"