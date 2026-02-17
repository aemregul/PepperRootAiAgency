"""
Auto Quality Control Service — GPT-4o Vision ile otomatik kalite kontrol.

Generate sonrası görsel/video kalitesini değerlendirir,
düşük kalitede otomatik retry yapar.
"""
import json
from typing import Optional, Dict, Any, Tuple
from openai import AsyncOpenAI
from app.core.config import settings


class QualityControlService:
    """Üretilen görselleri GPT-4o Vision ile değerlendir."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.min_quality_score = 6  # 1-10, altı retry
        self.max_retries = 2
    
    async def evaluate_image(
        self,
        image_url: str,
        original_prompt: str,
        reference_image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Üretilen görseli değerlendir.
        
        Returns:
            {
                "score": 8,           # 1-10
                "prompt_match": 9,    # Prompt'a uygunluk
                "face_match": 7,      # Yüz benzerliği (varsa)
                "quality": 8,         # Teknik kalite
                "feedback": "..."     # Kısa değerlendirme
                "pass": True          # Kabul/ret
            }
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """Sen bir görsel kalite kontrol uzmanısın. 
Üretilen görseli aşağıdaki kriterlere göre 1-10 arası puanla:

1. **prompt_match**: Orijinal prompt'a ne kadar uyuyor? (1-10)
2. **quality**: Teknik kalite (netlik, ışık, kompozisyon) (1-10)  
3. **face_match**: Yüz referansı varsa benzerlik (1-10, yoksa null)
4. **score**: Genel puan (1-10)
5. **feedback**: 1 cümle değerlendirme (Türkçe)
6. **pass**: score >= 6 ise true

SADECE JSON döndür, başka bir şey yazma."""
                },
                {
                    "role": "user",
                    "content": []
                }
            ]
            
            # Üretilen görsel
            messages[1]["content"].append({
                "type": "text",
                "text": f"Orijinal prompt: \"{original_prompt}\"\n\nBu görseli değerlendir:"
            })
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })
            
            # Referans yüz varsa ekle
            if reference_image_url:
                messages[1]["content"].append({
                    "type": "text",
                    "text": "Referans yüz (benzerliğini kontrol et):"
                })
                messages[1]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": reference_image_url}
                })
            
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # JSON parse
            if "```" in result_text:
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            result = json.loads(result_text)
            result["pass"] = result.get("score", 0) >= self.min_quality_score
            
            print(f"🔍 QC Sonucu: skor={result.get('score')}/10, "
                  f"prompt={result.get('prompt_match')}/10, "
                  f"geçti={'✅' if result['pass'] else '❌'}")
            
            return result
            
        except Exception as e:
            print(f"⚠️ QC değerlendirme hatası: {e}")
            # Hata durumunda geç say (üretimi engelleme)
            return {
                "score": 7,
                "prompt_match": 7,
                "quality": 7,
                "face_match": None,
                "feedback": "Kalite kontrolü yapılamadı, varsayılan geçiş.",
                "pass": True
            }
    
    async def evaluate_with_retry(
        self,
        generate_fn,
        generate_params: dict,
        original_prompt: str,
        reference_image_url: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Üret → değerlendir → düşük skor ise tekrar dene.
        
        Args:
            generate_fn: Async üretim fonksiyonu
            generate_params: Üretim parametreleri
            original_prompt: Orijinal prompt
            reference_image_url: Referans yüz URL
            
        Returns:
            (generation_result, qc_result)
        """
        best_result = None
        best_qc = None
        best_score = 0
        
        for attempt in range(self.max_retries + 1):
            # Üret
            result = await generate_fn(**generate_params)
            
            if not result.get("success"):
                return result, {"score": 0, "pass": False, "feedback": "Üretim başarısız"}
            
            image_url = result.get("image_url") or result.get("url")
            if not image_url:
                return result, {"score": 0, "pass": False, "feedback": "URL bulunamadı"}
            
            # Değerlendir
            qc = await self.evaluate_image(image_url, original_prompt, reference_image_url)
            
            if qc.get("score", 0) > best_score:
                best_score = qc["score"]
                best_result = result
                best_qc = qc
            
            if qc["pass"]:
                if attempt > 0:
                    print(f"🔄 {attempt + 1}. denemede kalite kontrolünü geçti!")
                best_qc["attempts"] = attempt + 1
                return best_result, best_qc
            
            if attempt < self.max_retries:
                print(f"⚠️ QC başarısız (skor: {qc.get('score')}/10), tekrar deneniyor... ({attempt + 2}/{self.max_retries + 1})")
        
        # Max retry'a ulaşıldı, en iyisini döndür
        best_qc["attempts"] = self.max_retries + 1
        best_qc["note"] = "Maksimum deneme sonrası en iyi sonuç seçildi"
        return best_result, best_qc


# Singleton
quality_control = QualityControlService()
