#!/usr/bin/env python3
"""Development server runner."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from src.main import settings
    import uvicorn
    
    print("🚀 Starting Neighborhood Sharing Platform API...")
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Database URL: {settings.database_url}")
    print("=" * 50)
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )