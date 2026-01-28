"""
Görsel üretim API endpoint'leri.
"""
from fastapi import APIRouter, HTTPException

from app.schemas.schemas import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    ImageToImageRequest,
)
from app.services.plugins.fal_plugin import fal_plugin
from app.core.config import settings


router = APIRouter(tags=["generate"])


@router.post("/image", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerateRequest):
    """
    Prompt'tan görsel üret.
    
    Desteklenen modeller:
    - fal-ai/flux/schnell (hızlı, ücretsiz tier)
    - fal-ai/flux/dev (daha kaliteli)
    - fal-ai/flux-pro (en kaliteli)
    
    Desteklenen boyutlar:
    - square_hd (1024x1024)
    - landscape_4_3 (1024x768)
    - portrait_4_3 (768x1024)
    - landscape_16_9 (1024x576)
    - portrait_16_9 (576x1024)
    """
    if not settings.FAL_KEY:
        raise HTTPException(
            status_code=500,
            detail="FAL_KEY yapılandırılmamış"
        )
    
    try:
        result = await fal_plugin.generate_image(
            prompt=request.prompt,
            model=request.model,
            image_size=request.image_size,
            num_images=request.num_images,
            seed=request.seed,
        )
        
        return ImageGenerateResponse(
            images=result.get("images", []),
            seed=result.get("seed"),
            prompt=request.prompt,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Görsel üretimi başarısız: {str(e)}"
        )


@router.post("/image-to-image", response_model=ImageGenerateResponse)
async def generate_image_from_reference(request: ImageToImageRequest):
    """
    Referans görsel kullanarak yeni görsel üret.
    
    strength parametresi:
    - 0.0: Orijinal görsele çok benzer
    - 1.0: Tamamen farklı (sadece prompt'a uygun)
    """
    if not settings.FAL_KEY:
        raise HTTPException(
            status_code=500,
            detail="FAL_KEY yapılandırılmamış"
        )
    
    try:
        result = await fal_plugin.generate_image_with_reference(
            prompt=request.prompt,
            image_url=request.image_url,
            model=request.model,
            strength=request.strength,
            image_size=request.image_size,
        )
        
        return ImageGenerateResponse(
            images=result.get("images", []),
            seed=result.get("seed"),
            prompt=request.prompt,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Görsel üretimi başarısız: {str(e)}"
        )
