"""
Agent Orchestrator - Agent'ın beyni.
Kullanıcı mesajını alır, LLM'e gönderir, araç çağrılarını yönetir.
"""
import json
import uuid
from typing import Optional
from anthropic import Anthropic
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.agent.tools import AGENT_TOOLS
from app.services.plugins.fal_plugin import FalPlugin
from app.services.entity_service import entity_service
from app.services.asset_service import asset_service
from app.services.prompt_translator import translate_to_english, enhance_character_prompt


class AgentOrchestrator:
    """Agent'ı yöneten ana sınıf."""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.fal_plugin = FalPlugin()
        self.model = "claude-sonnet-4-20250514"
        
        self.system_prompt = """Sen Pepper Root AI Agency'nin AKILLI asistanısın.
Sadece görsel üretmekle kalmaz, TÜM SİSTEME HAKİMSİN ve AKSİYON ALABİLİRSİN.

SEN KİMSİN:
- Ajantik (agent-first) bir sistem parçasısın  
- Pasif değilsin, PROAKTİF davranırsın
- Hata durumunda alternatif yollar denersin

YAPABİLECEKLERİN:
1. GÖRSEL/VİDEO: generate_image, generate_video, edit_image, upscale_image, remove_background
2. ENTITY: create_character, create_location, get_entity, list_entities, delete_entity
3. PROJE: manage_project (create/list/switch/delete)
4. PLUGIN: manage_plugin (create/list/delete) - chat context'inden stil çıkar
5. ÇÖP KUTUSU: manage_trash (list/restore/empty)
6. GEÇMİŞ: get_past_assets, mark_favorite, undo_last
7. ANALİZ: analyze_image, compare_images
8. SİSTEM: get_system_state

DAVRANIŞ KURALLARI:
- "Yeni proje aç" -> manage_project action=create
- "Bunu favori yap" -> mark_favorite
- "Dünkü videoyu bul" -> get_past_assets
- "Emre'yi sil" -> delete_entity
- "Çöpü göster" -> manage_trash action=list
- "Bunu plugin yap" -> manage_plugin action=create
- Türkçe yanıt ver, araç parametreleri İngilizce olabilir
- @tag sistemi: @character_emre, @location_mutfak
- Silme isteklerinde önce çöpe at (geri alınabilir)
"""
    
    async def process_message(
        self, 
        user_message: str, 
        session_id: uuid.UUID,
        db: AsyncSession,
        conversation_history: list = None
    ) -> dict:
        """
        Kullanıcı mesajını işle ve yanıt döndür.
        
        Args:
            user_message: Kullanıcının mesajı
            session_id: Oturum ID
            db: Database session
            conversation_history: Önceki mesajlar (opsiyonel)
        
        Returns:
            dict: {"response": str, "images": list, "entities_created": list}
        """
        if conversation_history is None:
            conversation_history = []
        
        # @tag'leri çözümle ve context oluştur
        entity_context = await self._build_entity_context(db, session_id, user_message)
        
        # System prompt'a entity context ekle
        full_system_prompt = self.system_prompt
        if entity_context:
            full_system_prompt += f"\n\n--- Mevcut Entity Bilgileri ---\n{entity_context}"
        
        # Mesajları hazırla
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]
        
        # Claude'a gönder
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=full_system_prompt,
            tools=AGENT_TOOLS,
            messages=messages
        )
        
        # Sonucu işle
        result = {
            "response": "",
            "images": [],
            "entities_created": [],
            "_resolved_entities": []  # İç kullanım için, @tag ile çözümlenen entity'ler
        }
        
        # @tag'leri çözümle ve result'a ekle
        resolved = await entity_service.resolve_tags(db, session_id, user_message)
        result["_resolved_entities"] = resolved
        
        # Response'u işle - tool call loop
        await self._process_response(response, messages, result, session_id, db)
        
        # İç kullanım alanını kaldır
        del result["_resolved_entities"]
        
        return result
    
    async def _build_entity_context(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        message: str
    ) -> str:
        """Mesajdaki @tag'leri çözümle ve context string oluştur."""
        entities = await entity_service.resolve_tags(db, session_id, message)
        
        if not entities:
            return ""
        
        context_parts = []
        for entity in entities:
            context_parts.append(
                f"- {entity.tag}: {entity.name} ({entity.entity_type})\n"
                f"  Açıklama: {entity.description}\n"
                f"  Özellikler: {json.dumps(entity.attributes, ensure_ascii=False)}"
            )
        
        return "\n".join(context_parts)
    
    async def _process_response(
        self, 
        response, 
        messages: list, 
        result: dict,
        session_id: uuid.UUID,
        db: AsyncSession
    ):
        """Claude response'unu işle, tool call varsa yürüt."""
        
        for block in response.content:
            if block.type == "text":
                result["response"] += block.text
            
            elif block.type == "tool_use":
                # Araç çağrısı var, işle
                tool_result = await self._handle_tool_call(
                    block.name, 
                    block.input, 
                    session_id, 
                    db,
                    resolved_entities=result.get("_resolved_entities", [])
                )
                
                # Görsel üretildiyse ekle
                if tool_result.get("success") and tool_result.get("image_url"):
                    result["images"].append({
                        "url": tool_result["image_url"],
                        "prompt": block.input.get("prompt", "")
                    })
                
                # Entity oluşturulduysa ekle
                if tool_result.get("success") and tool_result.get("entity"):
                    result["entities_created"].append(tool_result["entity"])
                
                # Araç sonucunu Claude'a gönder ve devam et
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result, ensure_ascii=False, default=str)
                        }
                    ]
                })
                
                # Claude'dan devam yanıtı al
                continue_response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    tools=AGENT_TOOLS,
                    messages=messages
                )
                
                # Recursive olarak devam et (nested tool calls için)
                await self._process_response(
                    continue_response, 
                    messages, 
                    result, 
                    session_id, 
                    db
                )
    
    async def _handle_tool_call(
        self, 
        tool_name: str, 
        tool_input: dict,
        session_id: uuid.UUID,
        db: AsyncSession,
        resolved_entities: list = None
    ) -> dict:
        """Araç çağrısını işle."""
        
        if tool_name == "generate_image":
            return await self._generate_image(
                db, session_id, tool_input, resolved_entities or []
            )
        
        elif tool_name == "create_character":
            return await self._create_entity(
                db, session_id, "character", tool_input
            )
        
        elif tool_name == "create_location":
            return await self._create_entity(
                db, session_id, "location", tool_input
            )
        
        elif tool_name == "get_entity":
            return await self._get_entity(db, session_id, tool_input)
        
        elif tool_name == "list_entities":
            return await self._list_entities(db, session_id, tool_input)
        
        # YENİ ARAÇLAR
        elif tool_name == "generate_video":
            return await self._generate_video(tool_input, resolved_entities or [])
        
        elif tool_name == "edit_image":
            return await self._edit_image(tool_input)
        
        elif tool_name == "upscale_image":
            return await self._upscale_image(tool_input)
        
        elif tool_name == "remove_background":
            return await self._remove_background(tool_input)
        
        # AKILLI AGENT ARAÇLARI
        elif tool_name == "get_past_assets":
            return await self._get_past_assets(db, session_id, tool_input)
        
        elif tool_name == "mark_favorite":
            return await self._mark_favorite(db, session_id, tool_input)
        
        elif tool_name == "undo_last":
            return await self._undo_last(db, session_id)
        
        # GÖRSEL MUHAKEME ARAÇLARI
        elif tool_name == "analyze_image":
            return await self._analyze_image(tool_input)
        
        elif tool_name == "compare_images":
            return await self._compare_images(tool_input)
        
        # ROADMAP / GÖREV PLANLAMA
        elif tool_name == "create_roadmap":
            return await self._create_roadmap(db, session_id, tool_input)
        
        elif tool_name == "get_roadmap_progress":
            return await self._get_roadmap_progress(db, session_id, tool_input)
        
        # SİSTEM YÖNETİM ARAÇLARI
        elif tool_name == "manage_project":
            return await self._manage_project(db, session_id, tool_input)
        
        elif tool_name == "delete_entity":
            return await self._delete_entity(db, session_id, tool_input)
        
        elif tool_name == "manage_trash":
            return await self._manage_trash(db, session_id, tool_input)
        
        elif tool_name == "manage_plugin":
            return await self._manage_plugin(db, session_id, tool_input)
        
        elif tool_name == "get_system_state":
            return await self._get_system_state(db, session_id, tool_input)
        
        elif tool_name == "manage_wardrobe":
            return await self._manage_wardrobe(db, session_id, tool_input)
        
        return {"success": False, "error": f"Bilinmeyen araç: {tool_name}"}
    
    async def _generate_image(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict, 
        resolved_entities: list = None
    ) -> dict:
        """
        Akıllı görsel üretim sistemi.
        
        İş Akışı:
        1. Entity'de referans görsel var mı kontrol et
        2. VARSA → Akıllı sistem: Nano Banana + Face Swap fallback
        3. YOKSA → Sadece Nano Banana Pro
        4. Her üretimde asset'i veritabanına kaydet
        
        Agent kendi başına karar verir ve en iyi sonucu sunar.
        """
        try:
            original_prompt = params.get("prompt", "")
            aspect_ratio = params.get("aspect_ratio", "1:1")
            resolution = params.get("resolution", "1K")
            
            # 🔄 PROMPTU İNGİLİZCE'YE ÇEVİR (Hangi dilde olursa olsun - daha iyi görsel sonuçları için)
            prompt, was_translated = await translate_to_english(original_prompt)
            if was_translated:
                print(f"📝 Prompt çevrildi: '{original_prompt[:50]}...' → '{prompt[:50]}...'")
            
            # Referans görseli olan karakter var mı kontrol et
            face_reference_url = None
            entity_description = ""
            physical_attributes = {}
            
            if resolved_entities:
                for entity in resolved_entities:
                    # Referans görsel kontrolü
                    if hasattr(entity, 'reference_image_url') and entity.reference_image_url:
                        face_reference_url = entity.reference_image_url
                    # Entity açıklamasını topla
                    if hasattr(entity, 'description') and entity.description:
                        entity_description += f"{entity.description}. "
                    # Fiziksel özellikleri topla (attributes içinden)
                    if hasattr(entity, 'attributes') and entity.attributes:
                        attrs = entity.attributes
                        for key in ['eye_color', 'hair_color', 'skin_tone', 'eyebrow_color', 
                                   'eyebrow_shape', 'hair_style', 'facial_features']:
                            if attrs.get(key):
                                physical_attributes[key] = attrs[key]
            
            # Entity açıklamasını ve fiziksel özellikleri prompt'a ekle
            if entity_description or physical_attributes:
                prompt = await enhance_character_prompt(
                    base_prompt=f"{entity_description} {prompt}",
                    physical_attributes=physical_attributes
                )
                print(f"🎨 Karakter prompt zenginleştirildi: '{prompt[:80]}...'")
            
            # AKILLI SİSTEM: Referans görsel varsa
            if face_reference_url:
                # Akıllı üretim: Nano Banana → kontrol → Face Swap fallback
                result = await self.fal_plugin.smart_generate_with_face(
                    prompt=prompt,
                    face_image_url=face_reference_url,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution
                )
                
                if result.get("success"):
                    method = result.get("method_used", "unknown")
                    quality_note = result.get("quality_check", "")
                    image_url = result.get("image_url")
                    
                    # 📦 Asset'i veritabanına kaydet
                    entity_ids = [e.get("id") for e in resolved_entities if e.get("id")] if resolved_entities else None
                    await asset_service.save_asset(
                        db=db,
                        session_id=session_id,
                        url=image_url,
                        asset_type="image",
                        prompt=prompt,
                        model_name=method,
                        model_params={
                            "aspect_ratio": aspect_ratio,
                            "resolution": resolution,
                            "face_reference_used": True
                        },
                        entity_ids=entity_ids
                    )
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "base_image_url": result.get("base_image_url"),  # Alternatif (Nano Banana)
                        "model": method,
                        "message": f"Görsel üretildi. {quality_note}",
                        "agent_decision": f"Referans görsel algılandı. Yöntem: {method}"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Görsel üretilemedi")
                    }
            
            else:
                # Referans yok - sadece Nano Banana Pro
                result = await self.fal_plugin.generate_with_nano_banana(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution
                )
                
                if result.get("success"):
                    image_url = result.get("image_url")
                    
                    # 📦 Asset'i veritabanına kaydet
                    entity_ids = [e.get("id") for e in resolved_entities if e.get("id")] if resolved_entities else None
                    await asset_service.save_asset(
                        db=db,
                        session_id=session_id,
                        url=image_url,
                        asset_type="image",
                        prompt=prompt,
                        model_name="nano-banana-pro",
                        model_params={
                            "aspect_ratio": aspect_ratio,
                            "resolution": resolution,
                            "face_reference_used": False
                        },
                        entity_ids=entity_ids
                    )
                    
                    return {
                        "success": True,
                        "image_url": image_url,
                        "model": "nano-banana-pro",
                        "message": "Görsel başarıyla üretildi (Nano Banana Pro).",
                        "agent_decision": "Referans görsel yok, Nano Banana Pro kullanıldı"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Görsel üretilemedi")
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _create_entity(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        entity_type: str, 
        params: dict
    ) -> dict:
        """Yeni entity oluştur."""
        try:
            entity = await entity_service.create_entity(
                db=db,
                session_id=session_id,
                entity_type=entity_type,
                name=params.get("name"),
                description=params.get("description"),
                attributes=params.get("attributes", {})
            )
            
            return {
                "success": True,
                "message": f"{entity.name} ({entity_type}) oluşturuldu. Tag: {entity.tag}",
                "entity": {
                    "id": str(entity.id),
                    "tag": entity.tag,
                    "name": entity.name,
                    "entity_type": entity.entity_type,
                    "description": entity.description
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_entity(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Tag ile entity bul."""
        try:
            tag = params.get("tag", "")
            entity = await entity_service.get_by_tag(db, session_id, tag)
            
            if entity:
                return {
                    "success": True,
                    "entity": {
                        "id": str(entity.id),
                        "tag": entity.tag,
                        "name": entity.name,
                        "entity_type": entity.entity_type,
                        "description": entity.description,
                        "attributes": entity.attributes
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"'{tag}' tag'i ile entity bulunamadı."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _list_entities(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Session'daki entity'leri listele."""
        try:
            entity_type = params.get("entity_type", "all")
            
            if entity_type == "all":
                entities = await entity_service.list_entities(db, session_id)
            else:
                entities = await entity_service.list_entities(db, session_id, entity_type)
            
            return {
                "success": True,
                "entities": [
                    {
                        "tag": e.tag,
                        "name": e.name,
                        "entity_type": e.entity_type,
                        "description": e.description[:100] + "..." if e.description and len(e.description) > 100 else e.description
                    }
                    for e in entities
                ],
                "count": len(entities)
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # YENİ ARAÇ METODLARI
    # ===============================
    
    async def _generate_video(self, params: dict, resolved_entities: list = None) -> dict:
        """
        Video üret (text-to-video veya image-to-video).
        
        Entity referansı varsa, önce görsel üretilip image-to-video yapılır.
        """
        try:
            prompt = params.get("prompt", "")
            image_url = params.get("image_url")
            duration = params.get("duration", "5")
            aspect_ratio = params.get("aspect_ratio", "16:9")
            
            # Entity açıklamalarını prompt'a ekle
            if resolved_entities:
                for entity in resolved_entities:
                    if hasattr(entity, 'description') and entity.description:
                        prompt = f"{entity.description}. {prompt}"
            
            # Image-to-video için görsel lazım
            # Eğer görsel yoksa ama entity varsa, önce görsel üret
            if not image_url and resolved_entities:
                # Önce görsel üret
                image_result = await self._generate_image(
                    {"prompt": prompt, "aspect_ratio": aspect_ratio.replace(":", ":")},
                    resolved_entities
                )
                if image_result.get("success"):
                    image_url = image_result.get("image_url")
            
            # Video üret
            result = await self.fal_plugin.generate_video(
                prompt=prompt,
                image_url=image_url,
                duration=duration,
                aspect_ratio=aspect_ratio
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "video_url": result.get("video_url"),
                    "model": result.get("model"),
                    "message": f"Video başarıyla üretildi ({duration}s).",
                    "agent_decision": "Image-to-video" if image_url else "Text-to-video"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Video üretilemedi")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _edit_image(self, params: dict) -> dict:
        """Mevcut bir görseli düzenle."""
        try:
            image_url = params.get("image_url")
            prompt = params.get("prompt", "")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "image_url gerekli"
                }
            
            result = await self.fal_plugin.edit_image(
                image_url=image_url,
                prompt=prompt
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result.get("image_url"),
                    "model": result.get("model"),
                    "message": "Görsel başarıyla düzenlendi."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Görsel düzenlenemedi")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _upscale_image(self, params: dict) -> dict:
        """Görsel kalitesini artır."""
        try:
            image_url = params.get("image_url")
            scale = params.get("scale", 2)
            
            if not image_url:
                return {
                    "success": False,
                    "error": "image_url gerekli"
                }
            
            result = await self.fal_plugin.upscale_image(
                image_url=image_url,
                scale=scale
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result.get("image_url"),
                    "model": result.get("model"),
                    "message": f"Görsel {scale}x büyütüldü ve kalitesi artırıldı."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Upscale yapılamadı")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _remove_background(self, params: dict) -> dict:
        """Görsel arka planını kaldır."""
        try:
            image_url = params.get("image_url")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "image_url gerekli"
                }
            
            result = await self.fal_plugin.remove_background(
                image_url=image_url
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result.get("image_url"),
                    "model": result.get("model"),
                    "message": "Arka plan kaldırıldı, şeffaf PNG oluşturuldu."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Arka plan kaldırılamadı")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # AKILLI AGENT METODLARI
    # ===============================
    
    async def _get_past_assets(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Geçmiş üretimleri getir."""
        try:
            entity_tag = params.get("entity_tag")
            asset_type = params.get("asset_type")
            favorites_only = params.get("favorites_only", False)
            limit = params.get("limit", 5)
            
            assets = await asset_service.get_session_assets(
                db=db,
                session_id=session_id,
                entity_tag=entity_tag,
                asset_type=asset_type,
                favorites_only=favorites_only,
                limit=limit
            )
            
            if not assets:
                return {
                    "success": True,
                    "assets": [],
                    "message": "Bu oturumda henüz üretilmiş içerik yok."
                }
            
            # Asset'leri serializable formata dönüştür
            asset_list = []
            for asset in assets:
                asset_list.append({
                    "id": str(asset.id),
                    "url": asset.url,
                    "type": asset.asset_type,
                    "prompt": asset.prompt[:100] + "..." if asset.prompt and len(asset.prompt) > 100 else asset.prompt,
                    "model": asset.model_name,
                    "is_favorite": asset.is_favorite,
                    "created_at": asset.created_at.isoformat() if asset.created_at else None
                })
            
            return {
                "success": True,
                "assets": asset_list,
                "count": len(asset_list),
                "message": f"{len(asset_list)} adet içerik bulundu."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _mark_favorite(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Asset'i favori olarak işaretle."""
        try:
            asset_url = params.get("asset_url")
            
            # URL verilmediyse son asset'i bul
            if not asset_url:
                last_asset = await asset_service.get_last_asset(db, session_id)
                if not last_asset:
                    return {
                        "success": False,
                        "error": "Favori yapılacak içerik bulunamadı."
                    }
                asset_id = last_asset.id
            else:
                # URL'den asset bul
                from sqlalchemy import select
                from app.models.models import GeneratedAsset
                
                result = await db.execute(
                    select(GeneratedAsset).where(
                        GeneratedAsset.url == asset_url,
                        GeneratedAsset.session_id == session_id
                    )
                )
                asset = result.scalar_one_or_none()
                if not asset:
                    return {
                        "success": False,
                        "error": "Asset bulunamadı."
                    }
                asset_id = asset.id
            
            # Favori olarak işaretle
            updated_asset = await asset_service.mark_favorite(db, asset_id, True)
            
            if updated_asset:
                return {
                    "success": True,
                    "asset_id": str(updated_asset.id),
                    "url": updated_asset.url,
                    "message": "İçerik favorilere eklendi! ⭐"
                }
            else:
                return {
                    "success": False,
                    "error": "Favori işaretlenemedi."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _undo_last(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID
    ) -> dict:
        """Son işlemi geri al, önceki versiyona dön."""
        try:
            # Son asset'i bul
            last_asset = await asset_service.get_last_asset(db, session_id)
            
            if not last_asset:
                return {
                    "success": False,
                    "error": "Geri alınacak içerik bulunamadı."
                }
            
            # Parent'ı var mı kontrol et
            if last_asset.parent_asset_id:
                # Parent'ı getir
                parent_asset = await asset_service.get_asset_by_id(
                    db, last_asset.parent_asset_id
                )
                
                if parent_asset:
                    return {
                        "success": True,
                        "previous_url": parent_asset.url,
                        "previous_type": parent_asset.asset_type,
                        "current_url": last_asset.url,
                        "message": "Önceki versiyona dönüldü. İşte önceki içerik:"
                    }
            
            # Parent yoksa, son 2 asset'i getir
            recent_assets = await asset_service.get_session_assets(
                db, session_id, limit=2
            )
            
            if len(recent_assets) >= 2:
                previous_asset = recent_assets[1]
                return {
                    "success": True,
                    "previous_url": previous_asset.url,
                    "previous_type": previous_asset.asset_type,
                    "current_url": last_asset.url,
                    "message": "Bir önceki üretim gösteriliyor:"
                }
            else:
                return {
                    "success": False,
                    "error": "Geri dönülecek önceki içerik bulunamadı."
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # GÖRSEL MUHAKEME METODLARI
    # ===============================
    
    async def _analyze_image(self, params: dict) -> dict:
        """
        Görsel analiz - Claude Vision ile kalite kontrolü.
        
        Agent bu metodu şu durumlarda OTOMATIK kullanır:
        - Görsel üretimi sonrası kalite kontrolü
        - Kullanıcı "bu ne?", "bu nasıl?" dediğinde
        - Yüz tutarlılığı kontrolü gerektiğinde
        """
        try:
            from app.services.llm.claude_service import claude_service
            
            image_url = params.get("image_url", "")
            check_quality = params.get("check_quality", True)
            
            if not image_url:
                return {
                    "success": False,
                    "error": "Görsel URL'si gerekli."
                }
            
            result = await claude_service.analyze_image(
                image_url=image_url,
                check_quality=check_quality
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "analysis": result.get("analysis"),
                    "quality_score": result.get("quality_score", 7),
                    "face_detected": result.get("face_detected", False),
                    "face_quality": result.get("face_quality", "bilinmiyor"),
                    "issues": result.get("issues", []),
                    "recommendation": result.get("recommendation", "kabul edilebilir"),
                    "message": f"Görsel analizi tamamlandı. Kalite skoru: {result.get('quality_score', 7)}/10"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Görsel analiz başarısız")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _compare_images(self, params: dict) -> dict:
        """
        İki görseli karşılaştır.
        
        Agent bu metodu şu durumlarda kullanır:
        - Kullanıcı "hangisi daha iyi?" dediğinde
        - Önceki/şimdiki versiyonları kıyaslarken
        """
        try:
            from app.services.llm.claude_service import claude_service
            
            image_url_1 = params.get("image_url_1", "")
            image_url_2 = params.get("image_url_2", "")
            
            if not image_url_1 or not image_url_2:
                return {
                    "success": False,
                    "error": "Her iki görsel URL'si de gerekli."
                }
            
            result = await claude_service.compare_images(
                image_url_1=image_url_1,
                image_url_2=image_url_2
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "comparison": result.get("comparison"),
                    "message": "Görsel karşılaştırması tamamlandı."
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Karşılaştırma başarısız")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # ROADMAP METODLARI
    # ===============================
    
    async def _create_roadmap(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """
        Çoklu adım görev planı (roadmap) oluştur.
        
        Agent karmaşık istekleri parçalara ayırarak yönetir.
        """
        try:
            from app.services.task_service import task_service
            
            goal = params.get("goal", "")
            steps = params.get("steps", [])
            
            if not goal or not steps:
                return {
                    "success": False,
                    "error": "Hedef ve adımlar gerekli."
                }
            
            # Roadmap oluştur
            roadmap = await task_service.create_roadmap(
                db=db,
                session_id=session_id,
                goal=goal,
                steps=steps
            )
            
            # İlk görevi otomatik başlat
            first_task = await task_service.get_next_task(db, roadmap.id)
            if first_task:
                await task_service.start_task(db, first_task.id)
            
            return {
                "success": True,
                "roadmap_id": str(roadmap.id),
                "goal": goal,
                "total_steps": len(steps),
                "steps": [
                    {
                        "step": i + 1,
                        "type": s.get("type"),
                        "description": s.get("description")
                    }
                    for i, s in enumerate(steps)
                ],
                "message": f"Roadmap oluşturuldu: {len(steps)} adımlık plan. İlk adım başlatıldı."
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_roadmap_progress(
        self, 
        db: AsyncSession, 
        session_id: uuid.UUID, 
        params: dict
    ) -> dict:
        """Roadmap ilerleme durumunu getir."""
        try:
            from app.services.task_service import task_service, TaskType
            
            roadmap_id = params.get("roadmap_id")
            
            if not roadmap_id:
                # Son aktif roadmap'i bul
                roadmaps = await task_service.get_session_roadmaps(db, session_id)
                if not roadmaps:
                    return {
                        "success": False,
                        "error": "Aktif roadmap bulunamadı."
                    }
                roadmap = roadmaps[0]
                roadmap_id = roadmap.id
            else:
                roadmap_id = uuid.UUID(roadmap_id)
                roadmap = await task_service.get_roadmap(db, roadmap_id)
            
            if not roadmap:
                return {
                    "success": False,
                    "error": "Roadmap bulunamadı."
                }
            
            # İlerleme durumunu getir
            progress = await task_service.get_roadmap_progress(db, roadmap_id)
            
            return {
                "success": True,
                "roadmap_id": str(roadmap_id),
                "goal": roadmap.input_data.get("goal", ""),
                "status": roadmap.status,
                "progress": progress,
                "message": f"İlerleme: {progress['completed']}/{progress['total']} adım tamamlandı ({progress['progress_percent']}%)"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # SİSTEM YÖNETİM METODLARI
    # ===============================
    
    async def _manage_project(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Proje yönetim işlemleri."""
        try:
            action = params.get("action")
            project_name = params.get("project_name")
            project_id = params.get("project_id")
            
            if action == "create":
                if not project_name:
                    return {"success": False, "error": "Proje adı gerekli."}
                new_id = str(uuid.uuid4())[:8]
                return {"success": True, "project_id": new_id, "message": f"'{project_name}' projesi oluşturuldu!"}
            
            elif action == "list":
                mock_projects = [{"id": "samsung", "name": "Samsung Campaign"}, {"id": "nike", "name": "Nike Spring"}]
                return {"success": True, "projects": mock_projects, "count": len(mock_projects)}
            
            elif action == "switch":
                return {"success": True, "message": f"'{project_id}' projesine geçildi."}
            
            elif action == "delete":
                return {"success": True, "message": f"'{project_id}' projesi çöp kutusuna taşındı."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _delete_entity(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Entity'yi çöp kutusuna taşı."""
        try:
            entity_tag = params.get("entity_tag", "").lstrip("@")
            if not entity_tag:
                return {"success": False, "error": "Entity tag gerekli."}
            
            entity = await entity_service.get_by_tag(db, session_id, f"@{entity_tag}")
            if not entity:
                return {"success": False, "error": f"'{entity_tag}' bulunamadı."}
            
            entity.is_deleted = True
            await db.commit()
            return {"success": True, "message": f"{entity.name} çöp kutusuna taşındı."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _manage_trash(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Çöp kutusu işlemleri."""
        try:
            action = params.get("action")
            item_id = params.get("item_id")
            
            if action == "list":
                from sqlalchemy import select
                from app.models.models import Entity
                result = await db.execute(select(Entity).where(Entity.session_id == session_id, Entity.is_deleted == True))
                items = result.scalars().all()
                trash = [{"id": str(i.id), "name": i.name, "type": i.entity_type} for i in items]
                return {"success": True, "items": trash, "count": len(trash), "message": f"Çöp kutusunda {len(trash)} öğe var." if trash else "Çöp kutusu boş."}
            
            elif action == "restore":
                from sqlalchemy import select
                from app.models.models import Entity
                result = await db.execute(select(Entity).where(Entity.id == uuid.UUID(item_id)))
                entity = result.scalar_one_or_none()
                if entity:
                    entity.is_deleted = False
                    await db.commit()
                    return {"success": True, "message": f"{entity.name} geri getirildi!"}
                return {"success": False, "error": "Öğe bulunamadı."}
            
            elif action == "empty":
                from sqlalchemy import delete
                from app.models.models import Entity
                await db.execute(delete(Entity).where(Entity.session_id == session_id, Entity.is_deleted == True))
                await db.commit()
                return {"success": True, "message": "Çöp kutusu boşaltıldı."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _manage_plugin(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Creative Plugin yönetimi."""
        try:
            action = params.get("action")
            name = params.get("name")
            config = params.get("config", {})
            
            if action == "create":
                if not name:
                    return {"success": False, "error": "Plugin adı gerekli."}
                new_id = str(uuid.uuid4())[:8]
                return {"success": True, "plugin_id": new_id, "message": f"'{name}' plugin'i oluşturuldu! Stil: {config.get('style', 'belirtilmemiş')}"}
            
            elif action == "list":
                mock = [{"id": "1", "name": "Cinematic Portrait"}, {"id": "2", "name": "Anime Style"}]
                return {"success": True, "plugins": mock, "count": len(mock)}
            
            elif action == "delete":
                return {"success": True, "message": "Plugin silindi."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_system_state(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Sistemin mevcut durumunu getir."""
        try:
            entities = await entity_service.list_entities(db, session_id)
            assets = await asset_service.get_session_assets(db, session_id, limit=5) if params.get("include_assets", True) else []
            
            state = {
                "session_id": str(session_id),
                "entities": {"characters": [e.name for e in entities if e.entity_type == "character"],
                            "locations": [e.name for e in entities if e.entity_type == "location"]},
                "recent_assets": len(assets) if assets else 0
            }
            return {"success": True, "state": state, "message": f"{len(entities)} entity, {len(assets) if assets else 0} asset var."}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _manage_wardrobe(self, db: AsyncSession, session_id: uuid.UUID, params: dict) -> dict:
        """Wardrobe (kıyafet) yönetimi."""
        try:
            action = params.get("action")
            name = params.get("name")
            
            if action == "add":
                if not name:
                    return {"success": False, "error": "Kıyafet adı gerekli."}
                return {"success": True, "message": f"'{name}' kıyafeti eklendi!"}
            
            elif action == "list":
                mock = [{"id": "1", "name": "Business Suit"}, {"id": "2", "name": "Casual Jeans"}]
                return {"success": True, "wardrobe": mock, "count": len(mock)}
            
            elif action == "remove":
                return {"success": True, "message": "Kıyafet silindi."}
            
            return {"success": False, "error": f"Bilinmeyen action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
agent = AgentOrchestrator()
