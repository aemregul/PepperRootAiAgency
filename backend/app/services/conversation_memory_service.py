"""
Conversation Memory Service — Kullanıcı Seviyesinde Hafıza.

Tek asistan, farklı projeler modeli:
- Her sohbet sonunda özet çıkar → user hafızasına kaydet
- Yeni sohbette geçmiş özetleri context'e ekle
- Başarılı prompt'ları hatırla (Self-Learning)
- Kullanıcı tercihlerini öğren
"""
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from app.core.config import settings


class ConversationMemoryService:
    """Kullanıcı seviyesinde hafıza — projeler arası hatırlama."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    # ===============================
    # SOHBET ÖZETLEMESİ
    # ===============================
    
    async def summarize_conversation(
        self,
        messages: List[Dict[str, str]],
        session_title: str = ""
    ) -> str:
        """
        Sohbet geçmişini özetle.
        Her sohbet kapandığında çağrılır.
        """
        if not messages or len(messages) < 2:
            return ""
        
        # Son 30 mesajı al
        recent = messages[-30:]
        conversation_text = "\n".join([
            f"{'Kullanıcı' if m['role'] == 'user' else 'Asistan'}: {m['content'][:200]}"
            for m in recent
        ])
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Hızlı ve ucuz
                messages=[
                    {
                        "role": "system",
                        "content": """Bir sohbet özetleme sistemisİn. Aşağıdaki sohbeti ÇOK KISA özetle (max 3 cümle):
- Ne yapıldı?
- Hangi entity'ler/markalar kullanıldı?
- Kullanıcı neyi beğendi/beğenmedi?
- Hangi stil/format tercih edildi?

