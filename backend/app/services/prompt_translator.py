"""
Prompt çeviri ve zenginleştirme servisi.
Türkçe promptları görsel üretim için optimize edilmiş İngilizce'ye çevirir.
"""
from anthropic import Anthropic
from app.core.config import settings

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)


async def translate_prompt_to_english(turkish_prompt: str, context: str = "") -> str:
    """
    Türkçe prompt'u İngilizce'ye çevirir ve görsel üretim için optimize eder.
    
    Args:
        turkish_prompt: Kullanıcının Türkçe prompt'u
        context: Ek bağlam (karakter özellikleri, lokasyon vs.)
    
    Returns:
        Optimize edilmiş İngilizce prompt
    """
    system_prompt = """You are a professional prompt translator and enhancer for AI image/video generation.

Your task:
1. Translate the Turkish prompt to English
2. Enhance it with professional photography/cinematography terms
3. Add artistic details that will improve image quality
4. Keep the core meaning and intent intact
5. Make it optimized for Flux, DALL-E, and similar AI models

Output ONLY the final English prompt, nothing else. No explanations, no "Here is the translation", just the prompt itself.

Important:
- Add lighting details (soft lighting, golden hour, studio lighting, etc.)
- Add camera/composition terms (close-up, wide shot, shallow depth of field)
- Add quality keywords (8k, highly detailed, professional photography, cinematic)
- If it's about a character, include realistic skin texture, detailed features
- Keep it concise but descriptive"""

    user_message = f"""Turkish prompt to translate and enhance:
{turkish_prompt}

{f"Additional context: {context}" if context else ""}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    return response.content[0].text.strip()


async def enhance_character_prompt(
    base_prompt: str,
    physical_attributes: dict = None
) -> str:
    """
    Karakter prompt'unu fiziksel özelliklerle zenginleştirir.
    
    Args:
        base_prompt: Temel karakter açıklaması
        physical_attributes: Fiziksel özellikler dict'i
            - eye_color: Göz rengi
            - hair_color: Saç rengi  
            - hair_style: Saç stili
            - eyebrow_color: Kaş rengi
            - eyebrow_shape: Kaş şekli
            - skin_tone: Ten rengi
            - age: Yaş
            - gender: Cinsiyet
            - facial_features: Yüz özellikleri
            - body_type: Vücut tipi
            - height: Boy
            - clothing: Kıyafet
    
    Returns:
        Zenginleştirilmiş İngilizce karakter prompt'u
    """
    if not physical_attributes:
        physical_attributes = {}
    
    # Fiziksel özellikleri prompt'a dönüştür
    attribute_parts = []
    
    attr_map = {
        "eye_color": "eyes",
        "hair_color": "hair",
        "hair_style": "hairstyle",
        "eyebrow_color": "eyebrows",
        "eyebrow_shape": "eyebrow shape",
        "skin_tone": "skin",
        "age": "age",
        "gender": "",
        "facial_features": "face",
        "body_type": "build",
        "height": "height",
        "clothing": "wearing"
    }
    
    for key, value in physical_attributes.items():
        if value and key in attr_map:
            label = attr_map[key]
            if label:
                attribute_parts.append(f"{value} {label}")
            else:
                attribute_parts.append(value)
    
    attributes_str = ", ".join(attribute_parts) if attribute_parts else ""
    
    system_prompt = """You are an expert at creating detailed character descriptions for AI image generation.

Your task:
1. Take the base description and physical attributes
2. Create a cohesive, detailed character portrait prompt
3. Add professional photography terms for best quality
4. Include realistic details (skin texture, pores, realistic lighting)
5. Make the prompt optimized for photorealistic AI image generation

Output ONLY the final English prompt. No explanations."""

    user_message = f"""Base character description:
{base_prompt}

Physical attributes: {attributes_str if attributes_str else "Not specified - use reasonable defaults"}

Create a detailed, photorealistic character portrait prompt."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=600,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    
    return response.content[0].text.strip()


# Convenience function for simple translations
async def auto_translate_if_turkish(text: str) -> tuple[str, bool]:
    """
    Metin Türkçe ise İngilizce'ye çevirir.
    
    Returns:
        (translated_text, was_translated)
    """
    # Türkçe karakterler kontrolü
    turkish_chars = set("çÇğĞıİöÖşŞüÜ")
    has_turkish = any(c in turkish_chars for c in text)
    
    # Yaygın Türkçe kelimeler kontrolü
    turkish_words = ["bir", "ve", "için", "ile", "olan", "bu", "da", "de", "oluştur", 
                     "yap", "çiz", "göster", "karakter", "sahne", "görsel", "video",
                     "mutfak", "ofis", "ev", "siyah", "beyaz", "mavi", "yeşil"]
    
    text_lower = text.lower()
    has_turkish_words = any(word in text_lower for word in turkish_words)
    
    if has_turkish or has_turkish_words:
        translated = await translate_prompt_to_english(text)
        return translated, True
    
    return text, False
