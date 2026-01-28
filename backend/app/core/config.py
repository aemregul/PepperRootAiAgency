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
    FAL_API_KEY: Optional[str] = None
    
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
