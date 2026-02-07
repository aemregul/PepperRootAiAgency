"""
Image Tasks - Image processing jobs.

Celery tasks for:
- Image generation
- Image upscaling
- Face swap
- Batch image processing
"""
from celery import shared_task
from typing import Optional, List
import asyncio


@shared_task(
    bind=True,
    name="app.tasks.image_tasks.generate_image",
    max_retries=3,
    soft_time_limit=300,  # 5 minutes
)
def generate_image(
    self,
    user_id: str,
    session_id: str,
    prompt: str,
    aspect_ratio: str = "16:9",
    model: str = "fal-ai/flux-pro/v1.1-ultra",
    num_images: int = 1
) -> dict:
    """
    Generate image using Fal.ai.
    """
    from app.services.fal_plugin import FalPlugin
    
    try:
        self.update_state(state="GENERATING", meta={"progress": 10})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            fal_plugin = FalPlugin()
            
            result = loop.run_until_complete(
                fal_plugin.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    model=model
                )
            )
            
            return {
                "success": True,
                "image_url": result.get("image_url"),
                "user_id": user_id,
                "session_id": session_id
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    name="app.tasks.image_tasks.upscale_image",
    max_retries=3,
    soft_time_limit=600,  # 10 minutes
)
def upscale_image(
    self,
    image_url: str,
    scale: int = 2,
    model: str = "fal-ai/aura-sr"
) -> dict:
    """
    Upscale image using Fal.ai.
    """
    from app.services.fal_plugin import FalPlugin
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            fal_plugin = FalPlugin()
            
            result = loop.run_until_complete(
                fal_plugin.upscale_image(
                    image_url=image_url,
                    model=model
                )
            )
            
            return {
                "success": True,
                "upscaled_url": result.get("image_url")
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    name="app.tasks.image_tasks.face_swap",
    max_retries=3,
    soft_time_limit=300,
)
def face_swap(
    self,
    target_image_url: str,
    face_image_url: str
) -> dict:
    """
    Swap face in target image with face from reference.
    """
    from app.services.fal_plugin import FalPlugin
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            fal_plugin = FalPlugin()
            
            result = loop.run_until_complete(
                fal_plugin.face_swap(
                    target_url=target_image_url,
                    swap_url=face_image_url
                )
            )
            
            return {
                "success": True,
                "result_url": result.get("image_url")
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    name="app.tasks.image_tasks.batch_generate",
    max_retries=2,
    soft_time_limit=1800,  # 30 minutes for large batches
)
def batch_generate(
    self,
    user_id: str,
    session_id: str,
    prompts: List[str],
    aspect_ratio: str = "16:9",
    model: str = "fal-ai/flux-pro/v1.1-ultra"
) -> dict:
    """
    Generate multiple images in batch.
    """
    from app.services.fal_plugin import FalPlugin
    
    try:
        results = []
        total = len(prompts)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            fal_plugin = FalPlugin()
            
            for i, prompt in enumerate(prompts):
                self.update_state(
                    state="GENERATING", 
                    meta={
                        "progress": int((i / total) * 100),
                        "current": i + 1,
                        "total": total
                    }
                )
                
                result = loop.run_until_complete(
                    fal_plugin.generate_image(
                        prompt=prompt,
                        aspect_ratio=aspect_ratio,
                        model=model
                    )
                )
                
                results.append({
                    "prompt": prompt,
                    "image_url": result.get("image_url"),
                    "success": True
                })
            
            return {
                "success": True,
                "images": results,
                "total": total,
                "user_id": user_id,
                "session_id": session_id
            }
            
        finally:
            loop.close()
            
    except Exception as e:
        raise self.retry(exc=e)
