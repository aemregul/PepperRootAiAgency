"""
Oturum API endpoint'leri.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Session, Message, Entity, GeneratedAsset
from app.schemas.schemas import SessionCreate, SessionResponse, MessageResponse, EntityResponse, AssetResponse

router = APIRouter(prefix="/sessions", tags=["Oturumlar"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Yeni oturum oluştur."""
    # Geçici user_id (auth eklenince değişecek)
    from uuid import uuid4
    temp_user_id = uuid4()
    
    new_session = Session(
        user_id=temp_user_id,
        title=session_data.title or "Yeni Oturum"
    )
    db.add(new_session)
    await db.flush()
    await db.refresh(new_session)
    return new_session


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Oturumları listele."""
    result = await db.execute(
        select(Session)
        .where(Session.is_active == True)
        .order_by(Session.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Oturum detayı."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    return session


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def get_session_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Oturumdaki mesajları getir."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


@router.get("/{session_id}/entities", response_model=list[EntityResponse])
async def get_session_entities(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Oturumdaki varlıkları getir."""
    result = await db.execute(
        select(Entity)
        .where(Entity.session_id == session_id)
        .order_by(Entity.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{session_id}/assets", response_model=list[AssetResponse])
async def get_session_assets(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Oturumdaki asset'leri getir."""
    result = await db.execute(
        select(GeneratedAsset)
        .where(GeneratedAsset.session_id == session_id)
        .order_by(GeneratedAsset.created_at.desc())
    )
    return result.scalars().all()


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Oturumu sil (soft delete)."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    
    session.is_active = False
    await db.flush()
