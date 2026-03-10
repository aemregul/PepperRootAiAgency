import os
import uuid
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.services.agent.orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_generate_video_does_not_use_stale_session_cache_without_explicit_reference(monkeypatch):
    session_id = uuid.uuid4()
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator._session_reference_images = {
        str(session_id): {"url": "https://stale.example/ref.png", "base64": None}
    }

    captured = {}

    async def fake_generate_video(db, current_session_id, params, resolved_entities):
        captured["params"] = dict(params)
        return {"success": True}

    monkeypatch.setattr(orchestrator, "_generate_video", fake_generate_video)

    result = await orchestrator._handle_tool_call(
        tool_name="generate_video",
        tool_input={"prompt": "sahilde koşan bir kedi için 5 saniyelik video oluştur", "duration": "5"},
        session_id=session_id,
        db=None,
        user_message="sahilde koşan bir kedi için 5 saniyelik video oluştur",
    )

    assert result["success"] is True
    assert "image_url" not in captured["params"]


@pytest.mark.asyncio
async def test_generate_video_resolves_first_matching_session_image(monkeypatch):
    session_id = uuid.uuid4()
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator._session_reference_images = {
        str(session_id): {"url": "https://stale.example/ref.png", "base64": None}
    }

    assets = [
        SimpleNamespace(url="https://assets.example/river.png", prompt="nehir manzarası görseli"),
        SimpleNamespace(url="https://assets.example/car.png", prompt="stüdyo kırmızı araba görseli"),
        SimpleNamespace(url="https://assets.example/cat.png", prompt="gün batımında sahilde koşan bir kedi görseli"),
        SimpleNamespace(url="https://assets.example/cup.png", prompt="beyaz fincan ürün çekimi"),
    ]

    async def fake_get_session_assets(db, session_id, asset_type=None, limit=20, **kwargs):
        assert asset_type == "image"
        return assets

    captured = {}

    async def fake_generate_video(db, current_session_id, params, resolved_entities):
        captured["params"] = dict(params)
        return {"success": True}

    monkeypatch.setattr("app.services.agent.orchestrator.asset_service.get_session_assets", fake_get_session_assets)
    monkeypatch.setattr(orchestrator, "_generate_video", fake_generate_video)

    result = await orchestrator._handle_tool_call(
        tool_name="generate_video",
        tool_input={"prompt": "bir video oluştur", "duration": "5"},
        session_id=session_id,
        db=None,
        user_message="ilk oluşturduğumuz kedi görselini videoya çevir",
    )

    assert result["success"] is True
    assert captured["params"]["image_url"] == "https://assets.example/cat.png"


@pytest.mark.asyncio
async def test_edit_video_resolves_matching_session_video(monkeypatch):
    session_id = uuid.uuid4()
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator._session_reference_images = {}

    assets = [
        SimpleNamespace(url="https://assets.example/river-video.mp4", prompt="nehir manzarası videosu", thumbnail_url=None, model_params={}),
        SimpleNamespace(
            url="https://assets.example/cat-video.mp4",
            prompt="sahilde koşan kedi videosu",
            thumbnail_url="https://assets.example/cat-thumb.png",
            model_params={"source_image": "https://assets.example/cat-source.png"},
        ),
    ]

    async def fake_get_session_assets(db, session_id, asset_type=None, limit=20, **kwargs):
        assert asset_type == "video"
        return assets

    monkeypatch.setattr("app.services.agent.orchestrator.asset_service.get_session_assets", fake_get_session_assets)
    captured = {}

    async def fake_queue_video_edit(**kwargs):
        params = kwargs["params"]
        message = kwargs["message"]
        captured["params"] = dict(params)
        captured["message"] = message
        return {"success": True, "is_background_task": True}

    monkeypatch.setattr(orchestrator, "_queue_video_edit", fake_queue_video_edit)

    result = await orchestrator._handle_tool_call(
        tool_name="edit_video",
        tool_input={"prompt": "önceki kedi videosunu anime yap"},
        session_id=session_id,
        db=None,
        user_message="önceki kedi videosunu anime yap",
    )

    assert result["success"] is True
    assert result["is_background_task"] is True
    assert captured["params"]["video_url"] == "https://assets.example/cat-video.mp4"
    assert captured["params"]["image_url"] == "https://assets.example/cat-thumb.png"


