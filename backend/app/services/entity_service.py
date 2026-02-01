"""
Entity Service - Karakter, mekan, nesne yönetimi.
"""
import re
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Entity


def slugify(text: str) -> str:
    """Türkçe karakterleri de destekleyen slug oluşturucu."""
    # Türkçe karakterleri dönüştür
    replacements = {
        'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
        'İ': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c'
    }
    for tr_char, en_char in replacements.items():
        text = text.replace(tr_char, en_char)
    
    # Küçük harfe çevir ve alfanumerik olmayanları _ ile değiştir
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    text = text.strip('_')
    return text


class EntityService:
    """Entity CRUD operasyonları."""
    
    async def create_entity(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        entity_type: str,
        name: str,
        description: Optional[str] = None,
        attributes: Optional[dict] = None,
        reference_image_url: Optional[str] = None,
        session_id: Optional[uuid.UUID] = None
    ) -> Entity:
        """
        Yeni entity oluştur.
        
        Args:
            db: Database session
            user_id: Kullanıcı ID (entity sahibi)
            entity_type: character, location, costume, object
            name: Entity adı
            description: Detaylı açıklama
            attributes: Ek özellikler (JSON)
            reference_image_url: Yüz/vücut referans görseli URL
            session_id: Opsiyonel - entity'nin oluşturulduğu proje
        
        Returns:
            Oluşturulan Entity
        """
        # Tag otomatik oluştur: sadece isim (@emre, @mutfak)
        name_slug = slugify(name)
        tag = f"@{name_slug}"
        
        entity = Entity(
            user_id=user_id,
            session_id=session_id,  # Opsiyonel
            entity_type=entity_type,
            name=name,
            tag=tag,
            description=description,
            attributes=attributes or {},
            reference_image_url=reference_image_url
        )
        
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
        
        return entity
    
    async def get_by_tag(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tag: str
    ) -> Optional[Entity]:
        """
        Tag ile entity bul (kullanıcıya ait).
        
        Args:
            db: Database session
            user_id: Kullanıcı ID
            tag: Entity tag'i (örn: @emre)
        
        Returns:
            Entity veya None
        """
        # @ işareti yoksa ekle
        if not tag.startswith('@'):
            tag = f"@{tag}"
        
        result = await db.execute(
            select(Entity).where(
                Entity.user_id == user_id,
                Entity.tag == tag
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID
    ) -> Optional[Entity]:
        """ID ile entity bul."""
        result = await db.execute(
            select(Entity).where(Entity.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def list_entities(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        entity_type: Optional[str] = None
    ) -> list[Entity]:
        """
        Kullanıcının entity'lerini listele.
        
        Args:
            db: Database session
            user_id: Kullanıcı ID
            entity_type: Opsiyonel filtre (character, location, vb.)
        
        Returns:
            Entity listesi
        """
        query = select(Entity).where(Entity.user_id == user_id)
        
        if entity_type:
            query = query.where(Entity.entity_type == entity_type)
        
        query = query.order_by(Entity.created_at.desc())
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def update_entity(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID,
        **updates
    ) -> Optional[Entity]:
        """
        Entity güncelle.
        
        Args:
            db: Database session
            entity_id: Entity ID
            **updates: Güncellenecek alanlar
        
        Returns:
            Güncellenmiş Entity veya None
        """
        entity = await self.get_by_id(db, entity_id)
        if not entity:
            return None
        
        for key, value in updates.items():
            if hasattr(entity, key) and key not in ('id', 'session_id', 'created_at'):
                setattr(entity, key, value)
        
        await db.commit()
        await db.refresh(entity)
        
        return entity
    
    async def delete_entity(
        self,
        db: AsyncSession,
        entity_id: uuid.UUID
    ) -> bool:
        """
        Entity sil.
        
        Returns:
            Silme başarılı mı
        """
        entity = await self.get_by_id(db, entity_id)
        if not entity:
            return False
        
        await db.delete(entity)
        await db.commit()
        
        return True
    
    def extract_tags(self, text: str) -> list[str]:
        """
        Metinden @tag'leri çıkar.
        
        Args:
            text: Kullanıcı mesajı
        
        Returns:
            Tag listesi (örn: ['@character_emre', '@location_orman'])
        """
        pattern = r'@[a-zA-Z0-9_]+'
        return re.findall(pattern, text)
    
    async def resolve_tags(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        text: str
    ) -> list[Entity]:
        """
        Metindeki @tag'leri entity'lere çözümle.
        
        Args:
            db: Database session
            user_id: Kullanıcı ID
            text: Kullanıcı mesajı
        
        Returns:
            Bulunan Entity listesi
        """
        tags = self.extract_tags(text)
        entities = []
        
        for tag in tags:
            entity = await self.get_by_tag(db, user_id, tag)
            if entity:
                entities.append(entity)
        
        return entities


# Singleton instance
entity_service = EntityService()
