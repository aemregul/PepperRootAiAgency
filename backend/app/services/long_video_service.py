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
    
    MAX_SEGMENT_DURATION = 10  # saniye (Fal.ai limiti)
    MIN_SEGMENT_DURATION = 5
    MAX_PARALLEL = 3  # Aynı anda max segment üretimi
    
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
                else:
                    prompt_txt = str(desc)
                    ref_img = None
                    
                dur = min(segment_duration, remaining_duration)
                segments.append(VideoSegment(
                    id=str(uuid.uuid4()),
                    order=order,
                    prompt=prompt_txt,
                    duration=str(dur),
                    status="pending",
                    reference_image_url=ref_img
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
                if dur < self.MIN_SEGMENT_DURATION and remaining_duration > self.MIN_SEGMENT_DURATION:
                    dur = self.MIN_SEGMENT_DURATION
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
        """Tüm segment'leri batch halinde paralel üret."""
        from app.services.plugins.fal_plugin_v2 import FalPluginV2
        fal = FalPluginV2()
        
        total_segments = len(job.segments)
        
        for i in range(0, total_segments, self.MAX_PARALLEL):
            batch = job.segments[i:i + self.MAX_PARALLEL]
            
            tasks = [
                self._generate_single_segment(fal, segment, job.aspect_ratio)
                for segment in batch
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Progress güncelle
            completed = sum(1 for s in job.segments if s.status == "completed")
            job.progress = int((completed / total_segments) * 80)
            
            if progress_callback:
                await progress_callback(
                    job.progress, 
                    f"Segment {completed}/{total_segments} tamamlandı"
                )
            
            print(f"📊 Long Video Progress: {completed}/{total_segments} segment")
    
    async def _generate_single_segment(
        self, 
        fal: "FalPluginV2",
        segment: VideoSegment,
        aspect_ratio: str
    ):
        """Tek bir segment üret."""
        try:
            segment.status = "generating"
            
            # FalPluginV2.execute kullan
            payload = {
                "prompt": segment.prompt,
                "duration": segment.duration,
                "aspect_ratio": aspect_ratio,
            }
            if segment.reference_image_url:
                payload["image_url"] = segment.reference_image_url
                print(f"🖼️ Scene {segment.order + 1} has reference image! Switching to Image-to-Video.")
                
            result = await fal.execute("generate_video", payload)
            
            if result.success and result.data:
                segment.video_url = result.data.get("video_url")
                segment.status = "completed"
                print(f"✅ Segment {segment.order + 1} tamamlandı")
            else:
                segment.status = "failed"
                segment.error = result.error or "Video üretilemedi"
                print(f"❌ Segment {segment.order + 1} başarısız: {segment.error}")
                
        except Exception as e:
            segment.status = "failed"
            segment.error = str(e)
            print(f"❌ Segment {segment.order + 1} hata: {e}")
    
    async def _stitch_segments(self, job: LongVideoJob) -> str:
        """
        Segment'leri fal.ai FFmpeg API ile birleştir.
        
        1. Completed segment'leri sıraya koy
        2. FFmpeg concat komutu oluştur
        3. fal.ai FFmpeg API'ye gönder
        4. Final video URL'sini döndür
        """
        import fal_client
        
        completed = sorted(
            [s for s in job.segments if s.status == "completed"],
            key=lambda s: s.order
        )
        
        if len(completed) < 2:
            return completed[0].video_url
        
        # FFmpeg concat komutu oluştur
        # Input olarak tüm video URL'lerini al, concat filtresi ile birleştir
        inputs = " ".join(f"-i {s.video_url}" for s in completed)
        n = len(completed)
        
        # filter_complex ile concat filtresi
        filter_inputs = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(n))
        concat_filter = f"{filter_inputs}concat=n={n}:v=1:a=1[outv][outa]"
        
        command = (
            f"ffmpeg {inputs} "
            f'-filter_complex "{concat_filter}" '
            f'-map "[outv]" -map "[outa]" '
            f"-c:v libx264 -c:a aac -movflags +faststart "
            f"output.mp4"
        )
        
        try:
            print(f"🔧 FFmpeg stitching: {n} segment birleştiriliyor...")
            result = await fal_client.subscribe_async(
                "fal-ai/ffmpeg-api",
                arguments={"command": command},
                with_logs=True,
            )
            
            if result and "outputs" in result and len(result["outputs"]) > 0:
                final_url = result["outputs"][0]["url"]
                print(f"✅ Video birleştirildi: {final_url[:60]}...")
                return final_url
            
            # Fallback: ses olmadan dene
            print("⚠️ Audio concat başarısız, sessiz birleştirme deneniyor...")
            filter_inputs_v = "".join(f"[{i}:v:0]" for i in range(n))
            concat_filter_v = f"{filter_inputs_v}concat=n={n}:v=1:a=0[outv]"
            
            command_v = (
                f"ffmpeg {inputs} "
                f'-filter_complex "{concat_filter_v}" '
                f'-map "[outv]" '
                f"-c:v libx264 -movflags +faststart "
                f"output.mp4"
            )
            
            result = await fal_client.subscribe_async(
                "fal-ai/ffmpeg-api",
                arguments={"command": command_v},
                with_logs=True,
            )
            
            if result and "outputs" in result and len(result["outputs"]) > 0:
                final_url = result["outputs"][0]["url"]
                print(f"✅ Video birleştirildi (sessiz): {final_url[:60]}...")
                return final_url
            
            raise RuntimeError("FFmpeg birleştirme başarısız")
            
        except Exception as e:
            print(f"❌ FFmpeg stitch hatası: {e}")
            # Ultimate fallback: ilk tamamlanan segmenti döndür
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
