"""
Video Editor Service — Phase 23: Real-time Interactive Video Editing

FFmpeg-tabanlı video düzenleme işlemleri:
- Trim (kırpma): Videonun belirli bir bölümünü kes
- Speed (hız): Slow motion veya fast forward
- Fade: Fade-in / fade-out geçişleri
- Text Overlay: Videoya yazı ekleme
- Concat: Birden fazla videoyu birleştirme
- Reverse: Videoyu ters çevir
- Resize: Boyut/aspect ratio dönüştürme
- Loop: Videoyu tekrarla
- Filters: Renk, parlaklık, kontrast ayarları

Tüm işlemler fal.ai FFmpeg API veya lokal FFmpeg ile yapılır.
Sonuçlar fal.ai storage'a yüklenir.
"""
import os
import uuid
import tempfile
import asyncio
import httpx
from typing import Optional, Dict, Any, List


class VideoEditorService:
    """FFmpeg tabanlı video düzenleme servisi."""

    # ── helpers ──────────────────────────────────────────────
    @staticmethod
    async def _download_file(url: str, suffix: str = ".mp4") -> str:
        """URL'den dosya indir, geçici dosya yolu döndür."""
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(resp.content)
            tmp.close()
            return tmp.name

    @staticmethod
    async def _upload_to_fal(path: str) -> str:
        """Dosyayı fal.ai storage'a yükle, URL döndür."""
        import fal_client
        url = await fal_client.upload_file_async(path)
        return url

    @staticmethod
    async def _run_ffmpeg(args: list[str], label: str = "ffmpeg") -> str:
        """FFmpeg çalıştır, çıktı dosya yolunu döndür."""
        print(f"   🔧 {label}: {' '.join(args[:10])}...")
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            err_text = stderr.decode()[:500] if stderr else "unknown"
            raise RuntimeError(f"FFmpeg hatası: {err_text}")
        return args[-1]  # convention: son arg = çıktı dosyası

    # ── TRIM ─────────────────────────────────────────────────
    async def trim(
        self,
        video_url: str,
        start_time: float = 0,
        end_time: Optional[float] = None,
        duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Videoyu belirli zaman aralığında kes.
        start_time / end_time saniye cinsindendir.
        """
        try:
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            cmd = ["ffmpeg", "-y", "-i", src, "-ss", str(start_time)]
            if end_time is not None:
                cmd += ["-to", str(end_time)]
            elif duration is not None:
                cmd += ["-t", str(duration)]
            cmd += ["-c:v", "libx264", "-c:a", "aac", "-preset", "fast", out]

            await self._run_ffmpeg(cmd, "trim")
            url = await self._upload_to_fal(out)

            # Temizlik
            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {"success": True, "video_url": url, "operation": "trim", "message": f"Video kırpıldı ({start_time}s → {end_time or 'end'}s)."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── SPEED ────────────────────────────────────────────────
    async def change_speed(
        self,
        video_url: str,
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Video hızını değiştir.
        speed < 1 = slow motion,  speed > 1 = fast forward
        """
        try:
            speed = max(0.25, min(4.0, speed))
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            # Video PTS = 1/speed,  Audio tempo = speed
            video_filter = f"setpts={1/speed}*PTS"
            audio_filter = f"atempo={speed}" if 0.5 <= speed <= 2.0 else f"atempo={min(2.0, max(0.5, speed))}"

            cmd = [
                "ffmpeg", "-y", "-i", src,
                "-filter:v", video_filter,
                "-filter:a", audio_filter,
                "-preset", "fast",
                out,
            ]
            await self._run_ffmpeg(cmd, "speed")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            label = "slow motion" if speed < 1 else "hızlandırılmış"
            return {"success": True, "video_url": url, "operation": "speed", "speed": speed, "message": f"Video {speed}x {label} yapıldı."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── FADE ─────────────────────────────────────────────────
    async def add_fade(
        self,
        video_url: str,
        fade_in: float = 0,
        fade_out: float = 0,
    ) -> Dict[str, Any]:
        """Fade-in ve/veya fade-out efekti ekle (saniye)."""
        try:
            if fade_in <= 0 and fade_out <= 0:
                return {"success": False, "error": "fade_in veya fade_out > 0 olmalı."}

            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            # Toplam süreyi al
            probe = await asyncio.create_subprocess_exec(
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", src,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await probe.communicate()
            total_dur = float(stdout.decode().strip())

            vfilters = []
            afilters = []
            if fade_in > 0:
                vfilters.append(f"fade=t=in:st=0:d={fade_in}")
                afilters.append(f"afade=t=in:st=0:d={fade_in}")
            if fade_out > 0:
                start_out = max(0, total_dur - fade_out)
                vfilters.append(f"fade=t=out:st={start_out}:d={fade_out}")
                afilters.append(f"afade=t=out:st={start_out}:d={fade_out}")

            cmd = ["ffmpeg", "-y", "-i", src]
            if vfilters:
                cmd += ["-vf", ",".join(vfilters)]
            if afilters:
                cmd += ["-af", ",".join(afilters)]
            cmd += ["-preset", "fast", out]

            await self._run_ffmpeg(cmd, "fade")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            parts = []
            if fade_in > 0: parts.append(f"fade-in {fade_in}s")
            if fade_out > 0: parts.append(f"fade-out {fade_out}s")
            return {"success": True, "video_url": url, "operation": "fade", "message": f"Video'ya {' + '.join(parts)} eklendi."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── TEXT OVERLAY ─────────────────────────────────────────
    async def add_text_overlay(
        self,
        video_url: str,
        text: str,
        position: str = "bottom",
        font_size: int = 48,
        font_color: str = "white",
        bg_color: str = "black@0.5",
        start_time: float = 0,
        duration: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Videoya metin yazısı ekle."""
        try:
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            # Pozisyon mapping
            pos_map = {
                "top": "x=(w-text_w)/2:y=30",
                "center": "x=(w-text_w)/2:y=(h-text_h)/2",
                "bottom": "x=(w-text_w)/2:y=h-text_h-30",
                "top-left": "x=30:y=30",
                "top-right": "x=w-text_w-30:y=30",
                "bottom-left": "x=30:y=h-text_h-30",
                "bottom-right": "x=w-text_w-30:y=h-text_h-30",
            }
            pos = pos_map.get(position, pos_map["bottom"])

            # Özel karakterleri escape et
            safe_text = text.replace("'", "\\'").replace(":", "\\:")

            drawtext = (
                f"drawtext=text='{safe_text}':{pos}:"
                f"fontsize={font_size}:fontcolor={font_color}:"
                f"box=1:boxcolor={bg_color}:boxborderw=8"
            )

            if start_time > 0 or duration is not None:
                enable = f"enable='between(t,{start_time},{start_time + (duration or 9999)})'"
                drawtext += f":{enable}"

            cmd = ["ffmpeg", "-y", "-i", src, "-vf", drawtext, "-c:a", "copy", "-preset", "fast", out]
            await self._run_ffmpeg(cmd, "text")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {
                "success": True, "video_url": url, "operation": "text_overlay",
                "message": f"Videoya '{text[:30]}...' metni ({position}) eklendi.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── REVERSE ──────────────────────────────────────────────
    async def reverse(self, video_url: str) -> Dict[str, Any]:
        """Videoyu ters çevir (boomerang efekti)."""
        try:
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            cmd = ["ffmpeg", "-y", "-i", src, "-vf", "reverse", "-af", "areverse", "-preset", "fast", out]
            await self._run_ffmpeg(cmd, "reverse")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {"success": True, "video_url": url, "operation": "reverse", "message": "Video ters çevrildi (boomerang)."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── RESIZE / ASPECT RATIO ────────────────────────────────
    async def resize(
        self,
        video_url: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Video boyutunu değiştir veya aspect ratio dönüştür."""
        try:
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            if aspect_ratio:
                ar_map = {"16:9": "1920:1080", "9:16": "1080:1920", "1:1": "1080:1080", "4:3": "1440:1080"}
                dims = ar_map.get(aspect_ratio, "1920:1080")
                w, h = dims.split(":")
                vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
            elif width and height:
                vf = f"scale={width}:{height}"
            elif width:
                vf = f"scale={width}:-2"
            elif height:
                vf = f"scale=-2:{height}"
            else:
                return {"success": False, "error": "width, height veya aspect_ratio gerekli."}

            cmd = ["ffmpeg", "-y", "-i", src, "-vf", vf, "-c:a", "copy", "-preset", "fast", out]
            await self._run_ffmpeg(cmd, "resize")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {
                "success": True, "video_url": url, "operation": "resize",
                "message": f"Video boyutu değiştirildi ({aspect_ratio or f'{width}x{height}'}).",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── CONCAT ───────────────────────────────────────────────
    async def concat(
        self,
        video_urls: list[str],
        transition: str = "none",
    ) -> Dict[str, Any]:
        """Birden fazla videoyu birleştir."""
        try:
            if len(video_urls) < 2:
                return {"success": False, "error": "En az 2 video URL gerekli."}

            # Videoları indir
            sources = []
            for url in video_urls:
                src = await self._download_file(url)
                sources.append(src)

            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            # concat filesi oluştur
            concat_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w")
            for src in sources:
                concat_file.write(f"file '{src}'\n")
            concat_file.close()

            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_file.name,
                "-c:v", "libx264", "-c:a", "aac", "-preset", "fast",
                out,
            ]
            await self._run_ffmpeg(cmd, "concat")
            url = await self._upload_to_fal(out)

            # Temizlik
            for f in sources + [out, concat_file.name]:
                try: os.unlink(f)
                except: pass

            return {
                "success": True, "video_url": url, "operation": "concat",
                "message": f"{len(video_urls)} video birleştirildi.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── LOOP ─────────────────────────────────────────────────
    async def loop(self, video_url: str, count: int = 2) -> Dict[str, Any]:
        """Videoyu N kez tekrarla."""
        try:
            count = max(2, min(10, count))
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            cmd = [
                "ffmpeg", "-y", "-stream_loop", str(count - 1),
                "-i", src,
                "-c:v", "libx264", "-c:a", "aac", "-preset", "fast",
                out,
            ]
            await self._run_ffmpeg(cmd, "loop")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {"success": True, "video_url": url, "operation": "loop", "message": f"Video {count} kez tekrarlandı."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── FILTERS ──────────────────────────────────────────────
    async def apply_filter(
        self,
        video_url: str,
        filter_name: str = "none",
        intensity: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Videoya görsel filtre uygula.
        Filtreler: grayscale, sepia, blur, sharpen, brightness, contrast, vintage, negative
        """
        try:
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name

            filter_map = {
                "grayscale": "hue=s=0",
                "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
                "blur": f"boxblur={int(5 * intensity)}",
                "sharpen": f"unsharp=5:5:{intensity}:5:5:0",
                "brightness": f"eq=brightness={0.1 * intensity}",
                "contrast": f"eq=contrast={1.0 + 0.5 * intensity}",
                "vintage": "curves=vintage",
                "negative": "negate",
                "vignette": "vignette",
            }

            vf = filter_map.get(filter_name)
            if not vf:
                return {
                    "success": False,
                    "error": f"Bilinmeyen filtre: {filter_name}. Desteklenen: {', '.join(filter_map.keys())}",
                }

            cmd = ["ffmpeg", "-y", "-i", src, "-vf", vf, "-c:a", "copy", "-preset", "fast", out]
            await self._run_ffmpeg(cmd, f"filter:{filter_name}")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {
                "success": True, "video_url": url, "operation": "filter",
                "filter": filter_name,
                "message": f"'{filter_name}' filtresi uygulandı.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── EXTRACT FRAME ────────────────────────────────────────
    async def extract_frame(
        self,
        video_url: str,
        timestamp: float = 0,
    ) -> Dict[str, Any]:
        """Videodan belirli bir karede görsel çıkar."""
        try:
            src = await self._download_file(video_url)
            out = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

            cmd = [
                "ffmpeg", "-y", "-ss", str(timestamp),
                "-i", src, "-vframes", "1", "-q:v", "2", out,
            ]
            await self._run_ffmpeg(cmd, "extract_frame")
            url = await self._upload_to_fal(out)

            for f in (src, out):
                try: os.unlink(f)
                except: pass

            return {
                "success": True, "image_url": url, "operation": "extract_frame",
                "timestamp": timestamp,
                "message": f"Video'nun {timestamp}s anından kare çıkarıldı.",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton
video_editor = VideoEditorService()
