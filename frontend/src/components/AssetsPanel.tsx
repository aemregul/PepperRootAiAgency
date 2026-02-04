"use client";

import { useState, useEffect } from "react";
import { Download, Copy, Globe, RefreshCw, Play, ChevronLeft, ChevronRight, MoreHorizontal, Star, Loader2, Trash2, X, ZoomIn, Shirt, CheckSquare, Square } from "lucide-react";
import { getAssets, GeneratedAsset, deleteAsset, saveAssetToWardrobe } from "@/lib/api";
import { useToast } from "./ToastProvider";

interface Asset {
    id: string;
    url: string;
    type: "image" | "video";
    label?: string;
    duration?: string;
    isFavorite?: boolean;
    savedToWardrobe?: boolean;
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
    const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
    const [isSelectMode, setIsSelectMode] = useState(false);
    const toast = useToast();

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
        e.preventDefault();

        const success = await deleteAsset(assetId);
        if (success) {
            setAssets(prev => prev.filter(a => a.id !== assetId));
            toast.success('Asset silindi');
        } else {
            toast.error('Silme başarısız');
        }
    };

    // Toggle selection for bulk operations
    const toggleSelection = (assetId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedIds(prev => {
            const newSet = new Set(prev);
            if (newSet.has(assetId)) {
                newSet.delete(assetId);
            } else {
                newSet.add(assetId);
            }
            return newSet;
        });
    };

    // Select/deselect all
    const toggleSelectAll = () => {
        if (selectedIds.size === displayAssets.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(displayAssets.map(a => a.id)));
        }
    };

    // Bulk delete
    const handleBulkDelete = async () => {
        if (selectedIds.size === 0) return;

        let successCount = 0;
        for (const assetId of selectedIds) {
            const success = await deleteAsset(assetId);
            if (success) successCount++;
        }

        setAssets(prev => prev.filter(a => !selectedIds.has(a.id)));
        setSelectedIds(new Set());
        setIsSelectMode(false);
        toast.success(`${successCount} asset silindi`);
    };

    // Drag start for chat drop
    const handleDragStart = (e: React.DragEvent, asset: Asset) => {
        e.dataTransfer.setData('text/plain', asset.url);
        e.dataTransfer.setData('application/x-asset-url', asset.url);
        e.dataTransfer.setData('application/x-asset-id', asset.id);
        e.dataTransfer.effectAllowed = 'copy';
    };

    // Save to wardrobe
    const handleSaveToWardrobe = async (asset: Asset, e: React.MouseEvent) => {
        e.stopPropagation();
        e.preventDefault();

        if (!sessionId) return;

        try {
            const wardrobeName = asset.label || `Wardrobe_${asset.id.slice(0, 6)}`;
            await saveAssetToWardrobe(sessionId, asset.url, wardrobeName);
            // Visual feedback - mark as saved
            setAssets(prev => prev.map(a =>
                a.id === asset.id ? { ...a, savedToWardrobe: true } : a
            ));
            // Could also trigger a sidebar refresh here
        } catch (error) {
            console.error('Wardrobe kaydetme hatası:', error);
        }
    };

    // Download all assets
    const handleDownloadAll = async () => {
        if (displayAssets.length === 0) {
            toast.warning('İndirilecek asset yok');
            return;
        }

        toast.info(`${displayAssets.length} asset indiriliyor...`);
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
        toast.success('İndirme tamamlandı');
    };

    // Copy first asset URL to clipboard
    const handleCopyLink = async () => {
        if (displayAssets.length === 0) {
            toast.warning('Kopyalanacak asset yok');
            return;
        }
        try {
            await navigator.clipboard.writeText(displayAssets[0].url);
            toast.success('Link kopyalandı!');
        } catch (error) {
            console.error('Copy failed:', error);
            toast.error('Kopyalama başarısız');
        }
    };

    // Share via Web Share API
    const handleShare = async () => {
        if (displayAssets.length === 0) {
            toast.warning('Paylaşılacak asset yok');
            return;
        }

        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'Pepper Root AI Agency - Generated Assets',
                    text: 'AI ile oluşturulmuş görseller',
                    url: displayAssets[0].url
                });
                toast.success('Paylaşıldı!');
            } catch (error) {
                // User cancelled
                console.log('Share cancelled');
            }
        } else {
            // Fallback: copy to clipboard
            handleCopyLink();
        }
    };

    const displayAssets = showFavoritesOnly ? assets.filter(a => a.isFavorite) : assets;
    const favoritesCount = assets.filter(a => a.isFavorite).length;

    // Navigate between assets in lightbox
    const navigateLightbox = (direction: 'prev' | 'next') => {
        if (!selectedAsset) return;
        const currentIndex = displayAssets.findIndex(a => a.id === selectedAsset.id);
        const newIndex = direction === 'next'
            ? (currentIndex + 1) % displayAssets.length
            : (currentIndex - 1 + displayAssets.length) % displayAssets.length;
        setSelectedAsset(displayAssets[newIndex]);
    };

    // Download single asset
    const downloadAsset = async (asset: Asset) => {
        try {
            const response = await fetch(asset.url);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `pepper_asset_${asset.id}.${asset.type === 'video' ? 'mp4' : 'png'}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Download failed:', error);
        }
    };

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
        <>
            {/* Lightbox Modal */}
            {selectedAsset && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
                    onClick={() => setSelectedAsset(null)}
                >
                    {/* Close button */}
                    <button
                        onClick={() => setSelectedAsset(null)}
                        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors z-10"
                    >
                        <X size={24} className="text-white" />
                    </button>

                    {/* Previous button */}
                    {displayAssets.length > 1 && (
                        <button
                            onClick={(e) => { e.stopPropagation(); navigateLightbox('prev'); }}
                            className="absolute left-4 p-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                        >
                            <ChevronLeft size={28} className="text-white" />
                        </button>
                    )}

                    {/* Image */}
                    <div
                        className="max-w-[90vw] max-h-[85vh] relative"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <img
                            src={selectedAsset.url}
                            alt="Full size asset"
                            className="max-w-full max-h-[85vh] object-contain rounded-lg shadow-2xl"
                        />

                        {/* Bottom controls */}
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 rounded-full bg-black/60">
                            <button
                                onClick={() => downloadAsset(selectedAsset)}
                                className="p-2 rounded-full hover:bg-white/10 transition-colors"
                                title="İndir"
                            >
                                <Download size={18} className="text-white" />
                            </button>
                            <button
                                onClick={() => toggleFavorite(selectedAsset.id)}
                                className="p-2 rounded-full hover:bg-white/10 transition-colors"
                                title="Favori"
                            >
                                <Star
                                    size={18}
                                    fill={selectedAsset.isFavorite ? "#eab308" : "none"}
                                    className={selectedAsset.isFavorite ? "text-yellow-500" : "text-white"}
                                />
                            </button>
                            <span className="text-white/70 text-sm px-2">
                                {displayAssets.findIndex(a => a.id === selectedAsset.id) + 1} / {displayAssets.length}
                            </span>
                        </div>
                    </div>

                    {/* Next button */}
                    {displayAssets.length > 1 && (
                        <button
                            onClick={(e) => { e.stopPropagation(); navigateLightbox('next'); }}
                            className="absolute right-4 p-3 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
                        >
                            <ChevronRight size={28} className="text-white" />
                        </button>
                    )}
                </div>
            )}

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
                    {isSelectMode ? (
                        <>
                            <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">{selectedIds.size} seçili</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={toggleSelectAll}
                                    className="p-1.5 rounded-lg hover:bg-[var(--card)] transition-colors text-xs"
                                    title={selectedIds.size === displayAssets.length ? "Seçimi Kaldır" : "Tümünü Seç"}
                                >
                                    {selectedIds.size === displayAssets.length ? <CheckSquare size={16} /> : <Square size={16} />}
                                </button>
                                <button
                                    onClick={handleBulkDelete}
                                    disabled={selectedIds.size === 0}
                                    className="p-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/40 transition-colors disabled:opacity-50"
                                    title="Seçilenleri Sil"
                                >
                                    <Trash2 size={16} className="text-red-500" />
                                </button>
                                <button
                                    onClick={() => { setIsSelectMode(false); setSelectedIds(new Set()); }}
                                    className="p-1.5 rounded-lg hover:bg-[var(--card)] transition-colors"
                                    title="İptal"
                                >
                                    <X size={16} />
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <h2 className="font-medium">Media Assets</h2>
                            <div className="flex items-center gap-1">
                                {/* Select Mode Toggle */}
                                {displayAssets.length > 0 && (
                                    <button
                                        onClick={() => setIsSelectMode(true)}
                                        className="p-1.5 rounded-lg hover:bg-[var(--card)] transition-colors"
                                        title="Çoklu Seçim"
                                    >
                                        <CheckSquare size={16} style={{ color: "var(--foreground-muted)" }} />
                                    </button>
                                )}
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
                        </>
                    )}
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
                                    className="asset-card cursor-pointer"
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, displayAssets[0])}
                                    onClick={() => setSelectedAsset(displayAssets[0])}
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
                                                onClick={(e) => handleSaveToWardrobe(displayAssets[0], e)}
                                                className={`p-1.5 rounded-full transition-colors ${displayAssets[0].savedToWardrobe ? 'bg-emerald-500/80' : 'bg-black/40 hover:bg-emerald-500/60'}`}
                                                title="Gardroba Kaydet"
                                            >
                                                <Shirt size={16} className={displayAssets[0].savedToWardrobe ? "text-white" : "text-white/70"} />
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
                                        className="asset-card group cursor-pointer"
                                        draggable
                                        onDragStart={(e) => handleDragStart(e, asset)}
                                        onClick={() => setSelectedAsset(asset)}
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
                                                    onClick={(e) => handleSaveToWardrobe(asset, e)}
                                                    className={`p-1 rounded-full transition-colors opacity-0 group-hover:opacity-100 ${asset.savedToWardrobe ? 'bg-emerald-500/80 opacity-100' : 'bg-black/40 hover:bg-emerald-500/60'}`}
                                                    title="Gardroba Kaydet"
                                                >
                                                    <Shirt size={14} className={asset.savedToWardrobe ? "text-white" : "text-white/70"} />
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
        </>
    );
}
