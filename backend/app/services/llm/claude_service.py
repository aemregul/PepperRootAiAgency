"""
Claude LLM Servisi - Anthropic API ile iletişim.

Vision desteği ile görsel analiz yeteneği.
"""
import base64
import httpx
from anthropic import AsyncAnthropic
from typing import Optional

from app.core.config import settings


class ClaudeService:
    """Claude ile sohbet ve görsel analiz servisi."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def chat(self, message: str, system_prompt: str = None) -> str:
        """
        Basit sohbet - mesaj gönder, yanıt al.
        
        Args:
            message: Kullanıcı mesajı
            system_prompt: Sistem talimatı (opsiyonel)
        
        Returns:
            Claude'un yanıtı
        """
        messages = [{"role": "user", "content": message}]
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt or "Sen yardımcı bir asistansın.",
            messages=messages
        )
        
        return response.content[0].text
    
    async def analyze_image(
        self, 
        image_url: str, 
        analysis_prompt: str = None,
        check_quality: bool = False
    ) -> dict:
        """
        Görsel analiz - Claude Vision API.
        
        Agent bu metodu şu durumlarda kullanır:
        - Üretilen görselin kalite kontrolü
        - Yüz tutarlılığı kontrolü
        - İçerik analizi
        
        Args:
            image_url: Analiz edilecek görselin URL'si
            analysis_prompt: Özel analiz sorusu (opsiyonel)
            check_quality: Kalite kontrolü modu
        
        Returns:
            dict: {
                "success": bool,
                "analysis": str,
                "quality_score": int (0-10),
                "issues": list[str],
                "face_detected": bool
            }
        """
        try:
            # Görseli indir ve base64'e çevir
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url, timeout=30.0)
                response.raise_for_status()
                image_data = base64.standard_b64encode(response.content).decode("utf-8")
                
                # Media type belirle
                content_type = response.headers.get("content-type", "image/png")
                media_type = content_type.split(";")[0]
            
            # Analiz prompt'u
            if check_quality:
                prompt = """Bu görseli analiz et ve şu kriterlere göre değerlendir:

1. Kalite Skoru (0-10): Genel görsel kalitesi
2. Yüz Kontrolü: Görselde yüz var mı? Varsa doğal görünüyor mu, bozukluk var mı?
3. Kompozisyon: Görsel düzeni ve denge
4. Sorunlar: Varsa sorunları listele (bulanıklık, bozukluk, yapay görünüm, vs.)

JSON formatında yanıt ver:
{
  "quality_score": 8,
  "face_detected": true,
  "face_quality": "iyi",
  "issues": ["hafif bulanıklık"],
  "recommendation": "kabul edilebilir"
}"""
            else:
                prompt = analysis_prompt or "Bu görseli detaylı analiz et. Ne görüyorsun? Kalitesi nasıl?"
            
            # Claude Vision API çağrısı
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            analysis_text = response.content[0].text
            
            # JSON parse etmeye çalış (kalite kontrolü modunda)
            if check_quality:
                try:
                    import json
                    # JSON bloğunu bul
                    if "```json" in analysis_text:
                        json_str = analysis_text.split("```json")[1].split("```")[0]
                    elif "{" in analysis_text and "}" in analysis_text:
                        start = analysis_text.index("{")
                        end = analysis_text.rindex("}") + 1
                        json_str = analysis_text[start:end]
                    else:
                        json_str = analysis_text
                    
                    result = json.loads(json_str)
                    return {
                        "success": True,
                        "analysis": analysis_text,
                        "quality_score": result.get("quality_score", 7),
                        "face_detected": result.get("face_detected", False),
                        "face_quality": result.get("face_quality", "bilinmiyor"),
                        "issues": result.get("issues", []),
                        "recommendation": result.get("recommendation", "kabul edilebilir")
                    }
                except:
                    pass
            
            return {
                "success": True,
                "analysis": analysis_text,
                "quality_score": 7,  # Default
                "issues": [],
                "face_detected": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": None
            }
    
    async def compare_images(self, image_url_1: str, image_url_2: str, comparison_prompt: str = None) -> dict:
        """
        İki görseli karşılaştır.
        
        Agent bu metodu şu durumlarda kullanır:
        - Kullanıcı "önceki daha iyiydi" dediğinde
        - Farklı versiyonları kıyaslamak için
        """
        try:
            # Her iki görseli de indir
            async with httpx.AsyncClient() as client:
                resp1 = await client.get(image_url_1, timeout=30.0)
                resp2 = await client.get(image_url_2, timeout=30.0)
                
                img1_data = base64.standard_b64encode(resp1.content).decode("utf-8")
                img2_data = base64.standard_b64encode(resp2.content).decode("utf-8")
                
                media_type_1 = resp1.headers.get("content-type", "image/png").split(";")[0]
                media_type_2 = resp2.headers.get("content-type", "image/png").split(";")[0]
            
            prompt = comparison_prompt or """Bu iki görseli karşılaştır:
1. Hangisi daha kaliteli?
2. Yüz tutarlılığı hangisinde daha iyi?
3. Hangi görseli tercih edersin ve neden?

JSON formatında yanıt ver:
{
  "preferred": 1 veya 2,
  "reason": "tercih nedeni",
  "image1_score": 0-10,
  "image2_score": 0-10
}"""
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": media_type_1, "data": img1_data}},
                            {"type": "image", "source": {"type": "base64", "media_type": media_type_2, "data": img2_data}},
                            {"type": "text", "text": prompt}
                        ],
                    }
                ],
            )
            
            return {
                "success": True,
                "comparison": response.content[0].text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
claude_service = ClaudeService()