"use client";

import { useState, useEffect, useCallback } from "react";
import { X, Store, Search, Star, Download, Plus, TrendingUp, Clock, Users, Loader2, Sparkles } from "lucide-react";
import { CreativePlugin } from "./CreativePluginModal";
import { getMarketplacePlugins, installMarketplacePlugin, type MarketplacePlugin } from "@/lib/api";

interface PluginMarketplaceModalProps {
    isOpen: boolean;
    onClose: () => void;
    onInstall: (plugin: CreativePlugin) => void;
    myPlugins: CreativePlugin[];
}

type SortMode = "downloads" | "rating" | "recent";
type CategoryMode = "all" | "community";

export function PluginMarketplaceModal({ isOpen, onClose, onInstall, myPlugins }: PluginMarketplaceModalProps) {
    const [searchQuery, setSearchQuery] = useState("");
    const [sortBy, setSortBy] = useState<SortMode>("downloads");
    const [category, setCategory] = useState<CategoryMode>("all");
    const [plugins, setPlugins] = useState<MarketplacePlugin[]>([]);
    const [loading, setLoading] = useState(false);
    const [installedIds, setInstalledIds] = useState<string[]>([]);

    const fetchPlugins = useCallback(async () => {
        setLoading(true);
        try {
            const data = await getMarketplacePlugins(sortBy, category, searchQuery);
            setPlugins(data);
        } catch (err) {
            console.error("Marketplace fetch error:", err);
        } finally {
            setLoading(false);
        }
    }, [sortBy, category, searchQuery]);

    useEffect(() => {
        if (isOpen) {
            fetchPlugins();
        }
    }, [isOpen, fetchPlugins]);

    // Debounce search
    useEffect(() => {
        if (!isOpen) return;
        const timer = setTimeout(() => {
            fetchPlugins();
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]); // eslint-disable-line react-hooks/exhaustive-deps

    if (!isOpen) return null;

    const isInstalled = (pluginId: string) => {
        return myPlugins.some(p => p.id === pluginId) || installedIds.includes(pluginId);
    };

    const handleInstall = async (plugin: MarketplacePlugin) => {
        // API ile install sayacını artır
        try {
            await installMarketplacePlugin(plugin.id);
        } catch {
            // Seed pluginler için hata olabilir, sorun değil
        }

        // Frontend CreativePlugin formatına çevir ve yükle
        const creativePlugin: CreativePlugin = {
            id: plugin.id,
            name: plugin.name,
            description: plugin.description,
            author: plugin.author,
            isPublic: false,
            config: {
                character: { id: "variable", name: "Karakter", isVariable: true },
                location: { id: "custom", name: "Custom", settings: "" },
                timeOfDay: (plugin.config?.timeOfDay as string) || "Auto",
                cameraAngles: (plugin.config?.cameraAngles as string[]) || ["Portrait", "Wide", "Close-up"],
                style: plugin.style || "Custom",
                promptTemplate: (plugin.config?.promptTemplate as string) || "",
            },
            createdAt: new Date(plugin.created_at),
            downloads: plugin.downloads,
            rating: plugin.rating,
        };
        onInstall(creativePlugin);
        setInstalledIds(prev => [...prev, plugin.id]);
    };

    const filterButtons: { sort: SortMode; icon: React.ReactNode; label: string }[] = [
        { sort: "downloads", icon: <TrendingUp size={12} />, label: "Popüler" },
        { sort: "rating", icon: <Star size={12} />, label: "En İyi" },
        { sort: "recent", icon: <Clock size={12} />, label: "Yeni" },
    ];

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
                            <h2 className="text-xl font-bold">Eklenti Mağazası</h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                {plugins.length} eklenti mevcut
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 rounded-xl hover:bg-[var(--background)] transition-all">
                        <X size={20} />
                    </button>
                </div>

                {/* Search & Filters */}
                <div className="flex flex-col gap-3 p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="flex items-center gap-3">
                        <div className="flex-1 relative">
                            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: "var(--foreground-muted)" }} />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Eklenti ara..."
                                className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm"
                                style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                            />
                        </div>
                    </div>

                    {/* Filter row: Sort + Category */}
                    <div className="flex items-center justify-between gap-2">
                        {/* Sort buttons */}
                        <div className="flex items-center gap-1 p-1 rounded-xl" style={{ background: "var(--background)" }}>
                            {filterButtons.map((fb) => (
                                <button
                                    key={fb.sort}
                                    onClick={() => setSortBy(fb.sort)}
                                    className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${sortBy === fb.sort ? "bg-purple-500 text-white" : ""}`}
                                >
                                    {fb.icon} {fb.label}
                                </button>
                            ))}
                        </div>

                        {/* Category toggle */}
                        <div className="flex items-center gap-1 p-1 rounded-xl" style={{ background: "var(--background)" }}>
                            <button
                                onClick={() => setCategory("all")}
                                className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${category === "all" ? "bg-blue-500 text-white" : ""}`}
                            >
                                <Sparkles size={12} /> Tümü
                            </button>
                            <button
                                onClick={() => setCategory("community")}
                                className={`px-3 py-1.5 text-xs rounded-lg flex items-center gap-1 transition-all ${category === "community" ? "bg-emerald-500 text-white" : ""}`}
                            >
                                <Users size={12} /> Topluluk
                            </button>
                        </div>
                    </div>
                </div>

                {/* Plugin Grid */}
                <div className="p-4 overflow-y-auto max-h-[calc(85vh-220px)]">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-16 gap-3">
                            <Loader2 size={32} className="animate-spin text-purple-500" />
                            <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>Eklentiler yükleniyor...</p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 gap-4 items-stretch">
                            {plugins.map((plugin) => (
                                <div
                                    key={plugin.id}
                                    className="p-4 rounded-xl transition-all hover:shadow-lg flex flex-col h-full"
                                    style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                                >
                                    {/* Header */}
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-start gap-2 flex-1 min-w-0">
                                            <span className="text-xl flex-shrink-0">{plugin.icon}</span>
                                            <div className="min-w-0">
                                                <h3 className="font-semibold text-sm truncate">{plugin.name}</h3>
                                                <div className="flex items-center gap-2 text-xs mt-1 flex-wrap" style={{ color: "var(--foreground-muted)" }}>
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
                                        {/* Source badge */}
                                        <span
                                            className="px-2 py-0.5 text-[10px] rounded-full font-medium flex-shrink-0 ml-2"
                                            style={{
                                                background: plugin.source === "official"
                                                    ? "rgba(139, 92, 246, 0.15)"
                                                    : "rgba(16, 185, 129, 0.15)",
                                                color: plugin.source === "official"
                                                    ? "#a78bfa"
                                                    : "#34d399",
                                            }}
                                        >
                                            {plugin.source === "official" ? "🏪 Resmi" : "👤 Topluluk"}
                                        </span>
                                    </div>

                                    {/* Description */}
                                    <p className="text-xs mb-3 line-clamp-2 flex-grow" style={{ color: "var(--foreground-muted)" }}>
                                        {plugin.description}
                                    </p>

                                    {/* Tags */}
                                    <div className="flex flex-wrap gap-1 mb-3">
                                        {plugin.style && (
                                            <span
                                                className="px-2 py-0.5 text-xs rounded"
                                                style={{ background: `${plugin.color}20`, color: plugin.color }}
                                            >
                                                {plugin.style}
                                            </span>
                                        )}
                                        {plugin.config?.cameraAngles && (plugin.config.cameraAngles as string[]).slice(0, 2).map((angle: string, i: number) => (
                                            <span key={i} className="px-2 py-0.5 text-xs rounded" style={{ background: "var(--card)" }}>
                                                {angle}
                                            </span>
                                        ))}
                                    </div>

                                    {/* Action */}
                                    <button
                                        onClick={() => handleInstall(plugin)}
                                        disabled={isInstalled(plugin.id)}
                                        className={`w-full py-2 text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-2 mt-auto ${isInstalled(plugin.id)
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
                    )}

                    {!loading && plugins.length === 0 && (
                        <div className="text-center py-12">
                            <Store size={48} className="mx-auto mb-4 opacity-20" />
                            <p style={{ color: "var(--foreground-muted)" }}>
                                {category === "community"
                                    ? "Henüz topluluk eklentisi yok"
                                    : "Arama sonucu bulunamadı"}
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
