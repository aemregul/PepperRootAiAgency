"""
WebSocket endpoint — Gerçek zamanlı ilerleme bildirimleri.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.progress_service import progress_service

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """
    WebSocket bağlantısı — session bazlı ilerleme takibi.
    
    Frontend bağlanır:
      ws://localhost:8000/ws/progress/{session_id}
    
    Gelen mesaj formatı:
      {"type": "progress", "task_type": "long_video", "progress": 0.5, "message": "Segment 3/6 üretiliyor..."}
      {"type": "complete", "task_type": "long_video", "result": {...}}
      {"type": "error", "task_type": "long_video", "message": "Hata: ..."}
    """
    await websocket.accept()
    progress_service.register(session_id, websocket)
    
    try:
        while True:
            # Client'tan gelen ping/pong veya mesajları dinle
            data = await websocket.receive_text()
            # Ping-pong heartbeat
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        progress_service.unregister(session_id, websocket)
    except Exception:
        progress_service.unregister(session_id, websocket)
