"""
fal.ai Plugin - Görsel/Video üretim servisi.
"""
import os
from typing import Optional
import fal_client
from app.core.config import settings


class FalPlugin:
    """fal.ai ile görsel ve video üretimi."""
    
    def __init__(self):
        # FAL_KEY environment variable olarak ayarlanmalı
        if settings.FAL_KEY:
            os.environ["FAL_KEY"] = settings.FAL_KEY
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "fal-ai/flux/schnell",
        image_size: str = "square_hd",
        num_images: int = 1,
        seed: Optional[int] = None,
    ) -> dict:
        """
        Prompt'tan görsel üret.
        
        Returns:
            dict: {"success": bool, "image_url": str, "error": str}
        """
        try:
            arguments = {
                "prompt": prompt,
                "image_size": image_size,
                "num_images": num_images,
            }
            
            if seed is not None:
                arguments["seed"] = seed
            
            # fal_client.subscribe_async ile çağır
            result = await fal_client.subscribe_async(
                model,
                arguments=arguments,
                with_logs=True,
            )
            
            # Sonucu işle
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                return {
                    "success": True,
                    "image_url": image_url,
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": "Görsel üretilemedi - boş sonuç"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_image_with_reference(
        self,
        prompt: str,
        image_url: str,
        model: str = "fal-ai/flux/dev/image-to-image",
        strength: float = 0.85,
        image_size: str = "square_hd",
    ) -> dict:
        """
        Referans görsel ile yeni görsel üret.
        
        Returns:
            dict: {"success": bool, "image_url": str, "error": str}
        """
        try:
            result = await fal_client.subscribe_async(
                model,
                arguments={
                    "prompt": prompt,
                    "image_url": image_url,
                    "strength": strength,
                    "image_size": image_size,
                },
                with_logs=True,
            )
            
            if result and "images" in result and len(result["images"]) > 0:
                return {
                    "success": True,
                    "image_url": result["images"][0]["url"],
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": "Görsel üretilemedi - boş sonuç"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
fal_plugin = FalPlugin()