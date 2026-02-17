"""
Voice & Audio Service — Sesli komut ve video'ya ses ekleme.

- Whisper API ile speech-to-text
- OpenAI TTS ile text-to-speech
- FFmpeg ile video'ya ses birleştirme
"""
import tempfile
import httpx
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from app.core.config import settings


class VoiceAudioService:
    """Ses işleme servisi."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    # ===============================
    # SPEECH-TO-TEXT (Whisper)
    # ===============================
    
    async def transcribe(
        self,
        audio_url: str,
        language: str = "tr"
    ) -> Dict[str, Any]:
        """
        Ses dosyasını metne çevir (Whisper API).
        
        Args:
            audio_url: Ses dosyası URL'si
            language: Dil kodu ('tr', 'en', 'auto')
        """
        try:
            # Ses dosyasını indir
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                audio_data = response.content
            
            # Geçici dosyaya yaz
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                temp_path = f.name
            
            # Whisper API ile transkript
            with open(temp_path, "rb") as audio_file:
                params = {"model": "whisper-1", "file": audio_file}
                if language != "auto":
                    params["language"] = language
                
                transcript = await self.client.audio.transcriptions.create(**params)
            
            print(f"🎤 Transkript: '{transcript.text[:80]}...'")
            
            return {
                "success": True,
                "text": transcript.text,
                "language": language
            }
            
        except Exception as e:
            print(f"❌ Transkript hatası: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # TEXT-TO-SPEECH (TTS)
    # ===============================
    
    async def text_to_speech(
        self,
        text: str,
        voice: str = "nova",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Metni sese çevir (OpenAI TTS).
        
        Args:
            text: Seslendirme metni
            voice: Ses tonu (alloy, echo, fable, onyx, nova, shimmer)
            speed: Hız (0.25 - 4.0)
        """
        try:
            response = await self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                speed=speed,
                response_format="mp3"
            )
            
            # Ses dosyasını kaydet ve fal.ai'ye yükle
            audio_data = response.content
            
            # fal.ai storage'a yükle
            import fal_client
            import base64
            
            audio_b64 = base64.b64encode(audio_data).decode()
            audio_url = await fal_client.upload_async(
                audio_data,
                content_type="audio/mpeg"
            )
            
            print(f"🔊 TTS oluşturuldu: voice={voice}, {len(text)} karakter")
            
            return {
                "success": True,
                "audio_url": audio_url,
                "voice": voice,
                "text_length": len(text)
            }
            
        except Exception as e:
            print(f"❌ TTS hatası: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ===============================
    # VİDEO + SES BİRLEŞTİRME
    # ===============================
    
    async def add_audio_to_video(
        self,
        video_url: str,
        audio_type: str,
        text: Optional[str] = None,
        music_style: Optional[str] = None,
        voice: str = "nova"
    ) -> Dict[str, Any]:
        """
        Video'ya ses ekle.
        
        Args:
            video_url: Video URL
            audio_type: 'tts', 'music', 'effect'
            text: TTS metni
            music_style: Müzik stili
            voice: TTS ses tonu
        """
        try:
            import fal_client
            
            if audio_type == "tts":
                if not text:
                    return {"success": False, "error": "TTS için metin gerekli"}
                
                # Sesi oluştur
                tts_result = await self.text_to_speech(text, voice)
                if not tts_result["success"]:
                    return tts_result
                
                audio_url = tts_result["audio_url"]
                
                # FFmpeg ile birleştir
                command = (
                    f"ffmpeg -i {video_url} -i {audio_url} "
                    f"-c:v copy -c:a aac -map 0:v:0 -map 1:a:0 "
                    f"-shortest output.mp4"
                )
                
                result = await fal_client.subscribe_async(
                    "fal-ai/ffmpeg-api",
                    arguments={"command": command},
                    with_logs=True,
                )
                
                if result and "outputs" in result and len(result["outputs"]) > 0:
                    final_url = result["outputs"][0]["url"]
                    return {
                        "success": True,
                        "video_url": final_url,
                        "audio_type": "tts",
                        "message": f"Video'ya seslendirme eklendi (voice: {voice})"
                    }
            
            elif audio_type == "music":
                # Müzik ekleme — şimdilik bilgi ver
                return {
                    "success": True,
                    "video_url": video_url,
                    "audio_type": "music",
                    "message": f"Müzik ekleme özelliği yakında aktif olacak. Stil: {music_style or 'ambient'}"
                }
            
            return {"success": False, "error": f"Desteklenmeyen audio_type: {audio_type}"}
            
        except Exception as e:
            print(f"❌ Video+ses birleştirme hatası: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Singleton
voice_audio_service = VoiceAudioService()
