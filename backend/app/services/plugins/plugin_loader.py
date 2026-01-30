"""
Plugin Loader - Pluginleri dinamik olarak yükler ve yönetir.

Özellikler:
- Plugin discovery (pluginleri bul)
- Plugin registry (kayıt et)
- Enable/disable (aç/kapa)
- Plugin yönetimi
"""
import importlib
import os
from typing import Optional, Type
from pathlib import Path

from app.services.plugins.plugin_base import PluginBase, PluginInfo, PluginCategory


class PluginRegistry:
    """
    Plugin Registry - Tüm pluginleri yönetir.
    
    Singleton pattern ile tek bir instance.
    """
    
    _instance: Optional["PluginRegistry"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins: dict[str, PluginBase] = {}
            cls._instance._initialized = False
        return cls._instance
    
    @property
    def plugins(self) -> dict[str, PluginBase]:
        """Kayıtlı tüm pluginler."""
        return self._plugins.copy()
    
    def register(self, plugin: PluginBase) -> bool:
        """
        Plugin kaydet.
        
        Args:
            plugin: Kaydedilecek plugin instance
        
        Returns:
            bool: Başarılı mı?
        """
        name = plugin.info.name
        
        if name in self._plugins:
            print(f"⚠️ Plugin zaten kayıtlı: {name}")
            return False
        
        self._plugins[name] = plugin
        print(f"✅ Plugin kaydedildi: {name} v{plugin.info.version}")
        return True
    
    def unregister(self, name: str) -> bool:
        """Plugin kaydını sil."""
        if name in self._plugins:
            del self._plugins[name]
            print(f"🗑️ Plugin silindi: {name}")
            return True
        return False
    
    def get(self, name: str) -> Optional[PluginBase]:
        """Plugin'i isimle getir."""
        return self._plugins.get(name)
    
    def get_by_category(self, category: PluginCategory) -> list[PluginBase]:
        """Kategoriye göre pluginleri getir."""
        return [
            p for p in self._plugins.values()
            if p.info.category == category
        ]
    
    def get_enabled(self) -> list[PluginBase]:
        """Sadece aktif pluginleri getir."""
        return [p for p in self._plugins.values() if p.is_enabled]
    
    def enable(self, name: str) -> bool:
        """Plugin'i aktif et."""
        plugin = self.get(name)
        if plugin:
            plugin.enable()
            return True
        return False
    
    def disable(self, name: str) -> bool:
        """Plugin'i devre dışı bırak."""
        plugin = self.get(name)
        if plugin:
            plugin.disable()
            return True
        return False
    
    def list_all(self) -> list[dict]:
        """Tüm pluginlerin bilgilerini listele."""
        result = []
        for name, plugin in self._plugins.items():
            info = plugin.info
            result.append({
                "name": info.name,
                "display_name": info.display_name,
                "version": info.version,
                "category": info.category.value,
                "description": info.description,
                "is_enabled": plugin.is_enabled,
                "capabilities": info.capabilities,
            })
        return result
    
    async def health_check_all(self) -> dict[str, bool]:
        """Tüm pluginlerin sağlık kontrolü."""
        results = {}
        for name, plugin in self._plugins.items():
            try:
                results[name] = await plugin.health_check()
            except Exception as e:
                results[name] = False
                print(f"❌ Plugin health check failed: {name} - {e}")
        return results


class PluginLoader:
    """
    Plugin Loader - Pluginleri dinamik olarak yükler.
    """
    
    def __init__(self, registry: Optional[PluginRegistry] = None):
        self.registry = registry or PluginRegistry()
    
    def load_plugin_class(self, module_path: str, class_name: str) -> Optional[Type[PluginBase]]:
        """
        Module'dan plugin class'ını yükle.
        
        Args:
            module_path: "app.services.plugins.fal_plugin"
            class_name: "FalPlugin"
        
        Returns:
            Plugin class veya None
        """
        try:
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name, None)
            
            if plugin_class and issubclass(plugin_class, PluginBase):
                return plugin_class
            else:
                print(f"⚠️ {class_name} PluginBase'den türetilmemiş")
                return None
                
        except ImportError as e:
            print(f"❌ Module yüklenemedi: {module_path} - {e}")
            return None
    
    def load_and_register(
        self, 
        module_path: str, 
        class_name: str,
        config: Optional[dict] = None
    ) -> Optional[PluginBase]:
        """
        Plugin'i yükle, instance oluştur ve kaydet.
        
        Returns:
            Plugin instance veya None
        """
        plugin_class = self.load_plugin_class(module_path, class_name)
        
        if plugin_class:
            try:
                plugin = plugin_class()
                
                if config:
                    plugin.configure(config)
                
                if self.registry.register(plugin):
                    return plugin
                    
            except Exception as e:
                print(f"❌ Plugin instance oluşturulamadı: {class_name} - {e}")
        
        return None
    
    def auto_discover(self, plugins_dir: str = "app/services/plugins") -> list[str]:
        """
        Plugins dizinindeki tüm pluginleri otomatik bul.
        
        Returns:
            Bulunan plugin dosyalarının listesi
        """
        discovered = []
        plugins_path = Path(plugins_dir)
        
        if plugins_path.exists():
            for file in plugins_path.glob("*_plugin.py"):
                if not file.name.startswith("_"):
                    discovered.append(file.stem)
        
        return discovered


# Singleton instances
plugin_registry = PluginRegistry()
plugin_loader = PluginLoader(plugin_registry)


def initialize_plugins():
    """
    Başlangıçta tüm pluginleri yükle.
    main.py'de çağrılmalı.
    """
    from app.services.plugins.fal_plugin_v2 import FalPluginV2
    
    # fal.ai plugin'i kaydet
    fal_plugin = FalPluginV2()
    plugin_registry.register(fal_plugin)
    
    print(f"📦 {len(plugin_registry.plugins)} plugin yüklendi")
