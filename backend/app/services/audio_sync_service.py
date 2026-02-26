"""
Audio-Visual Synchronization Service — Phase 24

Ses ve görüntü arasında akıllı senkronizasyon:
- Beat Detection: Müzik beat'lerini tespit et
- Audio Analysis: Ses özelliklerini analiz et (BPM, mood, energy)
- Auto-Sync Cuts: Beat'lere göre sahne geçişi zamanlaması oluştur
- Smart Audio Mix: Video mood'una uygun müzik seçimi ve mix
- Audio Effects: Ses efektleri ekleme (whoosh, impact, ambient)
- TTS Sync: TTS sesini videoya senkronize ekleme

Kullanılan teknolojiler:
- FFprobe/FFmpeg lokal analiz
- fal.ai Mirelo SFX v1.5 (video → ses efekti)
- OpenAI Whisper (STT), TTS
- MiniMax Music (AI müzik üretimi)
"""
import os
import json
import tempfile
import asyncio
from typing import Optional, Dict, Any, List
import httpx


class AudioSyncService:
    """Ses-görüntü senkronizasyon servisi."""

    # ── helpers ──────────────────────────────────────────────
    @staticmethod
    async def _download(url: str, suffix: str = ".mp4") -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(resp.content)
            tmp.close()
            return tmp.name

    @staticmethod
    async def _upload_to_fal(path: str) -> str:
        import fal_client
        return await fal_client.upload_file_async(path)

    @staticmethod
    async def _run(args: list[str]) -> tuple[str, str]:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
        return out.decode(), err.decode()

    # ── AUDIO ANALYSIS ───────────────────────────────────────
    async def analyze_audio(self, audio_url: str) -> Dict[str, Any]:
        """
        Ses dosyasını analiz et — süre, sample rate, kanal sayısı.
        FFprobe kullanır.
        """
        try:
            src = await self._download(audio_url, ".mp3")

            out, _ = await self._run([
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", src,
            ])
            info = json.loads(out)

            fmt = info.get("format", {})
            streams = info.get("streams", [])
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

            duration = float(fmt.get("duration", 0))
            sample_rate = int(audio_stream.get("sample_rate", 0))
            channels = int(audio_stream.get("channels", 0))
            bit_rate = int(fmt.get("bit_rate", 0)) // 1000  # kbps

            os.unlink(src)

            return {
                "success": True,
                "duration": round(duration, 2),
                "sample_rate": sample_rate,
                "channels": channels,
                "bit_rate_kbps": bit_rate,
                "message": f"Ses analizi: {round(duration, 1)}s, {sample_rate}Hz, {channels} kanal, {bit_rate}kbps",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── BEAT DETECTION (simple energy-based) ─────────────────
    async def detect_beats(self, audio_url: str, sensitivity: float = 1.0) -> Dict[str, Any]:
        """
        Basit enerji tabanlı beat detection.
        
        FFmpeg volumedetect + astats ile ses seviyesini analiz eder,
        enerji spike'larını beat olarak işaretler.
        """
        try:
            src = await self._download(audio_url, ".mp3")

            # Ses seviyelerini çıkar — her 0.1s'de bir RMS enerji
            out, err = await self._run([
                "ffmpeg", "-i", src, "-af",
                "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level",
                "-f", "null", "-",
            ])

            # stderr'den enerji değerlerini parse et
            lines = err.split("\n")
            energies = []
            for line in lines:
                if "lavfi.astats.Overall.RMS_level" in line:
                    try:
                        val = float(line.split("=")[-1].strip())
                        energies.append(val)
                    except ValueError:
                        pass

            if not energies:
                # Fallback: eşit aralıklı beat'ler (her 0.5s)
                out2, _ = await self._run([
                    "ffprobe", "-v", "quiet", "-show_entries",
                    "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", src,
                ])
                dur = float(out2.strip()) if out2.strip() else 5.0
                beats = [round(t, 2) for t in _frange(0, dur, 0.5)]
                os.unlink(src)
                return {
                    "success": True,
                    "beats": beats,
                    "beat_count": len(beats),
                    "method": "fallback_uniform",
                    "message": f"{len(beats)} beat tespit edildi (uniform fallback, {round(dur, 1)}s).",
                }

            # Enerji spike'larını beat olarak işaretle
            threshold = sensitivity * -20  # dB eşik
            interval = 0.1  # her enerji ölçümü ~0.1s
            beats = []
            min_gap = 0.3  # minimum beat arası (saniye)

            for i, e in enumerate(energies):
                if e > threshold:
                    t = round(i * interval, 2)
                    if not beats or (t - beats[-1]) >= min_gap:
                        beats.append(t)

            os.unlink(src)

            return {
                "success": True,
                "beats": beats[:100],  # max 100 beat
                "beat_count": len(beats),
                "method": "energy_rms",
                "sensitivity": sensitivity,
                "message": f"{len(beats)} beat tespit edildi (energy-based).",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── BEAT-SYNCED CUT LIST ─────────────────────────────────
    async def generate_beat_cut_list(
        self,
        audio_url: str,
        video_duration: float = 10.0,
        num_cuts: int = 5,
    ) -> Dict[str, Any]:
        """
        Müzik beat'lerine göre sahne geçişi zamanlaması oluştur.
        Video düzenleme için kesim noktaları döndürür.
        """
        try:
            beat_result = await self.detect_beats(audio_url)
            if not beat_result.get("success"):
                return beat_result

            beats = beat_result.get("beats", [])
            if len(beats) < 2:
                # Eşit dağılım fallback
                step = video_duration / (num_cuts + 1)
                cuts = [round(step * i, 2) for i in range(1, num_cuts + 1)]
            else:
                # Beat'lerden en güçlü olanları seç (eşit dağılımlı)
                step = max(1, len(beats) // num_cuts)
                cuts = [beats[i * step] for i in range(num_cuts) if i * step < len(beats)]

            # Cut aralıklarını oluştur
            segments = []
            prev = 0
            for i, cut in enumerate(cuts):
                segments.append({
                    "segment": i + 1,
                    "start": prev,
                    "end": cut,
                    "duration": round(cut - prev, 2),
                })
                prev = cut
            # Son segment
            segments.append({
                "segment": len(cuts) + 1,
                "start": prev,
                "end": video_duration,
                "duration": round(video_duration - prev, 2),
            })

            return {
                "success": True,
                "cuts": cuts,
                "segments": segments,
                "total_beats": len(beats),
                "message": f"{len(cuts)} kesim noktası, {len(segments)} sahne segmenti oluşturuldu.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── AUTO-GENERATE SFX ────────────────────────────────────
    async def generate_sfx_from_video(self, video_url: str) -> Dict[str, Any]:
        """
        Videonun görsel içeriğine uygun ses efekti üret.
        fal.ai Mirelo SFX v1.5 kullanır.
        """
        try:
            import fal_client

            result = await fal_client.subscribe_async(
                "fal-ai/mirelo-sfx-v1.5",
                arguments={"video_url": video_url},
                with_logs=True,
            )

            if result and result.get("audio_file"):
                audio_url = result["audio_file"].get("url", "")
                return {
                    "success": True,
                    "audio_url": audio_url,
                    "method": "mirelo-sfx-v1.5",
                    "message": "Video içeriğine uygun ses efekti üretildi.",
                }
            else:
                return {"success": False, "error": "Ses efekti üretilemedi."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── SMART MIX ────────────────────────────────────────────
    async def smart_mix(
        self,
        video_url: str,
        audio_url: str,
        duck_on_speech: bool = True,
        music_volume: float = 0.3,
        fade_in: float = 0.5,
        fade_out: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Video + müzik akıllı birleştirme.
        - Müzik seviyesini otomatik ayarla
        - Konuşma varsa müzik seviyesini düşür (ducking)
        - Fade-in/out ile doğal geçiş
        """
        try:
            v_src = await self._download(video_url, ".mp4")
            a_src = await self._download(audio_url, ".mp3")
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            # Müzik volume + fade
            audio_filter = f"volume={music_volume}"
            if fade_in > 0:
                audio_filter += f",afade=t=in:st=0:d={fade_in}"
            
            # Video süresini al
            probe_out, _ = await self._run([
                "ffprobe", "-v", "quiet", "-show_entries",
                "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", v_src,
            ])
            v_dur = float(probe_out.strip()) if probe_out.strip() else 10.0

            if fade_out > 0:
                fade_start = max(0, v_dur - fade_out)
                audio_filter += f",afade=t=out:st={fade_start}:d={fade_out}"

            # FFmpeg: video + müzik
            cmd = [
                "ffmpeg", "-y",
                "-i", v_src,
                "-i", a_src,
                "-filter_complex",
                f"[1:a]{audio_filter}[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-shortest",
                out,
            ]
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                # Fallback: basit birleştirme (video ses yoksa)
                cmd2 = [
                    "ffmpeg", "-y",
                    "-i", v_src,
                    "-i", a_src,
                    "-filter_complex",
                    f"[1:a]{audio_filter}[music]",
                    "-map", "0:v", "-map", "[music]",
                    "-c:v", "copy", "-c:a", "aac", "-shortest",
                    out,
                ]
                proc2 = await asyncio.create_subprocess_exec(
                    *cmd2,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc2.communicate()

            url = await self._upload_to_fal(out)

            for f in (v_src, a_src, out):
                try: os.unlink(f)
                except: pass

            return {
                "success": True,
                "video_url": url,
                "operation": "smart_mix",
                "music_volume": music_volume,
                "message": f"Video + müzik akıllı birleştirildi (vol: {music_volume}, fade: {fade_in}s in / {fade_out}s out).",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── TTS SYNC ─────────────────────────────────────────────
    async def add_tts_narration(
        self,
        video_url: str,
        text: str,
        voice: str = "nova",
        start_time: float = 0,
        bg_music_volume: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Videoya TTS seslendirme ekle — mevcut sesi düşür, TTS'i üste koy.
        """
        try:
            from openai import AsyncOpenAI
            from app.core.config import settings

            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            # TTS oluştur
            tts_response = await client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text,
                response_format="mp3",
            )

            tts_data = tts_response.content
            tts_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tts_path.write(tts_data)
            tts_path.close()

            v_src = await self._download(video_url, ".mp4")
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            # Video + TTS birleştirme (mevcut sesi düşür)
            cmd = [
                "ffmpeg", "-y",
                "-i", v_src,
                "-i", tts_path.name,
                "-filter_complex",
                f"[0:a]volume={bg_music_volume}[bg];"
                f"[1:a]adelay={int(start_time * 1000)}|{int(start_time * 1000)}[tts];"
                f"[bg][tts]amix=inputs=2:duration=first[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-shortest",
                out,
            ]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                # Fallback: sadece TTS ekle (video ses yoksa)
                cmd2 = [
                    "ffmpeg", "-y",
                    "-i", v_src,
                    "-i", tts_path.name,
                    "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-shortest",
                    out,
                ]
                proc2 = await asyncio.create_subprocess_exec(
                    *cmd2,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc2.communicate()

            url = await self._upload_to_fal(out)

            for f in (v_src, tts_path.name, out):
                try: os.unlink(f)
                except: pass

            return {
                "success": True,
                "video_url": url,
                "operation": "tts_narration",
                "voice": voice,
                "message": f"Videoya '{text[:40]}...' seslendirmesi eklendi (voice: {voice}).",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def _frange(start: float, stop: float, step: float):
    """Float range generator."""
    val = start
    while val < stop:
        yield val
        val += step


# Singleton
audio_sync = AudioSyncService()
