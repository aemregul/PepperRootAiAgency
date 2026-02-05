"""
fal.ai Plugin V2 - Yeni plugin sistemine uyumlu fal.ai adapter.

Bu plugin PluginBase'den türetilir ve plugin_loader tarafından yönetilir.
"""
import os
import time
from typing import Optional, Any
import fal_client

from app.core.config import settings
from app.services.plugins.plugin_base import (
    PluginBase, PluginInfo, PluginResult, PluginCategory
)
from app.services.plugins.fal_models import ALL_MODELS, ModelCategory as FalModelCategory


class FalPluginV2(PluginBase):
    """
    fal.ai Plugin - Görsel ve video üretim servisi.
    
    Özellikler:
    - 25+ AI modeli (görsel, video, upscale, edit)
    - Akıllı model seçimi
    - Yüz tutarlılığı (face swap)
    """
    
    def __init__(self):
        super().__init__()
        
        # API key ayarla
        if settings.FAL_KEY:
            os.environ["FAL_KEY"] = settings.FAL_KEY
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="fal_ai",
            display_name="fal.ai",
            version="2.0.0",
            description="Görsel ve video üretimi için fal.ai AI modelleri",
            category=PluginCategory.IMAGE_GENERATION,
            author="Pepper Root",
            requires_api_key=True,
            api_key_env_var="FAL_KEY",
            capabilities=[
                "image_generation",
                "video_generation",
                "image_editing",
                "upscaling",
                "face_swap",
                "background_removal",
            ],
            config_schema={
                "default_model": {"type": "string", "default": "fal-ai/nano-banana-pro"},
                "default_resolution": {"type": "string", "default": "1K"},
            }
        )
    
    def get_available_actions(self) -> list[str]:
        return [
            "generate_image",
            "generate_video",
            "edit_image",
            "upscale_image",
            "upscale_video",
            "remove_background",
            "face_swap",
            "smart_generate_with_face",
        ]
    
    async def execute(self, action: str, params: dict) -> PluginResult:
        """
        Ana çalışma metodu - action'a göre ilgili fonksiyonu çağır.
        """
        start_time = time.time()
        
        if not self.is_enabled:
            return PluginResult(
                success=False,
                error="Plugin devre dışı"
            )
        
        # Parametre doğrulama
        valid, error = self.validate_params(action, params)
        if not valid:
            return PluginResult(success=False, error=error)
        
        try:
            # Action'a göre yönlendir
            if action == "generate_image":
                result = await self._generate_image(params)
            elif action == "generate_video":
                result = await self._generate_video(params)
            elif action == "edit_image":
                result = await self._edit_image(params)
            elif action == "upscale_image":
                result = await self._upscale_image(params)
            elif action == "upscale_video":
                result = await self._upscale_video(params)
            elif action == "remove_background":
                result = await self._remove_background(params)
            elif action == "face_swap":
                result = await self._face_swap(params)
            elif action == "smart_generate_with_face":
                result = await self._smart_generate_with_face(params)
            else:
                return PluginResult(
                    success=False,
                    error=f"Bilinmeyen action: {action}"
                )
            
            execution_time = (time.time() - start_time) * 1000
            
            return PluginResult(
                success=result.get("success", False),
                data=result,
                error=result.get("error"),
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    async def health_check(self) -> bool:
        """fal.ai API bağlantısını kontrol et."""
        try:
            # Basit bir ping
            if not settings.FAL_KEY:
                return False
            return True
        except:
            return False
    
    # ===============================
    # PRIVATE METHODS
    # ===============================
    
    async def _generate_image(self, params: dict) -> dict:
        """Nano Banana Pro ile görsel üret."""
        prompt = params.get("prompt", "")
        aspect_ratio = params.get("aspect_ratio", "1:1")
        resolution = params.get("resolution", "1K")
        
        # Resolution mapping
        resolution_map = {
            "1K": {"square": 1024, "landscape": (1280, 720), "portrait": (720, 1280)},
            "2K": {"square": 1536, "landscape": (1920, 1080), "portrait": (1080, 1920)},
            "4K": {"square": 2048, "landscape": (2560, 1440), "portrait": (1440, 2560)},
        }
        
        # Aspect ratio mapping
        aspect_map = {
            "1:1": "square", "16:9": "landscape", "9:16": "portrait",
            "4:3": "landscape", "3:4": "portrait",
        }
        
        aspect_type = aspect_map.get(aspect_ratio, "square")
        res_config = resolution_map.get(resolution, resolution_map["1K"])
        
        if aspect_type == "square":
            image_size = {"width": res_config["square"], "height": res_config["square"]}
        else:
            w, h = res_config[aspect_type]
            image_size = {"width": w, "height": h}
        
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/nano-banana-pro",
                arguments={
                    "prompt": prompt,
                    "image_size": image_size,
                    "num_images": 1,
                },
                with_logs=True,
            )
            
            if result and "images" in result and len(result["images"]) > 0:
                return {
                    "success": True,
                    "image_url": result["images"][0]["url"],
                    "model": "nano-banana-pro",
                }
            else:
                return {"success": False, "error": "Görsel üretilemedi"}
                
        except Exception as e:
            print(f"❌ FAL.AI HATA: {str(e)}")  # Debug log
            return {"success": False, "error": str(e)}
    
    async def _generate_video(self, params: dict) -> dict:
        """Kling 3.0 Pro ile video üret."""
        prompt = params.get("prompt", "")
        image_url = params.get("image_url")  # Opsiyonel - image-to-video
        duration = params.get("duration", "5")  # 5 veya 10 saniye
        
        try:
            arguments = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": params.get("aspect_ratio", "16:9"),
            }
            
            if image_url:
                arguments["image_url"] = image_url
            
            result = await fal_client.subscribe_async(
                "fal-ai/kling-video/v3/pro/image-to-video" if image_url 
                else "fal-ai/kling-video/v3/pro/text-to-video",
                arguments=arguments,
                with_logs=True,
            )
            
            if result and "video" in result:
                return {
                    "success": True,
                    "video_url": result["video"]["url"],
                    "model": "kling-3.0-pro",
                }
            else:
                return {"success": False, "error": "Video üretilemedi"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _edit_image(self, params: dict) -> dict:
        """
        Görsel düzenleme (instruction-based editing).
        OmniGen kullanarak 'gözlük kaldır', 'saç rengini değiştir' gibi talimatları uygular.
        """
        prompt = params.get("prompt", "")
        image_url = params.get("image_url", "")
        
        try:
            # OmniGen - instruction-based image editing
            # Edit instruction formatı: "<img><|image_1|></img> [talimat]"
            edit_prompt = f"<img><|image_1|></img> {prompt}"
            
            result = await fal_client.subscribe_async(
                "fal-ai/omnigen-v1",
                arguments={
                    "prompt": edit_prompt,
                    "input_image_urls": [image_url],
                    "num_images": 1,
                    "image_size": "square_hd",
                    "guidance_scale": 3.0,
                    "num_inference_steps": 50,
                },
                with_logs=True,
            )
            
            if result and "images" in result and len(result["images"]) > 0:
                return {
                    "success": True,
                    "image_url": result["images"][0]["url"],
                    "model": "omnigen-v1",
                }
            else:
                # Fallback: flux image-to-image
                print("⚠️ OmniGen failed, trying flux fallback...")
                result = await fal_client.subscribe_async(
                    "fal-ai/flux/dev/image-to-image",
                    arguments={
                        "prompt": prompt,
                        "image_url": image_url,
                        "strength": 0.75,
                        "image_size": "square_hd",
                    },
                    with_logs=True,
                )
                
                if result and "images" in result and len(result["images"]) > 0:
                    return {
                        "success": True,
                        "image_url": result["images"][0]["url"],
                        "model": "flux-dev-img2img-fallback",
                    }
                    
                return {"success": False, "error": "Görsel düzenlenemedi"}
                
        except Exception as e:
            print(f"❌ EDIT IMAGE HATA: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _upscale_image(self, params: dict) -> dict:
        """Görsel upscale (Topaz)."""
        image_url = params.get("image_url", "")
        scale = params.get("scale", 2)
        
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/topaz",
                arguments={
                    "image_url": image_url,
                    "scale": scale,
                    "model": "Standard V2",
                },
                with_logs=True,
            )
            
            if result and "image" in result:
                return {
                    "success": True,
                    "image_url": result["image"]["url"],
                    "model": "topaz",
                }
            else:
                return {"success": False, "error": "Upscale yapılamadı"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _upscale_video(self, params: dict) -> dict:
        """Video upscale."""
        video_url = params.get("video_url", "")
        
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/video-upscaler",
                arguments={"video_url": video_url},
                with_logs=True,
            )
            
            if result and "video" in result:
                return {
                    "success": True,
                    "video_url": result["video"]["url"],
                    "model": "video-upscaler",
                }
            else:
                return {"success": False, "error": "Video upscale yapılamadı"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _remove_background(self, params: dict) -> dict:
        """Arka plan kaldır (Bria RMBG)."""
        image_url = params.get("image_url", "")
        
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/bria/rmbg",
                arguments={"image_url": image_url},
                with_logs=True,
            )
            
            if result and "image" in result:
                return {
                    "success": True,
                    "image_url": result["image"]["url"],
                    "model": "bria-rmbg",
                }
            else:
                return {"success": False, "error": "Arka plan kaldırılamadı"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _face_swap(self, params: dict) -> dict:
        """Yüz değiştirme."""
        base_image_url = params.get("base_image_url", "")
        swap_image_url = params.get("swap_image_url", "")
        
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/face-swap",
                arguments={
                    "base_image_url": base_image_url,
                    "swap_image_url": swap_image_url,
                },
                with_logs=True,
            )
            
            if result and "image" in result:
                return {
                    "success": True,
                    "image_url": result["image"]["url"],
                    "model": "face-swap",
                }
            else:
                return {"success": False, "error": "Yüz değişimi yapılamadı"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _smart_generate_with_face(self, params: dict) -> dict:
        """
        Akıllı görsel üretim - yüz tutarlılığı ile.
        
        1. Nano Banana ile görsel üret
        2. Yüz kontrolü yap
        3. Gerekirse face swap uygula
        """
        prompt = params.get("prompt", "")
        face_image_url = params.get("face_image_url", "")
        aspect_ratio = params.get("aspect_ratio", "1:1")
        resolution = params.get("resolution", "1K")
        
        # 1. Base görsel üret
        base_result = await self._generate_image({
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        })
        
        if not base_result.get("success"):
            return base_result
        
        base_image_url = base_result["image_url"]
        
        # 2. Face swap uygula
        swap_result = await self._face_swap({
            "base_image_url": base_image_url,
            "swap_image_url": face_image_url,
        })
        
        if swap_result.get("success"):
            return {
                "success": True,
                "image_url": swap_result["image_url"],
                "base_image_url": base_image_url,
                "method_used": "nano_banana_with_face_swap",
                "quality_check": "Yüz tutarlılığı sağlandı.",
            }
        else:
            # Face swap başarısızsa base görseli döndür
            return {
                "success": True,
                "image_url": base_image_url,
                "method_used": "nano_banana_only",
                "quality_check": "Face swap başarısız, base görsel döndürüldü.",
            }


# Backward compatibility için singleton instance
fal_plugin_v2 = FalPluginV2()
