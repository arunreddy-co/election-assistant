"""Configuration module for the VoteReady application.

This module loads environment variables and provides a singleton settings instance.
"""

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        """Initialize settings and validate required fields."""
        self.google_cloud_project: str = self._get_required("GOOGLE_CLOUD_PROJECT")
        self.google_cloud_region: str = os.getenv("GOOGLE_CLOUD_REGION", "asia-south1")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.0-flash")
        self.google_maps_api_key: str = self._get_required("GOOGLE_MAPS_API_KEY")
        self.google_translate_parent: str = self._get_required("GOOGLE_TRANSLATE_PARENT")
        
        self.firestore_collection_users: str = os.getenv("FIRESTORE_COLLECTION_USERS", "users")
        self.firestore_collection_cache: str = os.getenv("FIRESTORE_COLLECTION_CACHE", "response_cache")
        self.firestore_collection_checklist: str = os.getenv("FIRESTORE_COLLECTION_CHECKLIST", "checklists")
        
        self.rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
        
        origins = os.getenv("ALLOWED_ORIGINS", "")
        self.allowed_origins: List[str] = [origin.strip() for origin in origins.split(",")] if origins else []
        
        self.env: str = os.getenv("ENV", "development")

    def _get_required(self, key: str) -> str:
        """Get required environment variable or raise an error."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

# Singleton settings instance
settings = Settings()
