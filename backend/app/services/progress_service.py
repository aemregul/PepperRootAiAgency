"""
Real-Time Progress Service — WebSocket + Redis Pub/Sub.

Uzun süren işlemler (long video, batch campaign) için 
gerçek zamanlı ilerleme bildirimi.
"""
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime


class ProgressService:
    """Gerçek zamanlı ilerleme takip servisi."""
    
    _instance: Optional["ProgressService"] = None
    _connections: Dict[str, list] = {}  # session_id → [websocket connections]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._connections = {}
        return cls._instance
    
    def register(self, session_id: str, websocket):
        """WebSocket bağlantısı kaydet."""
        if session_id not in self._connections:
            self._connections[session_id] = []
        self._connections[session_id].append(websocket)
        print(f"🔌 WebSocket bağlandı: session={session_id[:8]}... (toplam: {len(self._connections[session_id])})")
    
    def unregister(self, session_id: str, websocket):
        """WebSocket bağlantısı kaldır."""
        if session_id in self._connections:
            self._connections[session_id] = [
                ws for ws in self._connections[session_id] if ws != websocket
            ]
            if not self._connections[session_id]:
                del self._connections[session_id]
        print(f"🔌 WebSocket ayrıldı: session={session_id[:8]}...")
    
    async def send_progress(
        self,
        session_id: str,
        task_type: str,
        progress: float,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        İlerleme bildirimi gönder.
        
        Args:
            session_id: Session ID
            task_type: İşlem tipi (long_video, campaign, quality_check)
            progress: 0.0 - 1.0 arası ilerleme
            message: Kullanıcıya gösterilecek mesaj
            details: Ek bilgiler (opsiyonel)
        """
        payload = {
            "type": "progress",
            "task_type": task_type,
            "progress": round(progress, 2),
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Redis pub/sub ile yayınla
        try:
            from app.core.cache import cache
            if cache.is_connected:
                await cache.set(
                    f"progress:{session_id}",
                    json.dumps(payload),
                    ttl=300  # 5 dakika
                )
        except Exception:
            pass
        
        # Doğrudan WebSocket'lere gönder
        if session_id in self._connections:
            dead_connections = []
            for ws in self._connections[session_id]:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead_connections.append(ws)
            
            # Ölü bağlantıları temizle
            for ws in dead_connections:
                self._connections[session_id].remove(ws)
    
    async def send_complete(
        self,
        session_id: str,
        task_type: str,
        result: Dict[str, Any]
    ):
        """İşlem tamamlandı bildirimi."""
        payload = {
            "type": "complete",
            "task_type": task_type,
            "progress": 1.0,
            "message": "Tamamlandı!",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if session_id in self._connections:
            for ws in self._connections[session_id]:
                try:
                    await ws.send_json(payload)
                except Exception:
                    pass
        
        # Cache temizle
        try:
            from app.core.cache import cache
            if cache.is_connected:
                await cache.delete(f"progress:{session_id}")
        except Exception:
            pass
    
    async def send_error(
        self,
        session_id: str,
        task_type: str,
        error: str
    ):
        """Hata bildirimi."""
        payload = {
            "type": "error",
            "task_type": task_type,
            "progress": 0,
            "message": f"Hata: {error}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if session_id in self._connections:
            for ws in self._connections[session_id]:
                try:
                    await ws.send_json(payload)
                except Exception:
                    pass


# Singleton
progress_service = ProgressService()
