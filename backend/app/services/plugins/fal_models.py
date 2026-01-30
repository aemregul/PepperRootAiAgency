"""
fal.ai Model Tanımları.

Tüm fal.ai modelleri, yetenekleri ve öncelikleri.
Agent bu bilgileri kullanarak en uygun modeli seçer.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ModelCategory(str, Enum):
    """Model kategorileri."""
    IMAGE_GENERATION = "image_generation"
    IMAGE_EDITING = "image_editing"
    FACE_CONSISTENCY = "face_consistency"
    VIDEO_GENERATION = "video_generation"
    UPSCALING = "upscaling"
    UTILITY = "utility"


class Priority(str, Enum):
    """Model önceliği."""
    PRIMARY = "primary"      # Ana tercih
    ALTERNATIVE = "alternative"  # Alternatif
    SPECIALIZED = "specialized"  # Özel durumlar


@dataclass
class FalModel:
    """fal.ai model tanımı."""
    name: str
    endpoint: str
    category: ModelCategory
    priority: Priority
    description: str
    best_for: list[str]
    supports_reference: bool = False
    supports_face: bool = False
    estimated_cost: float = 0.01  # USD per request


# ===============================
# GÖRSEL ÜRETİM MODELLERİ
# ===============================

IMAGE_GENERATION_MODELS = [
    FalModel(
        name="Nano Banana Pro",
        endpoint="fal-ai/nano-banana-pro",
        category=ModelCategory.IMAGE_GENERATION,
        priority=Priority.PRIMARY,
        description="Google'ın en gelişmiş görsel üretim modeli. Yüksek kalite ve yüz tutarlılığı.",
        best_for=["portrait", "realistic", "face_consistency", "high_quality"],
        supports_face=True,
        estimated_cost=0.01
    ),
    FalModel(
        name="Flux Pro Kontext",
        endpoint="fal-ai/flux-pro/kontext",
        category=ModelCategory.IMAGE_GENERATION,
        priority=Priority.ALTERNATIVE,
        description="Referans görsel ile hedefli düzenleme ve dönüşüm.",
        best_for=["reference_based", "editing", "transformation"],
        supports_reference=True,
        estimated_cost=0.02
    ),
    FalModel(
        name="Recraft V3",
        endpoint="fal-ai/recraft/v3/text-to-image",
        category=ModelCategory.IMAGE_GENERATION,
        priority=Priority.SPECIALIZED,
        description="Vektör, tipografi ve marka stili için en iyi.",
        best_for=["vector", "typography", "brand_style", "logo"],
        estimated_cost=0.01
    ),
    FalModel(
        name="Flux Schnell",
        endpoint="fal-ai/flux/schnell",
        category=ModelCategory.IMAGE_GENERATION,
        priority=Priority.SPECIALIZED,
        description="Hızlı görsel üretim için optimize edilmiş.",
        best_for=["fast", "prototype", "quick_preview"],
        estimated_cost=0.005
    ),
    FalModel(
        name="ImagineArt 1.5",
        endpoint="imagineart/imagineart-1.5-preview/text-to-image",
        category=ModelCategory.IMAGE_GENERATION,
        priority=Priority.ALTERNATIVE,
        description="Profesyonel kalite, doğru tipografi.",
        best_for=["professional", "realism", "typography"],
        estimated_cost=0.015
    ),
]


# ===============================
# GÖRSEL DÜZENLEME MODELLERİ
# ===============================

IMAGE_EDITING_MODELS = [
    FalModel(
        name="Nano Banana Edit",
        endpoint="fal-ai/nano-banana-pro/edit",
        category=ModelCategory.IMAGE_EDITING,
        priority=Priority.PRIMARY,
        description="Güçlü görsel düzenleme, Google Gemini tabanlı.",
        best_for=["general_editing", "inpainting", "transformation"],
        supports_reference=True,
        estimated_cost=0.015
    ),
    FalModel(
        name="Fibo Edit",
        endpoint="bria/fibo-edit/edit",
        category=ModelCategory.IMAGE_EDITING,
        priority=Priority.ALTERNATIVE,
        description="JSON + Mask ile hassas kontrol.",
        best_for=["precise_editing", "mask_based", "controlled"],
        supports_reference=True,
        estimated_cost=0.02
    ),
    FalModel(
        name="Seedream V4 Edit",
        endpoint="fal-ai/bytedance/seedream/v4/edit",
        category=ModelCategory.IMAGE_EDITING,
        priority=Priority.SPECIALIZED,
        description="ByteDance'ın stil dönüşüm modeli.",
        best_for=["style_transfer", "artistic"],
        estimated_cost=0.015
    ),
]


# ===============================
# YÜZ TUTARLILIĞI MODELLERİ
# ===============================

FACE_CONSISTENCY_MODELS = [
    FalModel(
        name="Face Swap",
        endpoint="fal-ai/face-swap",
        category=ModelCategory.FACE_CONSISTENCY,
        priority=Priority.PRIMARY,
        description="Yüz değiştirme, en güvenilir yüz tutarlılığı.",
        best_for=["face_swap", "identity_preservation"],
        supports_face=True,
        estimated_cost=0.02
    ),
    FalModel(
        name="Easel Advanced Face Swap",
        endpoint="fal-ai/easel/advanced-face-swap",
        category=ModelCategory.FACE_CONSISTENCY,
        priority=Priority.ALTERNATIVE,
        description="Detaylı yüz swap, daha fazla kontrol.",
        best_for=["detailed_face_swap", "multi_face"],
        supports_face=True,
        estimated_cost=0.025
    ),
    FalModel(
        name="Face Swap Video",
        endpoint="fal-ai/face-swap-video",
        category=ModelCategory.FACE_CONSISTENCY,
        priority=Priority.SPECIALIZED,
        description="Video içinde yüz değiştirme.",
        best_for=["video_face_swap"],
        supports_face=True,
        estimated_cost=0.10
    ),
]


# ===============================
# VİDEO ÜRETİM MODELLERİ
# ===============================

VIDEO_GENERATION_MODELS = [
    FalModel(
        name="Kling 2.5 Turbo Pro (Image-to-Video)",
        endpoint="fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
        category=ModelCategory.VIDEO_GENERATION,
        priority=Priority.PRIMARY,
        description="En iyi image-to-video, sinematik kalite.",
        best_for=["image_to_video", "cinematic", "professional"],
        supports_reference=True,
        estimated_cost=0.10
    ),
    FalModel(
        name="Kling 2.5 Turbo Pro (Text-to-Video)",
        endpoint="fal-ai/kling-video/v2.5-turbo/pro/text-to-video",
        category=ModelCategory.VIDEO_GENERATION,
        priority=Priority.PRIMARY,
        description="Metinden video üretimi, yüksek kalite.",
        best_for=["text_to_video", "animation"],
        estimated_cost=0.10
    ),
    FalModel(
        name="Veo 3.1 (Image-to-Video)",
        endpoint="fal-ai/veo3.1/image-to-video",
        category=ModelCategory.VIDEO_GENERATION,
        priority=Priority.ALTERNATIVE,
        description="Google DeepMind'ın en yeni video modeli.",
        best_for=["image_to_video", "high_fidelity"],
        supports_reference=True,
        estimated_cost=0.12
    ),
    FalModel(
        name="LTX-2 19B",
        endpoint="fal-ai/ltx-2-19b/image-to-video",
        category=ModelCategory.VIDEO_GENERATION,
        priority=Priority.SPECIALIZED,
        description="Sesli video üretimi.",
        best_for=["video_with_audio", "sound"],
        supports_reference=True,
        estimated_cost=0.08
    ),
    FalModel(
        name="PixVerse V5",
        endpoint="fal-ai/pixverse/v5/image-to-video",
        category=ModelCategory.VIDEO_GENERATION,
        priority=Priority.SPECIALIZED,
        description="Stilize video dönüşümü.",
        best_for=["stylized", "effects"],
        supports_reference=True,
        estimated_cost=0.08
    ),
]


# ===============================
# UPSCALING MODELLERİ
# ===============================

UPSCALING_MODELS = [
    FalModel(
        name="Topaz Image Upscale",
        endpoint="fal-ai/topaz/upscale/image",
        category=ModelCategory.UPSCALING,
        priority=Priority.PRIMARY,
        description="Profesyonel görsel kalite artırma.",
        best_for=["image_upscale", "detail_enhancement"],
        estimated_cost=0.05
    ),
    FalModel(
        name="Crystal Upscaler",
        endpoint="fal-ai/crystal-upscaler",
        category=ModelCategory.UPSCALING,
        priority=Priority.SPECIALIZED,
        description="Yüz detayları için özelleşmiş, 200x upscale.",
        best_for=["face_upscale", "portrait_enhancement"],
        supports_face=True,
        estimated_cost=0.06
    ),
    FalModel(
        name="Topaz Video Upscale",
        endpoint="fal-ai/topaz/upscale/video",
        category=ModelCategory.UPSCALING,
        priority=Priority.PRIMARY,
        description="Profesyonel video kalite artırma.",
        best_for=["video_upscale", "4k_conversion"],
        estimated_cost=0.15
    ),
]


# ===============================
# YARDIMCI ARAÇLAR
# ===============================

UTILITY_MODELS = [
    FalModel(
        name="Bria Background Remove",
        endpoint="fal-ai/bria/background/remove",
        category=ModelCategory.UTILITY,
        priority=Priority.PRIMARY,
        description="Görsel arka plan kaldırma.",
        best_for=["background_removal", "transparent"],
        estimated_cost=0.01
    ),
    FalModel(
        name="Video Background Remove",
        endpoint="bria/video/background-removal",
        category=ModelCategory.UTILITY,
        priority=Priority.PRIMARY,
        description="Video arka plan kaldırma.",
        best_for=["video_background_removal"],
        estimated_cost=0.08
    ),
    FalModel(
        name="NSFW Filter",
        endpoint="fal-ai/x-ailab/nsfw",
        category=ModelCategory.UTILITY,
        priority=Priority.PRIMARY,
        description="NSFW içerik tespiti.",
        best_for=["content_moderation", "safety"],
        estimated_cost=0.001
    ),
]


# ===============================
# TÜM MODELLERİ BİRLEŞTİR
# ===============================

ALL_MODELS = {
    ModelCategory.IMAGE_GENERATION: IMAGE_GENERATION_MODELS,
    ModelCategory.IMAGE_EDITING: IMAGE_EDITING_MODELS,
    ModelCategory.FACE_CONSISTENCY: FACE_CONSISTENCY_MODELS,
    ModelCategory.VIDEO_GENERATION: VIDEO_GENERATION_MODELS,
    ModelCategory.UPSCALING: UPSCALING_MODELS,
    ModelCategory.UTILITY: UTILITY_MODELS,
}


def get_models_by_category(category: ModelCategory) -> list[FalModel]:
    """Kategoriye göre modelleri getir."""
    return ALL_MODELS.get(category, [])


def get_primary_model(category: ModelCategory) -> Optional[FalModel]:
    """Kategorinin ana modelini getir."""
    models = get_models_by_category(category)
    for model in models:
        if model.priority == Priority.PRIMARY:
            return model
    return models[0] if models else None


def get_model_by_endpoint(endpoint: str) -> Optional[FalModel]:
    """Endpoint'e göre model bul."""
    for category_models in ALL_MODELS.values():
        for model in category_models:
            if model.endpoint == endpoint:
                return model
    return None


def get_face_supporting_models() -> list[FalModel]:
    """Yüz desteği olan modelleri getir."""
    result = []
    for category_models in ALL_MODELS.values():
        for model in category_models:
            if model.supports_face:
                result.append(model)
    return result
