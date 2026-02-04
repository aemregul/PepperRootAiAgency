"""
Kullanım İstatistikleri Tracking Servisi.

Görsel, video ve API çağrılarını günlük olarak takip eder.
"""
from datetime import datetime, date
from typing import Optional
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import UsageStats


class StatsService:
    """Kullanım istatistikleri servisi."""
    
    @staticmethod
    async def get_or_create_today_stats(
        db: AsyncSession, 
        user_id: Optional[uuid.UUID] = None
    ) -> UsageStats:
        """
        Bugünün istatistik kaydını getir veya oluştur.
        """
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Bugünün kaydını ara
        query = select(UsageStats).where(
            UsageStats.date >= today_start,
            UsageStats.date <= today_end
        )
        
        if user_id:
            query = query.where(UsageStats.user_id == user_id)
        else:
            query = query.where(UsageStats.user_id.is_(None))
        
        result = await db.execute(query)
        stats = result.scalar_one_or_none()
        
        # Yoksa yeni kayıt oluştur
        if not stats:
            stats = UsageStats(
                user_id=user_id,
                date=datetime.now(),
                api_calls=0,
                images_generated=0,
                videos_generated=0,
                tokens_used=0
            )
            db.add(stats)
            await db.commit()
            await db.refresh(stats)
        
        return stats
    
    @staticmethod
    async def track_api_call(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        tokens: int = 0
    ):
        """API çağrısı sayacını artır."""
        stats = await StatsService.get_or_create_today_stats(db, user_id)
        stats.api_calls += 1
        stats.tokens_used += tokens
        await db.commit()
    
    @staticmethod
    async def track_image_generation(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        model_name: Optional[str] = None
    ):
        """Görsel üretim sayacını artır."""
        stats = await StatsService.get_or_create_today_stats(db, user_id)
        stats.images_generated += 1
        stats.api_calls += 1
        if model_name:
            stats.model_name = model_name
        await db.commit()
    
    @staticmethod
    async def track_video_generation(
        db: AsyncSession,
        user_id: Optional[uuid.UUID] = None,
        model_name: Optional[str] = None
    ):
        """Video üretim sayacını artır."""
        stats = await StatsService.get_or_create_today_stats(db, user_id)
        stats.videos_generated += 1
        stats.api_calls += 1
        if model_name:
            stats.model_name = model_name
        await db.commit()


# Singleton instance
stats_service = StatsService()
