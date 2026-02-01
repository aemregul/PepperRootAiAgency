"""
Pepper Root AI Agency - Ana uygulama.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import sessions, chat, generate, entities, upload, plugins, admin, grid
from app.services.plugins.plugin_loader import initialize_plugins


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 {settings.APP_NAME} başlatılıyor...")
    
    # Pluginleri yükle
    initialize_plugins()
    
    yield
    print(f"👋 {settings.APP_NAME} kapatılıyor...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Route'ları
app.include_router(sessions.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(entities.router, prefix=settings.API_PREFIX)
app.include_router(upload.router, prefix=settings.API_PREFIX)
app.include_router(plugins.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(grid.router, prefix=settings.API_PREFIX)
app.include_router(generate.router, prefix=f"{settings.API_PREFIX}/generate")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    return {
        "message": f"Hoş geldiniz! {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health",
        "plugins": "/api/v1/plugins",
    }

