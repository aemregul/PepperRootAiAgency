"""
Task Service - Çoklu adım görev yönetimi ve roadmap oluşturma.

Agent karmaşık istekleri alt görevlere bölerek yönetir.
Örnek: "Samsung TV reklamı için 3 dakikalık video yap"
  → 1. Senaryo oluştur
  → 2. Görsel üret (3 sahne)
  → 3. Video üret
  → 4. Birleştir
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Task


class TaskStatus:
    """Görev durumları."""
    PENDING = "pending"      # Beklemede
    IN_PROGRESS = "in_progress"  # Devam ediyor
    COMPLETED = "completed"      # Tamamlandı
    FAILED = "failed"           # Başarısız
    CANCELLED = "cancelled"     # İptal edildi


class TaskType:
    """Görev tipleri."""
    ROADMAP = "roadmap"          # Ana plan
    GENERATE_IMAGE = "generate_image"
    GENERATE_VIDEO = "generate_video"
    EDIT_IMAGE = "edit_image"
    UPSCALE = "upscale"
    ANALYZE = "analyze"
    WEB_SCRAPE = "web_scrape"
    CUSTOM = "custom"


class TaskService:
    """Çoklu adım görev yönetimi."""
    
    async def create_roadmap(
        self,
        db: AsyncSession,
        session_id: uuid.UUID,
        goal: str,
        steps: list[dict]
    ) -> Task:
        """
        Roadmap (ana görev planı) oluştur.
        
        Args:
            goal: Ana hedef (kullanıcının isteği)
            steps: Alt görevler listesi [{"type": "generate_image", "description": "..."}]
        
        Returns:
            Task: Oluşturulan roadmap görevi
        """
        # Ana roadmap görevi oluştur
        roadmap = Task(
            session_id=session_id,
            task_type=TaskType.ROADMAP,
            status=TaskStatus.IN_PROGRESS,
            priority=0,
            input_data={
                "goal": goal,
                "total_steps": len(steps)
            }
        )
        db.add(roadmap)
        await db.flush()
        
        # Alt görevleri oluştur
        for i, step in enumerate(steps):
            subtask = Task(
                session_id=session_id,
                parent_task_id=roadmap.id,
                task_type=step.get("type", TaskType.CUSTOM),
                status=TaskStatus.PENDING,
                priority=i,  # Sıralama için
                input_data={
                    "description": step.get("description", ""),
                    "params": step.get("params", {}),
                    "step_number": i + 1
                }
            )
            db.add(subtask)
        
        await db.commit()
        await db.refresh(roadmap)
        
        return roadmap
    
    async def get_roadmap(
        self,
        db: AsyncSession,
        roadmap_id: uuid.UUID
    ) -> Optional[Task]:
        """Roadmap'i alt görevleriyle birlikte getir."""
        result = await db.execute(
            select(Task).where(Task.id == roadmap_id)
        )
        return result.scalar_one_or_none()
    
    async def get_pending_tasks(
        self,
        db: AsyncSession,
        roadmap_id: uuid.UUID
    ) -> list[Task]:
        """Bekleyen görevleri öncelik sırasına göre getir."""
        result = await db.execute(
            select(Task).where(
                Task.parent_task_id == roadmap_id,
                Task.status == TaskStatus.PENDING
            ).order_by(Task.priority)
        )
        return list(result.scalars().all())
    
    async def get_next_task(
        self,
        db: AsyncSession,
        roadmap_id: uuid.UUID
    ) -> Optional[Task]:
        """Sıradaki görevi getir."""
        result = await db.execute(
            select(Task).where(
                Task.parent_task_id == roadmap_id,
                Task.status == TaskStatus.PENDING
            ).order_by(Task.priority).limit(1)
        )
        return result.scalar_one_or_none()
    
    async def start_task(
        self,
        db: AsyncSession,
        task_id: uuid.UUID
    ) -> Optional[Task]:
        """Görevi başlat."""
        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow()
            await db.commit()
            await db.refresh(task)
        
        return task
    
    async def complete_task(
        self,
        db: AsyncSession,
        task_id: uuid.UUID,
        output_data: dict = None
    ) -> Optional[Task]:
        """Görevi tamamla."""
        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            if output_data:
                task.output_data = output_data
            await db.commit()
            await db.refresh(task)
            
            # Parent roadmap'i kontrol et - tümü tamamlandı mı?
            if task.parent_task_id:
                await self._check_roadmap_completion(db, task.parent_task_id)
        
        return task
    
    async def fail_task(
        self,
        db: AsyncSession,
        task_id: uuid.UUID,
        error_message: str
    ) -> Optional[Task]:
        """Görevi başarısız olarak işaretle."""
        result = await db.execute(
            select(Task).where(Task.id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if task:
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.utcnow()
            task.error_message = error_message
            await db.commit()
            await db.refresh(task)
        
        return task
    
    async def get_roadmap_progress(
        self,
        db: AsyncSession,
        roadmap_id: uuid.UUID
    ) -> dict:
        """Roadmap ilerleme durumunu getir."""
        result = await db.execute(
            select(Task).where(Task.parent_task_id == roadmap_id)
        )
        subtasks = list(result.scalars().all())
        
        total = len(subtasks)
        completed = sum(1 for t in subtasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in subtasks if t.status == TaskStatus.FAILED)
        in_progress = sum(1 for t in subtasks if t.status == TaskStatus.IN_PROGRESS)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "pending": total - completed - failed - in_progress,
            "progress_percent": round((completed / total) * 100, 1) if total > 0 else 0,
            "is_complete": completed == total and total > 0,
            "has_failures": failed > 0
        }
    
    async def _check_roadmap_completion(
        self,
        db: AsyncSession,
        roadmap_id: uuid.UUID
    ):
        """Tüm alt görevler tamamlandıysa roadmap'i tamamla."""
        progress = await self.get_roadmap_progress(db, roadmap_id)
        
        if progress["is_complete"]:
            result = await db.execute(
                select(Task).where(Task.id == roadmap_id)
            )
            roadmap = result.scalar_one_or_none()
            
            if roadmap:
                roadmap.status = TaskStatus.COMPLETED
                roadmap.completed_at = datetime.utcnow()
                roadmap.output_data = {
                    "total_steps": progress["total"],
                    "completed_steps": progress["completed"],
                    "failed_steps": progress["failed"]
                }
                await db.commit()
    
    async def get_session_roadmaps(
        self,
        db: AsyncSession,
        session_id: uuid.UUID
    ) -> list[Task]:
        """Session'daki tüm roadmap'leri getir."""
        result = await db.execute(
            select(Task).where(
                Task.session_id == session_id,
                Task.task_type == TaskType.ROADMAP
            ).order_by(Task.created_at.desc())
        )
        return list(result.scalars().all())


# Singleton instance
task_service = TaskService()
