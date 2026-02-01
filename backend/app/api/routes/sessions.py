"""
Oturum API endpoint'leri.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_required
from app.models.models import Session, Message, Entity, GeneratedAsset, TrashItem, User
from app.schemas.schemas import SessionCreate, SessionResponse, MessageResponse, EntityResponse, AssetResponse

router = APIRouter(prefix="/sessions", tags=["Oturumlar"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Yeni oturum oluştur."""
    try:
        new_session = Session(
            user_id=current_user.id if current_user else None,
            title=session_data.title or "Yeni Oturum"
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Oturum oluşturulurken hata: {str(e)}"
        )


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Oturumları listele (kullanıcıya özel)."""
    query = select(Session).where(Session.is_active == True)
    
    # Kullanıcı giriş yapmışsa sadece onun session'larını göster
    if current_user:
        query = query.where(Session.user_id == current_user.id)
    else:
        # Giriş yapmamışsa sadece user_id=None olanları göster
        query = query.where(Session.user_id == None)
    
    result = await db.execute(
        query.order_by(Session.updated_at.desc())
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


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: UUID,
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Oturum bilgilerini güncelle (rename)."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    
    if session_data.title:
        session.title = session_data.title
    
    await db.commit()
    await db.refresh(session)
    return session


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
    await db.commit()


@router.delete("/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Asset sil (soft delete - çöp kutusuna taşı)."""
    from datetime import timedelta
    
    result = await db.execute(
        select(GeneratedAsset).where(GeneratedAsset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset bulunamadı")
    
    # TrashItem oluştur
    from datetime import datetime
    trash_item = TrashItem(
        item_type="asset",
        item_id=str(asset.id),
        item_name=asset.prompt[:50] if asset.prompt else "Generated Asset",
        original_data={
            "url": asset.url,
            "type": asset.asset_type,
            "prompt": asset.prompt,
            "session_id": str(asset.session_id) if asset.session_id else None,
            "model_name": asset.model_name
        },
        session_id=asset.session_id,
        expires_at=datetime.now() + timedelta(days=3)
    )
    db.add(trash_item)
    
    # Asset'i sil
    await db.delete(asset)
    await db.flush()
