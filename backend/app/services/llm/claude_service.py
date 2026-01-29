"""
Claude LLM Servisi - Anthropic API ile iletişim.
"""
from anthropic import AsyncAnthropic

from app.core.config import settings


class ClaudeService:
    """Claude ile sohbet servisi."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-20250514"
    
    async def chat(self, message: str, system_prompt: str = None) -> str:
        """
        Basit sohbet - mesaj gönder, yanıt al.
        
        Args:
            message: Kullanıcı mesajı
            system_prompt: Sistem talimatı (opsiyonel)
        
        Returns:
            Claude'un yanıtı
        """
        messages = [{"role": "user", "content": message}]
        
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt or "Sen yardımcı bir asistansın.",
            messages=messages
        )
        
        return response.content[0].text


# Singleton instance
claude_service = ClaudeService()