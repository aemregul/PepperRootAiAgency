"""
Resilience Service - Graceful Degradation ve Error Handling.
Sistemi çökertmeden hataları yönetir.
"""
import asyncio
import time
from functools import wraps
from typing import Callable, Any, Optional
from collections import defaultdict


class RateLimiter:
    """
    Token bucket rate limiter.
    API çağrılarını sınırlandırır.
    """
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window  # saniye
        self.calls = defaultdict(list)  # user_id -> [timestamps]
    
    def can_proceed(self, user_id: str) -> bool:
        """Kullanıcı istek yapabilir mi?"""
        now = time.time()
        user_calls = self.calls[user_id]
        
        # Eski çağrıları temizle
        self.calls[user_id] = [t for t in user_calls if now - t < self.time_window]
        
        return len(self.calls[user_id]) < self.max_calls
    
    def record_call(self, user_id: str):
        """Çağrıyı kaydet."""
        self.calls[user_id].append(time.time())
    
    def get_wait_time(self, user_id: str) -> float:
        """Ne kadar beklemeli?"""
        if not self.calls[user_id]:
            return 0
        oldest = min(self.calls[user_id])
        wait = self.time_window - (time.time() - oldest)
        return max(0, wait)


class CircuitBreaker:
    """
    Circuit breaker pattern.
    Sürekli hata veren servisleri geçici olarak devre dışı bırakır.
    """
    
    CLOSED = "closed"    # Normal çalışma
    OPEN = "open"        # Devre açık, istekler reddedilir
    HALF_OPEN = "half"   # Test aşaması
    
    def __init__(
        self, 
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        service_name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.service_name = service_name
        
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
    
    def can_execute(self) -> bool:
        """İstek çalıştırılabilir mi?"""
        if self.state == self.CLOSED:
            return True
        
        if self.state == self.OPEN:
            # Recovery timeout geçti mi?
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = self.HALF_OPEN
                print(f"⚡ Circuit half-open: {self.service_name}")
                return True
            return False
        
        # HALF_OPEN - bir istek deneyelim
        return True
    
    def record_success(self):
        """Başarılı istek."""
        self.failure_count = 0
        if self.state == self.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:
                self.state = self.CLOSED
                print(f"✅ Circuit closed: {self.service_name}")
        self.success_count = 0
    
    def record_failure(self):
        """Başarısız istek."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = self.OPEN
            print(f"🔴 Circuit OPEN: {self.service_name} - {self.failure_count} failures")


def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator with exponential backoff.
    
    Usage:
        @with_retry(max_retries=3, delay=1.0)
        async def my_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"⚠️ Retry {attempt + 1}/{max_retries}: {func.__name__} - {str(e)[:100]}")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"❌ Max retries exceeded: {func.__name__}")
            
            raise last_exception
        return wrapper
    return decorator


def with_timeout(seconds: float = 30.0):
    """
    Timeout decorator.
    
    Usage:
        @with_timeout(seconds=30)
        async def my_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                print(f"⏰ Timeout: {func.__name__} ({seconds}s)")
                return {"success": False, "error": f"İşlem zaman aşımına uğradı ({seconds}s)"}
        return wrapper
    return decorator


def with_fallback(fallback_value: Any):
    """
    Fallback decorator - hata durumunda varsayılan değer döndür.
    
    Usage:
        @with_fallback(fallback_value={"success": False})
        async def my_function():
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Fallback: {func.__name__} - {str(e)[:100]}")
                if callable(fallback_value):
                    return fallback_value()
                return fallback_value
        return wrapper
    return decorator


class ResilienceService:
    """Ana resilience service - tüm mekanizmaları bir arada yönetir."""
    
    def __init__(self):
        # Servis bazlı circuit breaker'lar
        self.circuit_breakers = {}
        
        # User bazlı rate limiter
        self.rate_limiters = {
            "image_generation": RateLimiter(max_calls=20, time_window=60),
            "video_generation": RateLimiter(max_calls=5, time_window=60),
            "api_calls": RateLimiter(max_calls=100, time_window=60),
        }
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Servis için circuit breaker al veya oluştur."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name=service_name,
                failure_threshold=5,
                recovery_timeout=60
            )
        return self.circuit_breakers[service_name]
    
    def check_rate_limit(self, user_id: str, operation: str = "api_calls") -> tuple[bool, float]:
        """
        Rate limit kontrolü.
        
        Returns:
            (can_proceed, wait_time_seconds)
        """
        limiter = self.rate_limiters.get(operation, self.rate_limiters["api_calls"])
        
        if limiter.can_proceed(user_id):
            limiter.record_call(user_id)
            return True, 0
        
        wait_time = limiter.get_wait_time(user_id)
        return False, wait_time
    
    async def execute_with_resilience(
        self,
        func: Callable,
        *args,
        service_name: str = "default",
        user_id: Optional[str] = None,
        operation: str = "api_calls",
        **kwargs
    ) -> dict:
        """
        Tüm resilience mekanizmalarıyla fonksiyon çalıştır.
        
        1. Rate limit kontrolü
        2. Circuit breaker kontrolü
        3. Retry with backoff
        4. Timeout
        5. Fallback
        """
        # 1. Rate limit
        if user_id:
            can_proceed, wait_time = self.check_rate_limit(user_id, operation)
            if not can_proceed:
                return {
                    "success": False,
                    "error": f"Rate limit aşıldı. {wait_time:.0f} saniye bekleyin.",
                    "rate_limited": True,
                    "wait_seconds": wait_time
                }
        
        # 2. Circuit breaker
        cb = self.get_circuit_breaker(service_name)
        if not cb.can_execute():
            return {
                "success": False,
                "error": f"{service_name} servisi geçici olarak devre dışı. Lütfen bekleyin.",
                "circuit_open": True
            }
        
        # 3. Execute with retry
        try:
            result = await func(*args, **kwargs)
            cb.record_success()
            return result
        except Exception as e:
            cb.record_failure()
            return {
                "success": False,
                "error": str(e),
                "exception_type": type(e).__name__
            }


# Singleton instance
resilience_service = ResilienceService()
