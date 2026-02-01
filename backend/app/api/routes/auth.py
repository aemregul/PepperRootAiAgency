"""
Authentication API routes.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.config import settings
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_user_required,
    get_google_auth_url,
    exchange_google_code
)
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ============== SCHEMAS ==============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool


# ============== ENDPOINTS ==============

@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user with email and password."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password."""
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user_required)
):
    """Get current authenticated user."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        is_active=user.is_active
    )


@router.post("/logout")
async def logout():
    """Logout - client should discard the token."""
    return {"message": "Logged out successfully"}


# ============== GOOGLE OAUTH ==============

@router.get("/google")
async def google_login():
    """Redirect to Google OAuth."""
    auth_url = get_google_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback."""
    # Exchange code for user info
    google_user = await exchange_google_code(code)
    
    google_id = google_user.get("id")
    email = google_user.get("email")
    name = google_user.get("name")
    picture = google_user.get("picture")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    # Check if user exists by google_id
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Check if email exists (link accounts)
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user:
            # Link Google to existing account
            user.google_id = google_id
            user.avatar_url = picture
            if not user.full_name and name:
                user.full_name = name
        else:
            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                full_name=name,
                avatar_url=picture
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
    else:
        # Update avatar if changed
        if picture and user.avatar_url != picture:
            user.avatar_url = picture
            await db.commit()
    
    # Create token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # Redirect to frontend with token
    frontend_url = f"http://localhost:3000/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)
