"""
Google Video Service - Veo 3.1 Entegrasyonu
Google GenAI SDK üzerinden Veo 3.1 modeline istek atar.
Fallback: Kling V1.5 Pro (fal.ai üzerinden)
"""
import httpx
import time
import asyncio
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GoogleVideoService:
    """
    Google Veo 3.1 video üretim servisi.
    Video (text-to-video veya image-to-video) isteklerini Google API'lerine yönlendirir.
    Eğer SDK patlarsa, fal.ai üzerinden Kling'e fallback yapar.
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.veo_model = "veo-3.1-fast-generate-preview"  # Veo 3.1 Fast — confirmed available
        self._client = None
        
    @property
    def client(self):
        if self._client is None:
            from google import genai
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY tanımlı değil!")
            self._client = genai.Client(api_key=self.api_key)
        return self._client
        
    async def generate_video(self, params: dict) -> dict:
        """
        Veo 3.1 ile video üretir.
        
        Args:
            params: {
                "prompt": str,
                "duration": str ("5", "10" vb.),
                "aspect_ratio": str ("16:9", "9:16", "1:1"),
                "image_url": str (Opsiyonel, i2v için)
            }
        """
        prompt = params.get("prompt", "")
        image_url = params.get("image_url")
        duration = params.get("duration", "5")
        aspect_ratio = params.get("aspect_ratio", "16:9")
        
        logger.info(f"🎬 Veo Video İsteği Başladı: '{prompt[:60]}' (Süre: {duration}s)")
        
        try:
            from google.genai import types
            
            # --- Config ---
            config = types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                person_generation="allow_all",
                number_of_videos=1,
            )
            
            # --- Image-to-video: referans görsel varsa indir ve ekle ---
            source_image = None
            if image_url:
                try:
                    # Görseli indir
                    async with httpx.AsyncClient(timeout=30) as http:
                        logger.info(f"📥 Veo için referans resim indiriliyor: {image_url[:50]}...")
                        resp = await http.get(image_url)
                        resp.raise_for_status()
                        image_data = resp.content
                        mime = resp.headers.get("content-type", "image/jpeg")
                        if "png" in mime:
                            mime = "image/png"
                        elif "webp" in mime:
                            mime = "image/webp"
                        else:
                            mime = "image/jpeg"
                    
                    # Pillow ile boyutlandır (Veo max ~1280 önerilir)
                    try:
                        from PIL import Image as PILImage
                        import tempfile
                        import os
                        
                        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                            tmp.write(image_data)
                            tmp_path = tmp.name
                        
                        with PILImage.open(tmp_path) as img:
                            orig_w, orig_h = img.size
                            max_dim = 1280
                            if orig_w > max_dim or orig_h > max_dim:
                                if orig_w > orig_h:
                                    new_w = max_dim
                                    new_h = int(orig_h * (max_dim / orig_w))
                                else:
                                    new_h = max_dim
                                    new_w = int(orig_w * (max_dim / orig_h))
                                new_w = new_w - (new_w % 8)
                                new_h = new_h - (new_h % 8)
                                if img.mode != 'RGB':
                                    img = img.convert('RGB')
                                img = img.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
                                img.save(tmp_path, format="JPEG", quality=95)
                                logger.info(f"📐 Veo için görsel küçültüldü: {orig_w}x{orig_h} → {new_w}x{new_h}")
                        
                        with open(tmp_path, "rb") as f:
                            image_data = f.read()
                            mime = "image/jpeg"
                        os.remove(tmp_path)
                    except ImportError:
                        logger.warning("Pillow yüklü değil, görsel olduğu gibi gönderiliyor.")
                    
                    source_image = types.Image(image_bytes=image_data, mime_type=mime)
                    logger.info("✅ Referans resim Veo için hazırlandı.")
                except Exception as img_err:
                    logger.warning(f"⚠️ Referans resim hazırlanamadı: {img_err}. Sadece metin ile devam ediliyor.")
            
            # --- SDK Çağrısı ---
            client = self.client
            
            try:
                def run_veo_sync():
                    """Senkron thread'de Veo SDK çağrısı."""
                    if source_image:
                        # Image-to-video
                        op = client.models.generate_videos(
                            model=self.veo_model,
                            image=source_image,
                            prompt=prompt,
                            config=config,
                        )
                    else:
                        # Text-to-video
                        op = client.models.generate_videos(
                            model=self.veo_model,
                            prompt=prompt,
                            config=config,
                        )
                    
                    logger.info(f"⏳ Veo işlemi bekleniyor... (op name: {op.name})")
                    
                    # Poll using operation name (SDK no longer has refresh())
                    max_polls = 60  # Max 10 min
                    for i in range(max_polls):
                        time.sleep(10)
                        try:
                            updated_op = client.operations.get(name=op.name)
                            logger.info(f"   ... Veo poll #{i+1}: done={updated_op.done}")
                            if updated_op.done:
                                if updated_op.error:
                                    raise Exception(f"Veo API Hatası: {updated_op.error}")
                                # Extract video
                                result = updated_op.result
                                if result and result.generated_videos:
                                    video = result.generated_videos[0]
                                    return video.video.uri
                                else:
                                    raise Exception("Veo boş sonuç döndürdü")
                        except AttributeError:
                            # If operations.get doesn't work, try polling done on original op
                            if op.done:
                                if op.error:
                                    raise Exception(f"Veo API Hatası: {op.error}")
                                result = op.result
                                if result and result.generated_videos:
                                    video = result.generated_videos[0]
                                    return video.video.uri
                                else:
                                    raise Exception("Veo boş sonuç döndürdü")
                    
                    raise Exception("Veo zaman aşımı (10 dakika)")
                
                loop = asyncio.get_event_loop()
                video_url = await loop.run_in_executor(None, run_veo_sync)
                
                logger.info(f"✅ Veo ile video başarıyla üretildi: {video_url}")
                return {
                    "success": True,
                    "video_url": video_url,
                    "model": "veo-3.1"
                }
                
            except Exception as sdk_err:
                logger.warning(f"⚠️ Veo SDK hatası: {sdk_err}. Kling'e fallback yapılıyor...")
                
                # ===== FALLBACK: Kling V1.5 Pro (fal.ai) =====
                logger.info("ℹ️ Veo fallback → fal.ai Kling yönlendiriliyor...")
                from app.services.plugins.fal_plugin_v2 import FalPluginV2
                fal = FalPluginV2()
                
                payload = {
                    "prompt": prompt,
                    "duration": duration,
                    "aspect_ratio": aspect_ratio,
                    "model": "kling"  # Kling V1.5 Pro — en kaliteli fallback
                }
                if image_url:
                    payload["image_url"] = image_url
                    
                fallback_res = await fal.execute("generate_video", payload)
                
                if fallback_res.success:
                    return {
                        "success": True,
                        "video_url": fallback_res.data.get("video_url"),
                        "thumbnail_url": fallback_res.data.get("thumbnail_url"),
                        "model": "veo_fallback_kling"
                    }
                else:
                    return {"success": False, "error": f"Veo hatası: {sdk_err}. Kling fallback hatası: {fallback_res.error}"}
            
        except Exception as e:
            logger.error(f"❌ Google Video Service hatası: {str(e)}")
            return {"success": False, "error": str(e)}