@pytest.mark.asyncio
async def test_edit_video_reuses_stored_reference_image_when_video_url_already_present(monkeypatch):
    session_id = uuid.uuid4()
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator._session_reference_images = {}

    assets = [
        SimpleNamespace(
            url="https://assets.example/source-video.mp4",
            prompt="sahilde yürüyen kişi videosu",
            thumbnail_url="https://assets.example/source-thumb.png",
            model_params={"source_image": "https://assets.example/source-frame.png"},
        ),
    ]

    async def fake_get_session_assets(db, session_id, asset_type=None, limit=20, **kwargs):
        assert asset_type == "video"
        return assets

    monkeypatch.setattr("app.services.agent.orchestrator.asset_service.get_session_assets", fake_get_session_assets)
    captured = {}

    async def fake_queue_video_edit(**kwargs):
        captured["params"] = dict(kwargs["params"])
        return {"success": True, "is_background_task": True}

    monkeypatch.setattr(orchestrator, "_queue_video_edit", fake_queue_video_edit)

    result = await orchestrator._handle_tool_call(
        tool_name="edit_video",
        tool_input={
            "prompt": "videoyu anime stilinde tekrar yap",
            "video_url": "https://assets.example/source-video.mp4",
        },
        session_id=session_id,
        db=object(),
        user_message="videoyu anime stilinde tekrar yap",
    )

    assert result["success"] is True
    assert captured["params"]["video_url"] == "https://assets.example/source-video.mp4"
    assert captured["params"]["image_url"] == "https://assets.example/source-thumb.png"


@pytest.mark.asyncio
async def test_generate_video_reroutes_to_background_edit_for_attached_reference_video(monkeypatch):
    session_id = uuid.uuid4()
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator._session_reference_images = {}
    orchestrator.fal_plugin = SimpleNamespace(
        _extract_frame=lambda *_args, **_kwargs: None
    )

    captured = {}

    async def fake_extract_frame(video_url):
        assert video_url == "https://assets.example/current-ref.mp4"
        return {"success": True, "image_url": "https://assets.example/current-ref-frame.png"}

    orchestrator.fal_plugin = SimpleNamespace(_extract_frame=fake_extract_frame)

    async def fake_queue_video_edit(**kwargs):
        params = kwargs["params"]
        message = kwargs["message"]
        captured["params"] = dict(params)
        captured["message"] = message
        return {"success": True, "is_background_task": True}

    monkeypatch.setattr(orchestrator, "_queue_video_edit", fake_queue_video_edit)

    result = await orchestrator._handle_tool_call(
        tool_name="generate_video",
        tool_input={"prompt": "bu videoyu hareketlendir"},
        session_id=session_id,
        db=None,
        uploaded_reference_video_url="https://assets.example/current-ref.mp4",
        user_message="bu videoyu hareketlendir",
    )

    assert result["success"] is True
    assert result["is_background_task"] is True
    assert captured["params"]["video_url"] == "https://assets.example/current-ref.mp4"
    assert captured["params"]["prompt"] == "bu videoyu hareketlendir"
    assert captured["params"]["image_url"] == "https://assets.example/current-ref-frame.png"


@pytest.mark.asyncio
async def test_edit_video_does_not_queue_when_reference_frame_cannot_be_extracted(monkeypatch):
    session_id = uuid.uuid4()
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)
    orchestrator._session_reference_images = {}

    class FakeFalPlugin:
        async def _extract_frame(self, video_url):
            assert video_url == "https://assets.example/source.mp4"
            return {"success": False, "error": "ffmpeg failed"}

    orchestrator.fal_plugin = FakeFalPlugin()

    async def fail_queue_video_edit(**kwargs):
        raise AssertionError("Background queue should not start when frame extraction fails")

    monkeypatch.setattr(orchestrator, "_queue_video_edit", fail_queue_video_edit)

    result = await orchestrator._handle_tool_call(
        tool_name="edit_video",
        tool_input={"prompt": "videoyu anime yap", "video_url": "https://assets.example/source.mp4"},
        session_id=session_id,
        db=None,
        user_message="videoyu anime yap",
    )

    assert result["success"] is False
    assert "Referans kare çıkarılamadığı" in result["error"]
