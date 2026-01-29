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


class AgentOrchestrator:
    """Agent'ı yöneten ana sınıf."""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.fal_plugin = FalPlugin()
        self.model = "claude-sonnet-4-20250514"
        
        self.system_prompt = """Sen Pepper Root AI Agency'nin yaratıcı asistanısın.
Kullanıcıların görsel ve video içerik üretmesine yardımcı oluyorsun.

Görevlerin:
1. Kullanıcının ne istediğini anla
2. Karakter veya mekan oluşturması istenirse, önce create_character veya create_location aracını kullan
3. Görsel üretmek için generate_image aracını kullan
4. @tag formatında referans varsa, o entity'nin özelliklerini görsel prompt'una dahil et
5. Türkçe cevap ver, ama araç parametrelerini (description, prompt) İngilizce yaz

Entity (Karakter/Mekan) Sistemi:
- Kullanıcı "bir karakter oluştur" derse create_character kullan
- Kullanıcı "bir mekan oluştur" derse create_location kullan
- @character_xxx veya @location_xxx şeklinde referans yapılabilir
- Görsel üretirken referans verilen entity'nin description'ını prompt'a ekle

Görsel üretirken:
- Detaylı ve açıklayıcı prompt'lar yaz (İngilizce)
- Kullanıcının istediği tarzı ve detayları ekle
- Entity referansı varsa, o entity'nin özelliklerini dahil et
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
            "entities_created": []
        }
        
        # Response'u işle - tool call loop
        await self._process_response(response, messages, result, session_id, db)
        
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
                    db
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
        db: AsyncSession
    ) -> dict:
        """Araç çağrısını işle."""
        
        if tool_name == "generate_image":
            return await self._generate_image(tool_input)
        
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
        
        return {"success": False, "error": f"Bilinmeyen araç: {tool_name}"}
    
    async def _generate_image(self, params: dict) -> dict:
        """Görsel üret."""
        try:
            prompt = params.get("prompt", "")
            image_size = params.get("image_size", "square_hd")
            
            result = await self.fal_plugin.generate_image(
                prompt=prompt,
                image_size=image_size
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "image_url": result.get("image_url"),
                    "message": "Görsel başarıyla üretildi."
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


# Singleton instance
agent = AgentOrchestrator()
