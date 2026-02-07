"""
User Preferences Service - Agent için kullanıcı tercihlerini yönetir.
"""
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import UserPreferences


class PreferencesService:
    """Kullanıcı tercihlerini yönetir."""
    
    async def get_preferences(self, db: AsyncSession, user_id: uuid.UUID) -> dict:
        """
        Kullanıcı tercihlerini getir.
        Yoksa varsayılan değerlerle oluştur.
        """
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalars().first()
        
        if not prefs:
            # Varsayılan tercihler oluştur
            prefs = UserPreferences(user_id=user_id)
            db.add(prefs)
            await db.commit()
            await db.refresh(prefs)
        
        return {
            "aspect_ratio": prefs.default_aspect_ratio,
            "style": prefs.default_style,
            "image_model": prefs.default_image_model,
            "video_model": prefs.default_video_model,
            "video_duration": prefs.default_video_duration,
            "auto_face_swap": prefs.auto_face_swap,
            "auto_upscale": prefs.auto_upscale,
            "auto_translate": prefs.auto_translate_prompts,
            "language": prefs.response_language,
            "favorite_entities": prefs.favorite_entities or [],
            "learned": prefs.learned_preferences or {}
        }
    
    async def update_preferences(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        updates: dict
    ) -> dict:
        """Kullanıcı tercihlerini güncelle."""
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalars().first()
        
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.add(prefs)
        
        # Güncellenebilir alanlar
        field_mapping = {
            "aspect_ratio": "default_aspect_ratio",
            "style": "default_style",
            "image_model": "default_image_model",
            "video_model": "default_video_model",
            "video_duration": "default_video_duration",
            "auto_face_swap": "auto_face_swap",
            "auto_upscale": "auto_upscale",
            "auto_translate": "auto_translate_prompts",
            "language": "response_language",
            "favorite_entities": "favorite_entities"
        }
        
        for key, value in updates.items():
            if key in field_mapping:
                setattr(prefs, field_mapping[key], value)
        
        await db.commit()
        await db.refresh(prefs)
        
        return await self.get_preferences(db, user_id)
    
    async def learn_preference(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        key: str, 
        value: any
    ) -> None:
        """
        Agent tarafından öğrenilen tercihleri kaydet.
        Örn: Kullanıcı hep 9:16 aspect ratio kullanıyorsa bunu öğren.
        """
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        prefs = result.scalars().first()
        
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.add(prefs)
        
        learned = prefs.learned_preferences or {}
        learned[key] = value
        prefs.learned_preferences = learned
        
        await db.commit()
    
    async def get_preferences_for_prompt(self, db: AsyncSession, user_id: uuid.UUID) -> str:
        """
        System prompt'a eklenecek tercih özeti oluştur.
        Agent'ın tercihleri bilmesi için.
        """
        prefs = await self.get_preferences(db, user_id)
        
        prompt_parts = ["\n## 📋 KULLANICI TERCİHLERİ"]
        
        prompt_parts.append(f"- Varsayılan aspect ratio: {prefs['aspect_ratio']}")
        prompt_parts.append(f"- Varsayılan stil: {prefs['style']}")
        
        if not prefs['auto_face_swap']:
            prompt_parts.append("- ⚠️ Otomatik yüz değiştirme KAPALI")
        
        if prefs['auto_upscale']:
            prompt_parts.append("- ✅ Üretilen görselleri otomatik yükselt")
        
        if prefs['favorite_entities']:
            favs = ", ".join(prefs['favorite_entities'][:5])
            prompt_parts.append(f"- Favori karakterler/mekanlar: {favs}")
        
        learned = prefs.get('learned', {})
        if learned.get('preferred_colors'):
            prompt_parts.append(f"- Tercih edilen renkler: {', '.join(learned['preferred_colors'][:3])}")
        
        return "\n".join(prompt_parts)


# Singleton instance
preferences_service = PreferencesService()
