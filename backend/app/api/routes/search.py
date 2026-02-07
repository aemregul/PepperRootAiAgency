"""
Semantic Search API Routes.
Pinecone ile entity ve asset araması.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.services.embeddings.pinecone_service import pinecone_service


router = APIRouter(prefix="/search", tags=["Arama"])


class SearchResult(BaseModel):
    id: str
    score: float
    entity_type: str
    name: str
    description: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int


@router.get("/entities", response_model=SearchResponse, summary="Semantik Entity Arama")
async def search_entities(
    q: str = Query(..., description="Arama sorgusu", min_length=2),
    entity_type: Optional[str] = Query(None, description="Entity tipi filtresi (character, location, brand, wardrobe)"),
    limit: int = Query(10, ge=1, le=50, description="Maksimum sonuç sayısı")
):
    """
    Semantik olarak benzer entity'leri arar.
    
    Örnek sorgular:
    - "sarışın erkek karakter"
    - "plaj lokasyonu"
    - "spor giyim markası"
    """
    if not settings.USE_PINECONE:
        return SearchResponse(
            query=q,
            results=[],
            total=0
        )
    
    matches = await pinecone_service.search_similar(
        query=q,
        entity_type=entity_type,
        top_k=limit
    )
    
    results = []
    for match in matches:
        results.append(SearchResult(
            id=match["id"],
            score=match["score"],
            entity_type=match["metadata"].get("entity_type", "unknown"),
            name=match["metadata"].get("name", ""),
            description=match["metadata"].get("description", "")
        ))
    
    return SearchResponse(
        query=q,
        results=results,
        total=len(results)
    )


@router.get("/health", summary="Pinecone Sağlık Kontrolü")
async def search_health():
    """Pinecone bağlantı durumunu kontrol eder."""
    return await pinecone_service.health_check()
