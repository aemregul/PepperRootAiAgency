"""
Long Video Service - 3+ Dakikalık Video Üretimi.

Video segment'leri oluşturur ve birleştirir:
1. Kullanıcı prompt'unu segment'lere böl
2. Her segment için 5-10 saniyelik video üret
3. Segment'leri birleştir (stitch)
4. Final video'yu döndür

Dependencies: ffmpeg (Docker'da mevcut)
"""
import os
import uuid
import asyncio
import subprocess
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import tempfile
import httpx


@dataclass
class VideoSegment:
    """Video segment bilgisi."""
    id: str
    order: int
    prompt: str
    duration: int  # saniye
    status: str  # pending, generating, completed, failed
    video_url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class LongVideoJob:
    """Uzun video işi."""
    id: str
    user_id: str
    session_id: str
    total_duration: int  # hedef süre (saniye)
    segments: List[VideoSegment]
    status: str  # pending, processing, stitching, completed, failed
    progress: int  # 0-100
    final_video_url: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class LongVideoService:
    """
    Uzun video üretim servisi.
    
    3+ dakikalık videolar için:
    1. Prompt'u segment'lere böl
    2. Her segment'i paralel üret
    3. FFmpeg ile birleştir
    """
    
    MAX_SEGMENT_DURATION = 10  # saniye (Fal.ai limiti)
    MIN_SEGMENT_DURATION = 5
    
    def __init__(self):
        self.jobs: dict[str, LongVideoJob] = {}
    
    async def create_long_video(
        self,
        user_id: str,
        session_id: str,
        prompt: str,
        total_duration: int = 60,  # varsayılan 1 dakika
        aspect_ratio: str = "16:9",
        style: str = "cinematic"
    ) -> str:
        """
        Uzun video oluşturma işi başlat.
        
        Args:
            user_id: Kullanıcı ID
            session_id: Session ID
            prompt: Ana prompt
            total_duration: Hedef süre (saniye)
            aspect_ratio: Video oranı
            style: Video stili
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Segment'lere böl
        segments = self._create_segments(prompt, total_duration, style)
        
        job = LongVideoJob(
            id=job_id,
            user_id=user_id,
            session_id=session_id,
            total_duration=total_duration,
            segments=segments,
            status="pending",
            progress=0
        )
        
        self.jobs[job_id] = job
        
        # Celery task'ı başlat
        from app.tasks.video_tasks import generate_long_video
        generate_long_video.delay(job_id)
        
        print(f"🎬 Uzun video işi başlatıldı: {job_id} ({len(segments)} segment, {total_duration}s)")
        
        return job_id
    
    def _create_segments(
        self, 
        base_prompt: str, 
        total_duration: int,
        style: str
    ) -> List[VideoSegment]:
        """
        Prompt'u segment'lere böl.
        
        Her segment farklı bir sahne veya açı olabilir.
        """
        segments = []
        remaining_duration = total_duration
        order = 0
        
        # Segment açıklamaları (çeşitlilik için)
        variations = [
            "establishing shot, wide angle",
            "medium shot, focusing on details",
            "close-up, dramatic lighting",
            "dynamic movement, tracking shot",
            "slow motion, cinematic",
            "aerial view, sweeping",
            "intimate perspective, shallow depth of field",
            "action sequence, fast cuts",
        ]
        
        while remaining_duration > 0:
            # Segment süresi
            segment_duration = min(self.MAX_SEGMENT_DURATION, remaining_duration)
            if segment_duration < self.MIN_SEGMENT_DURATION and remaining_duration > self.MIN_SEGMENT_DURATION:
                segment_duration = self.MIN_SEGMENT_DURATION
            
            # Segment prompt'u oluştur
            variation = variations[order % len(variations)]
            segment_prompt = f"{base_prompt}, {variation}, {style} style, segment {order + 1}"
            
            segment = VideoSegment(
                id=str(uuid.uuid4()),
                order=order,
                prompt=segment_prompt,
                duration=segment_duration,
                status="pending"
            )
            
            segments.append(segment)
            remaining_duration -= segment_duration
            order += 1
        
        return segments
    
    async def process_job(self, job_id: str) -> dict:
        """
        Video işini işle - segment'leri üret ve birleştir.
        
        Bu metod Celery task'ından çağrılır.
        """
        job = self.jobs.get(job_id)
        if not job:
            return {"success": False, "error": "Job not found"}
        
        try:
            job.status = "processing"
            
            # 1. Segment'leri paralel üret
            await self._generate_segments(job)
            
            # 2. Segment'leri birleştir
            job.status = "stitching"
            job.progress = 90
            final_url = await self._stitch_segments(job)
            
            job.status = "completed"
            job.progress = 100
            job.final_video_url = final_url
            
            return {
                "success": True,
                "video_url": final_url,
                "duration": job.total_duration,
                "segments": len(job.segments)
            }
            
        except Exception as e:
            job.status = "failed"
            return {"success": False, "error": str(e)}
    
    async def _generate_segments(self, job: LongVideoJob):
        """Tüm segment'leri üret (paralel)."""
        from app.services.fal_plugin import FalPlugin
        fal = FalPlugin()
        
        total_segments = len(job.segments)
        
        # Batch halinde üret (max 3 paralel)
        batch_size = 3
        for i in range(0, total_segments, batch_size):
            batch = job.segments[i:i + batch_size]
            
            tasks = [
                self._generate_single_segment(fal, segment)
                for segment in batch
            ]
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Progress güncelle
            completed = sum(1 for s in job.segments if s.status == "completed")
            job.progress = int((completed / total_segments) * 80)  # %80'e kadar segment üretimi
    
    async def _generate_single_segment(
        self, 
        fal: "FalPlugin", 
        segment: VideoSegment
    ):
        """Tek bir segment üret."""
        try:
            segment.status = "generating"
            
            result = await fal.generate_video(
                prompt=segment.prompt,
                duration=segment.duration,
                aspect_ratio="16:9",
                model="fal-ai/kling-video/v1.5/pro/text-to-video"
            )
            
            segment.video_url = result.get("video_url")
            segment.status = "completed"
            
        except Exception as e:
            segment.status = "failed"
            segment.error = str(e)
    
    async def _stitch_segments(self, job: LongVideoJob) -> str:
        """
        Segment'leri FFmpeg ile birleştir.
        
        Returns:
            Final video URL
        """
        completed_segments = [s for s in job.segments if s.status == "completed"]
        
        if not completed_segments:
            raise ValueError("No completed segments to stitch")
        
        # Geçici dizin oluştur
        with tempfile.TemporaryDirectory() as temp_dir:
            # Segment videolarını indir
            segment_files = []
            
            async with httpx.AsyncClient() as client:
                for i, segment in enumerate(sorted(completed_segments, key=lambda s: s.order)):
                    file_path = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
                    
                    response = await client.get(segment.video_url)
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    
                    segment_files.append(file_path)
            
            # FFmpeg concat file oluştur
            concat_file = os.path.join(temp_dir, "concat.txt")
            with open(concat_file, "w") as f:
                for file_path in segment_files:
                    f.write(f"file '{file_path}'\n")
            
            # FFmpeg ile birleştir
            output_file = os.path.join(temp_dir, f"final_{job.id}.mp4")
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                output_file
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {process.stderr}")
            
            # TODO: Final videoyu cloud storage'a yükle (S3, Cloudflare R2, etc.)
            # Şimdilik local path döndür
            
            # Placeholder - gerçek implementasyonda cloud URL döner
            return f"https://storage.example.com/videos/{job.id}.mp4"
    
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
