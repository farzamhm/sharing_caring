# 🏠 Dual-Mode Food Sharing Platform

A sophisticated Telegram bot platform supporting both neighborhood-based and community-based food sharing. Built with Python, FastAPI, PostgreSQL, and Valkey streams for real-time event processing. Transform your community through smart food sharing with global reputation tracking.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Valkey](https://img.shields.io/badge/Valkey-7.2+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Epic Stories](https://img.shields.io/badge/Epic%20Stories-10-green.svg)
![User Stories](https://img.shields.io/badge/User%20Stories-58-blue.svg)

## 🌟 Features

### 🎯 Dual-Mode Architecture
- **🏠 Neighborhood Mode**: High-verification building-based sharing with SMS + address verification
- **👥 Community Mode**: Social-based sharing through Telegram groups with light verification
- **🔄 Flexible Switching**: Users can change modes with appropriate re-verification
- **🌐 Mode Isolation**: Complete separation between neighborhood and community interactions

### 🏆 Global Reputation System
- **⭐ Cross-Group Reputation**: Reputation follows users across all groups and modes
- **🎖️ Trust Levels**: Developing → Established → Trusted → Exemplary progression  
- **💎 Reputation-Based Privileges**: Premium features unlock based on trust level
- **🔧 Rehabilitation Programs**: Clear paths for users to improve declining reputation

### 💰 Advanced Credit Economy  
- **📈 Dynamic Earning**: Higher reputation users earn bonus credits
- **💸 Reputation Discounts**: Trust-based discounts on food claiming
- **🎁 Credit Gifting**: High-reputation users can gift credits to others
- **🛡️ Spending Controls**: Reputation-based limits prevent abuse

### Core Functionality
- **🍕 Food Sharing**: Post surplus food items with photos, descriptions, and pickup times
- **🔍 Smart Discovery**: Browse available food with filters for dietary restrictions and allergens  
- **🤝 Exchange Coordination**: Claim food and coordinate pickups with built-in messaging
- **🤝 Inter-Group Partnerships**: Groups can partner to expand food sharing networks
- **📱 Telegram Integration**: Full bot interface for easy access via Telegram

### 🏗️ Advanced Technical Features
- **Event-Driven Architecture**: Valkey streams for real-time event processing
- **FastAPI Backend**: Modern async Python web framework with automatic API documentation
- **PostgreSQL Database**: Optimized with performance indexes and materialized views
- **Global Reputation Engine**: Real-time cross-group reputation calculation
- **Advanced Admin Tools**: Group management, dispute resolution, automated monitoring
- **Privacy-First Design**: GDPR compliance with granular privacy controls
- **Predictive Analytics**: User behavior analysis and churn prevention
- **Auto-Scaling Infrastructure**: Kubernetes-ready with performance monitoring
- **Comprehensive Testing**: 80%+ code coverage with unit and integration tests
- **Docker Support**: Multi-container deployment with Valkey, PostgreSQL, and web services

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Valkey 7.2+ (or Redis 7+ with streams support)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Docker & Docker Compose (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/farzamhm/sharing_caring.git
cd sharing_caring
```

2. **Set up virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Set up database**
```bash
createdb sharing_caring
alembic upgrade head
```

5. **Run the application**
```bash
python -m src.bot.main
```

The Telegram bot will start and be ready to receive messages.

## 🐳 Docker Deployment (Recommended)

```bash
# Create environment file
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN and other settings

# Start all services (bot, database, valkey)
docker-compose up -d

# View logs
docker-compose logs -f

# Start with web dashboard (optional)
docker-compose --profile web up -d

# Stop services
docker-compose down
```

## 📁 Project Structure

```
├── src/
│   ├── api/          # FastAPI endpoints and routers
│   ├── bot/          # Telegram bot handlers
│   ├── core/         # Core utilities (database, valkey, config)
│   ├── models/       # SQLAlchemy database models
│   ├── services/     # Business logic layer
│   └── templates/    # HTML templates
├── docs/
│   └── product/      # Product documentation
│       ├── epics/    # 10 comprehensive epic specifications
│       └── stories/  # 58 user stories with acceptance criteria
├── tests/            # Test suite
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── fixtures/     # Test data
├── alembic/          # Database migrations
├── valkey.conf       # Valkey configuration for streams
├── docker-compose.yml # Multi-container deployment
└── requirements.txt  # Python dependencies with streams support
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5433/sharing_caring

# Valkey (Redis-compatible with streams)
REDIS_URL=redis://localhost:6380/0

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token-here

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
```

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Admin Dashboard**: http://localhost:8000/admin

### Key Endpoints

- `POST /auth/register` - User registration
- `POST /foods/` - Create food post
- `GET /foods/browse` - Browse available food
- `POST /foods/{id}/claim` - Claim food item
- `GET /exchanges/` - List user exchanges
- `GET /credits/balance` - Check credit balance

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
./scripts/test.sh

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/unit/test_food_service.py
```

## 📱 Telegram Bot Commands

### 🆕 Dual-Mode Commands
- `/start` - Register and choose your sharing mode (Neighborhood/Community)
- Mode selection with smart onboarding based on your community type

### 🍕 Food Sharing Commands  
- `/share` - Post new food item with photos and pickup details
- `/browse` - Browse available food with filtering options
- `/my_posts` - View and manage your active food posts
- `/exchanges` - Track your food exchange history and status

### 💰 Credits & Reputation
- `/credits` - Check credit balance and transaction history
- `/profile` - View reputation, trust level, and achievements
- `/help` - Get help and feature tutorials

## 🛡️ Advanced Admin Features

### 👥 Group Admin Dashboard  
- **Community Health Monitoring**: Real-time group activity and member engagement
- **Member Management Tools**: Warnings, restrictions, reputation boosts, removal
- **Content Moderation**: Food post review, content flagging, dispute resolution
- **Partnership Management**: Inter-group partnership requests and analytics

### 🏛️ Platform Admin Dashboard
- **Global Analytics**: Cross-platform metrics and business intelligence
- **Reputation System Oversight**: Trust level distribution and manipulation detection  
- **Automated Monitoring**: Smart alerts for spam, fraud, and safety concerns
- **Economic Balance Management**: Credit circulation and reputation-economy health

### CLI Tools
```bash
# Platform statistics
python -m src.admin_cli stats

# System health check
python -m src.admin_cli health

# View problematic exchanges
python -m src.admin_cli alerts
```

## 📈 Architecture

```mermaid
graph TD
    A[Telegram Users] -->|Telegram Bot API| B[Telegram Bot]
    B --> C[FastAPI Backend]
    C --> D[PostgreSQL Database]
    C --> E[Redis Cache]
    C --> F[S3/Local Storage]
    G[Web Users] -->|HTTP/HTTPS| C
    H[Admin Dashboard] --> C
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Telegram integration via [python-telegram-bot](https://python-telegram-bot.org/)
- Database ORM with [SQLAlchemy](https://www.sqlalchemy.org/)
- Redis caching with [redis-py](https://redis-py.readthedocs.io/)

## 📞 Support

For issues and questions:
- Open an [issue](https://github.com/yourusername/neighborhood-food-sharing/issues)
- Check the [documentation](docs/)
- Review the [FAQ](docs/FAQ.md)

## 🚦 Status

- ✅ Core Features Complete
- ✅ Testing Framework
- ✅ Docker Support
- ✅ Admin Dashboard
- 🔄 Production Deployment Guide
- 🔄 Multi-language Support

---

**Made with ❤️ for communities everywhere**