#!/usr/bin/env python3
"""Development environment setup script."""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Run a shell command and return success status."""
    print(f"📋 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_python_version() -> bool:
    """Check if Python version is 3.11+."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not supported. Need Python 3.11+")
        return False


def create_env_file():
    """Create .env file from example."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        env_file.write_text(env_example.read_text())
        print("✅ Created .env file from .env.example")
        print("⚠️  Please edit .env file with your configuration values")
    else:
        print("❌ .env.example file not found")


async def check_services():
    """Check if required services are available."""
    print("\n🔍 Checking required services...")
    
    # Check PostgreSQL
    pg_result = subprocess.run(
        "psql --version", 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if pg_result.returncode == 0:
        print("✅ PostgreSQL is installed")
    else:
        print("❌ PostgreSQL not found. Please install PostgreSQL 13+")
    
    # Check Redis
    redis_result = subprocess.run(
        "redis-cli --version", 
        shell=True, 
        capture_output=True, 
        text=True
    )
    if redis_result.returncode == 0:
        print("✅ Redis is installed")
    else:
        print("❌ Redis not found. Please install Redis 6+")


def setup_virtual_environment():
    """Set up Python virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📋 Creating virtual environment...")
    if run_command(f"{sys.executable} -m venv venv", "Create virtual environment"):
        print("✅ Virtual environment created")
        print("📋 To activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
        return True
    return False


def install_dependencies():
    """Install Python dependencies."""
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrade pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Install dependencies"):
        return False
    
    return True


def setup_database():
    """Set up database."""
    print("\n🗄️ Database setup instructions:")
    print("1. Create PostgreSQL database:")
    print("   createdb sharing_platform")
    print("2. Create test database:")
    print("   createdb sharing_platform_test")
    print("3. Update DATABASE_URL in .env file")
    print("4. Run migrations:")
    print("   alembic revision --autogenerate -m 'Initial migration'")
    print("   alembic upgrade head")
    print("5. Initialize sample data:")
    print("   python scripts/init_db.py")


def setup_telegram_bot():
    """Set up Telegram bot."""
    print("\n🤖 Telegram Bot setup instructions:")
    print("1. Create a bot with @BotFather on Telegram")
    print("2. Get your bot token")
    print("3. Update TELEGRAM_BOT_TOKEN in .env file")
    print("4. Optionally set up webhook URL for production")


def main():
    """Main setup function."""
    print("🚀 Setting up Neighborhood Sharing Platform Development Environment")
    print("=" * 70)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check services
    asyncio.run(check_services())
    
    # Database setup instructions
    setup_database()
    
    # Telegram bot setup instructions
    setup_telegram_bot()
    
    print("\n🎉 Development environment setup completed!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment: source venv/bin/activate")
    print("2. Edit .env file with your configuration")
    print("3. Set up PostgreSQL and Redis services")
    print("4. Run database migrations")
    print("5. Start the API: python run_dev.py")
    print("6. Start the bot: python run_bot.py")
    
    print("\n📚 Documentation:")
    print("- API docs: http://localhost:8000/docs")
    print("- Health check: http://localhost:8000/health")
    print("- Architecture: docs/architecture.md")
    print("- Legal docs: docs/legal/")


if __name__ == "__main__":
    main()