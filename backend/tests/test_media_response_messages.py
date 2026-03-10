import json
import os
import uuid
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.services.agent.orchestrator import AgentOrchestrator


def _fake_tool_call(name: str, arguments: dict, tool_id: str = "tool_1"):
    return SimpleNamespace(
        id=tool_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


@pytest.mark.asyncio
async def test_non_stream_media_tool_uses_deterministic_message(monkeypatch):
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)

    async def fake_handle_tool_call(*args, **kwargs):
        return {
            "success": True,
            "image_url": "https://assets.example/food.png",
            "message": "Görsel başarıyla üretildi (Nano Banana Pro).",
        }

    async def fake_auto_quality_check(*args, **kwargs):
        return None

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Final LLM completion should be skipped for successful media outputs")

    orchestrator._handle_tool_call = fake_handle_tool_call
    orchestrator._auto_quality_check = fake_auto_quality_check
    orchestrator.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fail_if_called)
        )
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content="30 saniyelik sahilde koşan kedi videosunu hazırlıyorum!",
                    tool_calls=[
                        _fake_tool_call(
                            "generate_image",
                            {"prompt": "filipino akşam yemeği görseli oluştur"},
                        )
                    ],
                )
            )
        ]
    )

    result = {
        "response": "",
        "images": [],
        "videos": [],
        "entities_created": [],
        "_resolved_entities": [],
        "_current_reference_image": None,
        "_uploaded_image_url": None,
        "_uploaded_image_urls": [],
        "_user_message": "filipino akşam yemeği görseli oluştur",
    }

    await orchestrator._process_response(
        response=response,
        messages=[],
        result=result,
        session_id=uuid.uuid4(),
        db=None,
    )

    assert result["response"] == "Görsel başarıyla üretildi (Nano Banana Pro)."
    assert result["images"] == [
        {
            "url": "https://assets.example/food.png",
            "prompt": "filipino akşam yemeği görseli oluştur",
        }
    ]


@pytest.mark.asyncio
async def test_stream_media_tool_marks_final_text_without_second_llm_call():
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)

    async def fake_handle_tool_call(*args, **kwargs):
        return {
            "success": True,
            "image_url": "https://assets.example/food.png",
            "message": "Görsel başarıyla üretildi (Nano Banana Pro).",
        }

    async def fail_if_called(*args, **kwargs):
        raise AssertionError("Final streamed LLM completion should be skipped for successful media outputs")

    orchestrator._handle_tool_call = fake_handle_tool_call
    orchestrator.async_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fail_if_called)
        )
    )

    result = {
        "images": [],
        "videos": [],
        "entities_created": [],
        "_resolved_entities": [],
        "_current_reference_image": None,
        "_uploaded_image_url": None,
        "_user_message": "filipino akşam yemeği görseli oluştur",
        "_bg_generations": [],
    }
    messages = []

    await orchestrator._process_tool_calls_for_stream(
        message=SimpleNamespace(
            tool_calls=[
                _fake_tool_call(
                    "generate_image",
                    {"prompt": "filipino akşam yemeği görseli oluştur"},
                )
            ]
        ),
        messages=messages,
        result=result,
        session_id=uuid.uuid4(),
        db=None,
        system_prompt="test prompt",
    )

    assert result["_skip_final_llm"] is True
    assert result["_final_text"] == "Görsel başarıyla üretildi (Nano Banana Pro)."
    assert result["images"] == [
        {
            "url": "https://assets.example/food.png",
            "prompt": "filipino akşam yemeği görseli oluştur",
        }
    ]


