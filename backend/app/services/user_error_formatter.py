"""
Kullanıcıya gösterilecek hata metinlerini tek yerde normalize eder.
"""
from __future__ import annotations

import re
from typing import Optional


_TASK_LABELS = {
    "video": "Video üretimi",
    "long_video": "Uzun video üretimi",
    "image": "Görsel üretimi",
    "chat": "Mesaj işleme",
    "audio": "Ses üretimi",
}


def _clean_error_text(error: Optional[str]) -> str:
    raw = (error or "").strip()
    raw = re.sub(r"^(hata|error|exception)\s*:\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw[:220]


def format_user_error_message(error: Optional[str], task_type: Optional[str] = None) -> str:
    """
    Ham teknik hatayı kullanıcıya gösterilecek Türkçe mesaja çevir.
    """
    cleaned = _clean_error_text(error)
    lower = cleaned.lower()
    task_label = _TASK_LABELS.get(task_type or "", "İşlem")

    if not cleaned:
        return f"{task_label} sırasında bir sorun oluştu. Lütfen tekrar deneyin."

    if "referans kare çıkarılamadı" in lower:
        return "Video düzenleme başlatılamadı. Kaynak videodan referans kare alınamadı."

    if "video referansı bulunamadı" in lower:
        return "Video düzenleme başlatılamadı. Düzenlenecek video bulunamadı."

    if "subprocess" in lower or "stderr de boş" in lower:
        return f"{task_label} sırasında sistem içi bir işleme hatası oluştu. İşlem tamamlanamadı."

    if "credit" in lower or "kredi" in lower or "quota" in lower:
        return f"{task_label} başlatılamadı. Bu işlem için yeterli kredi bulunmuyor."

    if "timeout" in lower or "time out" in lower or "zaman aşımı" in lower:
        return f"{task_label} zaman aşımına uğradı. Lütfen tekrar deneyin."

    if "429" in lower or "rate limit" in lower or "too many requests" in lower:
        return f"{task_label} şu anda başlatılamadı. Servis yoğun olduğu için biraz sonra tekrar dene."

    if "401" in lower or "403" in lower or "unauthorized" in lower or "forbidden" in lower:
        return f"{task_label} başlatılamadı. Servis yetkilendirmesi başarısız oldu."

    if "404" in lower or "not found" in lower or "bulunamadı" in lower:
        return cleaned[0].upper() + cleaned[1:] if cleaned else f"{task_label} için gerekli kaynak bulunamadı."

    if "boş sonuç" in lower or "empty result" in lower:
        return f"{task_label} tamamlanamadı. Servis boş sonuç döndürdü."

    if cleaned.endswith("."):
        return cleaned[0].upper() + cleaned[1:]

    return f"{task_label} sırasında bir sorun oluştu. Teknik neden: {cleaned}."
