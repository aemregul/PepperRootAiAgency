"""
Chat API endpoint'leri.
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import base64

from app.core.database import get_db
from app.models.models import Session, Message
from app.schemas.schemas import ChatRequest, ChatResponse, MessageResponse, AssetResponse, EntityResponse
from app.services.agent.orchestrator import agent

router = APIRouter(prefix="/chat", tags=["Sohbet"])


async def _process_chat(
    actual_session_id: Optional[str],
    actual_message: str,
    reference_image_base64: Optional[str],
    db: AsyncSession
) -> ChatResponse:
    """Chat işleme ortak logic."""
    
    # Session al veya oluştur
    if actual_session_id:
        try:
            session_uuid = UUID(actual_session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Geçersiz session ID formatı: {actual_session_id}")
        
        result = await db.execute(
            select(Session).where(Session.id == session_uuid)
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
        content=actual_message,
        metadata_={"has_reference_image": reference_image_base64 is not None} if reference_image_base64 else {}
    )
    db.add(user_message)
    await db.flush()
    await db.refresh(user_message)
    
    # ÖNCEKİ MESAJLARI ÇEK - conversation_history oluştur
    # ChatGPT gibi tüm sohbet geçmişini hatırlaması için gerekli!
    from sqlalchemy import asc
    previous_messages_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .where(Message.id != user_message.id)  # Yeni mesaj hariç
        .order_by(asc(Message.created_at))  # Kronolojik sıra
    )
    previous_messages = previous_messages_result.scalars().all()
    
    # Hata pattern'leri - bunları içeren asistan mesajlarını atla
    ERROR_PATTERNS = [
        "kredi", "credit", "yetersiz", "insufficient", 
        "hata", "error", "başarısız", "failed",
        "oluşturulamadı", "üretilemedi", "yapılamadı"
    ]
    
    # OpenAI formatına çevir - HATA MESAJLARINI FİLTRELE
    conversation_history = []
    for msg in previous_messages:
        content = msg.content.lower() if msg.content else ""
        
        # Asistan mesajlarında hata pattern'i varsa atla
        if msg.role == "assistant":
            has_error = any(pattern in content for pattern in ERROR_PATTERNS)
            if has_error:
                continue  # Bu mesajı geçmişe ekleme
        
        conversation_history.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Max 20 mesaj (son mesajlar)
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    
    print(f"📜 Conversation history: {len(conversation_history)} mesaj yüklendi (session: {session.id})")
    
    # Agent ile yanıt al - ARTIK CONVERSATION_HISTORY İLE!
    try:
        agent_result = await agent.process_message(
            user_message=actual_message,
            session_id=session.id,
            db=db,
            conversation_history=conversation_history,  # 🔑 KRİTİK: Sohbet geçmişi
            reference_image=reference_image_base64
        )
    except Exception as e:
        import traceback
        print(f"AGENT ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent hatası: {str(e)}")
    
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
                user_id=session.user_id,  # Session'dan user_id al
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


# JSON endpoint (normal mesajlar)
@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı mesajını işle ve yanıt ver (JSON)."""
    return await _process_chat(
        actual_session_id=str(request.session_id) if request.session_id else None,
        actual_message=request.message,
        reference_image_base64=None,
        db=db
    )


# FormData endpoint (dosya yükleme ile)
@router.post("/with-image", response_model=ChatResponse)
async def chat_with_image(
    session_id: str = Form(...),
    message: str = Form(...),
    reference_image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı mesajını referans görsel ile işle (FormData)."""
    # Görseli base64'e çevir
    image_content = await reference_image.read()
    reference_image_base64 = base64.b64encode(image_content).decode('utf-8')
    
    return await _process_chat(
        actual_session_id=session_id,
        actual_message=message,
        reference_image_base64=reference_image_base64,
        db=db
    )