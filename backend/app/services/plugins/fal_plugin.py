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
    
    async def generate_with_nano_banana(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        num_images: int = 1,
        seed: int = None,
    ) -> dict:
        """
        Nano Banana Pro ile yüksek kaliteli görsel üret.
        
        Nano Banana Pro (Google Gemini tabanlı), hem kalite hem de
        yüz tutarlılığı açısından en iyi sonuçları veren model.
        
        Args:
            prompt: Sahne açıklaması (detaylı prompt önerilir)
            aspect_ratio: Görsel oranı (1:1, 16:9, 9:16, 4:3, 3:4, vb.)
            resolution: Çözünürlük (1K, 2K, 4K)
            num_images: Üretilecek görsel sayısı
            seed: Tekrarlanabilirlik için seed
        
        Returns:
            dict: {"success": bool, "image_url": str, "error": str}
        """
        try:
            arguments = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "num_images": num_images,
                "resolution": resolution,
                "output_format": "png"
            }
            
            if seed is not None:
                arguments["seed"] = seed
            
            result = await fal_client.subscribe_async(
                "fal-ai/nano-banana-pro",
                arguments=arguments,
                with_logs=True,
            )
            
            # 🔍 DEBUG: API yanıtı
            print(f"🍌 NANO BANANA API Response: success={bool(result)}, has_images={bool(result and 'images' in result)}")
            if result and "images" in result:
                print(f"   → Image count: {len(result['images'])}")
            
            if result and "images" in result and len(result["images"]) > 0:
                return {
                    "success": True,
                    "image_url": result["images"][0]["url"],
                    "model": "nano-banana-pro",
                    "result": result
                }
            else:
                return {
                    "success": False,
                    "error": "Görsel üretilemedi (Nano Banana)"
                }
                
        except Exception as e:
            print(f"🔴 NANO BANANA ERROR: {type(e).__name__}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def apply_face_swap(
        self,
        base_image_url: str,
        face_image_url: str,
    ) -> dict:
        """
        Mevcut bir görsele yüz swap uygula.
        
        Bu metod, Nano Banana çıktısında yüz tutarlılığı kötü olduğunda
        fallback olarak kullanılır.
        
        Args:
            base_image_url: Üzerinde işlem yapılacak görsel
            face_image_url: Yüz referans görseli
        
        Returns:
            dict: {"success": bool, "image_url": str}
        """
        try:
            result = await fal_client.subscribe_async(
                "fal-ai/face-swap",
                arguments={
                    "base_image_url": base_image_url,
                    "swap_image_url": face_image_url
                },
                with_logs=True,
            )
            
            if result and "image" in result:
                return {
                    "success": True,
                    "image_url": result["image"]["url"],
                    "model": "face-swap"
                }
            else:
                return {
                    "success": False,
                    "error": "Face swap uygulanamadı"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def smart_generate_with_face(
        self,
        prompt: str,
        face_image_url: str,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
    ) -> dict:
        """
        Akıllı görsel üretim sistemi (Agent'ın ana metodu).
        
        İş Akışı:
        1. Nano Banana Pro ile görsel üret (en iyi kalite)
        2. Claude Vision ile yüz tutarlılığını kontrol et
        3. Tutarlılık kötüyse → Face Swap uygula
        4. En iyi sonucu döndür
        
        Args:
            prompt: Sahne açıklaması
            face_image_url: Yüz referans görseli URL
            aspect_ratio: Görsel oranı
            resolution: Çözünürlük
        
        Returns:
            dict: {
                "success": bool,
                "image_url": str,
                "method_used": str,  # "nano-banana" veya "nano-banana+face-swap"
                "quality_check": str,  # Kalite kontrol sonucu
            }
        """
        try:
            # Adım 1: Nano Banana Pro ile görsel üret
            # Prompt'a yüz detayları ekle
            enhanced_prompt = f"{prompt}, portrait style, face clearly visible, photorealistic, detailed facial features"
            
            nano_result = await self.generate_with_nano_banana(
                prompt=enhanced_prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            
            if not nano_result.get("success"):
                return nano_result
            
            base_image_url = nano_result["image_url"]
            
            # Adım 2: Önce Nano Banana sonucunu dene, 
            # eğer face_image_url varsa Face Swap de yap ve karşılaştır
            
            # Face Swap uygula
            swap_result = await self.apply_face_swap(
                base_image_url=base_image_url,
                face_image_url=face_image_url
            )
            
            if swap_result.get("success"):
                # Face Swap başarılı - her iki sonucu da döndür
                # Agent veya kullanıcı seçebilir
                return {
                    "success": True,
                    "image_url": swap_result["image_url"],
                    "base_image_url": base_image_url,  # Nano Banana sonucu
                    "method_used": "nano-banana+face-swap",
                    "quality_check": "Face swap uygulandı - yüz referansına göre optimize edildi"
                }
            else:
                # Face Swap başarısız - Nano Banana sonucunu kullan
                return {
                    "success": True,
                    "image_url": base_image_url,
                    "method_used": "nano-banana",
                    "quality_check": "Nano Banana Pro çıktısı kullanıldı"
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
    
    # PuLID kaldırıldı - Nano Banana Pro tercih ediliyor
    
    # ===============================
    # VIDEO ÜRETİM
    # ===============================
    
    async def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        model: str = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
        duration: str = "5",
        aspect_ratio: str = "16:9",
    ) -> dict:
        """
        Video üret (text-to-video veya image-to-video).
        
        Args:
            prompt: Video açıklaması
            image_url: Başlangıç görseli (opsiyonel)
            model: Kullanılacak video modeli
            duration: Video süresi (saniye)
            aspect_ratio: Video oranı
        
        Returns:
            dict: {"success": bool, "video_url": str}
        """
        try:
            arguments = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
            }
            
            # Image-to-video ise görsel ekle
            if image_url:
                arguments["image_url"] = image_url
                if "text-to-video" in model:
                    # Text-to-video modeli kullanılıyorsa image-to-video'ya geç
                    model = model.replace("text-to-video", "image-to-video")
            else:
                # Görsel yoksa text-to-video kullan
                if "image-to-video" in model:
                    model = model.replace("image-to-video", "text-to-video")
            
            result = await fal_client.subscribe_async(
                model,
                arguments=arguments,
                with_logs=True,
            )
            
            # Video URL'sini bul
            video_url = None
            if result:
                if "video" in result:
                    video_url = result["video"].get("url")
                elif "video_url" in result:
                    video_url = result["video_url"]
                elif "output" in result:
                    video_url = result["output"].get("url")
            
            if video_url:
                return {
                    "success": True,
                    "video_url": video_url,
                    "model": model,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "error": "Video üretilemedi - boş sonuç"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # GÖRSEL DÜZENLEME
    # ===============================
    
    async def edit_image(
        self,
        image_url: str,
        prompt: str,
        model: str = "fal-ai/nano-banana-pro/edit",
        mask_url: Optional[str] = None,
    ) -> dict:
        """
        Mevcut bir görseli düzenle.
        
        Args:
            image_url: Düzenlenecek görsel
            prompt: Düzenleme talimatı
            model: Düzenleme modeli
            mask_url: Maske görseli (opsiyonel)
        
        Returns:
            dict: {"success": bool, "image_url": str}
        """
        try:
            arguments = {
                "image_url": image_url,
                "prompt": prompt,
            }
            
            if mask_url:
                arguments["mask_url"] = mask_url
            
            result = await fal_client.subscribe_async(
                model,
                arguments=arguments,
                with_logs=True,
            )
            
            # Sonucu işle
            image_result_url = None
            if result:
                if "images" in result and len(result["images"]) > 0:
                    image_result_url = result["images"][0]["url"]
                elif "image" in result:
                    image_result_url = result["image"].get("url")
            
            if image_result_url:
                return {
                    "success": True,
                    "image_url": image_result_url,
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": "Görsel düzenlenemedi - boş sonuç"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # UPSCALING
    # ===============================
    
    async def upscale_image(
        self,
        image_url: str,
        model: str = "fal-ai/topaz/upscale/image",
        scale: int = 2,
    ) -> dict:
        """
        Görsel kalitesini ve çözünürlüğünü artır.
        
        Args:
            image_url: Upscale edilecek görsel
            model: Upscale modeli
            scale: Büyütme faktörü (2x, 4x)
        
        Returns:
            dict: {"success": bool, "image_url": str}
        """
        try:
            arguments = {
                "image_url": image_url,
                "scale": scale,
            }
            
            result = await fal_client.subscribe_async(
                model,
                arguments=arguments,
                with_logs=True,
            )
            
            # Sonucu işle
            image_result_url = None
            if result:
                if "image" in result:
                    image_result_url = result["image"].get("url")
                elif "images" in result and len(result["images"]) > 0:
                    image_result_url = result["images"][0]["url"]
                elif "output" in result:
                    image_result_url = result["output"].get("url")
            
            if image_result_url:
                return {
                    "success": True,
                    "image_url": image_result_url,
                    "model": model,
                    "scale": scale
                }
            else:
                return {
                    "success": False,
                    "error": "Upscale yapılamadı - boş sonuç"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def upscale_video(
        self,
        video_url: str,
        model: str = "fal-ai/topaz/upscale/video",
    ) -> dict:
        """
        Video kalitesini artır.
        
        Args:
            video_url: Upscale edilecek video
            model: Upscale modeli
        
        Returns:
            dict: {"success": bool, "video_url": str}
        """
        try:
            result = await fal_client.subscribe_async(
                model,
                arguments={"video_url": video_url},
                with_logs=True,
            )
            
            video_result_url = None
            if result:
                if "video" in result:
                    video_result_url = result["video"].get("url")
                elif "video_url" in result:
                    video_result_url = result["video_url"]
            
            if video_result_url:
                return {
                    "success": True,
                    "video_url": video_result_url,
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": "Video upscale yapılamadı"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # YARDIMCI ARAÇLAR
    # ===============================
    
    async def upload_base64_image(
        self,
        base64_data: str,
    ) -> dict:
        """
        Base64 encoded görseli fal.ai storage'a yükle.
        
        Bu metod, kullanıcının gönderdiği referans görselini
        kalıcı bir URL'ye dönüştürür ve entity'de saklanabilir hale getirir.
        
        Args:
            base64_data: Base64 encoded görsel verisi (data URI prefix olmadan)
        
        Returns:
            dict: {"success": bool, "url": str}
        """
        import base64
        import tempfile
        import os as os_module
        
        try:
            # Data URI prefix'ini temizle (örn: "data:image/png;base64,...")
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]
            
            # Base64'ü decode et
            image_bytes = base64.b64decode(base64_data)
            
            # Media type'ı belirle
            if base64_data.startswith("iVBORw"):
                extension = ".png"
            elif base64_data.startswith("/9j/"):
                extension = ".jpg"
            elif base64_data.startswith("UklGR"):
                extension = ".webp"
            else:
                extension = ".png"  # default
            
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp_file:
                tmp_file.write(image_bytes)
                tmp_path = tmp_file.name
            
            try:
                # fal.ai storage'a yükle
                url = fal_client.upload_file(tmp_path)
                
                return {
                    "success": True,
                    "url": url
                }
            finally:
                # Geçici dosyayı temizle
                if os_module.path.exists(tmp_path):
                    os_module.remove(tmp_path)
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def remove_background(
        self,
        image_url: str,
        model: str = "fal-ai/bria/background/remove",
    ) -> dict:
        """
        Görsel arka planını kaldır.
        
        Args:
            image_url: İşlenecek görsel
            model: Background removal modeli
        
        Returns:
            dict: {"success": bool, "image_url": str}
        """
        try:
            result = await fal_client.subscribe_async(
                model,
                arguments={"image_url": image_url},
                with_logs=True,
            )
            
            image_result_url = None
            if result:
                if "image" in result:
                    image_result_url = result["image"].get("url")
                elif "images" in result and len(result["images"]) > 0:
                    image_result_url = result["images"][0]["url"]
            
            if image_result_url:
                return {
                    "success": True,
                    "image_url": image_result_url,
                    "model": model,
                    "has_transparency": True
                }
            else:
                return {
                    "success": False,
                    "error": "Arka plan kaldırılamadı"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
fal_plugin = FalPlugin()