"""
Cleanup Tasks - Scheduled maintenance jobs.

Celery tasks for:
- Expired trash cleanup
- Old task result cleanup
- Pinecone reindexing
- Cache cleanup
"""
from celery import shared_task
from datetime import datetime, timedelta
import asyncio


@shared_task(
    bind=True,
    name="app.tasks.cleanup_tasks.cleanup_expired_trash",
)
def cleanup_expired_trash(self) -> dict:
    """
    Clean up trash items that have expired (after 3 days).
    Runs hourly via Celery Beat.
    """
    from app.core.database import async_sessionmaker
    from app.models.models import TrashItem
    from sqlalchemy import delete
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _cleanup():
            async with async_sessionmaker() as db:
                now = datetime.utcnow()
                result = await db.execute(
                    delete(TrashItem).where(TrashItem.expires_at < now)
                )
                deleted_count = result.rowcount
                await db.commit()
                return deleted_count
        
        try:
            deleted = loop.run_until_complete(_cleanup())
            
            if deleted > 0:
                print(f"🗑️ {deleted} expired trash items deleted")
            
            return {
                "success": True,
                "deleted_count": deleted,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        print(f"❌ Trash cleanup failed: {e}")
        return {"success": False, "error": str(e)}


@shared_task(
    bind=True,
    name="app.tasks.cleanup_tasks.cleanup_old_results",
)
def cleanup_old_results(self) -> dict:
    """
    Clean up old task results from Redis.
    Runs every 6 hours via Celery Beat.
    """
    from app.core.cache import cache
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Clean up old working memory
            cleaned = loop.run_until_complete(
                cache.cleanup_old_tasks() if hasattr(cache, 'cleanup_old_tasks') else None
            ) or 0
            
            return {
                "success": True,
                "cleaned_count": cleaned,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@shared_task(
    bind=True,
    name="app.tasks.cleanup_tasks.reindex_pinecone",
)
def reindex_pinecone(self) -> dict:
    """
    Reindex all entities in Pinecone.
    Runs daily at 3 AM via Celery Beat.
    """
    from app.core.config import settings
    
    if not settings.USE_PINECONE:
        return {"success": True, "message": "Pinecone disabled, skipping reindex"}
    
    try:
        from app.services.embeddings.pinecone_service import pinecone_service
        from app.core.database import async_sessionmaker
        from app.models.models import Entity
        from sqlalchemy import select
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _reindex():
            reindexed = 0
            async with async_sessionmaker() as db:
                result = await db.execute(select(Entity))
                entities = result.scalars().all()
                
                for entity in entities:
                    try:
                        await pinecone_service.upsert_entity(
                            entity_id=str(entity.id),
                            entity_type=entity.entity_type,
                            name=entity.name,
                            description=entity.description or "",
                            attributes=entity.attributes,
                            metadata={
                                "user_id": str(entity.user_id),
                                "tag": entity.tag
                            }
                        )
                        reindexed += 1
                    except Exception as e:
                        print(f"⚠️ Reindex failed for {entity.tag}: {e}")
            
            return reindexed
        
        try:
            count = loop.run_until_complete(_reindex())
            print(f"🔄 Reindexed {count} entities in Pinecone")
            
            return {
                "success": True,
                "reindexed_count": count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        return {"success": False, "error": str(e)}


@shared_task(
    bind=True,
    name="app.tasks.cleanup_tasks.cleanup_orphan_assets",
)
def cleanup_orphan_assets(self) -> dict:
    """
    Clean up assets that are not linked to any entity or session.
    """
    # TODO: Implement orphan asset cleanup
    return {
        "success": True,
        "message": "Orphan asset cleanup not yet implemented"
    }
