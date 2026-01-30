"use client";

import { useState } from "react";
import { X, Store, Search, Star, Download, Plus, Filter, TrendingUp, Clock, Users } from "lucide-react";
import { CreativePlugin } from "./CreativePluginModal";

interface PluginMarketplaceModalProps {
    isOpen: boolean;
    onClose: () => void;
    onInstall: (plugin: CreativePlugin) => void;
    myPlugins: CreativePlugin[];
}

// Mock community plugins
const communityPlugins: CreativePlugin[] = [
    {
        id: "comm1",
        name: "Cinematic Portrait Pack",
        description: "Hollywood tarzı portre çekimleri için hazır ayarlar. Dramatic lighting ve bokeh efektleri.",
        author: "StudioPro",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Değişken", isVariable: true },
            location: { id: "studio", name: "Professional Studio", settings: "" },
            timeOfDay: "Golden Hour",
            cameraAngles: ["Close-up", "Medium Shot", "Over Shoulder"],
            style: "Cinematic",
            promptTemplate: "professional portrait, dramatic lighting, shallow depth of field, {character}"
        },
        createdAt: new Date("2026-01-15"),
        downloads: 1250,
        rating: 4.9
    },
    {
        id: "comm2",
        name: "E-Commerce Product Shots",
        description: "Online mağaza için ürün fotoğrafları. Beyaz arka plan, soft shadows.",
        author: "ShopVisuals",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Ürün", isVariable: true },
            location: { id: "whitebg", name: "White Background", settings: "" },
            timeOfDay: "Studio Light",
            cameraAngles: ["Front View", "45 Degree", "Top Down"],
            style: "Commercial",
            promptTemplate: "product photography, white background, soft shadows, professional lighting"
        },
        createdAt: new Date("2026-01-20"),
        downloads: 890,
        rating: 4.7
    },
    {
        id: "comm3",
        name: "Urban Street Style",
        description: "Sokak modası çekimleri için şehir ortamları ve doğal ışık.",
        author: "StreetVision",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Değişken", isVariable: true },
            location: { id: "urban", name: "Urban Street", settings: "" },
            timeOfDay: "Afternoon",
            cameraAngles: ["Wide Shot", "Medium Shot", "Dutch Angle"],
            style: "Editorial",
            promptTemplate: "street fashion photography, urban environment, natural light, {character}"
        },
        createdAt: new Date("2026-01-25"),
        downloads: 720,
        rating: 4.6
    },
    {
        id: "comm4",
        name: "Food Photography Pro",
        description: "Yemek fotoğrafçılığı için profesyonel ayarlar.",
        author: "FoodieShots",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Yemek", isVariable: true },
            location: { id: "restaurant", name: "Restaurant Table", settings: "" },
            timeOfDay: "Warm Light",
            cameraAngles: ["Top Down", "45 Degree", "Close-up"],
            style: "Warm Tones",
            promptTemplate: "food photography, appetizing, warm tones, shallow depth of field"
        },
        createdAt: new Date("2026-01-28"),
        downloads: 560,
        rating: 4.8
    },
    {
        id: "comm5",
        name: "Minimalist Interior",
        description: "İç mekan tasarımı ve mimari fotoğraflar için minimalist yaklaşım.",
        author: "ArchViz",
        isPublic: true,
        config: {
            character: { id: "none", name: "Yok", isVariable: false },
            location: { id: "interior", name: "Modern Interior", settings: "" },
            timeOfDay: "Natural Light",
            cameraAngles: ["Wide Shot", "Corner View", "Detail Shot"],
            style: "Minimalist",
            promptTemplate: "interior photography, minimalist design, natural light, clean lines"
        },
        createdAt: new Date("2026-01-29"),
        downloads: 340,
        rating: 4.5
    }
];

