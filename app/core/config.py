"""
Configuration settings for the Meme Generator API
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Meme Generator API"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered meme generation API using SuperMeme AI"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # CORS Configuration
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    # SuperMeme AI Configuration
    supermeme_api_url: str = "https://supermeme.ai/api/meme/text-to-meme-2"
    supabase_url: str = "https://hlhmmkpugruknefsttlr.supabase.co/auth/v1"
    supabase_api_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJhbm9uIiwiaWF0IjoxNjQyNzg1NjkzLCJleHAiOjE5NTgzNjE2OTN9._oD1XWLrvhw0Yc0TCPA-ujflEd929zr_f08bLdjUK0g"
    
    # Mail service configuration
    mail_api_url: str = "https://api.mail.tm"
    
    # File storage
    output_directory: str = "generated_memes"
    max_file_size_mb: int = 10
    
    # Rate limiting
    rate_limit_per_minute: int = 10
    
    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings() 