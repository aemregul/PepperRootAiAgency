"""
Chat API endpoint'leri.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Session, Message
from app.schemas.schemas import ChatRequest, ChatResponse, MessageResponse, AssetResponse, EntityResponse
from app.services.agent.orchestrator import agent

router = APIRouter(prefix="/chat", tags=["Sohbet"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı mesajını işle ve yanıt ver."""
    
    # Session al veya oluştur
    if request.session_id:
        result = await db.execute(
            select(Session).where(Session.id == request.session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    else:
        # Yeni anonim session oluştur
        session = Session(title="Yeni Sohbet")
        db.add(session)
        await db.flush()
        await db.refresh(session)
    
    # Kullanıcı mesajını kaydet
    user_message = Message(
        session_id=session.id,
        role="user",
        content=request.message
    )
    db.add(user_message)
    await db.flush()
    await db.refresh(user_message)
    
    # Agent ile yanıt al (db ve session_id dahil)
    agent_result = await agent.process_message(
        user_message=request.message,
        session_id=session.id,
        db=db
    )
    
    response_content = agent_result.get("response", "")
    images = agent_result.get("images", [])
    entities_created = agent_result.get("entities_created", [])
    
    # Assistant yanıtını kaydet
    assistant_message = Message(
        session_id=session.id,
        role="assistant",
        content=response_content,
        metadata_={
            "images": images,
            "entities_created": [e.get("tag") for e in entities_created if isinstance(e, dict)]
        } if images or entities_created else {}
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    # Assets listesi oluştur
    assets = []
    for img in images:
        assets.append(AssetResponse(
            id=None,
            asset_type="image",
            url=img.get("url", ""),
            prompt=img.get("prompt", "")
        ))
    
    # Entities response listesi oluştur
    entity_responses = []
    for entity_data in entities_created:
        if isinstance(entity_data, dict):
            entity_responses.append(EntityResponse(
                id=entity_data.get("id"),
                session_id=session.id,
                entity_type=entity_data.get("entity_type", ""),
                name=entity_data.get("name", ""),
                tag=entity_data.get("tag", ""),
                description=entity_data.get("description"),
                attributes=entity_data.get("attributes"),
                created_at=assistant_message.created_at
            ))
    
    return ChatResponse(
        session_id=session.id,
        message=MessageResponse(
            id=user_message.id,
            session_id=user_message.session_id,
            role=user_message.role,
            content=user_message.content,
            metadata_=user_message.metadata_,
            created_at=user_message.created_at
        ),
        response=MessageResponse(
            id=assistant_message.id,
            session_id=assistant_message.session_id,
            role=assistant_message.role,
            content=assistant_message.content,
            metadata_=assistant_message.metadata_,
            created_at=assistant_message.created_at
        ),
        assets=assets,
        entities_created=entity_responses
    )