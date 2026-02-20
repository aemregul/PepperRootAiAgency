"""
Gemini Image Generation Service — Hibrit pipeline için.
Referans görsel varsa Gemini ile üretir (face identity korunur).
"""
import base64
import httpx
from typing import Optional
from app.core.config import settings


class GeminiImageService:
    """Gemini 2.5 Flash ile görsel üretim/düzenleme."""
    
    def __init__(self):
        self._client = None
        self.model = "gemini-2.5-flash-image"
    
    @property
    def client(self):
        if self._client is None:
            from google import genai
            api_key = settings.GEMINI_API_KEY
            if not api_key:
                raise ValueError("GEMINI_API_KEY tanımlı değil!")
            self._client = genai.Client(api_key=api_key)
        return self._client
    
    async def generate_with_reference(
        self,
        prompt: str,
        reference_image_url: str,
        reference_images_urls: list[str] = None,
        aspect_ratio: str = "1:1"
    ) -> dict:
        """
        Referans görsel(ler) ile Gemini üzerinden yeni görsel üret.
        Gemini native olarak yüz kimliğini korur.
        
        Args:
            prompt: Üretim talimatı
            reference_image_url: Ana referans görsel URL'i
            reference_images_urls: Ek referans görselleri (opsiyonel)
            aspect_ratio: Aspect ratio (1:1, 16:9, 9:16 vb.)
        
        Returns:
            dict: {success, image_url, method_used, ...}
        """
        from google.genai import types
        
        try:
            # Tüm referans URL'leri topla
            all_urls = []
            if reference_images_urls:
                all_urls = list(reference_images_urls)
            elif reference_image_url:
                all_urls = [reference_image_url]
            
            if not all_urls:
                return {"success": False, "error": "Referans görsel URL'si gerekli"}
            
            print(f"🤖 Gemini ile üretim başlıyor — {len(all_urls)} referans görsel")
            
            # Referans görselleri indir ve Gemini content parts oluştur
            contents = []
            async with httpx.AsyncClient(timeout=30) as http:
                for i, url in enumerate(all_urls[:5]):  # Max 5 referans
                    try:
                        resp = await http.get(url)
                        if resp.status_code == 200:
                            image_data = resp.content
                            mime = resp.headers.get("content-type", "image/png")
                            if "jpeg" in mime or "jpg" in mime:
                                mime = "image/jpeg"
                            elif "webp" in mime:
                                mime = "image/webp"
                            else:
                                mime = "image/png"
                            
                            contents.append(
                                types.Part.from_bytes(data=image_data, mime_type=mime)
                            )
                            print(f"   📥 Referans {i+1} indirildi ({len(image_data)} bytes)")
                    except Exception as dl_err:
                        print(f"   ⚠️ Referans {i+1} indirilemedi: {dl_err}")
            
            if not contents:
                return {"success": False, "error": "Referans görseller indirilemedi"}
            
            # Aspect ratio'ya göre boyut ipucu ekle
            size_hint = ""
            if aspect_ratio == "16:9":
                size_hint = " Wide landscape format (16:9)."
            elif aspect_ratio == "9:16":
                size_hint = " Vertical portrait format (9:16)."
            elif aspect_ratio == "4:3":
                size_hint = " Standard 4:3 format."
            
            # Prompt'u oluştur — Gemini'ye referans görsellerdeki kişileri korumasını söyle
            if len(all_urls) > 1:
                gemini_prompt = (
                    f"You have been provided {len(contents)} reference images. "
                    f"CRITICAL INSTRUCTION: The VERY FIRST image is the primary subject. You MUST preserve the exact facial features, face shape, skin tone, and identity ONLY from the FIRST image. "
                    f"The other images are provided merely as contextual references for body types, tattoos, clothing, or environment. Do NOT use the faces from the subsequent images. "
                    f"WARNING: If the text prompt mentions a famous celebrity or character (e.g., 'The Rock', 'Johnny Depp'), it is ONLY to describe a body type, vibe, or style. "
                    f"DO NOT draw the celebrity's face under any circumstances. You MUST strictly use the anonymous face from the FIRST image. "
                    f"Generate a new image based on this prompt: {prompt}. "
                    f"Again, keep the identity from the FIRST image perfectly recognizable and DO NOT override it with the celebrity.{size_hint}"
                )
            else:
                gemini_prompt = (
                    f"Using this reference image of a person, generate a new image: {prompt}. "
                    f"IMPORTANT: Preserve the exact facial features, face shape, skin tone, and identity of the person. "
                    f"WARNING: If the text prompt mentions a famous celebrity or character (e.g., 'The Rock', 'Johnny Depp'), it is ONLY for vibe or style. "
                    f"DO NOT draw the celebrity's face. You MUST strictly keep the anonymous identity of the provided reference image. "
                    f"Do NOT change their face. Keep their identity recognizable.{size_hint}"
                )
            
            contents.append(gemini_prompt)
            
            print(f"   📝 Gemini prompt: {gemini_prompt[:120]}...")
            
            # Gemini API çağrısı
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )
            
            # Sonucu parse et
            generated_image = None
            generated_mime = None
            text_response = ""
            
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        generated_image = part.inline_data.data
                        generated_mime = part.inline_data.mime_type
                    elif part.text:
                        text_response = part.text
            
            if not generated_image:
                finish_reason = ""
                if response.candidates:
                    fr = getattr(response.candidates[0], 'finish_reason', None)
                    if fr:
                        finish_reason = f" (finish_reason: {fr})"
                return {
                    "success": False,
                    "error": f"Gemini görsel üretemedi{finish_reason}. Text: {text_response[:200]}"
                }
            
            # Görseli fal.ai'ye yükle (URL olarak döndürmek için)
            image_url = await self._upload_to_fal(generated_image, generated_mime or "image/png")
            
            if not image_url:
                return {"success": False, "error": "Gemini görseli üretildi ama fal.ai'ye yüklenemedi"}
            
            print(f"   ✅ Gemini görsel üretildi ve yüklendi: {image_url[:60]}...")
            
            return {
                "success": True,
                "image_url": image_url,
                "method_used": "gemini-2.5-flash",
                "model_display_name": "Gemini 2.5 Flash (Native Identity)",
                "quality_notes": "Gemini native identity preservation — yüz kimliği korunmuştur",
                "text_response": text_response
            }
            
    async def edit_with_reference(
        self,
        prompt: str,
        image_to_edit_url: str,
        reference_images_urls: list[str],
        mask_image_url: Optional[str] = None
    ) -> dict:
        """
        Görseli düzenle (inpainting) ve kimliği koru.
        
        Args:
            prompt: Düzenleme talimatı (inpainting prompt)
            image_to_edit_url: Düzenlenecek ana görsel (canvas)
            reference_images_urls: Kimlik/Nesne referansları listesi
            mask_image_url: Opsiyonel inpainting maskesi.
            
        Returns:
            dict: {success, image_url, ...}
        """
        from google.genai import types
        
        try:
            if not image_to_edit_url:
                return {"success": False, "error": "Düzenlenecek görsel URL'si gerekli"}
            
            print(f"🤖 Gemini ile düzenleme başlıyor — Canvas + {len(reference_images_urls)} referans")
            
            contents = []
            async with httpx.AsyncClient(timeout=30) as http:
                # 1. CANVAS (Düzenlenecek görsel) - HER ZAMAN İLK OLMALI
                try:
                    resp = await http.get(image_to_edit_url)
                    if resp.status_code == 200:
                        contents.append(types.Part.from_bytes(data=resp.content, mime_type=resp.headers.get("content-type", "image/png")))
                        print(f"   📥 Canvas indirildi ({len(resp.content)} bytes)")
                except Exception as e:
                    return {"success": False, "error": f"Canvas görseli indirilemedi: {e}"}
                
                # 2. REFERANSLAR (Kimlik/Nesne referansları)
                for i, url in enumerate(reference_images_urls[:4]): # Max 4 ek referans
                    try:
                        if url == image_to_edit_url: continue # Çiftleme yapma
                        resp = await http.get(url)
                        if resp.status_code == 200:
                            contents.append(types.Part.from_bytes(data=resp.content, mime_type=resp.headers.get("content-type", "image/png")))
                            print(f"   📥 Referans {i+1} indirildi ({len(resp.content)} bytes)")
                    except Exception as e:
                        print(f"   ⚠️ Referans {i+1} indirilemedi: {e}")

            # Prompt oluştur
            # Gemini'ye ilk görselin "değiştirilecek ana sahne" olduğunu, 
            # diğerlerinin ise "kimlik/nesne referansı" olduğunu açıkla.
            inpainting_prompt = (
                f"You are an expert image editor. The VERY FIRST image provided is the ORIGINAL image (the canvas) that needs to be modified. "
                f"The SUBSEQUENT images are identity or subject references. "
                f"TASK: Modify the ORIGINAL image according to this instruction: {prompt}. "
                f"CRITICAL: You MUST preserve the facial features and identity from the reference image(s) perfectly when adding or modifying people. "
                f"Maintain the background, lighting, and style of the ORIGINAL image for everything outside the modification area. "
                "Output the modified image."
            )
            
            contents.append(inpainting_prompt)
            
            # API Çağrısı
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                ),
            )
            
            generated_image = None
            generated_mime = None
            
            if response.candidates and response.candidates[0].content:
                for part in response.candidates[0].content.parts:
                    if part.inline_data is not None:
                        generated_image = part.inline_data.data
                        generated_mime = part.inline_data.mime_type
                        break
            
            if not generated_image:
                return {"success": False, "error": "Gemini düzenlenmiş görseli üretemedi."}
            
            # fal.ai'ye yükle
            image_url = await self._upload_to_fal(generated_image, generated_mime or "image/png")
            
            return {
                "success": True,
                "image_url": image_url,
                "method_used": "gemini-inpainting-identity",
                "message": "Görsel Gemini ile kimlik korunarak düzenlendi."
            }
            
        except Exception as e:
            print(f"   ❌ Gemini düzenleme hatası: {e}")
            return {"success": False, "error": str(e)}

    async def _upload_to_fal(self, image_data: bytes, mime_type: str) -> Optional[str]:
        """Gemini'den gelen görseli fal.ai storage'a yükle."""
        try:
            b64 = base64.b64encode(image_data).decode("utf-8")
            
            # fal_plugin üzerinden yükle
            from app.services.plugins.fal_plugin_v2 import FalPluginV2
            fal = FalPluginV2()
            result = await fal.upload_base64_image(b64)
            if result.get("success"):
                return result.get("url")
            return None
        except Exception as e:
            print(f"   ⚠️ fal.ai upload hatası: {e}")
            return None


# Singleton
gemini_image_service = GeminiImageService()
