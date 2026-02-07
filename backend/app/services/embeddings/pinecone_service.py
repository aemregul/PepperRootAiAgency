"""
Pinecone Semantic Search Service.
Entity ve Asset'ler için vektör tabanlı semantik arama.
"""
import hashlib
from typing import Optional, List, Dict, Any
from openai import OpenAI

from app.core.config import settings


class PineconeService:
    """Pinecone ile semantic search servisi."""
    
    def __init__(self):
        self._index = None
        self._openai_client = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Pinecone ve OpenAI bağlantısını başlat."""
        if self._initialized:
            return True
            
        if not settings.USE_PINECONE or not settings.PINECONE_API_KEY:
            print("⚠️ Pinecone devre dışı (USE_PINECONE=false veya PINECONE_API_KEY eksik)")
            return False
        
        try:
            from pinecone import Pinecone
            
            # Pinecone client
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Index'e bağlan veya oluştur
            index_name = settings.PINECONE_INDEX_NAME
            
            # Mevcut index'leri kontrol et
            existing_indexes = [idx.name for idx in pc.list_indexes()]
            
            if index_name not in existing_indexes:
                # Index oluştur (1536 = OpenAI ada-002 dimension)
                pc.create_index(
                    name=index_name,
                    dimension=1536,
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": settings.PINECONE_ENVIRONMENT
                        }
                    }
                )
                print(f"✅ Pinecone index '{index_name}' oluşturuldu")
            
            self._index = pc.Index(index_name)
            
            # OpenAI client (embedding için)
            if settings.OPENAI_API_KEY:
                self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            else:
                print("⚠️ OPENAI_API_KEY eksik - embedding oluşturulamayacak")
                return False
            
            self._initialized = True
            print(f"✅ Pinecone bağlantısı kuruldu: {index_name}")
            return True
            
        except Exception as e:
            print(f"❌ Pinecone başlatma hatası: {e}")
            return False
    
    async def create_embedding(self, text: str) -> Optional[List[float]]:
        """
        Metin için OpenAI ada-002 embedding oluştur.
        
        Args:
            text: Embedding oluşturulacak metin
            
        Returns:
            1536 boyutlu float listesi veya None
        """
        if not self._openai_client:
            return None
            
        try:
            response = self._openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding oluşturma hatası: {e}")
            return None
    
    def _generate_id(self, entity_type: str, entity_id: str) -> str:
        """Benzersiz vektör ID'si oluştur."""
        return f"{entity_type}_{entity_id}"
    
    async def upsert_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        description: str = "",
        attributes: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Entity'yi Pinecone'a ekle veya güncelle.
        
        Args:
            entity_id: Entity UUID
            entity_type: character, location, brand, wardrobe
            name: Entity adı
            description: Açıklama
            attributes: Ek özellikler
            metadata: Ekstra metadata
            
        Returns:
            Başarı durumu
        """
        if not await self.initialize():
            return False
        
        try:
            # Embedding için metin oluştur
            text_parts = [name]
            if description:
                text_parts.append(description)
            if attributes:
                for key, value in attributes.items():
                    text_parts.append(f"{key}: {value}")
            
            full_text = " ".join(text_parts)
            
            # Embedding oluştur
            embedding = await self.create_embedding(full_text)
            if not embedding:
                return False
            
            # Metadata hazırla
            vector_metadata = {
                "entity_type": entity_type,
                "name": name,
                "description": description[:500] if description else "",
            }
            if metadata:
                vector_metadata.update(metadata)
            
            # Pinecone'a ekle
            vector_id = self._generate_id(entity_type, entity_id)
            self._index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": embedding,
                    "metadata": vector_metadata
                }]
            )
            
            print(f"✅ Entity Pinecone'a eklendi: {vector_id}")
            return True
            
        except Exception as e:
            print(f"❌ Pinecone upsert hatası: {e}")
            return False
    
    async def search_similar(
        self,
        query: str,
        entity_type: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Semantik olarak benzer entity'leri bul.
        
        Args:
            query: Arama sorgusu
            entity_type: Filtrelemek için entity tipi (opsiyonel)
            top_k: Döndürülecek maksimum sonuç sayısı
            
        Returns:
            Eşleşen entity'lerin listesi
        """
        if not await self.initialize():
            return []
        
        try:
            # Query için embedding oluştur
            query_embedding = await self.create_embedding(query)
            if not query_embedding:
                return []
            
            # Filtre oluştur
            filter_dict = None
            if entity_type:
                filter_dict = {"entity_type": {"$eq": entity_type}}
            
            # Arama yap
            results = self._index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Sonuçları formatla
            matches = []
            for match in results.matches:
                matches.append({
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata
                })
            
            return matches
            
        except Exception as e:
            print(f"❌ Pinecone search hatası: {e}")
            return []
    
    async def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        """
        Entity'yi Pinecone'dan sil.
        
        Args:
            entity_type: Entity tipi
            entity_id: Entity UUID
            
        Returns:
            Başarı durumu
        """
        if not await self.initialize():
            return False
        
        try:
            vector_id = self._generate_id(entity_type, entity_id)
            self._index.delete(ids=[vector_id])
            print(f"✅ Entity Pinecone'dan silindi: {vector_id}")
            return True
        except Exception as e:
            print(f"❌ Pinecone delete hatası: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Pinecone bağlantı durumunu kontrol et."""
        if not await self.initialize():
            return {"status": "disabled", "message": "Pinecone devre dışı"}
        
        try:
            stats = self._index.describe_index_stats()
            return {
                "status": "healthy",
                "index_name": settings.PINECONE_INDEX_NAME,
                "total_vectors": stats.total_vector_count,
                "dimension": stats.dimension
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance
pinecone_service = PineconeService()
