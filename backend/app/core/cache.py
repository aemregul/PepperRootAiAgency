"""
Redis Cache Service for Pepper Root AI Agency.
Provides caching for sessions, entities, and AI responses.
"""
import json
from typing import Optional, Any
from datetime import timedelta

import redis.asyncio as redis
from app.core.config import settings


class RedisCache:
    """Redis-based cache service."""
    
    _instance: Optional["RedisCache"] = None
    _client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Connect to Redis."""
        if not settings.USE_REDIS or not settings.REDIS_URL:
            return False
        
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self._client.ping()
            print("✅ Redis bağlantısı başarılı")
            return True
        except Exception as e:
            print(f"❌ Redis bağlantı hatası: {e}")
            self._client = None
            return False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None
    
    @property
    def is_connected(self) -> bool:
        return self._client is not None
    
    # ============== BASIC OPERATIONS ==============
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if not self._client:
            return None
        try:
            return await self._client.get(key)
        except Exception:
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set key-value with optional TTL (seconds)."""
        if not self._client:
            return False
        try:
            if ttl:
                await self._client.setex(key, ttl, value)
            else:
                await self._client.set(key, value)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        if not self._client:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._client:
            return False
        try:
            return await self._client.exists(key) > 0
        except Exception:
            return False
    
    # ============== JSON OPERATIONS ==============
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set JSON value."""
        try:
            json_str = json.dumps(value, default=str)
            return await self.set(key, json_str, ttl)
        except (TypeError, ValueError):
            return False
    
    # ============== SESSION CACHE ==============
    
    async def cache_session(self, session_id: str, data: dict, ttl: int = 3600):
        """Cache session data (1 hour default)."""
        key = f"session:{session_id}"
        return await self.set_json(key, data, ttl)
    
    async def get_cached_session(self, session_id: str) -> Optional[dict]:
        """Get cached session."""
        key = f"session:{session_id}"
        return await self.get_json(key)
    
    async def invalidate_session(self, session_id: str):
        """Invalidate session cache."""
        key = f"session:{session_id}"
        await self.delete(key)
    
    # ============== ENTITY CACHE ==============
    
    async def cache_entities(self, user_id: str, entities: list, ttl: int = 1800):
        """Cache user's entities (30 min default)."""
        key = f"entities:{user_id}"
        return await self.set_json(key, entities, ttl)
    
    async def get_cached_entities(self, user_id: str) -> Optional[list]:
        """Get cached entities."""
        key = f"entities:{user_id}"
        return await self.get_json(key)
    
    async def invalidate_entities(self, user_id: str):
        """Invalidate entity cache."""
        key = f"entities:{user_id}"
        await self.delete(key)
    
    # ============== AI RESPONSE CACHE ==============
    
    async def cache_ai_response(
        self, 
        prompt_hash: str, 
        response: str, 
        ttl: int = 86400  # 24 hours
    ):
        """Cache AI response for similar prompts."""
        key = f"ai_response:{prompt_hash}"
        return await self.set(key, response, ttl)
    
    async def get_cached_ai_response(self, prompt_hash: str) -> Optional[str]:
        """Get cached AI response."""
        key = f"ai_response:{prompt_hash}"
        return await self.get(key)
    
    # ============== RATE LIMITING ==============
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        limit: int = 100, 
        window: int = 3600
    ) -> tuple[bool, int]:
        """Check if user is within rate limit. Returns (allowed, remaining)."""
        if not self._client:
            return True, limit
        
        key = f"rate_limit:{user_id}"
        try:
            current = await self._client.get(key)
            if current is None:
                await self._client.setex(key, window, "1")
                return True, limit - 1
            
            count = int(current)
            if count >= limit:
                return False, 0
            
            await self._client.incr(key)
            return True, limit - count - 1
        except Exception:
            return True, limit


# Singleton instance
cache = RedisCache()


async def get_cache() -> RedisCache:
    """Dependency for getting cache instance."""
    return cache
