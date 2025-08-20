"""Main entry point for the application."""

import uvicorn

from .api.main import app
from .core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )