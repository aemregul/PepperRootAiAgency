"""
Episodic Memory Service - Agent'ın önemli olayları hatırlaması.

Örnek olaylar:
- "Kullanıcı @emre karakterini beğendi"
- "Nike markası için 5 görsel üretildi"
- "16:9 aspect ratio tercih ediliyor"

Bu bilgiler uzun vadeli hafızada saklanır ve context olarak kullanılır.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Base
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column


# Not: Bu model henüz migration'a eklenmedi
# Şimdilik Redis ile çalışacak, daha sonra DB'ye migrate edilecek

class EpisodicMemoryEntry:
    """Episodic memory entry (in-memory representation)."""
    
    def __init__(
        self,
        user_id: str,
        event_type: str,
        content: str,
        metadata: dict = None,
        importance: int = 5  # 1-10, 10 = çok önemli
    ):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.event_type = event_type
        self.content = content
        self.metadata = metadata or {}
        self.importance = importance
        self.created_at = datetime.utcnow()
        self.access_count = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "access_count": self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EpisodicMemoryEntry":
        entry = cls(
            user_id=data["user_id"],
            event_type=data["event_type"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 5)
        )
        entry.id = data["id"]
        entry.created_at = datetime.fromisoformat(data["created_at"])
        entry.access_count = data.get("access_count", 0)
        return entry


class EpisodicMemoryService:
    """
    Episodic Memory Service - Olayları hatırla.
    
    Event Types:
    - preference: Kullanıcı tercihi öğrenildi
    - creation: Entity/asset oluşturuldu
    - feedback: Kullanıcı geri bildirimi
    - error: Hata yaşandı
    - success: Başarılı işlem
    - interaction: Kullanıcı etkileşimi
    """
    
    # Event önem seviyeleri
    IMPORTANCE_LEVELS = {
        "preference": 8,      # Tercihler çok önemli
        "feedback": 9,        # Geri bildirim çok önemli
        "creation": 6,        # Oluşturma orta önemde
        "success": 4,         # Başarı düşük
        "error": 7,           # Hatalar önemli (tekrarlanmasın)
        "interaction": 3      # Etkileşimler düşük
    }
    
    def __init__(self):
        self.memories: dict[str, List[EpisodicMemoryEntry]] = {}  # user_id -> memories
        self.max_memories_per_user = 100  # Max hafıza
    
    async def remember(
        self,
        user_id: str,
        event_type: str,
        content: str,
        metadata: dict = None
    ) -> EpisodicMemoryEntry:
        """
        Yeni bir olayı hatırla.
        
        Args:
            user_id: Kullanıcı ID
            event_type: Olay tipi (preference, creation, feedback, vb.)
            content: Olay açıklaması
            metadata: Ek bilgiler
        """
        importance = self.IMPORTANCE_LEVELS.get(event_type, 5)
        
        entry = EpisodicMemoryEntry(
            user_id=user_id,
            event_type=event_type,
            content=content,
            metadata=metadata,
            importance=importance
        )
        
        if user_id not in self.memories:
            self.memories[user_id] = []
        
        self.memories[user_id].append(entry)
        
        # Max limit aşıldıysa en düşük önemli olanları sil
        if len(self.memories[user_id]) > self.max_memories_per_user:
            self._prune_memories(user_id)
        
        print(f"🧠 Remembered: [{event_type}] {content[:50]}...")
        return entry
    
    def _prune_memories(self, user_id: str):
        """En az önemli ve en eski hafızaları sil."""
        memories = self.memories[user_id]
        
        # Önce önem, sonra tarih sırasına göre sırala
        sorted_memories = sorted(
            memories,
            key=lambda m: (m.importance, m.created_at.timestamp()),
            reverse=True
        )
        
        # En önemli max_memories_per_user kadarını sakla
        self.memories[user_id] = sorted_memories[:self.max_memories_per_user]
    
    async def recall(
        self,
        user_id: str,
        event_type: str = None,
        query: str = None,
        limit: int = 10
    ) -> List[EpisodicMemoryEntry]:
        """
        Hafızadan olayları hatırla.
        
        Args:
            user_id: Kullanıcı ID
            event_type: Filtrelenecek olay tipi (opsiyonel)
            query: Arama sorgusu (opsiyonel, basit string matching)
            limit: Max sonuç sayısı
        """
        if user_id not in self.memories:
            return []
        
        memories = self.memories[user_id]
        
        # Filtrele
        if event_type:
            memories = [m for m in memories if m.event_type == event_type]
        
        if query:
            query_lower = query.lower()
            memories = [m for m in memories if query_lower in m.content.lower()]
        
        # Önem ve tarihe göre sırala
        sorted_memories = sorted(
            memories,
            key=lambda m: (m.importance, m.created_at.timestamp()),
            reverse=True
        )
        
        # Erişim sayısını artır
        for m in sorted_memories[:limit]:
            m.access_count += 1
        
        return sorted_memories[:limit]
    
    async def get_context_for_prompt(
        self,
        user_id: str,
        max_entries: int = 5
    ) -> str:
        """
        System prompt'a eklenecek hafıza özeti oluştur.
        """
        memories = await self.recall(user_id, limit=max_entries)
        
        if not memories:
            return ""
        
        prompt_parts = ["\n## 🧠 HAFIZA (Önceki Olaylar)"]
        
        for m in memories:
            icon = {
                "preference": "⭐",
                "feedback": "💬",
                "creation": "✨",
                "success": "✅",
                "error": "⚠️",
                "interaction": "💡"
            }.get(m.event_type, "📝")
            
            prompt_parts.append(f"- {icon} {m.content}")
        
        return "\n".join(prompt_parts)
    
    async def forget(self, user_id: str, memory_id: str) -> bool:
        """Belirli bir hafızayı unut."""
        if user_id not in self.memories:
            return False
        
        self.memories[user_id] = [
            m for m in self.memories[user_id] if m.id != memory_id
        ]
        return True
    
    async def clear_user_memories(self, user_id: str) -> int:
        """Kullanıcının tüm hafızasını temizle."""
        if user_id not in self.memories:
            return 0
        count = len(self.memories[user_id])
        self.memories[user_id] = []
        return count
    
    # Convenience methods for common events
    async def remember_preference(self, user_id: str, preference: str, value: any):
        """Tercih hatırla."""
        await self.remember(
            user_id=user_id,
            event_type="preference",
            content=f"Kullanıcı {preference}: {value} tercih ediyor",
            metadata={"preference": preference, "value": value}
        )
    
    async def remember_creation(self, user_id: str, entity_type: str, name: str):
        """Oluşturma hatırla."""
        await self.remember(
            user_id=user_id,
            event_type="creation",
            content=f"{entity_type.capitalize()} oluşturuldu: @{name}",
            metadata={"entity_type": entity_type, "name": name}
        )
    
    async def remember_feedback(self, user_id: str, feedback: str, positive: bool):
        """Geri bildirim hatırla."""
        await self.remember(
            user_id=user_id,
            event_type="feedback",
            content=f"{'👍' if positive else '👎'} {feedback}",
            metadata={"positive": positive}
        )


# Singleton instance
episodic_memory = EpisodicMemoryService()
