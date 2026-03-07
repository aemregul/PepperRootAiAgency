import uuid

import pytest

from app.services.preferences_service import PreferencesService


@pytest.mark.asyncio
async def test_get_preferences_for_prompt_includes_learned_memory(monkeypatch):
    service = PreferencesService()

    async def fake_get_preferences(db, user_id):
        return {
            "aspect_ratio": "16:9",
            "style": "realistic",
            "image_model": "nano_banana",
            "video_model": "kling",
            "video_duration": 5,
            "auto_face_swap": True,
            "auto_upscale": False,
            "auto_translate": True,
            "language": "tr",
            "favorite_entities": ["@johny"],
            "learned": {
                "brand": ["Nike için yalnızca siyah beyaz kullan"],
                "workflow": ["Önce planı yaz, sonra üretime geç"],
                "preferred_colors": ["#111111", "#f5f5f5"],
            },
        }

    monkeypatch.setattr(service, "get_preferences", fake_get_preferences)

    prompt = await service.get_preferences_for_prompt(db=None, user_id=uuid.uuid4())

    assert "## 🧠 ÖĞRENİLMİŞ TERCİHLER VE KURALLAR" in prompt
    assert "- Marka kuralları: Nike için yalnızca siyah beyaz kullan" in prompt
    assert "- Çalışma biçimi: Önce planı yaz, sonra üretime geç" in prompt
    assert "- Tercih edilen renkler: #111111" in prompt
