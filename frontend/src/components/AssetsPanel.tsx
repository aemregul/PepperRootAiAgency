"use client";

import { useState } from "react";
import { Download, Heart, Play, ChevronLeft, ChevronRight } from "lucide-react";

interface Asset {
    id: string;
    url: string;
    type: "image" | "video";
    isFavorite: boolean;
    createdAt: Date;
}

// Mock data
const mockAssets: Asset[] = [
    {
        id: "1",
        url: "https://fal.media/files/penguin/ttzc_uRNnT2DW-b0c-WRD.png",
        type: "image",
        isFavorite: false,
        createdAt: new Date(),
    },
    {
        id: "2",
        url: "https://fal.media/files/tiger/DL-2D_z3wVHxM1OPJVYHS.png",
        type: "image",
        isFavorite: true,
        createdAt: new Date(),
    },
    {
        id: "3",
        url: "https://fal.media/files/lion/VoLY3j7gPj_rEV9lqTaVB.png",
        type: "image",
        isFavorite: false,
        createdAt: new Date(),
    },
    {
        id: "4",
        url: "https://fal.media/files/elephant/6Xbc7RaBCW8dFx-xgG8d5.png",
        type: "image",
        isFavorite: false,
        createdAt: new Date(),
    },
];

interface AssetsPanelProps {
    collapsed?: boolean;
    onToggle?: () => void;
}

export function AssetsPanel({ collapsed = false, onToggle }: AssetsPanelProps) {
    const [assets, setAssets] = useState<Asset[]>(mockAssets);

    const toggleFavorite = (id: string) => {
        setAssets((prev) =>
            prev.map((asset) =>
                asset.id === id ? { ...asset, isFavorite: !asset.isFavorite } : asset
            )
        );
    };

    const downloadAsset = (url: string) => {
        window.open(url, "_blank");
    };

    if (collapsed) {
        return (
            <button
                onClick={onToggle}
                className="hidden lg:flex fixed right-0 top-1/2 -translate-y-1/2 p-2 rounded-l-lg z-30"
                style={{ background: "var(--card)" }}
            >
                <ChevronLeft size={20} />
            </button>
        );
    }

    return (
        <aside
            className="
        hidden lg:flex flex-col
        w-[320px] xl:w-[380px]
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
                <h2 className="font-semibold">Üretilen İçerikler</h2>
                <button
                    onClick={onToggle}
                    className="p-1.5 rounded-lg hover:bg-[var(--card)] transition-colors"
                >
                    <ChevronRight size={18} />
                </button>
            </header>

            {/* Assets Grid */}
            <div className="flex-1 overflow-y-auto p-4">
                {assets.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <p style={{ color: "var(--foreground-muted)" }}>
                            Henüz içerik üretilmedi
                        </p>
                        <p className="text-sm mt-1" style={{ color: "var(--foreground-muted)" }}>
                            Chat&apos;te bir şeyler isteyin!
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-3">
                        {assets.map((asset) => (
                            <div
                                key={asset.id}
                                className="group relative rounded-xl overflow-hidden"
                                style={{ background: "var(--card)" }}
                            >
                                {/* Thumbnail */}
                                <div className="aspect-square relative">
                                    <img
                                        src={asset.url}
                                        alt="Generated asset"
                                        className="w-full h-full object-cover"
                                    />

                                    {/* Video play icon */}
                                    {asset.type === "video" && (
                                        <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                                            <Play size={32} fill="white" className="text-white" />
                                        </div>
                                    )}

                                    {/* Hover overlay */}
                                    <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                                        <button
                                            onClick={() => downloadAsset(asset.url)}
                                            className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
                                            title="İndir"
                                        >
                                            <Download size={18} className="text-white" />
                                        </button>
                                        <button
                                            onClick={() => toggleFavorite(asset.id)}
                                            className="p-2 rounded-lg bg-white/20 hover:bg-white/30 transition-colors"
                                            title="Favorile"
                                        >
                                            <Heart
                                                size={18}
                                                className={asset.isFavorite ? "text-red-500" : "text-white"}
                                                fill={asset.isFavorite ? "currentColor" : "none"}
                                            />
                                        </button>
                                    </div>
                                </div>

                                {/* Actions (mobile visible) */}
                                <div
                                    className="lg:hidden flex items-center justify-between p-2"
                                    style={{ background: "var(--card)" }}
                                >
                                    <button
                                        onClick={() => downloadAsset(asset.url)}
                                        className="flex items-center gap-1 text-xs px-2 py-1 rounded"
                                        style={{ color: "var(--accent)" }}
                                    >
                                        <Download size={14} />
                                        İndir
                                    </button>
                                    <button
                                        onClick={() => toggleFavorite(asset.id)}
                                        className="flex items-center gap-1 text-xs px-2 py-1 rounded"
                                        style={{ color: asset.isFavorite ? "#ef4444" : "var(--foreground-muted)" }}
                                    >
                                        <Heart size={14} fill={asset.isFavorite ? "currentColor" : "none"} />
                                        Favori
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </aside>
    );
}
