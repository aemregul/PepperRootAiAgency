"""
Admin API Routes - Sistem yönetimi, istatistikler, modeller.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import (
    AIModel, InstalledPlugin, UsageStats, UserSettings, 
    CreativePlugin, TrashItem, Session, GeneratedAsset, Message
)


router = APIRouter(prefix="/admin", tags=["Admin"])


# ============== SCHEMAS ==============

class AIModelResponse(BaseModel):
    id: str
    name: str
    display_name: str
    model_type: str
    provider: str
    description: Optional[str]
    icon: str
    is_enabled: bool

class AIModelToggle(BaseModel):
    is_enabled: bool

class InstalledPluginResponse(BaseModel):
    id: str
    plugin_id: str
    name: str
    description: Optional[str]
    icon: str
    category: str
    is_enabled: bool

class InstallPluginRequest(BaseModel):
    plugin_id: str
    name: str
    description: Optional[str]
    icon: str
    category: str
    api_key: Optional[str]

class UserSettingsResponse(BaseModel):
    id: str
    theme: str
    language: str
    notifications_enabled: bool
    auto_save: bool
    default_model: str

class UserSettingsUpdate(BaseModel):
    theme: Optional[str]
    language: Optional[str]
    notifications_enabled: Optional[bool]
    auto_save: Optional[bool]
    default_model: Optional[str]

class UsageStatsResponse(BaseModel):
    date: str
    api_calls: int
    images_generated: int
    videos_generated: int

class CreativePluginCreate(BaseModel):
    name: str
    description: Optional[str]
    icon: str = "✨"
    color: str = "#22c55e"
    system_prompt: Optional[str]
    is_public: bool = False

class CreativePluginResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    icon: str
    color: str
    system_prompt: Optional[str]
    is_public: bool
    usage_count: int

class TrashItemResponse(BaseModel):
    id: str
    item_type: str
    item_id: str
    item_name: str
    original_data: Optional[dict] = None
    deleted_at: datetime
    expires_at: datetime

class OverviewStats(BaseModel):
    total_sessions: int
    total_assets: int
    total_messages: int
    active_models: int
    total_images: int = 0
    total_videos: int = 0


# ============== AI MODELS ==============

@router.get("/models", response_model=list[AIModelResponse])
async def list_ai_models(db: AsyncSession = Depends(get_db)):
    """Tüm AI modellerini listele. İlk çağrıda ~38 gerçek modeli seed eder."""
    
    # Tüm modellerin master listesi — her biri gerçekten projede kullanılan model
    MASTER_MODELS = [
        # 🤖 LLM
        ("gpt4o", "GPT-4o", "llm", "openai", "Ana dil modeli — sohbet, analiz, orchestration", "🤖"),
        
        # 🖼️ Görsel Üretim
        ("nano_banana_pro", "Nano Banana Pro", "image", "fal", "Varsayılan görsel üretim — en iyi kalite", "🖼️"),
        ("nano_banana_2", "Nano Banana 2", "image", "fal", "Hızlı görsel üretim — Gemini 3.1 Flash", "⚡"),
        ("flux2", "Flux.2", "image", "fal", "Metin/tipografi render — yazılı görseller", "✍️"),
        ("flux2_max", "Flux 2 Max", "image", "fal", "Ultra detaylı premium görseller", "💎"),
        ("gpt_image", "GPT Image 1", "image", "fal", "Anime/Ghibli/cartoon tarzı görseller", "🎨"),
        ("reve", "Reve", "image", "fal", "Alternatif görsel üretim", "🌟"),
        ("seedream", "Seedream 4.5", "image", "fal", "ByteDance görsel modeli", "🌱"),
        ("recraft", "Recraft V3", "image", "fal", "Vektör tarzı ve illüstrasyon", "📐"),
        
        # 🎨 Görsel Düzenleme
        ("flux_kontext", "Flux Kontext", "edit", "fal", "Akıllı lokal görsel düzenleme", "🎯"),
        ("flux_kontext_pro", "Flux Kontext Pro", "edit", "fal", "Profesyonel görsel düzenleme", "🎯"),
        ("omnigen", "OmniGen V1", "edit", "fal", "Instruction-based düzenleme", "✨"),
        ("flux_inpainting", "Flux Inpainting", "edit", "fal", "Bölgesel dolgu düzenleme", "🖌️"),
        ("object_removal", "Object Removal", "edit", "fal", "Nesne silme", "🗑️"),
        ("outpainting", "Outpainting", "edit", "fal", "Görsel genişletme", "🔲"),
        ("nano_banana_2_edit", "Nano Banana 2 Edit", "edit", "fal", "AI resize + aspect ratio dönüşümü", "📐"),
        
        # 🎬 Video Üretim
        ("kling", "Kling 3.0 Pro", "video", "fal", "Varsayılan video — yüksek kalite", "🎬"),
        ("sora2", "Sora 2 Pro", "video", "fal", "Uzun/hikaye anlatımı videoları", "🎥"),
        ("veo_fast", "Veo 3.1 Fast", "video", "fal", "Hızlı sinematik video", "⚡"),
        ("veo_quality", "Veo 3.1 Quality", "video", "fal", "En yüksek kalite video — premium", "💎"),
        ("veo_google", "Veo 3.1 (Google SDK)", "video", "google", "Google GenAI SDK ile direkt video", "🔷"),
        ("seedance", "Seedance 1.5 Pro", "video", "fal", "ByteDance video modeli", "🌱"),
        ("hailuo", "Hailuo 02", "video", "fal", "Kısa/hızlı sosyal medya videoları", "📱"),
        
        # 🔧 Araç & Utility
        ("face_swap", "Face Swap", "utility", "fal", "Yüz değiştirme — karakter tutarlılığı", "👤"),
        ("topaz_upscale", "Topaz Upscale", "utility", "fal", "Görsel çözünürlük artırma", "🔍"),
        ("rembg", "Background Removal", "utility", "fal", "Arka plan kaldırma", "✂️"),
        ("style_transfer", "Style Transfer", "utility", "fal", "Sanatsal stil aktarımı", "🎨"),
        
        # 🔊 Ses & Müzik
        ("elevenlabs_tts", "ElevenLabs TTS", "audio", "elevenlabs", "Metin → ses dönüştürme", "🗣️"),
        ("whisper", "Whisper STT", "audio", "openai", "Ses → metin dönüştürme", "🎤"),
        ("mmaudio", "MMAudio (V2A)", "audio", "fal", "Video → ses efekti üretimi", "🔊"),
        ("stable_audio", "Stable Audio", "audio", "fal", "Müzik üretimi", "🎵"),
        ("elevenlabs_sfx", "ElevenLabs SFX", "audio", "elevenlabs", "Ses efekti üretimi", "💥"),
    ]
    
    # Mevcut modelleri çek
    result = await db.execute(select(AIModel))
    existing = {m.name: m for m in result.scalars().all()}
    
    # Eksik modelleri ekle (mevcut modellerin is_enabled durumunu koru)
    added = 0
    for name, display, mtype, provider, desc, icon in MASTER_MODELS:
        if name not in existing:
            db.add(AIModel(
                name=name, display_name=display, model_type=mtype,
                provider=provider, description=desc, icon=icon, is_enabled=True
            ))
            added += 1
    
    if added > 0:
        await db.commit()
    
    # Tümünü model_type sırasına göre getir
    result = await db.execute(
        select(AIModel).order_by(AIModel.model_type, AIModel.display_name)
    )
    models = result.scalars().all()
    
    return [AIModelResponse(
        id=str(m.id),
        name=m.name,
        display_name=m.display_name,
        model_type=m.model_type,
        provider=m.provider,
        description=m.description,
        icon=m.icon,
        is_enabled=m.is_enabled
    ) for m in models]


@router.patch("/models/{model_id}", response_model=AIModelResponse)
async def toggle_ai_model(
    model_id: UUID,
    data: AIModelToggle,
    db: AsyncSession = Depends(get_db)
):
    """AI modelini aktif/pasif yap."""
    result = await db.execute(select(AIModel).where(AIModel.id == model_id))
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model bulunamadı")
    
    model.is_enabled = data.is_enabled
    await db.commit()
    await db.refresh(model)
    
    # Smart router cache'ini invalidate et
    try:
        from app.services.plugins.fal_plugin_v2 import fal_plugin_v2
        fal_plugin_v2.invalidate_model_cache()
    except Exception:
        pass
    
    return AIModelResponse(
        id=str(model.id),
        name=model.name,
        display_name=model.display_name,
        model_type=model.model_type,
        provider=model.provider,
        description=model.description,
        icon=model.icon,
        is_enabled=model.is_enabled
    )


# ============== INSTALLED PLUGINS ==============

@router.get("/plugins/installed", response_model=list[InstalledPluginResponse])
async def list_installed_plugins(db: AsyncSession = Depends(get_db)):
    """Yüklü pluginleri listele."""
    result = await db.execute(select(InstalledPlugin).order_by(InstalledPlugin.installed_at.desc()))
    plugins = result.scalars().all()
    
    # Varsayılan pluginleri ekle
    if not plugins:
        default_plugins = [
            InstalledPlugin(plugin_id="falai", name="fal.ai", description="Hızlı görsel üretimi", icon="🖼️", category="Görsel", is_enabled=True),
            InstalledPlugin(plugin_id="kling", name="Kling 2.5 Video", description="AI video üretimi", icon="🎬", category="Video", is_enabled=True),
        ]
        for plugin in default_plugins:
            db.add(plugin)
        await db.commit()
        
        result = await db.execute(select(InstalledPlugin).order_by(InstalledPlugin.installed_at.desc()))
        plugins = result.scalars().all()
    
    return [InstalledPluginResponse(
        id=str(p.id),
        plugin_id=p.plugin_id,
        name=p.name,
        description=p.description,
        icon=p.icon,
        category=p.category,
        is_enabled=p.is_enabled
    ) for p in plugins]


@router.post("/plugins/install", response_model=InstalledPluginResponse)
async def install_plugin(
    data: InstallPluginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Yeni plugin yükle."""
    plugin = InstalledPlugin(
        plugin_id=data.plugin_id,
        name=data.name,
        description=data.description,
        icon=data.icon,
        category=data.category,
        api_key_encrypted=data.api_key,  # Gerçek uygulamada şifrelenecek
        is_enabled=True
    )
    db.add(plugin)
    await db.commit()
    await db.refresh(plugin)
    
    return InstalledPluginResponse(
        id=str(plugin.id),
        plugin_id=plugin.plugin_id,
        name=plugin.name,
        description=plugin.description,
        icon=plugin.icon,
        category=plugin.category,
        is_enabled=plugin.is_enabled
    )


