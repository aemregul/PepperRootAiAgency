import os

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.services.plugins.fal_plugin_v2 import FalPluginV2


@pytest.mark.asyncio
async def test_select_video_edit_model_falls_back_to_enabled_admin_model(monkeypatch):
    plugin = FalPluginV2.__new__(FalPluginV2)

    async def fake_is_model_enabled(model_name: str) -> bool:
        enabled = {
            "kling": False,
            "veo_quality": False,
            "veo": False,
            "seedance": True,
        }
        return enabled.get(model_name, False)

    monkeypatch.setattr(plugin, "is_model_enabled", fake_is_model_enabled)

    selected = await plugin._select_video_edit_model("videoyu anime yap")

    assert selected == "seedance"


@pytest.mark.asyncio
async def test_edit_video_style_flow_uses_managed_models_only(monkeypatch):
    plugin = FalPluginV2.__new__(FalPluginV2)

    async def fake_is_model_enabled(model_name: str) -> bool:
        return model_name in {"style_transfer", "kling"}

    async def fake_extract_frame(video_url: str) -> dict:
        assert video_url == "https://assets.example/source.mp4"
        return {"success": True, "image_url": "https://assets.example/frame.png"}

    async def fake_apply_style(params: dict) -> dict:
        assert params["image_url"] == "https://assets.example/frame.png"
        assert params["style"] == "anime"
        return {
            "success": True,
            "image_url": "https://assets.example/styled-frame.png",
            "method_used": "style_transfer",
            "model": "style-transfer",
        }

    async def fake_generate_video(params: dict) -> dict:
        assert params["image_url"] == "https://assets.example/styled-frame.png"
        assert params["model"] == "kling"
        return {
            "success": True,
            "video_url": "https://assets.example/final.mp4",
            "model": "kling",
        }

    async def fail_video_to_video(*args, **kwargs):
        raise AssertionError("Legacy video-to-video yolu kullanılmamalı")

    monkeypatch.setattr(plugin, "is_model_enabled", fake_is_model_enabled)
    monkeypatch.setattr(plugin, "_extract_frame", fake_extract_frame)
    monkeypatch.setattr(plugin, "_apply_style", fake_apply_style)
    monkeypatch.setattr(plugin, "_generate_video", fake_generate_video)
    monkeypatch.setattr(plugin, "_video_to_video", fail_video_to_video)

    result = await plugin._edit_video({
        "video_url": "https://assets.example/source.mp4",
        "prompt": "önceki videoyu anime yap",
    })

    assert result["success"] is True
    assert result["video_url"] == "https://assets.example/final.mp4"
    assert result["method_used"] == "style_transfer_plus_kling"
