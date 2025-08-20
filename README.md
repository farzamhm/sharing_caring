# 🏠 Neighborhood Food Sharing Platform

A Telegram bot-based platform for neighborhood food sharing built with Python, FastAPI, and PostgreSQL. Connect with neighbors to reduce food waste and build community.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Redis](https://img.shields.io/badge/Redis-7+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Features

### Core Functionality
- **🍕 Food Sharing**: Post surplus food items with photos, descriptions, and pickup times
- **🔍 Smart Discovery**: Browse available food with filters for dietary restrictions and allergens
- **🤝 Exchange Coordination**: Claim food and coordinate pickups with built-in messaging
- **💰 Credit System**: Fair sharing with credits - earn by sharing, spend by claiming
- **📱 Telegram Integration**: Full bot interface for easy access via Telegram
- **🏢 Building Management**: Organize users by apartment buildings for local sharing

### Technical Features
- **FastAPI Backend**: Modern async Python web framework with automatic API documentation
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Redis Caching**: Fast session management and rate limiting
- **Photo Processing**: Automatic image compression and thumbnail generation
- **Admin Dashboard**: Web-based monitoring and management interface
- **Comprehensive Testing**: 80%+ code coverage with unit and integration tests
- **Docker Support**: Easy deployment with Docker Compose

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/neighborhood-food-sharing.git
cd neighborhood-food-sharing
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
createdb sharing_platform
alembic upgrade head
```

5. **Run the application**
```bash
python run_dev.py
```

The API will be available at http://localhost:8000

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📁 Project Structure

```
├── src/
│   ├── api/          # FastAPI endpoints and routers
│   ├── bot/          # Telegram bot handlers
│   ├── core/         # Core utilities (database, redis, config)
│   ├── models/       # SQLAlchemy database models
│   ├── services/     # Business logic layer
│   └── templates/    # HTML templates
├── tests/            # Test suite
│   ├── unit/         # Unit tests
│   ├── integration/  # Integration tests
│   └── fixtures/     # Test data
├── alembic/          # Database migrations
├── docker/           # Docker configuration
├── scripts/          # Utility scripts
└── docs/             # Documentation
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
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/sharing_platform

# Redis
REDIS_URL=redis://localhost:6379/0

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

- `/start` - Register and get started
- `/share` - Post new food item
- `/browse` - Browse available food
- `/my_posts` - View your food posts
- `/exchanges` - View your exchanges
- `/balance` - Check credit balance
- `/help` - Get help

## 🛡️ Admin Features

### Web Dashboard
- Platform statistics and metrics
- User management
- Exchange monitoring
- System health checks
- Intervention tools

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