"""
Plugin Admin API - Plugin yönetimi için REST endpoints.

Endpoints:
- GET /plugins - Tüm pluginleri listele
- GET /plugins/{name} - Plugin detayı
- POST /plugins/{name}/enable - Plugin'i aktif et
- POST /plugins/{name}/disable - Plugin'i devre dışı bırak
- GET /plugins/health - Tüm pluginlerin sağlık durumu
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.plugins.plugin_loader import plugin_registry


router = APIRouter(prefix="/plugins", tags=["plugins"])


class PluginResponse(BaseModel):
    name: str
    display_name: str
    version: str
    category: str
    description: str
    is_enabled: bool
    capabilities: list[str]


class PluginConfigRequest(BaseModel):
    config: dict


class PluginActionResponse(BaseModel):
    success: bool
    message: str
    plugin_name: Optional[str] = None


@router.get("/", response_model=list[PluginResponse])
async def list_plugins():
    """Tüm pluginleri listele."""
    plugins = plugin_registry.list_all()
    return plugins


@router.get("/health")
async def health_check_all():
    """Tüm pluginlerin sağlık kontrolü."""
    results = await plugin_registry.health_check_all()
    return {
        "status": "ok" if all(results.values()) else "degraded",
        "plugins": results
    }


@router.get("/{name}", response_model=PluginResponse)
async def get_plugin(name: str):
    """Plugin detayını getir."""
    plugin = plugin_registry.get(name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin bulunamadı: {name}")
    
    info = plugin.info
    return {
        "name": info.name,
        "display_name": info.display_name,
        "version": info.version,
        "category": info.category.value,
        "description": info.description,
        "is_enabled": plugin.is_enabled,
        "capabilities": info.capabilities,
    }


@router.post("/{name}/enable", response_model=PluginActionResponse)
async def enable_plugin(name: str):
    """Plugin'i aktif et."""
    success = plugin_registry.enable(name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Plugin bulunamadı: {name}")
    
    return {
        "success": True,
        "message": f"Plugin aktif edildi: {name}",
        "plugin_name": name
    }


@router.post("/{name}/disable", response_model=PluginActionResponse)
async def disable_plugin(name: str):
    """Plugin'i devre dışı bırak."""
    success = plugin_registry.disable(name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Plugin bulunamadı: {name}")
    
    return {
        "success": True,
        "message": f"Plugin devre dışı bırakıldı: {name}",
        "plugin_name": name
    }


@router.post("/{name}/configure", response_model=PluginActionResponse)
async def configure_plugin(name: str, request: PluginConfigRequest):
    """Plugin ayarlarını güncelle."""
    plugin = plugin_registry.get(name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin bulunamadı: {name}")
    
    plugin.configure(request.config)
    
    return {
        "success": True,
        "message": f"Plugin ayarları güncellendi: {name}",
        "plugin_name": name
    }


@router.get("/{name}/config")
async def get_plugin_config(name: str):
    """Plugin ayarlarını getir."""
    plugin = plugin_registry.get(name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail=f"Plugin bulunamadı: {name}")
    
    return {
        "name": name,
        "config": plugin.get_config(),
        "config_schema": plugin.info.config_schema
    }
