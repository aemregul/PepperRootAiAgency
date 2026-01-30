"use client";

import { useState } from "react";
import { X, Shield, Puzzle, Users, Activity, Database, Zap } from "lucide-react";

interface AdminPanelModalProps {
    isOpen: boolean;
    onClose: () => void;
}

// Mock plugin data
const plugins = [
    { id: "p1", name: "fal.ai", status: "active", type: "Görsel", requests: 128 },
    { id: "p2", name: "Minimax", status: "active", type: "Video", requests: 45 },
    { id: "p3", name: "Anthropic Claude", status: "active", type: "LLM", requests: 512 },
];

// Mock stats
const stats = {
    totalImages: 156,
    totalVideos: 23,
    totalCharacters: 5,
    totalLocations: 3,
    apiCalls: 685,
};

export function AdminPanelModal({ isOpen, onClose }: AdminPanelModalProps) {
    const [activeTab, setActiveTab] = useState<"overview" | "plugins" | "usage">("overview");

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="relative w-full max-w-2xl max-h-[80vh] rounded-xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="flex items-center gap-2">
                        <Shield size={20} style={{ color: "var(--accent)" }} />
                        <h2 className="text-lg font-semibold">Admin Panel</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-lg hover:bg-[var(--background)] transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b" style={{ borderColor: "var(--border)" }}>
                    {[
                        { id: "overview", label: "Genel Bakış", icon: Activity },
                        { id: "plugins", label: "Pluginler", icon: Puzzle },
                        { id: "usage", label: "Kullanım", icon: Database },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`flex items-center gap-2 px-4 py-3 text-sm transition-colors ${activeTab === tab.id
                                    ? "border-b-2"
                                    : "opacity-60 hover:opacity-100"
                                }`}
                            style={{
                                borderColor: activeTab === tab.id ? "var(--accent)" : "transparent",
                            }}
                        >
                            <tab.icon size={16} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="p-4 overflow-y-auto max-h-[60vh]">
                    {activeTab === "overview" && (
                        <div className="space-y-4">
                            <h3 className="text-sm font-medium" style={{ color: "var(--foreground-muted)" }}>
                                İstatistikler
                            </h3>
                            <div className="grid grid-cols-3 gap-3">
                                {[
                                    { label: "Görseller", value: stats.totalImages, icon: "🖼️" },
                                    { label: "Videolar", value: stats.totalVideos, icon: "🎬" },
                                    { label: "Karakterler", value: stats.totalCharacters, icon: "👤" },
                                    { label: "Lokasyonlar", value: stats.totalLocations, icon: "📍" },
                                    { label: "API Çağrısı", value: stats.apiCalls, icon: "⚡" },
                                    { label: "Aktif Plugin", value: plugins.length, icon: "🧩" },
                                ].map((stat) => (
                                    <div
                                        key={stat.label}
                                        className="p-3 rounded-lg text-center"
                                        style={{ background: "var(--background)" }}
                                    >
                                        <div className="text-2xl mb-1">{stat.icon}</div>
                                        <div className="text-xl font-bold">{stat.value}</div>
                                        <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                            {stat.label}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {activeTab === "plugins" && (
                        <div className="space-y-3">
                            {plugins.map((plugin) => (
                                <div
                                    key={plugin.id}
                                    className="flex items-center justify-between p-3 rounded-lg"
                                    style={{ background: "var(--background)" }}
                                >
                                    <div className="flex items-center gap-3">
                                        <Puzzle size={20} style={{ color: "var(--accent)" }} />
                                        <div>
                                            <div className="font-medium">{plugin.name}</div>
                                            <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                                {plugin.type} • {plugin.requests} istek
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span
                                            className="px-2 py-1 text-xs rounded-full"
                                            style={{
                                                background: plugin.status === "active" ? "rgba(34, 197, 94, 0.2)" : "rgba(239, 68, 68, 0.2)",
                                                color: plugin.status === "active" ? "#22c55e" : "#ef4444",
                                            }}
                                        >
                                            {plugin.status === "active" ? "Aktif" : "Pasif"}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {activeTab === "usage" && (
                        <div className="space-y-4">
                            <div className="p-4 rounded-lg" style={{ background: "var(--background)" }}>
                                <div className="flex items-center gap-2 mb-2">
                                    <Zap size={16} style={{ color: "var(--accent)" }} />
                                    <span className="font-medium">API Kullanımı</span>
                                </div>
                                <div className="text-2xl font-bold">{stats.apiCalls}</div>
                                <div className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                                    Bu ayki toplam istek
                                </div>
                            </div>

                            <div className="p-4 rounded-lg" style={{ background: "var(--background)" }}>
                                <div className="flex items-center gap-2 mb-2">
                                    <Users size={16} style={{ color: "var(--accent)" }} />
                                    <span className="font-medium">Entity Sayısı</span>
                                </div>
                                <div className="text-2xl font-bold">
                                    {stats.totalCharacters + stats.totalLocations}
                                </div>
                                <div className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                                    {stats.totalCharacters} karakter, {stats.totalLocations} lokasyon
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
