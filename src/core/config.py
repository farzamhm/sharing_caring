"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Database
    database_url: str = Field(..., description="Database connection URL")
    database_test_url: str = Field(
        default="", description="Test database connection URL"
    )
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    
    # Telegram Bot
    telegram_bot_token: str = Field(..., description="Telegram bot token")
    telegram_webhook_url: str = Field(default="", description="Webhook URL")
    telegram_webhook_secret: str = Field(default="", description="Webhook secret")
    
    # Security
    secret_key: str = Field(..., description="Secret key for JWT")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # SMS Verification
    twilio_account_sid: str = Field(default="", description="Twilio Account SID")
    twilio_auth_token: str = Field(default="", description="Twilio Auth Token")
    twilio_phone_number: str = Field(default="", description="Twilio phone number")
    
    # Application
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    max_users_per_building: int = Field(default=100)
    credit_initial_balance: int = Field(default=10)
    food_post_expiry_hours: int = Field(default=24)
    
    # Admin
    admin_username: str = Field(default="admin")
    admin_password: str = Field(..., description="Admin password")
    admin_telegram_ids: str = Field(default="", description="Comma-separated admin IDs")
    
    # Email (Optional)
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_username: str = Field(default="")
    smtp_password: str = Field(default="")
    
    # File Storage
    storage_type: str = Field(default="local")
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_bucket_name: str = Field(default="")
    aws_region: str = Field(default="us-east-1")
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=30)
    rate_limit_burst: int = Field(default=10)
    
    @property
    def admin_telegram_id_list(self) -> List[int]:
        """Get list of admin Telegram IDs."""
        if not self.admin_telegram_ids:
            return []
        return [int(id_str.strip()) for id_str in self.admin_telegram_ids.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()