Türkçe yaz. Sadece özet, başka bir şey yazma."""
                    },
                    {
                        "role": "user",
                        "content": f"Proje: {session_title}\n\nSohbet:\n{conversation_text}"
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            print(f"📝 Sohbet özeti oluşturuldu: {summary[:80]}...")
            return summary
            
        except Exception as e:
            print(f"⚠️ Özet oluşturma hatası: {e}")
            return ""
    
    async def save_conversation_summary(
        self,
        db,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        summary: str
    ):
        """Özeti Redis + DB'ye kaydet."""
        from app.core.cache import cache
        
        # Redis'e kaydet (hızlı erişim)
        memory_key = f"user_memory:{user_id}"
        existing = await cache.get_json(memory_key) or {
            "summaries": [],
            "preferences": {},
            "successful_prompts": [],
            "style_preferences": {}
        }
        
        existing["summaries"].append({
            "session_id": str(session_id),
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Son 20 özeti tut
        if len(existing["summaries"]) > 20:
            existing["summaries"] = existing["summaries"][-20:]
        
        await cache.set_json(memory_key, existing, ttl=604800)  # 7 gün
        print(f"💾 Hafıza kaydedildi: user={str(user_id)[:8]}...")
    
    # ===============================
    # KULLANICI HAFIZASı YÜKLEME
    # ===============================
    
    async def get_user_memory(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Kullanıcının tüm hafızasını getir."""
        from app.core.cache import cache
        
        memory_key = f"user_memory:{user_id}"
        memory = await cache.get_json(memory_key)
        
        if not memory:
            return {
                "summaries": [],
                "preferences": {},
                "successful_prompts": [],
                "style_preferences": {}
            }
        
        return memory
    
    async def build_memory_context(self, user_id: uuid.UUID) -> str:
        """
        Geçmiş hafızayı system prompt'a eklenecek context'e dönüştür.
        Agent bu bilgiyle kullanıcıyı "tanır".
        """
        memory = await self.get_user_memory(user_id)
        
        parts = []
        
        # Geçmiş sohbet özetleri
        if memory.get("summaries"):
            recent_summaries = memory["summaries"][-5:]  # Son 5 proje
            summaries_text = "\n".join([
                f"- {s['summary']}" for s in recent_summaries
            ])
            parts.append(f"📋 SON PROJELER:\n{summaries_text}")
        
        # Tercihler
        if memory.get("preferences"):
            prefs = memory["preferences"]
            prefs_text = ", ".join([f"{k}: {v}" for k, v in prefs.items()])
            parts.append(f"⚙️ TERCİHLER: {prefs_text}")
        
        # Başarılı prompt'lar
        if memory.get("successful_prompts"):
            recent_prompts = memory["successful_prompts"][-3:]
            prompts_text = "\n".join([
                f"- \"{p['prompt'][:100]}\" (skor: {p.get('score', '?')})"
                for p in recent_prompts
            ])
            parts.append(f"⭐ BAŞARILI PROMPTLAR:\n{prompts_text}")
        
        # Stil tercihleri
        if memory.get("style_preferences"):
            style = memory["style_preferences"]
            style_text = ", ".join([f"{k}: {v}" for k, v in style.items()])
            parts.append(f"🎨 STİL: {style_text}")
        
        if not parts:
            return ""
        
        return "\n\n".join(parts)
    
    # ===============================
    # SELF-LEARNING: BAŞARILI PROMPT'LAR
    # ===============================
    
    async def save_successful_prompt(
        self,
        user_id: uuid.UUID,
        prompt: str,
        result_url: str,
        score: int,
        asset_type: str = "image"
    ):
        """Kullanıcı beğendiğinde prompt'u hafızaya kaydet."""
        from app.core.cache import cache
        
        memory_key = f"user_memory:{user_id}"
        memory = await cache.get_json(memory_key) or {
            "summaries": [],
            "preferences": {},
            "successful_prompts": [],
            "style_preferences": {}
        }
        
        memory["successful_prompts"].append({
            "prompt": prompt,
            "result_url": result_url,
            "score": score,
            "asset_type": asset_type,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Son 50 başarılı prompt
        if len(memory["successful_prompts"]) > 50:
            memory["successful_prompts"] = memory["successful_prompts"][-50:]
        
        await cache.set_json(memory_key, memory, ttl=604800)
        print(f"⭐ Başarılı prompt kaydedildi: '{prompt[:50]}...' (skor: {score})")
    
    async def find_similar_prompts(
        self,
        user_id: uuid.UUID,
        query: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Geçmiş başarılı prompt'lardan benzerleri bul."""
        memory = await self.get_user_memory(user_id)
        prompts = memory.get("successful_prompts", [])
        
        if not prompts:
            return []
        
        # Basit kelime eşleştirmesi (Pinecone yoksa fallback)
        query_words = set(query.lower().split())
        scored = []
        
        for p in prompts:
            prompt_words = set(p["prompt"].lower().split())
            overlap = len(query_words & prompt_words)
            if overlap > 0:
                scored.append((overlap, p))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]
    
    # ===============================
    # TERCİH ÖĞRENME
    # ===============================
    
    async def update_preferences(
        self,
        user_id: uuid.UUID,
        key: str,
        value: str
    ):
        """Kullanıcı tercihini güncelle."""
        from app.core.cache import cache
        
        memory_key = f"user_memory:{user_id}"
        memory = await cache.get_json(memory_key) or {
            "summaries": [],
            "preferences": {},
            "successful_prompts": [],
            "style_preferences": {}
        }
        
        memory["preferences"][key] = value
        await cache.set_json(memory_key, memory, ttl=604800)
    
    async def update_style_preference(
        self,
        user_id: uuid.UUID,
        style_key: str,
        style_value: str
    ):
        """Stil tercihini kaydet."""
        from app.core.cache import cache
        
        memory_key = f"user_memory:{user_id}"
        memory = await cache.get_json(memory_key) or {
            "summaries": [],
            "preferences": {},
            "successful_prompts": [],
            "style_preferences": {}
        }
        
        memory["style_preferences"][style_key] = style_value
        await cache.set_json(memory_key, memory, ttl=604800)


# Singleton
conversation_memory = ConversationMemoryService()
