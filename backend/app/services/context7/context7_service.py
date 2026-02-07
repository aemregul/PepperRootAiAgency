"""
Context7 MCP Service.
Kütüphane dokümantasyonlarını çekmek için Context7 API'sini kullanır.
"""
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class Context7Service:
    """Context7 MCP dokümantasyon servisi."""
    
    # Popüler kütüphanelerin Context7 ID'leri
    LIBRARY_IDS = {
        # Frontend
        "react": "/facebook/react",
        "nextjs": "/vercel/next.js",
        "next.js": "/vercel/next.js",
        "vue": "/vuejs/vue",
        "angular": "/angular/angular",
        "svelte": "/sveltejs/svelte",
        "tailwind": "/tailwindlabs/tailwindcss",
        "tailwindcss": "/tailwindlabs/tailwindcss",
        
        # Backend - Python
        "fastapi": "/tiangolo/fastapi",
        "django": "/django/django",
        "flask": "/pallets/flask",
        "sqlalchemy": "/sqlalchemy/sqlalchemy",
        "pydantic": "/pydantic/pydantic",
        "langchain": "/langchain-ai/langchain",
        
        # AI/ML
        "fal": "/fal-ai/fal",
        "fal.ai": "/fal-ai/fal",
        "fal-ai": "/fal-ai/fal",
        "openai": "/openai/openai-python",
        "anthropic": "/anthropic-ai/anthropic-sdk-python",
        "transformers": "/huggingface/transformers",
        
        # Database
        "prisma": "/prisma/prisma",
        "supabase": "/supabase/supabase",
        "mongodb": "/mongodb/mongo-python-driver",
        "redis": "/redis/redis-py",
        
        # Node.js
        "express": "/expressjs/express",
        "nestjs": "/nestjs/nest",
        "node": "/nodejs/node",
        
        # Diğer
        "typescript": "/microsoft/typescript",
        "stripe": "/stripe/stripe-python",
        "aws": "/aws/aws-sdk",
        "vercel": "/vercel/vercel",
    }
    
    BASE_URL = "https://context7.com/api"
    
    def __init__(self):
        self.api_key = getattr(settings, 'CONTEXT7_API_KEY', None)
    
    def _get_library_id(self, library_name: str) -> Optional[str]:
        """Kütüphane adından Context7 ID'sini çıkart."""
        name = library_name.lower().strip()
        
        # Önce bilinen kütüphanelerde ara
        if name in self.LIBRARY_IDS:
            return self.LIBRARY_IDS[name]
        
        # Eğer zaten / ile başlıyorsa doğrudan kullan
        if library_name.startswith("/"):
            return library_name
        
        # Bilinmiyorsa None döndür (arama yapılacak)
        return None
    
    async def resolve_library_id(self, library_name: str) -> Optional[str]:
        """
        Context7 API'den kütüphane ID'sini çözümle.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/v1/resolve",
                    params={"libraryName": library_name},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("libraries") and len(data["libraries"]) > 0:
                        return data["libraries"][0].get("id")
                
                return None
        except Exception as e:
            print(f"⚠️ Context7 resolve hatası: {e}")
            return None
    
    def _get_headers(self) -> Dict[str, str]:
        """API headers oluştur."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get_library_docs(
        self,
        library_name: str,
        query: Optional[str] = None,
        tokens: int = 5000
    ) -> Dict[str, Any]:
        """
        Kütüphane dokümantasyonunu çek.
        
        Args:
            library_name: Kütüphane adı (örn: 'react', 'fastapi')
            query: Spesifik arama sorgusu (opsiyonel)
            tokens: Maksimum token sayısı
            
        Returns:
            Dokümantasyon içeriği ve metadata
        """
        try:
            # Kütüphane ID'sini çözümle
            library_id = self._get_library_id(library_name)
            
            if not library_id:
                # Bilinen kütüphanelerde yoksa, API'den çözümle
                library_id = await self.resolve_library_id(library_name)
            
            if not library_id:
                return {
                    "success": False,
                    "error": f"'{library_name}' kütüphanesi Context7'de bulunamadı",
                    "suggestion": "Lütfen kütüphane adını kontrol edin veya tam ID kullanın (örn: /facebook/react)"
                }
            
            # Dokümantasyonu çek
            async with httpx.AsyncClient(timeout=60.0) as client:
                params = {
                    "tokens": min(tokens, 10000)  # Max 10K token
                }
                if query:
                    params["topic"] = query
                
                response = await client.get(
                    f"{self.BASE_URL}/v1{library_id}",
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return {
                        "success": True,
                        "library": library_name,
                        "library_id": library_id,
                        "query": query,
                        "content": data.get("content", ""),
                        "title": data.get("title", library_name),
                        "description": data.get("description", ""),
                        "version": data.get("version"),
                        "source_url": data.get("url", f"https://context7.com{library_id}"),
                        "tokens_used": data.get("tokens", tokens)
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "error": f"Dokümantasyon bulunamadı: {library_id}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Context7 API hatası: {response.status_code}"
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Context7 API zaman aşımına uğradı"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Beklenmeyen hata: {str(e)}"
            }
    
    async def search_libraries(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Context7'de kütüphane ara.
        
        Args:
            query: Arama sorgusu
            limit: Maksimum sonuç sayısı
            
        Returns:
            Eşleşen kütüphaneler listesi
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/v1/search",
                    params={"q": query, "limit": limit},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    data = response.json()
                    libraries = data.get("libraries", [])
                    
                    return {
                        "success": True,
                        "query": query,
                        "results": [
                            {
                                "id": lib.get("id"),
                                "name": lib.get("name"),
                                "description": lib.get("description", "")[:200]
                            }
                            for lib in libraries[:limit]
                        ],
                        "total": len(libraries)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Arama hatası: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Arama hatası: {str(e)}"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Context7 API durumunu kontrol et."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/health",
                    headers=self._get_headers()
                )
                return {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "has_api_key": bool(self.api_key)
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Singleton instance
context7_service = Context7Service()
