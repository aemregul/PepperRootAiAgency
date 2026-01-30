"""
Görsel yükleme endpoint'i.
Kullanıcıdan gelen görselleri fal.ai storage'a yükler.
"""
import fal_client
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/upload", tags=["Yükleme"])


class UploadResponse(BaseModel):
    """Yükleme yanıtı."""
    url: str
    content_type: str
    size: int


@router.post("/image", response_model=UploadResponse, summary="Görsel Yükle")
async def upload_image(file: UploadFile = File(...)):
    """
    Görsel yükler ve URL döndürür.
    
    Bu URL entity'lere referans görsel olarak bağlanabilir.
    fal.ai storage kullanılır.
    """
    # Dosya tipini kontrol et
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Sadece görsel dosyaları yüklenebilir (image/*)"
        )
    
    # Maksimum boyut kontrolü (10MB)
    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Dosya boyutu 10MB'dan büyük olamaz"
        )
    
    try:
        # fal.ai storage'a yükle
        url = fal_client.upload(content, file.content_type)
        
        return UploadResponse(
            url=url,
            content_type=file.content_type,
            size=len(content)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Görsel yükleme hatası: {str(e)}"
        )
