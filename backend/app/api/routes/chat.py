"""
Chat API endpoint'leri.
"""
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Session, Message
from app.schemas.schemas import ChatRequest, ChatResponse, MessageResponse

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
        # Yeni session oluştur
        temp_user_id = uuid4()
        session = Session(user_id=temp_user_id, title="Yeni Sohbet")
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
    
    # TODO: Agent entegrasyonu burada olacak
    # Şimdilik basit echo yanıtı
    response_content = f"Mesajınız alındı: '{request.message}'. Agent entegrasyonu yakında..."
    
    # Assistant yanıtını kaydet
    assistant_message = Message(
        session_id=session.id,
        role="assistant",
        content=response_content
    )
    db.add(assistant_message)
    await db.flush()
    await db.refresh(assistant_message)
    
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
        assets=[],
        entities_created=[]
    )
