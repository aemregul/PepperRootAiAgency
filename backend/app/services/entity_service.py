"""
Entity Service - Karakter, mekan, nesne yönetimi.
"""
import re
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Entity
from app.core.config import settings


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
            entity_type: character, location, costume, object, brand
            name: Entity adı
            description: Detaylı açıklama
            attributes: Ek özellikler (JSON)
            reference_image_url: Yüz/vücut referans görseli URL
            session_id: Opsiyonel - entity'nin oluşturulduğu proje
        
        Returns:
            Oluşturulan Entity
            
        Raises:
            ValueError: Aynı isimde entity zaten varsa
        """
        # Tag otomatik oluştur: sadece isim (@emre, @mutfak)
        name_slug = slugify(name)
        tag = f"@{name_slug}"
        
        # 🔒 UNIQUE CONSTRAINT: Aynı tag varsa hata fırlat
        # Projeler hariç tüm entity tipleri için kontrol et
        existing = await self.get_by_tag(db, user_id, tag)
        if existing:
            raise ValueError(
                f"Bu isimde bir {existing.entity_type} zaten var: {tag}. "
                f"Lütfen farklı bir isim kullanın (örn: {name}_2, {name}_yeni)"
            )
        
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
        
        # 🔍 Pinecone'a ekle (arka planda, hata durumunda sessizce devam et)
        if settings.USE_PINECONE:
            try:
                from app.services.embeddings.pinecone_service import pinecone_service
                await pinecone_service.upsert_entity(
                    entity_id=str(entity.id),
                    entity_type=entity_type,
                    name=name,
                    description=description or "",
                    attributes=attributes,
                    metadata={"user_id": str(user_id), "tag": tag}
                )
            except Exception as e:
                print(f"⚠️ Pinecone upsert uyarısı: {e}")
        
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
        Entity'yi çöp kutusuna taşı.
        
        Returns:
            Silme başarılı mı
        """
        from datetime import datetime, timedelta
        from sqlalchemy import delete
        from app.models.models import TrashItem, EntityAsset
        
        entity = await self.get_by_id(db, entity_id)
        if not entity:
            return False
        
        # Çöp kutusuna ekle
        trash_item = TrashItem(
            user_id=entity.user_id,
            session_id=None,  # Entity bağımsız olduğu için NULL
            item_type=entity.entity_type,  # character, location, brand, etc.
            item_id=str(entity.id),
            item_name=entity.name,
            original_data={
                "tag": entity.tag,
                "description": entity.description,
                "attributes": entity.attributes,
                "reference_image_url": entity.reference_image_url,
                "entity_type": entity.entity_type
            },
            expires_at=datetime.now() + timedelta(days=3)
        )
        db.add(trash_item)
        
        # Önce ilişkili entity_assets kayıtlarını sil (NOT NULL constraint)
        await db.execute(
            delete(EntityAsset).where(EntityAsset.entity_id == entity_id)
        )
        
        # Entity'yi sil
        await db.delete(entity)
        await db.commit()
        
        # 🔍 Pinecone'dan sil
        if settings.USE_PINECONE:
            try:
                from app.services.embeddings.pinecone_service import pinecone_service
                await pinecone_service.delete_entity(entity.entity_type, str(entity_id))
            except Exception as e:
                print(f"⚠️ Pinecone delete uyarısı: {e}")
        
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
