import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.services.agent.orchestrator import AgentOrchestrator


def test_extract_independent_image_prompts_splits_repeated_requests():
    prompts = AgentOrchestrator._extract_independent_image_prompts(
        "beyaz fonda bir kahve fincan görseli oluştur kırmızı spor araba stüdyo görseli oluştur yani 2 farklı görsel oluştur 2 çıktı olacak şekilde"
    )

    assert len(prompts) == 2
    assert "kahve" in prompts[0].lower()
    assert "araba" in prompts[1].lower()
    assert all("no grid" in prompt.lower() for prompt in prompts)


def test_extract_numbered_scene_prompts_prevents_grid_storyboard_bias():
    prompts = AgentOrchestrator._extract_numbered_scene_prompts(
        "bana bir erkeğin tüm gününü anlatan 4 farklı görsel çıktısı ver. 1. uyansın 2. araba sürsün 3. iş yapsın 4. kahve içsin"
    )

    assert len(prompts) == 4
    assert "scene 1" in prompts[0].lower()
    assert "uyansın" in prompts[0].lower()
    assert "same adult man" in prompts[0].lower()
    assert all("no grid" in prompt.lower() for prompt in prompts)
