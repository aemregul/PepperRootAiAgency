"""
Grid Generator API - 3x3 grid görsel üretimi.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import base64
import io

from app.core.config import settings

router = APIRouter(prefix="/grid", tags=["grid"])


class GridGenerateRequest(BaseModel):
    """Grid üretim isteği."""
    image: str  # Base64 encoded image
    aspect: str = "16:9"  # 16:9, 9:16, 1:1
    mode: str = "angles"  # angles, storyboard
    prompt: Optional[str] = None


class GridGenerateResponse(BaseModel):
    """Grid üretim yanıtı."""
    success: bool
    gridImage: Optional[str] = None  # Base64 or URL
    error: Optional[str] = None


def build_grid_prompt(mode: str, character_prompt: str = "") -> str:
    """Grid için prompt oluştur."""
    base = character_prompt or "the subject from the reference image"
    
    if mode == "angles":
        return f"""Create a seamless 3x3 grid of 9 cinematic camera angles showing: {base}

GRID REQUIREMENTS:
- NO white borders or gaps between panels
- Each panel edge-to-edge, flowing into the next
- The SAME EXACT person in ALL 9 panels - identical face, identical features

9 CAMERA ANGLES (left to right, top to bottom):
1. WIDE SHOT - full body, environment visible
2. MEDIUM WIDE - head to knees
3. MEDIUM SHOT - waist up, classic portrait
4. MEDIUM CLOSE-UP - chest and head
5. CLOSE-UP - face fills 70% of frame
6. THREE-QUARTER VIEW - face angled 45°, dramatic
7. LOW ANGLE - camera below eye level, heroic
8. HIGH ANGLE - camera above, looking down
9. PROFILE - side view with rim lighting

CRITICAL: Face must be clearly visible in ALL panels. Cinematic, photorealistic, 8K quality."""

    elif mode == "storyboard":
        return f"""Create a seamless 3x3 grid of 9 sequential storyboard panels showing: {base}

GRID REQUIREMENTS:
- NO white borders or gaps between panels
- Each panel edge-to-edge, flowing into the next
- The SAME EXACT person in ALL 9 panels

9 STORY BEATS (read left to right, top to bottom):
1. ESTABLISHING - calm moment, wide shot
2. TENSION - notices something, medium shot
3. REACTION - close-up, concern/interest
4. ACTION BEGINS - starts moving, wide shot
5. PEAK ACTION - dynamic movement, medium
6. INTENSITY - extreme close-up, emotion
7. CLIMAX - dramatic action, full body
8. RESOLUTION - medium shot, conflict ending
9. CONCLUSION - close-up, final emotion

CRITICAL: Same character throughout. Cinematic storyboard quality."""

    else:
        return f"Create a seamless 3x3 grid showing 9 variations of: {base}. NO borders, NO gaps. Photorealistic, cinematic."


async def generate_with_nano_banana(image_data: str, prompt: str, aspect: str, api_key: str) -> str:
    """Nano Banana Pro ile grid üret."""
    aspect_ratio = "16:9" if aspect == "16:9" else "9:16" if aspect == "9:16" else "1:1"
    
    request_body = {
        "prompt": prompt,
        "image_urls": [image_data],
        "num_images": 1,
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
        "resolution": "2K",
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://fal.run/fal-ai/nano-banana-pro/edit",
            headers={
                "Authorization": f"Key {api_key}",
                "Content-Type": "application/json",
            },
            json=request_body
        )
        
        if response.status_code != 200:
            raise Exception(f"Nano Banana Pro failed: {response.status_code} - {response.text}")
        
        data = response.json()
        if data.get("images") and len(data["images"]) > 0:
            return data["images"][0]["url"]
        
        raise Exception("No images in response")


async def generate_with_flux_dev(image_data: str, prompt: str, aspect: str, api_key: str) -> str:
    """FLUX 1 dev ile fallback grid üret."""
    if aspect == "16:9":
        image_size = {"width": 1920, "height": 1080}
    elif aspect == "9:16":
        image_size = {"width": 1080, "height": 1920}
    else:
        image_size = {"width": 1024, "height": 1024}
    
    request_body = {
        "prompt": prompt,
        "image_url": image_data,
        "strength": 0.75,
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
        "image_size": image_size,
        "num_images": 1,
        "enable_safety_checker": False,
        "output_format": "png",
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://fal.run/fal-ai/flux/dev/image-to-image",
            headers={
                "Authorization": f"Key {api_key}",
                "Content-Type": "application/json",
            },
            json=request_body
        )
        
        if response.status_code != 200:
            raise Exception(f"FLUX dev failed: {response.status_code} - {response.text}")
        
        data = response.json()
        if data.get("images") and len(data["images"]) > 0:
            return data["images"][0]["url"]
        
        raise Exception("No images in response")


@router.post("/generate", response_model=GridGenerateResponse)
async def generate_grid(request: GridGenerateRequest):
    """3x3 grid görsel üret."""
    
    if not settings.FAL_KEY:
        raise HTTPException(status_code=500, detail="FAL API key not configured")
    
    print(f"=== GRID GENERATION ===")
    print(f"Mode: {request.mode}")
    print(f"Aspect: {request.aspect}")
    
    # Prompt oluştur
    grid_prompt = request.prompt or build_grid_prompt(request.mode)
    print(f"Prompt: {grid_prompt[:100]}...")
    
    result_image = None
    
    # 1. Nano Banana Pro dene
    try:
        print("Trying Nano Banana Pro...")
        result_image = await generate_with_nano_banana(
            request.image, grid_prompt, request.aspect, settings.FAL_KEY
        )
        print("Nano Banana Pro success!")
    except Exception as e:
        print(f"Nano Banana Pro failed: {e}")
    
    # 2. FLUX dev fallback
    if not result_image:
        try:
            print("Trying FLUX dev...")
            result_image = await generate_with_flux_dev(
                request.image, grid_prompt, request.aspect, settings.FAL_KEY
            )
            print("FLUX dev success!")
        except Exception as e:
            print(f"FLUX dev failed: {e}")
            raise HTTPException(status_code=500, detail=f"Grid generation failed: {e}")
    
    return GridGenerateResponse(
        success=True,
        gridImage=result_image
    )
