"use client";

import { useState, useEffect } from "react";
import { Download, Copy, Globe, RefreshCw, Play, ChevronLeft, ChevronRight, MoreHorizontal, Star, Loader2, Trash2 } from "lucide-react";
import { getAssets, GeneratedAsset, deleteAsset } from "@/lib/api";

interface Asset {
    id: string;
    url: string;
    type: "image" | "video";
    label?: string;
    duration?: string;
    isFavorite?: boolean;
}

// Mock data with more realistic images
const mockAssets: Asset[] = [
    {
        id: "1",
        url: "https://fal.media/files/penguin/ttzc_uRNnT2DW-b0c-WRD.png",
        type: "video",
        label: "Location_kitchen at night",
        duration: "3:00",
        isFavorite: true,
    },
    {
        id: "2",
        url: "https://fal.media/files/tiger/DL-2D_z3wVHxM1OPJVYHS.png",
        type: "image",
        isFavorite: false,
    },
    {
        id: "3",
        url: "https://fal.media/files/lion/VoLY3j7gPj_rEV9lqTaVB.png",
        type: "image",
        isFavorite: true,
    },
    {
        id: "4",
        url: "https://fal.media/files/elephant/6Xbc7RaBCW8dFx-xgG8d5.png",
        type: "image",
        isFavorite: false,
    },
    {
        id: "5",
        url: "https://fal.media/files/penguin/ttzc_uRNnT2DW-b0c-WRD.png",
        type: "image",
        isFavorite: false,
    },
    {
        id: "6",
        url: "https://fal.media/files/tiger/DL-2D_z3wVHxM1OPJVYHS.png",
        type: "image",
        isFavorite: false,
    },
];

interface AssetsPanelProps {
    collapsed?: boolean;
    onToggle?: () => void;
    sessionId?: string | null;
    refreshKey?: number;
}

