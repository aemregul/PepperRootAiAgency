"""
Chat API endpoint'leri — Tek Asistan Mimarisi.
Mesajlar ana chat session'a, asset'ler aktif projeye kaydedilir.
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import base64

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_required
from app.models.models import Session, Message, User
from app.schemas.schemas import ChatRequest, ChatResponse, MessageResponse, AssetResponse, EntityResponse
from app.services.agent.orchestrator import agent

router = APIRouter(prefix="/chat", tags=["Sohbet"])


@router.get("/main-session")
async def get_main_chat_session(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_required)
):
    """Kullanıcının ana chat session'ını döndür. Yoksa otomatik oluştur."""
    
    # Mevcut main chat session var mı?
    if current_user.main_chat_session_id:
        result = await db.execute(
            select(Session).where(
                Session.id == current_user.main_chat_session_id,
                Session.is_active == True
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            return {"session_id": str(existing.id), "title": existing.title}
    
    # Yoksa yeni oluştur
    main_session = Session(
        user_id=current_user.id,
        title="Ana Sohbet",
        description="Tüm projeler için tek asistan sohbeti",
        category="main_chat"
    )
    db.add(main_session)
    await db.flush()
    await db.refresh(main_session)
    
    # User'a bağla
    current_user.main_chat_session_id = main_session.id
    await db.commit()
    
    return {"session_id": str(main_session.id), "title": main_session.title}


async def _process_chat(
    actual_session_id: Optional[str],
    actual_message: str,
    reference_image_base64: Optional[str],
    db: AsyncSession,
    active_project_id: Optional[str] = None
) -> ChatResponse:
    """Chat işleme ortak logic. Mesajlar session'a, asset'ler active_project'e kaydedilir."""
    
    # Asset'ler hangi projeye kaydedilecek?
    asset_session_id = None
    if active_project_id:
        try:
            asset_session_id = UUID(active_project_id)
        except ValueError:
            pass
    
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
    last_reference_url_from_history = None  # DB'den referans URL çıkar
    
    for msg in previous_messages:
        content = msg.content.lower() if msg.content else ""
        
        # Asistan mesajlarında hata pattern'i varsa atla
        if msg.role == "assistant":
            has_error = any(pattern in content for pattern in ERROR_PATTERNS)
            if has_error:
                continue  # Bu mesajı geçmişe ekleme
        
        # Mesaj içeriğini hazırla
        msg_content = msg.content or ""
        
        # Assistant mesajlarında metadata'dan image/video URL'lerini ekle
        # (content'ten kaldırıldı ama GPT-4o'nun bunları bilmesi gerekiyor)
        if msg.role == "assistant" and msg.metadata_:
            meta = msg.metadata_ if isinstance(msg.metadata_, dict) else {}
            images = meta.get("images", [])
            videos = meta.get("videos", [])
            if images:
                urls = [img.get("url", "") for img in images if isinstance(img, dict) and img.get("url")]
                if urls:
                    msg_content += "\n\n[Bu mesajda üretilen görseller: " + ", ".join(urls) + "]"
                    last_reference_url_from_history = urls[-1]  # Son üretilen görseli referans olarak kaydet
            if videos:
                urls = [vid.get("url", "") for vid in videos if isinstance(vid, dict) and vid.get("url")]
                if urls:
                    msg_content += "\n\n[Bu mesajda üretilen videolar: " + ", ".join(urls) + "]"
        
        # User mesajlarında referans görsel URL'si varsa çıkar
        if msg.role == "user" and msg.metadata_:
            meta = msg.metadata_ if isinstance(msg.metadata_, dict) else {}
            if meta.get("has_reference_image") and meta.get("reference_url"):
                last_reference_url_from_history = meta["reference_url"]
        
        conversation_history.append({
            "role": msg.role,
            "content": msg_content
        })
    
    # Max 20 mesaj (son mesajlar)
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    
    print(f"📜 Conversation history: {len(conversation_history)} mesaj yüklendi (session: {session.id})")
    
    # Agent ile yanıt al - ARTIK CONVERSATION_HISTORY İLE!
    try:
        agent_result = await agent.process_message(
            user_message=actual_message,
            session_id=asset_session_id or session.id,  # Asset'ler aktif projeye
            db=db,
            conversation_history=conversation_history,
            reference_image=reference_image_base64,
            last_reference_url=last_reference_url_from_history
        )
    except Exception as e:
        import traceback
        print(f"AGENT ERROR: {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent hatası: {str(e)}")
    
    response_content = agent_result.get("response", "")
    images = agent_result.get("images", [])
    videos = agent_result.get("videos", [])
    entities_created = agent_result.get("entities_created", [])
    
    # Assistant yanıtını kaydet — URL'ler metadata'da saklanır, content'e eklenmez
    enriched_content = response_content
    
    assistant_message = Message(
        session_id=session.id,
        role="assistant",
        content=enriched_content,
        metadata_={
            "images": images,
            "videos": videos,
            "entities_created": [e.get("tag") for e in entities_created if isinstance(e, dict)]
        } if images or videos or entities_created else {}
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)
    
    # === AUTO SUMMARY: Projeler arası hafıza ===
    # Her 10 mesajda bir sohbet özeti kaydet
    total_messages = len(conversation_history) + 2  # +2 = yeni user + assistant
    if total_messages >= 10 and total_messages % 5 == 0 and session.user_id:
        try:
            from app.services.conversation_memory_service import conversation_memory
            summary_messages = conversation_history[-10:] + [
                {"role": "user", "content": actual_message},
                {"role": "assistant", "content": response_content}
            ]
            await conversation_memory.save_conversation_summary(
                user_id=session.user_id,
                session_id=session.id,
                messages=summary_messages,
                project_name=session.title
            )
            print(f"💾 Auto-summary kaydedildi (proje: {session.title}, mesaj: {total_messages})")
        except Exception as e:
            print(f"⚠️ Auto-summary hatası: {e}")
    
    # Assets listesi oluştur
    assets = []
    for img in images:
        assets.append(AssetResponse(
            id=None,
            asset_type="image",
            url=img.get("url", ""),
            prompt=img.get("prompt", "")
        ))
        
    for vid in videos:
        assets.append(AssetResponse(
            id=None,
            asset_type="video",
            url=vid.get("url", ""),
            prompt=vid.get("prompt", ""),
            thumbnail_url=vid.get("thumbnail_url")
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
        db=db,
        active_project_id=str(request.active_project_id) if request.active_project_id else None
    )


# FormData endpoint (dosya yükleme ile)
@router.post("/with-image", response_model=ChatResponse)
async def chat_with_image(
    session_id: str = Form(...),
    message: str = Form(...),
    reference_image: UploadFile = File(...),
    active_project_id: Optional[str] = Form(None),
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
        db=db,
        active_project_id=active_project_id
    )


# SSE Streaming endpoint
@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı mesajını işle ve SSE ile stream et (ChatGPT tarzı)."""
    print(f"🔴 STREAM ENDPOINT HIT! message={request.message[:50]}")
    from sqlalchemy import asc
    import json
    
    actual_session_id = str(request.session_id) if request.session_id else None
    active_project_id = str(request.active_project_id) if request.active_project_id else None
    actual_message = request.message
    
    # Asset hedef session
    asset_session_id = None
    if active_project_id:
        try:
            asset_session_id = UUID(active_project_id)
        except ValueError:
            pass
    
    # Session al
    if actual_session_id:
        try:
            session_uuid = UUID(actual_session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Geçersiz session ID")
        result = await db.execute(select(Session).where(Session.id == session_uuid))
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status_code=404, detail="Oturum bulunamadı")
    else:
        session = Session(title="Yeni Sohbet")
        db.add(session)
        await db.flush()
        await db.refresh(session)
    
    # Kullanıcı mesajını kaydet
    user_msg = Message(session_id=session.id, role="user", content=actual_message)
    db.add(user_msg)
    await db.flush()
    await db.refresh(user_msg)
    
    # Geçmiş mesajları çek
    prev_result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .where(Message.id != user_msg.id)
        .order_by(asc(Message.created_at))
    )
    previous_messages = prev_result.scalars().all()
    
    ERROR_PATTERNS = ["kredi", "credit", "yetersiz", "insufficient", "hata", "error", "başarısız", "failed"]
    conversation_history = []
    last_reference_url_from_history = None
    
    for msg in previous_messages:
        content = msg.content.lower() if msg.content else ""
        if msg.role == "assistant" and any(p in content for p in ERROR_PATTERNS):
            continue
        
        msg_content = msg.content or ""
        
        # Assistant mesajlarında metadata'dan image/video URL'lerini ekle
        if msg.role == "assistant" and msg.metadata_:
            meta = msg.metadata_ if isinstance(msg.metadata_, dict) else {}
            images = meta.get("images", [])
            videos = meta.get("videos", [])
            if images:
                urls = [img.get("url", "") for img in images if isinstance(img, dict) and img.get("url")]
                if urls:
                    msg_content += "\n\n[Bu mesajda üretilen görseller: " + ", ".join(urls) + "]"
                    last_reference_url_from_history = urls[-1]
            if videos:
                urls = [vid.get("url", "") for vid in videos if isinstance(vid, dict) and vid.get("url")]
                if urls:
                    msg_content += "\n\n[Bu mesajda üretilen videolar: " + ", ".join(urls) + "]"
        
        if msg.role == "user" and msg.metadata_:
            meta = msg.metadata_ if isinstance(msg.metadata_, dict) else {}
            if meta.get("has_reference_image") and meta.get("reference_url"):
                last_reference_url_from_history = meta["reference_url"]
        
        conversation_history.append({"role": msg.role, "content": msg_content})
    
    if len(conversation_history) > 20:
        conversation_history = conversation_history[-20:]
    
    async def event_generator():
        full_response = ""
        all_images = []
        all_videos = []
        all_entities = []
        
        try:
            async for event in agent.process_message_stream(
                user_message=actual_message,
                session_id=asset_session_id or session.id,
                db=db,
                conversation_history=conversation_history
            ):
                yield event
                
                # Tam yanıtı biriktir (DB'ye kaydetmek için)
                if event.startswith("event: token"):
                    data_line = event.split("data: ", 1)[1].strip()
                    try:
                        token = json.loads(data_line)
                        full_response += token
                    except:
                        pass
                elif event.startswith("event: assets"):
                    data_line = event.split("data: ", 1)[1].strip()
                    try:
                        all_images = json.loads(data_line)
                    except:
                        pass
                elif event.startswith("event: videos"):
                    data_line = event.split("data: ", 1)[1].strip()
                    try:
                        all_videos = json.loads(data_line)
                    except:
                        pass
        except Exception as e:
            yield f"event: error\ndata: {json.dumps(str(e))}\n\n"
        
        # Yanıtı DB'ye kaydet — üretilen görsellerin URL'lerini de mesaja ekle
        try:
            # Image/video URL'leri metadata'da saklanır, content'e eklenmez
            enriched_response = full_response or "(stream yanıtı)"
            
            assistant_msg = Message(
                session_id=session.id,
                role="assistant",
                content=enriched_response,
                metadata_={
                    "images": all_images,
                    "videos": all_videos,
                    "streamed": True
                } if all_images or all_videos else {"streamed": True}
            )
            db.add(assistant_msg)
            await db.commit()
        except Exception as e:
            print(f"⚠️ Stream DB kayıt hatası: {e}")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )