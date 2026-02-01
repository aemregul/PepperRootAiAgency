"""
Uygulama konfigürasyonu.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Uygulama ayarları."""
    
    # Uygulama
    APP_NAME: str = "Pepper Root AI Agency"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api/v1"
    
    # Veritabanı
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pepperroot"
    
    # Güvenlik
    SECRET_KEY: str = "gizli-anahtar-production-da-degistir"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # AI APIs
    ANTHROPIC_API_KEY: Optional[str] = None
    FAL_KEY: Optional[str] = None
    SERPAPI_KEY: Optional[str] = None  # Web search for images
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    
    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./uploads"
    
    # Redis (Faz 2)
    REDIS_URL: Optional[str] = None
    USE_REDIS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
