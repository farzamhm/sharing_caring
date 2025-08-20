# Neighborhood Sharing Platform - MVP

A Telegram bot-based platform for neighborhood food sharing built with Python, FastAPI, and PostgreSQL.

## 🏠 Overview

This platform enables neighbors to share excess food within their residential building through a user-friendly Telegram bot interface. The system promotes community building while reducing food waste through a credit-based exchange system.

### Key Features
- 📱 **Telegram Bot Interface** - Easy-to-use conversational interface
- 🏢 **Building-Based Communities** - Secure, resident-only food sharing
- ⭐ **Credit System** - Fair exchange mechanism with starter credits
- 📞 **Phone Verification** - Enhanced security and trust
- 🛡️ **Safety Guidelines** - Built-in food safety best practices
- 📊 **Admin Dashboard** - Building management and monitoring tools

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
git clone <repository-url>
cd sharing_caring
python setup_dev.py
```

### Option 2: Docker Setup
```bash
# Start all services
docker-compose up

# Or just infrastructure
docker-compose up postgres redis

# API and bot separately
python run_dev.py  # API server
python run_bot.py  # Telegram bot
```

### Option 3: Manual Setup
```bash
# 1. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 4. Set up database
createdb sharing_platform
createdb sharing_platform_test
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
python scripts/init_db.py

# 5. Start services
python run_dev.py  # API (port 8000)
python run_bot.py  # Bot
```

## 📋 Development Status

**Current Phase**: MVP Core Features Complete 🎉

### ✅ Completed Features
- **Infrastructure**
  - Python 3.11+ FastAPI backend with async SQLAlchemy
  - PostgreSQL database with comprehensive models  
  - Redis for caching and session management
  - Docker containerization setup
  
- **User Management**
  - Telegram-based authentication
  - Phone number verification with SMS
  - Building assignment and verification
  - User profiles with dietary restrictions
  
- **Database Models**
  - Users, Buildings, Foods, Exchanges, Credits
  - Relationships and constraints properly defined
  - Alembic migrations configured
  
- **API Endpoints**
  - RESTful API with OpenAPI documentation
  - User registration and profile management
  - Phone verification workflow
  - Health checks and monitoring
  
- **Telegram Bot**
  - Conversation-based registration flow
  - Menu system and command handlers
  - Phone number collection and verification
  - Help system and user guidance

### 🔄 In Progress
- **Food Posting & Discovery**
  - Photo upload and storage
  - Category-based food classification
  - Search and filtering capabilities
  - Allergen disclosure system

### 📋 Next Phase
- **Exchange Coordination**
  - Claiming and unclaiming food
  - Pickup coordination messaging
  - Exchange confirmation system
  - Credit transfer mechanisms
  
- **Admin Dashboard**
  - Web interface for building management
  - User and exchange monitoring
  - Safety incident reporting
  - System analytics
  
- **Testing & Quality**
  - Unit and integration tests
  - Bot conversation testing
  - Performance optimization
  - Security audit

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │    FastAPI       │    │   PostgreSQL    │
│                 │◄──►│    Backend       │◄──►│    Database     │
│  - Commands     │    │  - REST API      │    │  - Users        │
│  - Conversations│    │  - Business      │    │  - Buildings    │
│  - Notifications│    │    Logic         │    │  - Foods        │
└─────────────────┘    │  - Validation    │    │  - Exchanges    │
                       └──────────────────┘    │  - Credits      │
                                ▲              └─────────────────┘
                                │
                       ┌──────────────────┐    
                       │      Redis       │    
                       │                  │    
                       │  - Sessions      │    
                       │  - Rate Limiting │    
                       │  - Caching       │    
                       └──────────────────┘    
```

## 📖 API Documentation

When running locally:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health
- **Ready Check**: http://localhost:8000/health/ready

### Key Endpoints
```
POST /users/                     # Create user
GET  /users/me                   # Current user profile
PATCH /users/me                  # Update profile
POST /users/verify-phone         # Request phone verification
POST /users/verify-phone/confirm # Confirm verification code

GET  /buildings/                 # List buildings
GET  /foods/                     # Browse available food
POST /foods/                     # Post food item
POST /foods/{id}/claim           # Claim food

GET  /exchanges/                 # User's exchanges
GET  /credits/balance            # Credit balance
GET  /credits/transactions       # Transaction history
```

## 🤖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Get started or restart registration |
| `/menu` | Show main menu with all options |
| `/share` | Share food with neighbors |
| `/browse` | Browse available food |
| `/myposts` | View your food posts |
| `/profile` | Manage your profile |
| `/help` | Get help and see all commands |

## 🔧 Configuration

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/sharing_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# SMS Verification (optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# Application
SECRET_KEY=your-secret-key
ENVIRONMENT=development
DEBUG=true
CREDIT_INITIAL_BALANCE=10
```

### Optional Services
- **Twilio**: For SMS phone verification
- **AWS S3**: For photo storage (local storage by default)
- **Email SMTP**: For notifications (optional)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test types
pytest tests/api/        # API tests
pytest tests/bot/        # Bot tests  
pytest tests/services/   # Service layer tests
```

## 🚀 Deployment

### Production Checklist
- [ ] Update environment variables for production
- [ ] Set up proper PostgreSQL and Redis instances
- [ ] Configure Telegram webhook instead of polling
- [ ] Set up proper logging and monitoring
- [ ] Implement rate limiting and security measures
- [ ] Set up backup and recovery procedures
- [ ] Complete legal compliance review

### Docker Production
```bash
# Build production image
docker build -t sharing-platform .

# Deploy with docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## ⚖️ Legal Compliance

**🚨 CRITICAL**: Review legal documentation before deployment:

- **Food Safety Compliance** - Review federal, state, and local regulations
- **Building Approval** - Get written permission from building management  
- **Insurance Coverage** - Obtain appropriate liability insurance
- **Legal Documentation** - Attorney review of all user agreements

📁 **Legal Documents Location**: `/docs/legal/`
- Legal compliance assessment
- Terms of service template  
- Privacy policy template
- User liability waiver
- Food safety guidelines
- Implementation checklist

## 📊 System Requirements

### Minimum Requirements
- **Python**: 3.11+
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Memory**: 1GB RAM
- **Storage**: 5GB available space

### Production Recommendations
- **Python**: 3.11+
- **PostgreSQL**: 15+ with connection pooling
- **Redis**: 7+ with persistence
- **Memory**: 4GB+ RAM
- **Storage**: 20GB+ SSD
- **Network**: HTTPS with valid SSL certificate

## 🔍 Monitoring & Observability

The application includes built-in observability features:

- **Structured Logging** - JSON logs with correlation IDs
- **Health Checks** - Database and Redis connectivity
- **Metrics Collection** - User activity and system performance
- **Error Tracking** - Comprehensive error logging and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines
- Follow Python PEP 8 style guidelines
- Write comprehensive docstrings
- Add type hints for all functions
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check `/docs/` directory for detailed guides
- **Issues**: Report bugs via GitHub Issues
- **Legal Questions**: Consult with qualified legal counsel
- **Security Issues**: Report privately to project maintainers

---

**⚠️ Disclaimer**: This software is provided as-is. Users are responsible for compliance with all applicable laws and regulations. Consult legal counsel before deployment.