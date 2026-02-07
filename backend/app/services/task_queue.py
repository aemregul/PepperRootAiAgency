"""
Background Task Queue - Async job processing.

Celery yerine basit asyncio tabanlı bir queue.
Uzun süren işlemler (video rendering, bulk upload) için kullanılır.

Not: Production'da Celery + Redis kullanılmalı.
Bu, basit bir asyncio çözümüdür.
"""
import asyncio
import uuid
from datetime import datetime
from typing import Callable, Any, Optional
from enum import Enum
from dataclasses import dataclass, field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundTask:
    """Arka plan görevi."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0  # 0-100
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }


class TaskQueue:
    """Async background task queue."""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.tasks: dict[str, BackgroundTask] = {}
        self.queue: asyncio.Queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self.running = False
    
    async def start(self):
        """Queue worker'ları başlat."""
        if self.running:
            return
        
        self.running = True
        print(f"🚀 TaskQueue başlatıldı ({self.max_concurrent} worker)")
        
        # Worker'ları başlat
        for i in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker(i))
            self.workers.append(worker)
    
    async def stop(self):
        """Queue worker'ları durdur."""
        self.running = False
        
        # Workers'ı iptal et
        for worker in self.workers:
            worker.cancel()
        
        self.workers = []
        print("⏹️ TaskQueue durduruldu")
    
    async def _worker(self, worker_id: int):
        """Background worker."""
        while self.running:
            try:
                # Queue'dan görev al (timeout ile)
                try:
                    task_id, func, args, kwargs = await asyncio.wait_for(
                        self.queue.get(), 
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue
                
                task = self.tasks.get(task_id)
                if not task:
                    continue
                
                # Görevi çalıştır
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                print(f"🔄 Worker-{worker_id}: {task.name} başladı")
                
                try:
                    # Eğer func coroutine ise await et
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        # Sync func'ı thread pool'da çalıştır
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, func, *args, **kwargs)
                    
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    task.progress = 100
                    print(f"✅ Worker-{worker_id}: {task.name} tamamlandı")
                    
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    print(f"❌ Worker-{worker_id}: {task.name} başarısız - {e}")
                
                finally:
                    task.completed_at = datetime.utcnow()
                    self.queue.task_done()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Worker-{worker_id} hatası: {e}")
    
    async def enqueue(
        self,
        func: Callable,
        *args,
        name: str = "Task",
        metadata: dict = None,
        **kwargs
    ) -> str:
        """
        Görevi queue'ya ekle.
        
        Returns:
            Task ID
        """
        task = BackgroundTask(
            name=name,
            metadata=metadata or {}
        )
        self.tasks[task.id] = task
        
        await self.queue.put((task.id, func, args, kwargs))
        print(f"📥 Göreve eklendi: {name} (ID: {task.id[:8]})")
        
        return task.id
    
    def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Görev durumunu al."""
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """Görev durumunu dict olarak al."""
        task = self.get_task(task_id)
        return task.to_dict() if task else None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Görevi iptal et (sadece pending olanlar)."""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True
        
        return False
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Eski tamamlanmış görevleri temizle."""
        from datetime import timedelta
        
        now = datetime.utcnow()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED):
                if task.completed_at and (now - task.completed_at) > timedelta(hours=max_age_hours):
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        if to_remove:
            print(f"🧹 {len(to_remove)} eski görev temizlendi")
    
    def get_stats(self) -> dict:
        """Queue istatistikleri."""
        status_counts = {s.value: 0 for s in TaskStatus}
        for task in self.tasks.values():
            status_counts[task.status.value] += 1
        
        return {
            "total_tasks": len(self.tasks),
            "queue_size": self.queue.qsize(),
            "workers": len(self.workers),
            "running": self.running,
            "by_status": status_counts
        }


# Singleton instance
task_queue = TaskQueue(max_concurrent=5)


# Convenience functions
async def run_in_background(
    func: Callable,
    *args,
    name: str = "Background Task",
    **kwargs
) -> str:
    """Fonksiyonu arka planda çalıştır."""
    if not task_queue.running:
        await task_queue.start()
    
    return await task_queue.enqueue(func, *args, name=name, **kwargs)


def get_task_status(task_id: str) -> Optional[dict]:
    """Görev durumunu al."""
    return task_queue.get_task_status(task_id)
