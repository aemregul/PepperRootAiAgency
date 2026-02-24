"""
Long Video Service - 3+ Dakikalık Video Üretimi.

Video segment'leri oluşturur ve birleştirir:
1. Kullanıcı prompt'unu akıllı segment'lere böl
2. Her segment için 5-10 saniyelik video üret (FalPluginV2)
3. Segment'leri FFmpeg API ile birleştir (stitch)
4. Final video'yu döndür

Celery gerektirmez — tamamen async çalışır.
"""
import uuid
import asyncio
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VideoSegment:
    """Video segment bilgisi."""
    id: str
    order: int
    prompt: str
    duration: str  # "5" veya "10" (fal.ai string istiyor)
    status: str  # pending, generating, completed, failed
    video_url: Optional[str] = None
    reference_image_url: Optional[str] = None
    model: Optional[str] = "veo"  # Varsayılan model Veo 3.1
    error: Optional[str] = None


@dataclass
class LongVideoJob:
    """Uzun video işi."""
    id: str
    user_id: str
    session_id: str
    total_duration: int  # hedef süre (saniye)
    aspect_ratio: str
    segments: List[VideoSegment] = field(default_factory=list)
    status: str = "pending"  # pending, processing, stitching, completed, failed
    progress: int = 0  # 0-100
    final_video_url: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class LongVideoService:
    """
    Uzun video üretim servisi.
    
    3+ dakikalık videolar için:
    1. Prompt'u sinematik sahnelere böl
    2. Her sahneyi paralel üret (FalPluginV2)
    3. fal.ai FFmpeg API ile birleştir
    """
    
    MAX_SEGMENT_DURATION = 10  # Saniye (API max 10s)
    MIN_SEGMENT_DURATION = 5   # Saniye
    MAX_PARALLEL = 1           # Sıralı üretim (karakter tutarlılığı için zincirleme i2v)
    MAX_RETRIES = 2            # Max retry per segment üretimi
    CROSSFADE_DURATION = 0.5   # Sahne geçiş süresi (saniye)
    
    def __init__(self):
        self.jobs: dict[str, LongVideoJob] = {}
    
    def _create_segments(
        self, 
        base_prompt: str, 
        total_duration: int,
        scene_descriptions: Optional[List[Any]] = None
    ) -> List[VideoSegment]:
        """
        Prompt'u segment'lere böl.
        
        Eğer scene_descriptions verilmişse onları kullanır,
        yoksa otomatik sinematik çeşitlilik ekler.
        """
        segments = []
        remaining_duration = total_duration
        order = 0
        
        if scene_descriptions:
            # Kullanıcı kendi sahne listesini verdi
            segment_duration = max(
                self.MIN_SEGMENT_DURATION,
                min(self.MAX_SEGMENT_DURATION, total_duration // len(scene_descriptions))
            )
            for desc in scene_descriptions:
                if remaining_duration <= 0:
                    break
                
                if isinstance(desc, dict):
                    prompt_txt = desc.get("prompt", str(desc))
                    ref_img = desc.get("reference_image_url")
                    model_val = desc.get("model", "veo")
                else:
                    prompt_txt = str(desc)
                    ref_img = None
                    model_val = "veo"
                    
                dur = min(segment_duration, remaining_duration)
                # API sadece 5 veya 10 kabul ediyor — en yakına snap
                if dur <= 7:
                    dur = 5
                else:
                    dur = 10
                segments.append(VideoSegment(
                    id=str(uuid.uuid4()),
                    order=order,
                    prompt=prompt_txt,
                    duration=str(dur),
                    status="pending",
                    reference_image_url=ref_img,
                    model=model_val
                ))
                remaining_duration -= dur
                order += 1
        else:
            # Otomatik sinematik çeşitlendirme
            variations = [
                "establishing wide shot, cinematic opening",
                "medium shot, focusing on key details",
                "close-up shot, dramatic lighting and emotion",
                "dynamic tracking shot, smooth camera movement",
                "slow motion capture, atmospheric and cinematic",
                "aerial perspective, sweeping wide view",
                "intimate handheld shot, shallow depth of field",
                "dramatic reveal shot, building tension",
                "action sequence, dynamic and energetic",
                "closing shot, reflective and contemplative",
            ]
            
            while remaining_duration > 0:
                dur = min(self.MAX_SEGMENT_DURATION, remaining_duration)
                # API sadece 5 veya 10 kabul ediyor
                if dur <= 7:
                    dur = 5
                elif dur > 7:
                    dur = 10
                if dur < self.MIN_SEGMENT_DURATION and remaining_duration > self.MIN_SEGMENT_DURATION:
                    dur = 5
                elif dur < self.MIN_SEGMENT_DURATION:
                    # Çok kısa kaldı — son segment'e ekle
                    if segments:
                        # Son segment'i uzat (max 10)
                        last = segments[-1]
                        new_dur = min(self.MAX_SEGMENT_DURATION, int(last.duration) + dur)
                        last.duration = str(new_dur)
                    break
                
                variation = variations[order % len(variations)]
                segment_prompt = f"{base_prompt}, {variation}"
                
                segments.append(VideoSegment(
                    id=str(uuid.uuid4()),
                    order=order,
                    prompt=segment_prompt,
                    duration=str(dur),
                    status="pending"
                ))
                remaining_duration -= dur
                order += 1
        
        return segments
    
    async def create_and_process(
        self,
        user_id: str,
        session_id: str,
        prompt: str,
        total_duration: int = 60,
        aspect_ratio: str = "16:9",
        scene_descriptions: Optional[List[Any]] = None,
        progress_callback=None
    ) -> dict:
        """
        Uzun video oluştur ve işle (async, Celery gerektirmez).
        
        Args:
            user_id: Kullanıcı ID
            session_id: Session ID
            prompt: Ana prompt
            total_duration: Hedef süre (saniye), max 180
            aspect_ratio: Video oranı
            scene_descriptions: Opsiyonel sahne açıklamaları
            progress_callback: İlerleme bildirimi (async callable)
        
        Returns:
            {"success": bool, "video_url": str, "duration": int, "segments": int}
        """
        # Süre sınırı
        total_duration = min(total_duration, 180)  # Max 3 dakika
        
        job_id = str(uuid.uuid4())
        segments = self._create_segments(prompt, total_duration, scene_descriptions)
        
        job = LongVideoJob(
            id=job_id,
            user_id=user_id,
            session_id=session_id,
            total_duration=total_duration,
            aspect_ratio=aspect_ratio,
            segments=segments,
        )
        self.jobs[job_id] = job
        
        print(f"🎬 Uzun video işi başlatıldı: {job_id} ({len(segments)} segment, {total_duration}s)")
        
        try:
            # 0. Roadmap göster (planı kullanıcıya bildir)
            if progress_callback:
                roadmap_text = f"🗺️ Video Planı ({len(segments)} sahne, {total_duration}s):\n"
                for s in segments:
                    model_icon = "🌟" if s.model == "veo" else "🎬"
                    roadmap_text += f"  {model_icon} Sahne {s.order + 1}: {s.prompt[:60]}... ({s.duration}s, {s.model})\n"
                await progress_callback(5, roadmap_text)
            
            # 1. Segment'leri paralel üret
            job.status = "processing"
            await self._generate_segments(job, progress_callback)
            
            # Kaç segment başarılı?
            completed = [s for s in job.segments if s.status == "completed"]
            if not completed:
                job.status = "failed"
                return {"success": False, "error": "Hiçbir video segmenti üretilemedi."}
            
            if len(completed) == 1:
                # Tek segment — birleştirmeye gerek yok
                job.status = "completed"
                job.progress = 100
                job.final_video_url = completed[0].video_url
                return {
                    "success": True,
                    "video_url": completed[0].video_url,
                    "duration": int(completed[0].duration),
                    "segments": 1,
                    "note": f"{len(job.segments) - 1} segment başarısız oldu." if len(job.segments) > 1 else None
                }
            
            # 2. Segment'leri birleştir
            job.status = "stitching"
            job.progress = 85
            if progress_callback:
                await progress_callback(85, "Segment'ler birleştiriliyor...")
            
            final_url = await self._stitch_segments(job)
            
            job.status = "completed"
            job.progress = 100
            job.final_video_url = final_url
            
            return {
                "success": True,
                "video_url": final_url,
                "duration": sum(int(s.duration) for s in completed),
                "segments": len(completed),
                "failed_segments": len(job.segments) - len(completed)
            }
            
        except Exception as e:
            job.status = "failed"
            print(f"❌ Uzun video hatası: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_segments(self, job: LongVideoJob, progress_callback=None):
        """Segment'leri SIRALI üret — her sahne bir öncekinin son frame'inden başlar (karakter tutarlılığı)."""
        from app.services.plugins.fal_plugin_v2 import FalPluginV2
        fal = FalPluginV2()
        
        total_segments = len(job.segments)
        last_frame_url = None  # Bir önceki sahnenin son karesi
        
        for i, segment in enumerate(job.segments):
            # Zincirleme i2v: önceki sahnenin son frame'ini referans olarak ver
            if last_frame_url and not segment.reference_image_url:
                segment.reference_image_url = last_frame_url
                print(f"   🔗 Sahne {i+1}: Önceki sahnenin son karesi referans olarak verildi (i2v)")
            
            await self._generate_single_segment(fal, segment, job.aspect_ratio)
            
            # Başarılıysa son frame'ı çıkar
            if segment.status == "completed" and segment.video_url:
                try:
                    extracted = await self._extract_last_frame(segment.video_url)
                    if extracted:
                        last_frame_url = extracted
                        print(f"   📸 Sahne {i+1} son frame çıkarıldı: {extracted[:50]}...")
                except Exception as e:
                    print(f"   ⚠️ Son frame çıkarılamadı: {e}")
            
            # Progress güncelle
            completed = sum(1 for s in job.segments if s.status == "completed")
            job.progress = int((completed / total_segments) * 80)
            
            if progress_callback:
                await progress_callback(
                    job.progress, 
                    f"Sahne {completed}/{total_segments} tamamlandı"
                )
            
            print(f"📊 Long Video Progress: {completed}/{total_segments} segment")
    
    async def _extract_last_frame(self, video_url: str) -> str:
        """Video'nun son karesini çıkar, fal storage'a yükle, URL döndür."""
        import httpx
        import tempfile
        import subprocess
        import os
        import fal_client
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_path = os.path.join(tmp_dir, "video.mp4")
            frame_path = os.path.join(tmp_dir, "last_frame.jpg")
            
            # Video indir
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                resp = await client.get(video_url)
                if resp.status_code != 200:
                    return None
                with open(video_path, "wb") as f:
                    f.write(resp.content)
            
            # Son kareyi çıkar
            cmd = [
                "ffmpeg", "-y",
                "-sseof", "-0.1",  # Son 0.1 saniye
                "-i", video_path,
                "-frames:v", "1",
                "-q:v", "2",
                frame_path
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if proc.returncode != 0 or not os.path.exists(frame_path):
                return None
            
            # fal'a yükle
            frame_url = fal_client.upload_file(frame_path)
            return frame_url
    
    async def _generate_single_segment(
        self, 
        fal: "FalPluginV2",
        segment: VideoSegment,
        aspect_ratio: str
    ):
        """Tek bir segment üret. Retry logic ile."""
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                segment.status = "generating"
                
                # Sadece veo ve kling destekleniyor
                model_to_use = segment.model or "veo"
                if model_to_use not in ("veo", "kling"):
                    model_to_use = "veo"  # Diğer modeller kaldırıldı
                duration = int(segment.duration)
                
                
                payload = {
                    "prompt": segment.prompt,
                    "duration": segment.duration,
                    "aspect_ratio": aspect_ratio,
                    "model": model_to_use,
                }
                if segment.reference_image_url:
                    payload["image_url"] = segment.reference_image_url
                    print(f"   🖼️ Sahne {segment.order + 1} referans görselli (image-to-video)")
                
                if model_to_use == "veo":
                    print(f"   🎬 Sahne {segment.order + 1} Veo ile üretiliyor (deneme {attempt+1})...")
                    from app.services.google_video_service import GoogleVideoService
                    veo_svc = GoogleVideoService()
                    result_dict = await veo_svc.generate_video(payload)
                    
                    from types import SimpleNamespace
                    if result_dict.get("success"):
                        result = SimpleNamespace(success=True, data={"video_url": result_dict.get("video_url")}, error=None)
                    else:
                        result = SimpleNamespace(success=False, data=None, error=result_dict.get("error"))
                else:
                    print(f"   🎬 Sahne {segment.order + 1} {model_to_use.upper()} ile üretiliyor (deneme {attempt+1})...")
                    result = await fal.execute("generate_video", payload)
                
                if result.success and result.data:
                    segment.video_url = result.data.get("video_url")
                    segment.status = "completed"
                    print(f"   ✅ Sahne {segment.order + 1} tamamlandı (Model: {model_to_use})")
                    return  # Başarılı, çık
                else:
                    error_msg = result.error or "Video üretilemedi"
                    print(f"   ⚠️ Sahne {segment.order + 1} başarısız (deneme {attempt+1}): {error_msg}")
                    
                    # Veo başarısız olduysa Kling'e fallback
                    if model_to_use == "veo" and attempt < self.MAX_RETRIES:
                        print(f"   🔄 Kling'e geçiliyor...")
                        segment.model = "kling"
                    elif attempt >= self.MAX_RETRIES:
                        segment.status = "failed"
                        segment.error = error_msg
                        
            except Exception as e:
                print(f"   ❌ Sahne {segment.order + 1} hata (deneme {attempt+1}): {e}")
                if attempt >= self.MAX_RETRIES:
                    segment.status = "failed"
                    segment.error = str(e)
                else:
                    # Retry ile Kling'e fallback
                    segment.model = "kling"
                    await asyncio.sleep(2)  # Kısa bekleme
    
    async def _stitch_segments(self, job: LongVideoJob) -> str:
        """
        Segment'leri LOKAL FFmpeg ile birleştir + crossfade geçiş ekle.
        
        1. Completed segment'leri indir
        2. Crossfade (xfade) geçişle birleştir
        3. fal.ai storage'a yükle
        """
        import fal_client
        import httpx
        import tempfile
        import subprocess
        import os
        
        completed = sorted(
            [s for s in job.segments if s.status == "completed"],
            key=lambda s: s.order
        )
        
        if len(completed) < 2:
            return completed[0].video_url
        
        n = len(completed)
        
        try:
            print(f"🔧 FFmpeg stitching: {n} segment birleştiriliyor (lokal + crossfade)...")
            
            with tempfile.TemporaryDirectory() as tmp_dir:
                # 1. Tüm segment'leri indir
                segment_paths = []
                async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                    for i, seg in enumerate(completed):
                        seg_path = os.path.join(tmp_dir, f"segment_{i}.mp4")
                        print(f"   ⬇️ Segment {i+1}/{n} indiriliyor...")
                        resp = await client.get(seg.video_url)
                        if resp.status_code != 200:
                            print(f"   ⚠️ Segment {i+1} indirilemedi, atlanıyor")
                            continue
                        with open(seg_path, "wb") as f:
                            f.write(resp.content)
                        segment_paths.append(seg_path)
                
                if len(segment_paths) < 2:
                    print("⚠️ Yeterli segment indirilemedi")
                    return completed[0].video_url
                
                output_path = os.path.join(tmp_dir, "output.mp4")
                fade_dur = self.CROSSFADE_DURATION
                
                # 2. Crossfade ile birleştir (xfade filter)
                if len(segment_paths) == 2:
                    # 2 segment: basit xfade
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", segment_paths[0],
                        "-i", segment_paths[1],
                        "-filter_complex",
                        f"[0:v][1:v]xfade=transition=fade:duration={fade_dur}:offset=4.5[outv]",
                        "-map", "[outv]",
                        "-c:v", "libx264", "-preset", "fast",
                        "-crf", "23", "-maxrate", "4M", "-bufsize", "8M",
                        "-movflags", "+faststart",
                        "-an",
                        output_path
                    ]
                else:
                    # 3+ segment: zincirleme xfade
                    inputs = []
                    for p in segment_paths:
                        inputs.extend(["-i", p])
                    
                    # Her segment ~5s durations için offset hesapla
                    # Get durations with ffprobe
                    durations = []
                    for p in segment_paths:
                        probe_cmd = [
                            "ffprobe", "-v", "error",
                            "-show_entries", "format=duration",
                            "-of", "csv=p=0", p
                        ]
                        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
                        try:
                            dur = float(probe_result.stdout.strip())
                        except:
                            dur = 5.0
                        durations.append(dur)
                    
                    # Build xfade filter chain
                    filter_parts = []
                    current_offset = durations[0] - fade_dur
                    
                    # First pair
                    filter_parts.append(
                        f"[0:v][1:v]xfade=transition=fade:duration={fade_dur}:offset={current_offset}[v1]"
                    )
                    
                    for i in range(2, len(segment_paths)):
                        current_offset += durations[i-1] - fade_dur
                        prev_label = f"v{i-1}"
                        out_label = f"v{i}" if i < len(segment_paths) - 1 else "outv"
                        filter_parts.append(
                            f"[{prev_label}][{i}:v]xfade=transition=fade:duration={fade_dur}:offset={current_offset}[{out_label}]"
                        )
                    
                    filter_complex = ";".join(filter_parts)
                    
                    cmd = inputs + [
                        "-filter_complex", filter_complex,
                        "-map", "[outv]",
                        "-c:v", "libx264", "-preset", "fast",
                        "-crf", "23", "-maxrate", "4M", "-bufsize", "8M",
                        "-movflags", "+faststart",
                        "-an",
                        output_path
                    ]
                    cmd = ["ffmpeg", "-y"] + cmd
                
                print(f"   🔧 FFmpeg crossfade birleştirme çalıştırılıyor...")
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if proc.returncode != 0:
                    # Crossfade başarısız — basit concat dene
                    print(f"   ⚠️ Crossfade başarısız, basit concat deneniyor...")
                    print(f"   FFmpeg stderr: {proc.stderr[:300]}")
                    
                    concat_file = os.path.join(tmp_dir, "concat.txt")
                    with open(concat_file, "w") as f:
                        for path in segment_paths:
                            f.write(f"file '{path}'\n")
                    
                    cmd_fallback = [
                        "ffmpeg", "-y",
                        "-f", "concat", "-safe", "0",
                        "-i", concat_file,
                        "-c:v", "libx264", "-preset", "fast",
                        "-crf", "23", "-maxrate", "4M", "-bufsize", "8M",
                        "-c:a", "aac",
                        "-movflags", "+faststart",
                        output_path
                    ]
                    proc = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=300)
                    
                    if proc.returncode != 0:
                        print(f"   ❌ Concat de başarısız: {proc.stderr[:200]}")
                        return completed[0].video_url
                
                if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                    print("   ❌ Çıktı dosyası oluşturulamadı")
                    return completed[0].video_url
                
                print(f"   ✅ Birleştirme tamamlandı: {os.path.getsize(output_path)} bytes")
                
                # 3. fal storage'a yükle
                print("   ⬆️ fal.ai storage'a yükleniyor...")
                final_url = fal_client.upload_file(output_path)
                print(f"   ✅ Yüklendi: {final_url[:60]}...")
                
                return final_url
            
        except Exception as e:
            print(f"❌ FFmpeg stitch hatası: {e}")
            import traceback
            traceback.print_exc()
            print("⚠️ Fallback: İlk segment döndürülüyor")
            return completed[0].video_url
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Job durumunu al."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "id": job.id,
            "status": job.status,
            "progress": job.progress,
            "total_duration": job.total_duration,
            "segments": [
                {
                    "order": s.order,
                    "status": s.status,
                    "duration": s.duration
                }
                for s in job.segments
            ],
            "final_video_url": job.final_video_url,
            "created_at": job.created_at.isoformat()
        }


# Singleton instance
long_video_service = LongVideoService()