export function PluginMarketplaceModal({ isOpen, onClose, onInstall, myPlugins }: PluginMarketplaceModalProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [sortBy, setSortBy] = useState<"downloads" | "rating" | "recent">("downloads");
    const [installedIds, setInstalledIds] = useState<string[]>([]);

    if (!isOpen) return null;

    // Filter by search
    const filteredPlugins = communityPlugins.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.author.toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Sort
    const sortedPlugins = [...filteredPlugins].sort((a, b) => {
        if (sortBy === "downloads") return b.downloads - a.downloads;
        if (sortBy === "rating") return b.rating - a.rating;
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    });

    // Check if already installed
    const isInstalled = (pluginId: string) => {
        return myPlugins.some(p => p.id === pluginId) || installedIds.includes(pluginId);
    };

    const handleInstall = (plugin: CreativePlugin) => {
        onInstall(plugin);
        setInstalledIds([...installedIds, plugin.id]);
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose} />

            <div
                className="relative w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-5 border-b"
                    style={{ borderColor: "var(--border)", background: "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)" }}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
                            <Store size={24} className="text-purple-500" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Plugin Marketplace</h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Topluluk tarafından oluşturulan Creative Plugin'ler
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 rounded-xl hover:bg-[var(--background)] transition-all">
                        <X size={20} />
                    </button>
                </div>

                {/* Search & Filters */}
                <div className="flex items-center gap-3 p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="flex-1 relative">
                        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--foreground-muted)" }} />
                        <input
                            type="text"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            placeholder="Plugin ara..."
                            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm"
                            style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                        />
                    </div>
                    <div className="flex items-center gap-1 p-1 rounded-xl" style={{ background: "var(--background)" }}>
                        <button
                            onClick={() => setSortBy("downloads")}
                            className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === "downloads" ? "bg-purple-500 text-white" : ""}`}
                        >
                            <Download size={12} /> Popüler
                        </button>
                        <button
                            onClick={() => setSortBy("rating")}
                            className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === "rating" ? "bg-purple-500 text-white" : ""}`}
                        >
                            <Star size={12} /> En İyi
                        </button>
                        <button
                            onClick={() => setSortBy("recent")}
                            className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === "recent" ? "bg-purple-500 text-white" : ""}`}
                        >
                            <Clock size={12} /> Yeni
                        </button>
                    </div>
                </div>

                {/* Plugin Grid */}
                <div className="p-4 overflow-y-auto max-h-[calc(85vh-180px)]">
                    <div className="grid grid-cols-2 gap-4">
                        {sortedPlugins.map((plugin) => (
                            <div
                                key={plugin.id}
                                className="p-4 rounded-xl transition-all hover:shadow-lg"
                                style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                            >
                                {/* Header */}
                                <div className="flex items-start justify-between mb-3">
                                    <div>
                                        <h3 className="font-semibold">{plugin.name}</h3>
                                        <div className="flex items-center gap-2 text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                            <span className="flex items-center gap-1">
                                                <Users size={10} /> {plugin.author}
                                            </span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Star size={10} className="text-yellow-500" /> {plugin.rating}
                                            </span>
                                            <span>•</span>
                                            <span className="flex items-center gap-1">
                                                <Download size={10} /> {plugin.downloads.toLocaleString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* Description */}
                                <p className="text-xs mb-3 line-clamp-2" style={{ color: "var(--foreground-muted)" }}>
                                    {plugin.description}
                                </p>

                                {/* Tags */}
                                <div className="flex flex-wrap gap-1 mb-3">
                                    {plugin.config.style && (
                                        <span className="px-2 py-0.5 text-xs rounded" style={{ background: "var(--card)" }}>
                                            {plugin.config.style}
                                        </span>
                                    )}
                                    {plugin.config.cameraAngles && plugin.config.cameraAngles.slice(0, 2).map((angle, i) => (
                                        <span key={i} className="px-2 py-0.5 text-xs rounded" style={{ background: "var(--card)" }}>
                                            {angle}
                                        </span>
                                    ))}
                                </div>

                                {/* Action */}
                                <button
                                    onClick={() => handleInstall(plugin)}
                                    disabled={isInstalled(plugin.id)}
                                    className={`w-full py-2 text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-2 ${isInstalled(plugin.id)
                                            ? "bg-green-500/20 text-green-500 cursor-default"
                                            : "hover:opacity-90"
                                        }`}
                                    style={!isInstalled(plugin.id) ? { background: "var(--accent)", color: "var(--background)" } : {}}
                                >
                                    {isInstalled(plugin.id) ? (
                                        <>✓ Yüklendi</>
                                    ) : (
                                        <><Plus size={14} /> Projeme Ekle</>
                                    )}
                                </button>
                            </div>
                        ))}
                    </div>

                    {sortedPlugins.length === 0 && (
                        <div className="text-center py-12">
                            <Store size={48} className="mx-auto mb-4 opacity-20" />
                            <p style={{ color: "var(--foreground-muted)" }}>
                                Arama sonucu bulunamadı
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
