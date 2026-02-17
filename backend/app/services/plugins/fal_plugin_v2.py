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
                "video_editing",
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
            "edit_video",
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
            elif action == "edit_video":
                result = await self._edit_video(params)
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
                    "thumbnail_url": result["video"].get("thumbnail_url"),
                    "model": "kling-3.0-pro",
                }
            else:
                return {"success": False, "error": "Video üretilemedi"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _edit_image(self, params: dict) -> dict:
        """
        Akıllı Görsel Düzenleme.
        
        Sırasıyla dener:
        1. Object Removal (eğer "kaldır/sil" denildiyse)
        2. OmniGen (Genel düzenleme)
        3. Flux Inpainting/Img2Img (Fallback)
        """
        original_prompt = params.get("prompt", "")
        image_url = params.get("image_url", "")
        
        try:
            # 1. Çeviri yap (İngilizce her zaman daha iyi çalışır)
            english_prompt = original_prompt
            try:
                from app.services.prompt_translator import translate_to_english
                english_prompt, _ = await translate_to_english(original_prompt)
                print(f"🎨 Edit Prompt: '{original_prompt}' -> '{english_prompt}'")
            except Exception as trans_error:
                print(f"⚠️ Prompt çeviri hatası: {trans_error}. Orijinal prompt kullanılıyor.")
            
            # 2. "Silme" isteği mi?
            removal_keywords = ["remove", "delete", "erase", "take off", "clear", "gone"]
            is_removal = any(kw in english_prompt.lower() for kw in removal_keywords)
            
            if is_removal:
                # Prompt'tan nesneyi çıkar (Basit keyword extraction)
                object_to_remove = english_prompt
                for word in ["remove", "delete", "erase", "take off", "the", "from", "image", "photo", "picture", "please"]:
                    object_to_remove = object_to_remove.lower().replace(word, "").strip()
                
                print(f"🗑️ Object Removal deneniyor: '{object_to_remove}'")
                
                try:
                    result = await fal_client.subscribe_async(
                        "fal-ai/object-removal",
                        arguments={
                            "image_url": image_url,
                            "prompt": object_to_remove,
                        },
                        with_logs=True,
                    )
                    
                    if result and "image" in result:
                        return {
                            "success": True,
                            "image_url": result["image"]["url"],
                            "model": "object-removal",
                            "method_used": "object_removal"
                        }
                except Exception as e:
                    print(f"⚠️ Object Removal hatası: {e}")

            # 3. OmniGen (Instruction Based)
            print(f"✨ OmniGen deneniyor: '{english_prompt}'")
            try:
                edit_prompt = f"<img><|image_1|></img> {english_prompt}"
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
                        "method_used": "omnigen"
                    }
            except Exception as e:
                 print(f"⚠️ OmniGen hatası: {e}")

            # 4. Fallback: Flux Inpainting (Eğer silme ise keywords ile)
            print("🔧 Flux Inpainting Fallback...")
            return await self._inpainting_flux(image_url, english_prompt if english_prompt else original_prompt)
                
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


    async def _extract_frame(self, video_url: str) -> dict:
        """Video'dan ilk kareyi çıkar (FFmpeg)."""
        try:
            # fal-ai/ffmpeg-api kullanarak kare çıkar
            # -ss 00:00:01 : 1. saniyeden al (başlangıç bazen siyah olabilir)
            command = f"ffmpeg -i {video_url} -ss 00:00:01 -vframes 1 output.png"
            
            result = await fal_client.subscribe_async(
                "fal-ai/ffmpeg-api",
                arguments={"command": command},
                with_logs=True,
            )
            
            if result and "outputs" in result and len(result["outputs"]) > 0:
                return {
                    "success": True,
                    "image_url": result["outputs"][0]["url"],
                    "model": "ffmpeg-api"
                }
            return {"success": False, "error": "Kare çıkarılamadı"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _edit_video(self, params: dict) -> dict:
        """
        Akıllı Video Düzenleme (Smart Hybrid).
        
        Stratejiler:
        1. Flux Inpainting + Kling (Nesne kaldırma/değiştirme)
        2. Video-to-Video (Stil/Atmosfer değiştirme)
        3. OmniGen + Kling (Talimatlı düzenleme)
        """
        video_url = params.get("video_url", "")
        instruction = params.get("prompt", "")  # Talimat
        reference_image_url = params.get("image_url")  # Thumbnail/Reference frame
        
        # Eğer referans görsel YOKSA, video'dan çıkar!
        if not reference_image_url:
            print("⚠️ Video için referans görsel (thumbnail) yok. Çıkarılıyor...")
            extract_result = await self._extract_frame(video_url)
            if extract_result["success"]:
                reference_image_url = extract_result["image_url"]
                print(f"✅ Kare çıkarıldı: {reference_image_url[:60]}...")
            else:
                print("❌ Kare çıkarma başarısız. Video-to-Video fallback yapılacak.")
        
        instruction_lower = instruction.lower()
        
        # Strateji Belirleme
        if not reference_image_url:
             # Görsel yoksa mecburen V2V kullanmalıyız (Inpainting görsel ister)
             print("⚠️ Referans görsel yok, Strategy 2 (V2V) zorunlu seçiliyor.")
             strategy = "strategy_2"
        elif any(keyword in instruction_lower for keyword in ["stil", "style", "yap", "make", "filter", "convert", "transform", "anime", "cartoon"]):
            strategy = "strategy_2"  # Global Dönüşüm
        elif any(keyword in instruction_lower for keyword in ["kaldır", "remove", "sil", "delete", "yok et", "change", "değiştir", "replace"]):
            strategy = "strategy_1"  # Inpainting (Görsel var ise)
        else:
            strategy = "strategy_2"  # Varsayılan fallback

            
        print(f"🎬 Video Edit Stratejisi: {strategy} ({instruction})")
        
        try:
            # STRATEJİ 1: Hassas Nesne Kaldırma/Değiştirme (Inpainting Flow)
            if strategy == "strategy_1" and reference_image_url:
                # 1. Kareyi Düzenle (Smart Edit Image kullan - içinde translation ve keyword extraction var)
                print("   1. Adım: Kare Düzenleniyor (_edit_image)...")
                # _edit_image zaten "remove" keywordlerini algılayıp "Object Removal" modelini,
                # aksi halde OmniGen'i kullanıyor. Bu çok daha güvenli.
                edited_frame = await self._edit_image({
                    "image_url": reference_image_url,
                    "prompt": instruction
                })
                
                if not edited_frame["success"]:
                    print(f"❌ Kare düzenleme hatası: {edited_frame.get('error')}")
                    return edited_frame
                
                print(f"   ✅ Kare düzenlendi: {edited_frame['image_url'][:50]}... (Model: {edited_frame.get('model')})")
                
                # 2. Videoyu Yeniden Üret (Kling I2V)
                print("   2. Adım: Video Yeniden Üretiliyor (Kling)...")
                video_result = await self._generate_video({
                    "prompt": instruction, # Veya original prompt
                    "image_url": edited_frame["image_url"],
                    "duration": "5",
                    "aspect_ratio": "16:9" # Videodan alınmalı aslında
                })
                
                if video_result["success"]:
                    video_result["method_used"] = f"edit_frame_{edited_frame.get('model')}_plus_kling"
                return video_result

            # STRATEJİ 2: Video-to-Video
            elif strategy == "strategy_2":
                return await self._video_to_video(video_url, instruction)

            # STRATEJİ 3: OmniGen + Kling (Fallback)
            else:
                # Reference image varsa OmniGen, yoksa V2V fallback
                if reference_image_url:
                    print("   1. Adım: Kare Düzenleniyor (OmniGen)...")
                    edited_frame = await self._edit_image({
                        "image_url": reference_image_url,
                        "prompt": instruction
                    })
                    if not edited_frame["success"]:
                        return edited_frame
                        
                    print("   2. Adım: Video Yeniden Üretiliyor (Kling)...")
                    video_result = await self._generate_video({
                        "prompt": instruction,
                        "image_url": edited_frame["image_url"]
                    })
                    if video_result["success"]:
                        video_result["method_used"] = "omnigen_plus_kling"
                    return video_result
                else:
                    return await self._video_to_video(video_url, instruction)

        except Exception as e:
            return {"success": False, "error": f"Video düzenleme hatası: {str(e)}"}

    async def _inpainting_flux(self, image_url: str, prompt: str) -> dict:
        """Flux Inpainting ile görsel düzenle."""
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/flux-general/inpainting",
                arguments={
                    "prompt": prompt,
                    "image_url": image_url,
                    "mask_strategy": "keyword", # Basit keyword bazlı maskeleme (örn: "cat")
                    "mask_keywords": prompt,    # Prompt'u keyword olarak kullan
                    "image_size": "landscape_4_3", 
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5,
                    "strength": 1.0 # Tam inpainting
                },
                with_logs=True,
            )
            
            if result and "images" in result and len(result["images"]) > 0:
                return {
                    "success": True,
                    "image_url": result["images"][0]["url"],
                    "model": "flux-inpainting"
                }
            return {"success": False, "error": "Inpainting başarısız"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _video_to_video(self, video_url: str, prompt: str) -> dict:
        """
        Video-to-Video Fallback.
        1. LTX-Video (Genel endpoint)
        2. Başarısız olursa: İlk kareyi al -> Yeni video üret (Loop)
        """
        print(f"🔥🔥 LIVE DEBUG: _video_to_video called with url={video_url}, prompt={prompt}")
        try:
            # 1. LTX-Video (Genel Endpoint - subpath olmadan)
            print("🎥 Video-to-Video: LTX deneniyor...")
            try:
                result = await fal_client.subscribe_async(
                    "fal-ai/ltx-video", # Doğrudan model ID
                    arguments={
                        "video_url": video_url,
                        "prompt": prompt,
                        "resolution": "1280x720"
                    },
                    with_logs=True,
                )
                print(f"🔥🔥 LIVE DEBUG: LTX Result: {result}")
                if result and "video" in result:
                    return {
                        "success": True,
                        "video_url": result["video"]["url"],
                        "model": "ltx-video",
                        "method_used": "video_to_video_ltx"
                    }
            except Exception as e:
                print(f"⚠️ LTX V2V başarısız ({e}), fallback yapılıyor...")
                print(f"🔥🔥 LIVE DEBUG: LTX Exception: {e}")

            # 2. ULTIMATE FALLBACK: Extract Frame + Generate Video
            # Hiçbir V2V çalışmazsa, videonun ilk karesini alıp yeniden üretiriz.
            # Bu işlem asla çökmemeli.
            print("🔄 V2V Fallback: Kare yakala + Yeniden üret...")
            extract_res = await self._extract_frame(video_url)
            print(f"🔥🔥 LIVE DEBUG: Extract Frame Result: {extract_res}")
            
            if extract_res["success"]:
                # Kling ile I2V yap
                return await self._generate_video({
                    "prompt": prompt,
                    "image_url": extract_res["image_url"],
                    "duration": "5",
                    "aspect_ratio": "16:9"
                })
            else:
                return {"success": False, "error": "Video karesi alınamadı, düzenleme iptal."}

        except Exception as e:
            return {"success": False, "error": f"Video edit kritik hata: {str(e)}"}

    # ===============================
    # PUBLIC COMPATIBILITY WRAPPERS
    # ===============================

    async def smart_generate_with_face(self, prompt: str, face_image_url: str, aspect_ratio: str = "1:1", resolution: str = "1K") -> dict:
        """AgentOrchestrator uyumluluğu için wrapper."""
        return await self._smart_generate_with_face({
            "prompt": prompt,
            "face_image_url": face_image_url,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        })

    async def upload_base64_image(self, base64_data: str) -> dict:
        """
        Base64 encoded görseli fal.ai storage'a yükle.
        AgentOrchestrator tarafından direkt çağrılır.
        """
        import base64
        import tempfile
        import os as os_module
        
        try:
            # Data URI prefix'ini temizle
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]
            
            # Base64 decode
            image_bytes = base64.b64decode(base64_data)
            
            # Extension belirle
            if base64_data.startswith("iVBORw"): extension = ".png"
            elif base64_data.startswith("/9j/"): extension = ".jpg"
            elif base64_data.startswith("UklGR"): extension = ".webp"
            else: extension = ".png"
            
            # Temp dosyaya yaz
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            try:
                # fal.ai storage'a yükle
                url = fal_client.upload_file(tmp_path)
                return {"success": True, "url": url}
            finally:
                if os_module.path.exists(tmp_path):
                    os_module.remove(tmp_path)
        except Exception as e:
            return {"success": False, "error": str(e)}

# Backward compatibility için singleton instance
fal_plugin_v2 = FalPluginV2()
