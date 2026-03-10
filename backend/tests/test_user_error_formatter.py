import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from app.services.user_error_formatter import format_user_error_message


def test_formatter_converts_subprocess_error_to_turkish_message():
    result = format_user_error_message("Video subprocess hatası (Exit 1): stderr de boş", "video")
    assert result == "Video üretimi sırasında sistem içi bir işleme hatası oluştu. İşlem tamamlanamadı."


def test_formatter_preserves_specific_reference_frame_error():
    result = format_user_error_message(
        "Referans kare çıkarılamadığı için video düzenleme başlatılamadı.",
        "video",
    )
    assert result == "Video düzenleme başlatılamadı. Kaynak videodan referans kare alınamadı."
