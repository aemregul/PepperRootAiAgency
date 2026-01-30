"""
Entity API Routes - Karakter, mekan yönetimi.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import EntityCreate, EntityResponse
from app.services.entity_service import entity_service


router = APIRouter(prefix="/entities", tags=["Varlıklar"])


@router.post("/", response_model=EntityResponse, summary="Entity Oluştur")
async def create_entity(
    session_id: UUID,
    data: EntityCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Yeni bir entity (karakter/mekan/nesne) oluşturur.
    
    Tag otomatik oluşturulur: @{entity_type}_{name}
    reference_image_url ile yüz/vücut referansı bağlanabilir.
    """
    entity = await entity_service.create_entity(
        db=db,
        session_id=session_id,
        entity_type=data.entity_type,
        name=data.name,
        description=data.description,
        attributes=data.attributes,
        reference_image_url=data.reference_image_url
    )
    return entity


@router.get("/", response_model=list[EntityResponse], summary="Entity Listele")
async def list_entities(
    session_id: UUID,
    entity_type: Optional[str] = Query(None, description="Filtre: character, location, vb."),
    db: AsyncSession = Depends(get_db)
):
    """
    Session'daki tüm entity'leri listeler.
    
    Opsiyonel olarak entity_type ile filtrelenebilir.
    """
    entities = await entity_service.list_entities(
        db=db,
        session_id=session_id,
        entity_type=entity_type
    )
    return entities


@router.get("/{tag}", response_model=EntityResponse, summary="Tag ile Entity Bul")
async def get_entity_by_tag(
    session_id: UUID,
    tag: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Tag ile entity arar.
    
    Tag formatı: @character_emre veya character_emre (@ opsiyonel)
    """
    entity = await entity_service.get_by_tag(db, session_id, tag)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"'{tag}' tag'i ile entity bulunamadı")
    
    return entity


@router.delete("/{entity_id}", summary="Entity Sil")
async def delete_entity(
    entity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Entity siler."""
    success = await entity_service.delete_entity(db, entity_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Entity bulunamadı")
    
    return {"success": True, "message": "Entity silindi"}
