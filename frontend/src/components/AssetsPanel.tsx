"use client";

import { useState } from "react";
import { Download, Copy, Globe, RefreshCw, Play, ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react";

interface Asset {
    id: string;
    url: string;
    type: "image" | "video";
    label?: string;
    duration?: string;
}

// Mock data with more realistic images
const mockAssets: Asset[] = [
    {
        id: "1",
        url: "https://fal.media/files/penguin/ttzc_uRNnT2DW-b0c-WRD.png",
        type: "video",
        label: "Location_kitchen at night",
        duration: "3:00",
    },
    {
        id: "2",
        url: "https://fal.media/files/tiger/DL-2D_z3wVHxM1OPJVYHS.png",
        type: "image",
    },
    {
        id: "3",
        url: "https://fal.media/files/lion/VoLY3j7gPj_rEV9lqTaVB.png",
        type: "image",
    },
    {
        id: "4",
        url: "https://fal.media/files/elephant/6Xbc7RaBCW8dFx-xgG8d5.png",
        type: "image",
    },
    {
        id: "5",
        url: "https://fal.media/files/penguin/ttzc_uRNnT2DW-b0c-WRD.png",
        type: "image",
    },
    {
        id: "6",
        url: "https://fal.media/files/tiger/DL-2D_z3wVHxM1OPJVYHS.png",
        type: "image",
    },
];

interface AssetsPanelProps {
    collapsed?: boolean;
    onToggle?: () => void;
}

export function AssetsPanel({ collapsed = false, onToggle }: AssetsPanelProps) {
    const [assets] = useState<Asset[]>(mockAssets);

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
                {assets.length === 0 ? (
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
                        {assets[0] && (
                            <div className="asset-card">
                                <div className="aspect-video relative">
                                    <img
                                        src={assets[0].url}
                                        alt="Featured asset"
                                        className="w-full h-full object-cover"
                                    />
                                    {assets[0].type === "video" && (
                                        <>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <div className="w-12 h-12 rounded-full bg-black/50 flex items-center justify-center">
                                                    <Play size={24} fill="white" className="text-white ml-1" />
                                                </div>
                                            </div>
                                            <div className="absolute bottom-2 left-2 px-2 py-1 rounded text-xs font-medium bg-black/60 text-white">
                                                VIDEO • {assets[0].duration}
                                            </div>
                                        </>
                                    )}
                                </div>
                                {assets[0].label && (
                                    <div className="p-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
                                        ▪ {assets[0].label}
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Grid of smaller assets */}
                        <div className="grid grid-cols-2 gap-2">
                            {assets.slice(1).map((asset) => (
                                <div key={asset.id} className="asset-card group">
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

                                        {/* Hover overlay */}
                                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                            <button className="p-2 rounded-lg bg-white/20 hover:bg-white/30">
                                                <Download size={16} className="text-white" />
                                            </button>
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
                    <button className="p-2 rounded-lg hover:bg-[var(--card)]" title="Download all">
                        <Download size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-[var(--card)]" title="Copy link">
                        <Copy size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                    <button className="p-2 rounded-lg hover:bg-[var(--card)]" title="Share">
                        <Globe size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                </div>
                <button className="p-2 rounded-lg hover:bg-[var(--card)]">
                    <MoreHorizontal size={18} style={{ color: "var(--foreground-muted)" }} />
                </button>
            </div>
        </aside>
    );
}