export function AssetsPanel({ collapsed = false, onToggle, sessionId, refreshKey }: AssetsPanelProps) {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    // API'den asset'leri çek
    useEffect(() => {
        const fetchAssets = async () => {
            if (!sessionId) {
                setAssets([]);
                return;
            }

            setIsLoading(true);
            try {
                const apiAssets = await getAssets(sessionId);
                const mappedAssets: Asset[] = apiAssets.map((a: GeneratedAsset) => ({
                    id: a.id,
                    url: a.url,
                    type: a.type,
                    label: a.prompt?.substring(0, 30),
                    isFavorite: false
                }));
                setAssets(mappedAssets);
            } catch (error) {
                console.error('Asset yükleme hatası:', error);
                setAssets([]);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAssets();
    }, [sessionId, refreshKey]);

    const toggleFavorite = (assetId: string) => {
        setAssets(prev => prev.map(asset =>
            asset.id === assetId ? { ...asset, isFavorite: !asset.isFavorite } : asset
        ));
    };

    // Delete asset
    const handleDelete = async (assetId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Bu görseli silmek istediğinize emin misiniz?')) return;

        const success = await deleteAsset(assetId);
        if (success) {
            setAssets(prev => prev.filter(a => a.id !== assetId));
        } else {
            alert('Silme işlemi başarısız oldu');
        }
    };

    // Drag start for chat drop
    const handleDragStart = (e: React.DragEvent, asset: Asset) => {
        e.dataTransfer.setData('text/plain', asset.url);
        e.dataTransfer.setData('application/x-asset-url', asset.url);
        e.dataTransfer.setData('application/x-asset-id', asset.id);
        e.dataTransfer.effectAllowed = 'copy';
    };

    // Download all assets
    const handleDownloadAll = async () => {
        for (const asset of displayAssets) {
            try {
                const response = await fetch(asset.url);
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `asset_${asset.id}.${asset.type === 'video' ? 'mp4' : 'png'}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } catch (error) {
                console.error('Download failed:', error);
            }
        }
    };

    // Copy first asset URL to clipboard
    const handleCopyLink = async () => {
        if (displayAssets.length > 0) {
            try {
                await navigator.clipboard.writeText(displayAssets[0].url);
                alert('Link kopyalandı!');
            } catch (error) {
                console.error('Copy failed:', error);
            }
        }
    };

    // Share via Web Share API
    const handleShare = async () => {
        if (displayAssets.length > 0 && navigator.share) {
            try {
                await navigator.share({
                    title: 'Pepper Root AI Agency - Generated Assets',
                    text: 'AI ile oluşturulmuş görseller',
                    url: displayAssets[0].url
                });
            } catch (error) {
                // User cancelled or share failed
                console.log('Share cancelled');
            }
        } else {
            // Fallback: copy to clipboard
            handleCopyLink();
        }
    };

    const displayAssets = showFavoritesOnly ? assets.filter(a => a.isFavorite) : assets;
    const favoritesCount = assets.filter(a => a.isFavorite).length;

    if (collapsed) {
        return (
            <button
                onClick={onToggle}
                className="hidden lg:flex fixed right-0 top-1/2 -translate-y-1/2 p-2 rounded-l-lg z-30"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                <ChevronLeft size={20} />
            </button>
        );
    }

    return (
        <aside
            className="
        hidden lg:flex flex-col
        w-[300px] xl:w-[340px]
        h-screen
        border-l
      "
            style={{
                background: "var(--background-secondary)",
                borderColor: "var(--border)"
            }}
        >
            {/* Header */}
            <header
                className="h-14 px-4 flex items-center justify-between border-b shrink-0"
                style={{ borderColor: "var(--border)" }}
            >
                <h2 className="font-medium">Media Assets</h2>
                <div className="flex items-center gap-1">
                    {/* Favorites Filter */}
                    <button
                        onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
                        className={`p-1.5 rounded-lg transition-colors flex items-center gap-1 ${showFavoritesOnly ? 'bg-yellow-500/20' : 'hover:bg-[var(--card)]'}`}
                        title={showFavoritesOnly ? "Tümünü Göster" : "Sadece Favoriler"}
                    >
                        <Star size={16} fill={showFavoritesOnly ? "#eab308" : "none"} style={{ color: showFavoritesOnly ? "#eab308" : "var(--foreground-muted)" }} />
                        {favoritesCount > 0 && (
                            <span className="text-xs" style={{ color: showFavoritesOnly ? "#eab308" : "var(--foreground-muted)" }}>{favoritesCount}</span>
                        )}
                    </button>
                    <button
                        className="p-1.5 rounded-lg hover:bg-[var(--card)] transition-colors"
                        title="Refresh"
                    >
                        <RefreshCw size={16} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                    <button
                        onClick={onToggle}
                        className="p-1.5 rounded-lg hover:bg-[var(--card)] transition-colors"
                    >
                        <ChevronRight size={16} />
                    </button>
                </div>
            </header>

            {/* Assets Grid */}
            <div className="flex-1 overflow-y-auto p-3">
                {displayAssets.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <p style={{ color: "var(--foreground-muted)" }}>
                            No assets yet
                        </p>
                        <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
                            Start chatting to generate content!
                        </p>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {/* Featured video/image */}
                        {displayAssets[0] && (
                            <div
                                className="asset-card cursor-grab active:cursor-grabbing"
                                draggable
                                onDragStart={(e) => handleDragStart(e, displayAssets[0])}
                            >
                                <div className="aspect-video relative group">
                                    <img
                                        src={displayAssets[0].url}
                                        alt="Featured asset"
                                        className="w-full h-full object-cover"
                                    />
                                    {/* Action buttons */}
                                    <div className="absolute top-2 right-2 flex gap-1 z-10">
                                        <button
                                            onClick={() => toggleFavorite(displayAssets[0].id)}
                                            className="p-1.5 rounded-full bg-black/40 hover:bg-black/60 transition-colors"
                                        >
                                            <Star
                                                size={16}
                                                fill={displayAssets[0].isFavorite ? "#eab308" : "none"}
                                                className={displayAssets[0].isFavorite ? "text-yellow-500" : "text-white/70"}
                                            />
                                        </button>
                                        <button
                                            onClick={(e) => handleDelete(displayAssets[0].id, e)}
                                            className="p-1.5 rounded-full bg-black/40 hover:bg-red-500/80 transition-colors"
                                            title="Sil"
                                        >
                                            <Trash2 size={16} className="text-white/70" />
                                        </button>
                                    </div>
                                    {displayAssets[0].type === "video" && (
                                        <>
                                            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                                <div className="w-12 h-12 rounded-full bg-black/50 flex items-center justify-center">
                                                    <Play size={24} fill="white" className="text-white ml-1" />
                                                </div>
                                            </div>
                                            <div className="absolute bottom-2 left-2 px-2 py-1 rounded text-xs font-medium bg-black/60 text-white">
                                                VIDEO • {displayAssets[0].duration}
                                            </div>
                                        </>
                                    )}
                                    {/* Drag hint */}
                                    <div className="absolute bottom-2 right-2 px-2 py-1 rounded text-xs bg-black/60 text-white/70 opacity-0 group-hover:opacity-100 transition-opacity">
                                        Sürükle → Chat
                                    </div>
                                </div>
                                {displayAssets[0].label && (
                                    <div className="p-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
                                        ▪ {displayAssets[0].label}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Grid of smaller assets */}
                        <div className="grid grid-cols-2 gap-2">
                            {displayAssets.slice(1).map((asset) => (
                                <div
                                    key={asset.id}
                                    className="asset-card group cursor-grab active:cursor-grabbing"
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, asset)}
                                >
                                    <div className="aspect-square relative">
                                        <img
                                            src={asset.url}
                                            alt="Generated asset"
                                            className="w-full h-full object-cover"
                                        />

                                        {asset.type === "video" && (
                                            <div className="absolute top-2 left-2">
                                                <Play size={16} fill="white" className="text-white drop-shadow-lg" />
                                            </div>
                                        )}

                                        {/* Action buttons */}
                                        <div className="absolute top-2 right-2 flex gap-1">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); toggleFavorite(asset.id); }}
                                                className="p-1 rounded-full bg-black/40 hover:bg-black/60 transition-colors"
                                            >
                                                <Star
                                                    size={14}
                                                    fill={asset.isFavorite ? "#eab308" : "none"}
                                                    className={asset.isFavorite ? "text-yellow-500" : "text-white/70"}
                                                />
                                            </button>
                                            <button
                                                onClick={(e) => handleDelete(asset.id, e)}
                                                className="p-1 rounded-full bg-black/40 hover:bg-red-500/80 transition-colors opacity-0 group-hover:opacity-100"
                                                title="Sil"
                                            >
                                                <Trash2 size={14} className="text-white/70" />
                                            </button>
                                        </div>

                                        {/* Hover overlay with download */}
                                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                                            <span className="text-xs text-white/70 px-2 py-1 bg-black/50 rounded">Sürükle → Chat</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Bottom actions */}
            <div
                className="p-3 border-t flex items-center justify-between"
                style={{ borderColor: "var(--border)" }}
            >
                <div className="flex items-center gap-1">
                    <button
                        onClick={handleDownloadAll}
                        className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                        title="Tümünü İndir"
                    >
                        <Download size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                    <button
                        onClick={handleCopyLink}
                        className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                        title="Link Kopyala"
                    >
                        <Copy size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                    <button
                        onClick={handleShare}
                        className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                        title="Paylaş"
                    >
                        <Globe size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                </div>
                <button
                    className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                    title="Daha Fazla"
                >
                    <MoreHorizontal size={18} style={{ color: "var(--foreground-muted)" }} />
                </button>
            </div>
        </aside>
    );
}