@pytest.mark.asyncio
async def test_stream_background_task_preserves_tool_message():
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)

    async def fake_handle_tool_call(*args, **kwargs):
        return {
            "success": True,
            "is_background_task": True,
            "message": "🎬 Video düzenleme arka planda başladı! Hazır olduğunda otomatik bildirim gelecek.",
            "_bg_generation": {"type": "video", "prompt": "anime yap"},
        }

    orchestrator._handle_tool_call = fake_handle_tool_call

    result = {
        "images": [],
        "videos": [],
        "entities_created": [],
        "_resolved_entities": [],
        "_current_reference_image": None,
        "_uploaded_image_url": None,
        "_user_message": "önceki videoyu anime yap",
        "_bg_generations": [],
    }
    messages = []

    await orchestrator._process_tool_calls_for_stream(
        message=SimpleNamespace(
            tool_calls=[
                _fake_tool_call(
                    "edit_video",
                    {"prompt": "önceki videoyu anime yap", "video_url": "https://assets.example/video.mp4"},
                )
            ]
        ),
        messages=messages,
        result=result,
        session_id=uuid.uuid4(),
        db=None,
        system_prompt="test prompt",
    )

    assert result["is_background_task"] is True
    assert result["message"] == "🎬 Video düzenleme arka planda başladı! Hazır olduğunda otomatik bildirim gelecek."


@pytest.mark.asyncio
async def test_stream_edit_video_failure_does_not_retry_with_alternative_tool():
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)

    async def fake_handle_tool_call(*args, **kwargs):
        return {
            "success": False,
            "error": "Referans kare çıkarılamadığı için video düzenleme başlatılamadı.",
        }

    async def fail_if_called(*args, **kwargs):
        raise AssertionError("Failed edit_video should not trigger a second LLM retry")

    orchestrator._handle_tool_call = fake_handle_tool_call
    orchestrator.async_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fail_if_called)
        )
    )

    result = {
        "images": [],
        "videos": [],
        "entities_created": [],
        "_resolved_entities": [],
        "_current_reference_image": None,
        "_uploaded_image_url": None,
        "_user_message": "videoyu anime stilinde tekrar yap",
        "_bg_generations": [],
    }
    messages = []

    await orchestrator._process_tool_calls_for_stream(
        message=SimpleNamespace(
            tool_calls=[
                _fake_tool_call(
                    "edit_video",
                    {"prompt": "videoyu anime stilinde tekrar yap", "video_url": "https://assets.example/video.mp4"},
                )
            ]
        ),
        messages=messages,
        result=result,
        session_id=uuid.uuid4(),
        db=None,
        system_prompt="test prompt",
    )

    assert result["_skip_final_llm"] is True
    assert result["_final_text"] == "Hata: Referans kare çıkarılamadığı için video düzenleme başlatılamadı."


@pytest.mark.asyncio
async def test_non_stream_edit_video_failure_does_not_retry_with_alternative_tool():
    orchestrator = AgentOrchestrator.__new__(AgentOrchestrator)

    async def fake_handle_tool_call(*args, **kwargs):
        return {
            "success": False,
            "error": "Referans kare çıkarılamadığı için video düzenleme başlatılamadı.",
        }

    def fail_if_called(*args, **kwargs):
        raise AssertionError("Failed edit_video should not trigger a second LLM retry")

    orchestrator._handle_tool_call = fake_handle_tool_call
    orchestrator._auto_quality_check = lambda *args, **kwargs: None
    orchestrator.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fail_if_called)
        )
    )

    response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    content=None,
                    tool_calls=[
                        _fake_tool_call(
                            "edit_video",
                            {"prompt": "videoyu anime stilinde tekrar yap", "video_url": "https://assets.example/video.mp4"},
                        )
                    ],
                )
            )
        ]
    )

    result = {
        "response": "",
        "images": [],
        "videos": [],
        "entities_created": [],
        "_resolved_entities": [],
        "_current_reference_image": None,
        "_uploaded_image_url": None,
        "_uploaded_image_urls": [],
        "_user_message": "videoyu anime stilinde tekrar yap",
    }

    await orchestrator._process_response(
        response=response,
        messages=[],
        result=result,
        session_id=uuid.uuid4(),
        db=None,
    )

    assert result["response"] == "Hata: Referans kare çıkarılamadığı için video düzenleme başlatılamadı."