@router.delete("/plugins/{plugin_id}")
async def uninstall_plugin(plugin_id: UUID, db: AsyncSession = Depends(get_db)):
    """Plugin kaldır."""
    result = await db.execute(select(InstalledPlugin).where(InstalledPlugin.id == plugin_id))
    plugin = result.scalar_one_or_none()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")
    
    await db.delete(plugin)
    await db.commit()
    
    return {"success": True, "message": "Plugin kaldırıldı"}


# ============== USER SETTINGS ==============

@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(db: AsyncSession = Depends(get_db)):
    """Kullanıcı ayarlarını getir."""
    result = await db.execute(select(UserSettings).limit(1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = UserSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return UserSettingsResponse(
        id=str(settings.id),
        theme=settings.theme,
        language=settings.language,
        notifications_enabled=settings.notifications_enabled,
        auto_save=settings.auto_save,
        default_model=settings.default_model
    )


@router.patch("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    data: UserSettingsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı ayarlarını güncelle."""
    result = await db.execute(select(UserSettings).limit(1))
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = UserSettings()
        db.add(settings)
    
    if data.theme is not None:
        settings.theme = data.theme
    if data.language is not None:
        settings.language = data.language
    if data.notifications_enabled is not None:
        settings.notifications_enabled = data.notifications_enabled
    if data.auto_save is not None:
        settings.auto_save = data.auto_save
    if data.default_model is not None:
        settings.default_model = data.default_model
    
    await db.commit()
    await db.refresh(settings)
    
    return UserSettingsResponse(
        id=str(settings.id),
        theme=settings.theme,
        language=settings.language,
        notifications_enabled=settings.notifications_enabled,
        auto_save=settings.auto_save,
        default_model=settings.default_model
    )


# ============== USAGE STATS ==============

@router.get("/stats/usage", response_model=list[UsageStatsResponse])
async def get_usage_stats(days: int = 7, db: AsyncSession = Depends(get_db)):
    """Son N günün kullanım istatistiklerini getir."""
    start_date = datetime.now() - timedelta(days=days)
    
    result = await db.execute(
        select(UsageStats)
        .where(UsageStats.date >= start_date)
        .order_by(UsageStats.date)
    )
    stats = result.scalars().all()
    
    # Eğer veritabanında veri yoksa, son 7 gün için sıfır değerlerle döndür
    if not stats:
        day_names = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        today = datetime.now()
        return [
            UsageStatsResponse(
                date=day_names[(today - timedelta(days=6-i)).weekday()],
                api_calls=0,
                images_generated=0,
                videos_generated=0
            )
            for i in range(7)
        ]
    
    return [UsageStatsResponse(
        date=s.date.strftime("%a"),
        api_calls=s.api_calls,
        images_generated=s.images_generated,
        videos_generated=s.videos_generated
    ) for s in stats]


@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_stats(db: AsyncSession = Depends(get_db)):
    """Genel sistem istatistikleri."""
    sessions_count = await db.execute(select(func.count(Session.id)))
    assets_count = await db.execute(select(func.count(GeneratedAsset.id)))
    messages_count = await db.execute(select(func.count(Message.id)))
    models_count = await db.execute(select(func.count(AIModel.id)).where(AIModel.is_enabled == True))
    
    # Görsel ve video sayılarını ayrı ayrı hesapla
    images_count = await db.execute(
        select(func.count(GeneratedAsset.id)).where(GeneratedAsset.asset_type == "image")
    )
    videos_count = await db.execute(
        select(func.count(GeneratedAsset.id)).where(GeneratedAsset.asset_type == "video")
    )
    
    return OverviewStats(
        total_sessions=sessions_count.scalar() or 0,
        total_assets=assets_count.scalar() or 0,
        total_messages=messages_count.scalar() or 0,
        active_models=models_count.scalar() or 0,
        total_images=images_count.scalar() or 0,
        total_videos=videos_count.scalar() or 0
    )


class ModelDistributionItem(BaseModel):
    name: str
    value: int
    color: str


@router.get("/stats/model-distribution", response_model=list[ModelDistributionItem])
async def get_model_distribution(db: AsyncSession = Depends(get_db)):
    """Model kullanım dağılımı - Hangi model ne kadar kullanılmış."""
    
    # GeneratedAsset tablosundan model_name grupla
    result = await db.execute(
        select(
            GeneratedAsset.model_name,
            func.count(GeneratedAsset.id).label("count")
        )
        .where(GeneratedAsset.model_name.isnot(None))
        .group_by(GeneratedAsset.model_name)
    )
    
    model_counts = result.all()
    
    # Renk haritası
    color_map = {
        "nano-banana-pro": "#22c55e",      # Yeşil - Görsel
        "nano_banana_with_face_swap": "#10b981",  # Koyu yeşil
        "face-swap": "#8b5cf6",            # Mor
        "kling-3.0-pro": "#3b82f6",        # Mavi - Video
        "kling-2.5-turbo": "#60a5fa",      # Açık mavi
        "flux-dev-img2img": "#f59e0b",     # Turuncu
        "topaz": "#ec4899",                # Pembe
        "bria-rmbg": "#6366f1",            # İndigo
    }
    
    distribution = []
    for model_name, count in model_counts:
        # Model adını kısalt ve güzelleştir
        display_name = model_name
        if "nano-banana" in model_name.lower():
            display_name = "Nano Banana"
        elif "kling" in model_name.lower():
            display_name = "Kling Video"
        elif "face" in model_name.lower():
            display_name = "Face Swap"
        elif "flux" in model_name.lower():
            display_name = "Flux"
        elif "topaz" in model_name.lower():
            display_name = "Topaz"
        
        color = color_map.get(model_name, "#6b7280")  # Default gray
        
        distribution.append(ModelDistributionItem(
            name=display_name,
            value=count,
            color=color
        ))
    
    # Veri yoksa default değerler
    if not distribution:
        distribution = [
            ModelDistributionItem(name="GPT-4o", value=0, color="#22c55e"),
            ModelDistributionItem(name="fal.ai", value=0, color="#8b5cf6"),
            ModelDistributionItem(name="Kling", value=0, color="#3b82f6"),
        ]
    
    return distribution


# ============== CREATIVE PLUGINS ==============

@router.get("/creative-plugins", response_model=list[CreativePluginResponse])
async def list_creative_plugins(
    session_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Kullanıcı tanımlı creative pluginleri listele."""
    query = select(CreativePlugin)
    if session_id:
        query = query.where(CreativePlugin.session_id == session_id)
    query = query.order_by(CreativePlugin.created_at.desc())
    
    result = await db.execute(query)
    plugins = result.scalars().all()
    
    return [CreativePluginResponse(
        id=str(p.id),
        name=p.name,
        description=p.description,
        icon=p.icon,
        color=p.color,
        system_prompt=p.system_prompt,
        is_public=p.is_public,
        usage_count=p.usage_count
    ) for p in plugins]


@router.post("/creative-plugins", response_model=CreativePluginResponse)
async def create_creative_plugin(
    data: CreativePluginCreate,
    session_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """Yeni creative plugin oluştur."""
    plugin = CreativePlugin(
        session_id=session_id,
        name=data.name,
        description=data.description,
        icon=data.icon,
        color=data.color,
        system_prompt=data.system_prompt,
        is_public=data.is_public
    )
    db.add(plugin)
    await db.commit()
    await db.refresh(plugin)
    
    return CreativePluginResponse(
        id=str(plugin.id),
        name=plugin.name,
        description=plugin.description,
        icon=plugin.icon,
        color=plugin.color,
        system_prompt=plugin.system_prompt,
        is_public=plugin.is_public,
        usage_count=plugin.usage_count
    )


@router.delete("/creative-plugins/{plugin_id}")
async def delete_creative_plugin(plugin_id: UUID, db: AsyncSession = Depends(get_db)):
    """Creative plugin sil."""
    result = await db.execute(select(CreativePlugin).where(CreativePlugin.id == plugin_id))
    plugin = result.scalar_one_or_none()
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin bulunamadı")
    
    await db.delete(plugin)
    await db.commit()
    
    return {"success": True, "message": "Creative plugin silindi"}


# ============== TRASH ==============

@router.get("/trash", response_model=list[TrashItemResponse])
async def list_trash_items(db: AsyncSession = Depends(get_db)):
    """Çöp kutusundaki öğeleri listele."""
    result = await db.execute(
        select(TrashItem)
        .where(TrashItem.expires_at > datetime.now())
        .order_by(TrashItem.deleted_at.desc())
    )
    items = result.scalars().all()
    
    return [TrashItemResponse(
        id=str(i.id),
        item_type=i.item_type,
        item_id=i.item_id,
        item_name=i.item_name,
        original_data=i.original_data,
        deleted_at=i.deleted_at,
        expires_at=i.expires_at
    ) for i in items]


@router.post("/trash/{item_id}/restore")
async def restore_trash_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    """Çöpteki öğeyi geri yükle."""
    result = await db.execute(select(TrashItem).where(TrashItem.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Öğe bulunamadı")
    
    original_data = item.original_data or {}
    item_type = item.item_type
    restored_item = None
    
    try:
        # Session (proje) geri yükleme
        if item_type == "session":
            from uuid import UUID as UUIDType
            session_result = await db.execute(
                select(Session).where(Session.id == UUIDType(item.item_id))
            )
            session = session_result.scalar_one_or_none()
            if session:
                session.is_active = True
                restored_item = {"type": "session", "id": str(session.id), "title": session.title}
            else:
                # Session tamamen silinmişse yeniden oluştur
                new_session = Session(
                    id=UUIDType(item.item_id),
                    user_id=UUIDType(original_data.get("user_id")) if original_data.get("user_id") else None,
                    title=original_data.get("title", "Restored Project"),
                    is_active=True
                )
                db.add(new_session)
                restored_item = {"type": "session", "id": str(new_session.id), "title": new_session.title}
        
        # Entity (karakter, lokasyon, marka) geri yükleme
        elif item_type in ["character", "location", "brand"]:
            from app.models.models import Entity
            new_entity = Entity(
                user_id=item.user_id,
                session_id=None,  # Session bağımsız olarak geri yükle
                entity_type=original_data.get("entity_type", item_type),
                name=item.item_name,
                tag=original_data.get("tag", f"@{item.item_name.lower().replace(' ', '_')}"),
                description=original_data.get("description"),
                attributes=original_data.get("attributes", {}),
                reference_image_url=original_data.get("reference_image_url")
            )
            db.add(new_entity)
            await db.flush()
            restored_item = {"type": item_type, "id": str(new_entity.id), "name": new_entity.name, "tag": new_entity.tag}
        
        # Asset geri yükleme
        elif item_type == "asset":
            from app.models.models import GeneratedAsset
            from uuid import UUID as UUIDType
            new_asset = GeneratedAsset(
                session_id=UUIDType(original_data.get("session_id")) if original_data.get("session_id") else None,
                asset_type=original_data.get("type", "image"),
                url=original_data.get("url", ""),
                prompt=original_data.get("prompt"),
                model_name=original_data.get("model_name")
            )
            db.add(new_asset)
            await db.flush()
            restored_item = {"type": "asset", "id": str(new_asset.id), "url": new_asset.url}
        
        else:
            # Bilinmeyen tip - sadece çöpten sil
            restored_item = {"type": item_type, "data": original_data}
        
        # TrashItem'ı sil
        await db.delete(item)
        await db.commit()
        
        return {"success": True, "message": f"{item_type} başarıyla geri yüklendi!", "restored": restored_item}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Geri yükleme hatası: {str(e)}")


@router.delete("/trash/{item_id}")
async def permanent_delete_trash_item(item_id: UUID, db: AsyncSession = Depends(get_db)):
    """Öğeyi kalıcı olarak sil."""
    result = await db.execute(select(TrashItem).where(TrashItem.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Öğe bulunamadı")
    
    await db.delete(item)
    await db.commit()
    
    return {"success": True, "message": "Öğe kalıcı olarak silindi"}
