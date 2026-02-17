"""
Multi-Agent Framework — Uzmanlaşmış alt-agent'lar.

3 uzman agent:
1. Creative Agent: Prompt yazma, sahne planlama
2. QC Agent: Kalite kontrol, tutarlılık
3. Orchestrator: Koordinasyon (mevcut AgentOrchestrator)
"""
from typing import Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings


class SubAgent:
    """Temel sub-agent sınıfı."""
    
    def __init__(self, name: str, system_prompt: str, model: str = "gpt-4o"):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def think(self, task: str, context: str = "") -> str:
        """Agent'a bir görev ver, düşünsün ve yanıt versin."""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Görev: {task}\n\nContext: {context}" if context else f"Görev: {task}"}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Agent hatası: {e}"


class CreativeAgent(SubAgent):
    """Yaratıcı Agent — Prompt yazma ve sahne planlama."""
    
    def __init__(self):
        super().__init__(
            name="Creative Director",
            system_prompt="""Sen bir yaratıcı yönetmensin. Görevin:

1. **Prompt Engineering**: Kullanıcının isteklerini detaylı, etkili görsel/video prompt'larına dönüştür.
2. **Sahne Planlama**: Uzun videolar için sahne sahne senaryo yaz.
3. **Stil Önerisi**: Renk paleti, ışık, atmosfer öner.
4. **Copy Writing**: Kampanya için metin/slogan öner.

KURALLAR:
- Prompt'lar İngilizce olmalı
- Teknik terimler kullan (cinematic, bokeh, 8K, etc.)
- Her prompt 50-150 kelime arası olmalı
- Sahneler birbirine görsel olarak tutarlı olmalı

Yanıtını her zaman JSON formatında ver.""",
            model="gpt-4o-mini"  # Maliyet optimizasyonu
        )
    
    async def enhance_prompt(self, user_prompt: str, style: str = "") -> str:
        """Kullanıcı prompt'unu zenginleştir."""
        task = f"Bu prompt'u zenginleştir ve profesyonel hale getir: '{user_prompt}'"
        if style:
            task += f"\nStil: {style}"
        return await self.think(task)
    
    async def plan_scenes(self, concept: str, duration: int = 30, scene_count: int = 3) -> str:
        """Uzun video için sahne planla."""
        task = f"""'{concept}' konsepti için {duration} saniyelik video planla.
{scene_count} sahne oluştur. Her sahne için:
- Sahne açıklaması (İngilizce, detaylı)
- Süre (saniye)
- Kamera açısı
- Geçiş efekti

JSON formatında döndür: {{"scenes": [{{"description": "...", "duration": N, "camera": "...", "transition": "..."}}]}}"""
        return await self.think(task)


class QCAgent(SubAgent):
    """Kalite Kontrol Agent'ı."""
    
    def __init__(self):
        super().__init__(
            name="Quality Inspector",
            system_prompt="""Sen bir kalite kontrol uzmanısın. Görevin:

1. Üretilen görsellerin/videoların kalitesini değerlendir
2. Prompt'a uygunluğu kontrol et
3. Yüz tutarlılığını doğrula
4. İyileştirme önerileri sun

Yanıtını JSON formatında ver:
{"score": 1-10, "issues": ["..."], "suggestions": ["..."], "pass": true/false}""",
            model="gpt-4o-mini"
        )
    
    async def check_consistency(self, prompts: list) -> str:
        """Birden fazla prompt'un stilistik tutarlılığını kontrol et."""
        task = f"Bu prompt'ların stilistik tutarlılığını kontrol et:\n" + "\n".join([f"- {p}" for p in prompts])
        return await self.think(task)


class MultiAgentOrchestrator:
    """Alt-agent'ları koordine eden üst orchestrator."""
    
    def __init__(self):
        self.creative = CreativeAgent()
        self.qc = QCAgent()
    
    async def enhance_and_validate(self, prompt: str, style: str = "") -> Dict[str, Any]:
        """
        Creative agent ile prompt zenginleştir,
        QC agent ile doğrula.
        """
        # 1. Creative agent prompt'u zenginleştirir
        enhanced = await self.creative.enhance_prompt(prompt, style)
        
        # 2. QC agent doğrular
        validation = await self.qc.check_consistency([enhanced])
        
        return {
            "original_prompt": prompt,
            "enhanced_prompt": enhanced,
            "validation": validation
        }
    
    async def plan_video(self, concept: str, duration: int = 30) -> str:
        """Video sahne planlaması."""
        return await self.creative.plan_scenes(concept, duration)


# Singleton
multi_agent = MultiAgentOrchestrator()
