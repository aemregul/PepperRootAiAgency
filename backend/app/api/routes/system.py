"""
System Status API routes.
"""
from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status")
async def get_system_status():
    """Get system status including API key availability."""
    return {
        "status": "online",
        "version": settings.APP_VERSION,
        "api_keys": {
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "fal_ai": bool(settings.FAL_KEY),
            "serpapi": bool(settings.SERPAPI_KEY),
            "google_oauth": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
        },
        "features": {
            "chat": bool(settings.ANTHROPIC_API_KEY),
            "image_generation": bool(settings.FAL_KEY),
            "video_generation": bool(settings.FAL_KEY),
            "web_search": bool(settings.SERPAPI_KEY),
            "google_login": bool(settings.GOOGLE_CLIENT_ID),
            "redis_cache": settings.USE_REDIS and bool(settings.REDIS_URL),
        }
    }


@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
