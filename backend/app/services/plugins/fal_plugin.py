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
        
        Args:
            prompt: Görsel açıklaması
            model: Kullanılacak model (varsayılan: flux/schnell)
            image_size: Boyut (square_hd, landscape_4_3, portrait_4_3, vb.)
            num_images: Üretilecek görsel sayısı
            seed: Rastgelelik tohumu (tekrarlanabilirlik için)
        
        Returns:
            fal.ai API yanıtı (images listesi içerir)
        """
        arguments = {
            "prompt": prompt,
            "image_size": image_size,
            "num_images": num_images,
        }
        
        if seed is not None:
            arguments["seed"] = seed
        
        # fal_client.subscribe async generator döndürür
        result = await fal_client.subscribe_async(
            model,
            arguments=arguments,
            with_logs=True,
        )
        
        return result
    
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
        
        Args:
            prompt: Görsel açıklaması
            image_url: Referans görsel URL'i
            model: Kullanılacak model
            strength: Değişiklik gücü (0-1, yüksek = daha çok değişir)
            image_size: Boyut
        
        Returns:
            fal.ai API yanıtı
        """
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
        
        return result


# Singleton instance
fal_plugin = FalPlugin()
