#!/usr/bin/env python3
"""
Development run script for the Meme Generator API
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print("🎭 Starting Meme Generator API...")
    print(f"📍 Server: http://{settings.api_host}:{settings.api_port}")
    print(f"📚 Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    print(f"🏥 Health Check: http://{settings.api_host}:{settings.api_port}/health")
    print("")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    ) 