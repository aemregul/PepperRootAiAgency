"""
API şemaları (Pydantic modelleri).
"""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr


# ============== KULLANICI ==============

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== OTURUM ==============

class SessionCreate(BaseModel):
    title: Optional[str] = "Yeni Oturum"


class SessionResponse(BaseModel):
    id: UUID
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== MESAJ ==============

class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    metadata_: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== VARLIK ==============

class EntityCreate(BaseModel):
    entity_type: str
    name: str
    description: Optional[str] = None
    attributes: Optional[dict] = None
    reference_image_url: Optional[str] = None  # Yüz/vücut referans görseli


class EntityResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_id: Optional[UUID] = None  # Artık opsiyonel
    entity_type: str
    name: str
    tag: str
    description: Optional[str] = None
    attributes: Optional[dict] = None
    reference_image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== ASSET ==============

class AssetResponse(BaseModel):
    id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    asset_type: str
    url: str
    thumbnail_url: Optional[str] = None
    prompt: Optional[str] = None
    model_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== CHAT ==============

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    session_id: UUID
    message: MessageResponse
    response: MessageResponse
    assets: list[AssetResponse] = []
    entities_created: list[EntityResponse] = []


# ============== GÖRSEL ÜRETİM ==============

class ImageGenerateRequest(BaseModel):
    prompt: str
    model: str = "fal-ai/flux/schnell"
    image_size: str = "square_hd"
    num_images: int = 1
    seed: Optional[int] = None


class ImageGenerateResponse(BaseModel):
    images: list[dict]
    seed: Optional[int] = None
    prompt: str


class ImageToImageRequest(BaseModel):
    prompt: str
    image_url: str
    model: str = "fal-ai/flux/dev/image-to-image"
    strength: float = 0.85
    image_size: str = "square_hd"
