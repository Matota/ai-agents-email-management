"""Configuration settings for the Email Management Agent."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Email Configuration
    email_address: str
    
    # Database
    db_path: str = "./data/emails.db"
    
    # Agent Settings
    max_emails_to_fetch: int = 50
    categorization_model: str = "gpt-4"
    summary_model: str = "gpt-3.5-turbo"
    response_model: str = "gpt-4"
    
    # Logging
    log_level: str = "INFO"
    
    # Gmail API
    gmail_credentials_path: str = "./credentials.json"
    gmail_token_path: str = "./token.json"
    gmail_scopes: list[str] = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Ensure data directory exists
DATA_DIR = Path(settings.db_path).parent
DATA_DIR.mkdir(parents=True, exist_ok=True)
