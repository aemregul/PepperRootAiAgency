"""
Agent Orchestrator - Agent'ın beyni.
Kullanıcı mesajını alır, LLM'e gönderir, araç çağrılarını yönetir.
"""
import json
from typing import Optional
from anthropic import Anthropic

from app.core.config import settings
from app.services.agent.tools import AGENT_TOOLS
from app.services.plugins.fal_plugin import FalPlugin


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
2. Gerekirse görsel üretmek için generate_image aracını kullan
3. Türkçe cevap ver, ama görsel prompt'larını İngilizce yaz

Görsel üretirken:
- Detaylı ve açıklayıcı prompt'lar yaz
- Kullanıcının istediği tarzı ve detayları ekle
- Prompt'u İngilizce yaz (daha iyi sonuç verir)
"""
    
    async def process_message(self, user_message: str, conversation_history: list = None) -> dict:
        """
        Kullanıcı mesajını işle ve yanıt döndür.
        
        Args:
            user_message: Kullanıcının mesajı
            conversation_history: Önceki mesajlar (opsiyonel)
        
        Returns:
            dict: {"response": str, "images": list}
        """
        if conversation_history is None:
            conversation_history = []
        
        # Mesajları hazırla
        messages = conversation_history + [
            {"role": "user", "content": user_message}
        ]
        
        # Claude'a gönder
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            tools=AGENT_TOOLS,
            messages=messages
        )
        
        # Sonucu işle
        result = {
            "response": "",
            "images": []
        }
        
        # Response'u işle
        for block in response.content:
            if block.type == "text":
                result["response"] += block.text
            
            elif block.type == "tool_use":
                # Araç çağrısı var, işle
                tool_result = await self._handle_tool_call(block.name, block.input)
                
                if tool_result.get("success") and tool_result.get("image_url"):
                    result["images"].append({
                        "url": tool_result["image_url"],
                        "prompt": block.input.get("prompt", "")
                    })
                
                # Araç sonucunu Claude'a gönder ve devam et
                messages.append({"role": "assistant", "content": response.content})
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(tool_result)
                        }
                    ]
                })
                
                # Claude'dan son yanıtı al
                final_response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    tools=AGENT_TOOLS,
                    messages=messages
                )
                
                for final_block in final_response.content:
                    if final_block.type == "text":
                        result["response"] += final_block.text
        
        return result
    
    async def _handle_tool_call(self, tool_name: str, tool_input: dict) -> dict:
        """Araç çağrısını işle."""
        
        if tool_name == "generate_image":
            return await self._generate_image(tool_input)
        
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


# Singleton instance
agent = AgentOrchestrator()
