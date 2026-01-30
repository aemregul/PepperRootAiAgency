"use client";

import { useState } from "react";
import { X, Sparkles, Share2, Download, Check, Users, MapPin, Clock, Camera, Palette, FileJson } from "lucide-react";

export interface CreativePlugin {
    id: string;
    name: string;
    description: string;
    author: string;
    isPublic: boolean;
    preview?: string;
    config: {
        character?: {
            id: string;
            name: string;
            isVariable: boolean;
        };
        location?: {
            id: string;
            name: string;
            settings: string;
        };
        timeOfDay?: string;
        cameraAngles?: string[];
        style?: string;
        promptTemplate?: string;
    };
    createdAt: Date;
    downloads: number;
    rating: number;
}

// =====================================================
// 1. SAVE PLUGIN MODAL (AI tarafından tetiklenir)
// =====================================================
interface SavePluginModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (name: string, isPublic: boolean) => void;
    suggestedName?: string;
    pluginPreview: Partial<CreativePlugin["config"]>;
}

export function SavePluginModal({ isOpen, onClose, onSave, suggestedName, pluginPreview }: SavePluginModalProps) {
    const [name, setName] = useState(suggestedName || "");
    const [isPublic, setIsPublic] = useState(false);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose} />

            <div
                className="relative w-full max-w-md rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="p-5 border-b"
                    style={{ borderColor: "var(--border)", background: "linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, transparent 100%)" }}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
                            <Sparkles size={24} className="text-purple-500" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold">Plugin Olarak Kaydet</h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Bu kombinasyonu kaydet ve tekrar kullan
                            </p>
                        </div>
                    </div>
                </div>

                {/* Preview */}
                <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="text-xs font-medium mb-2" style={{ color: "var(--foreground-muted)" }}>
                        Algılanan Ayarlar:
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {pluginPreview.character && (
                            <span className="px-2 py-1 text-xs rounded-lg flex items-center gap-1" style={{ background: "var(--background)" }}>
                                <Users size={12} /> {pluginPreview.character.name}
                            </span>
                        )}
                        {pluginPreview.location && (
                            <span className="px-2 py-1 text-xs rounded-lg flex items-center gap-1" style={{ background: "var(--background)" }}>
                                <MapPin size={12} /> {pluginPreview.location.name}
                            </span>
                        )}
                        {pluginPreview.timeOfDay && (
                            <span className="px-2 py-1 text-xs rounded-lg flex items-center gap-1" style={{ background: "var(--background)" }}>
                                <Clock size={12} /> {pluginPreview.timeOfDay}
                            </span>
                        )}
                        {pluginPreview.cameraAngles && pluginPreview.cameraAngles.length > 0 && (
                            <span className="px-2 py-1 text-xs rounded-lg flex items-center gap-1" style={{ background: "var(--background)" }}>
                                <Camera size={12} /> {pluginPreview.cameraAngles.length} açı
                            </span>
                        )}
                        {pluginPreview.style && (
                            <span className="px-2 py-1 text-xs rounded-lg flex items-center gap-1" style={{ background: "var(--background)" }}>
                                <Palette size={12} /> {pluginPreview.style}
                            </span>
                        )}
                    </div>
                </div>

                {/* Form */}
                <div className="p-4 space-y-4">
                    <div>
                        <label className="text-sm font-medium mb-2 block">Plugin Adı</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="Örn: Mutfak Akşam Seti"
                            className="w-full px-4 py-3 rounded-xl text-sm"
                            style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                            autoFocus
                        />
                    </div>

                    <div
                        className="flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-all"
                        style={{ background: isPublic ? "rgba(139, 92, 246, 0.1)" : "var(--background)" }}
                        onClick={() => setIsPublic(!isPublic)}
                    >
                        <div
                            className={`w-5 h-5 rounded flex items-center justify-center transition-all ${isPublic ? "bg-purple-500" : ""}`}
                            style={!isPublic ? { border: "2px solid var(--border)" } : {}}
                        >
                            {isPublic && <Check size={14} className="text-white" />}
                        </div>
                        <div className="flex-1">
                            <div className="font-medium text-sm flex items-center gap-2">
                                <Share2 size={14} />
                                Marketplace'te Paylaş
                            </div>
                            <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Diğer kullanıcılar bu plugin'i görüp kullanabilir
                            </div>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 p-4 border-t" style={{ borderColor: "var(--border)" }}>
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2.5 text-sm rounded-xl hover:bg-[var(--background)] transition-colors"
                        style={{ border: "1px solid var(--border)" }}
                    >
                        İptal
                    </button>
                    <button
                        onClick={() => { onSave(name, isPublic); onClose(); }}
                        disabled={!name.trim()}
                        className="flex-1 px-4 py-2.5 text-sm font-medium rounded-xl transition-colors disabled:opacity-50"
                        style={{ background: "var(--accent)", color: "var(--background)" }}
                    >
                        Kaydet
                    </button>
                </div>
            </div>
        </div>
    );
}

// =====================================================
// 2. PLUGIN DETAIL MODAL (Tıklayınca açılır)
// =====================================================
interface PluginDetailModalProps {
    isOpen: boolean;
    onClose: () => void;
    plugin: CreativePlugin | null;
    onDelete?: (id: string) => void;
    onUse?: (plugin: CreativePlugin) => void;
}

export function PluginDetailModal({ isOpen, onClose, plugin, onDelete, onUse }: PluginDetailModalProps) {
    if (!isOpen || !plugin) return null;

    const handleDownload = () => {
        const pluginData = {
            name: plugin.name,
            description: plugin.description,
            version: "1.0",
            author: plugin.author,
            createdAt: plugin.createdAt,
            config: plugin.config
        };

        const blob = new Blob([JSON.stringify(pluginData, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${plugin.name.toLowerCase().replace(/\s+/g, "_")}.pepper-plugin.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose} />

            <div
                className="relative w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-5 border-b"
                    style={{ borderColor: "var(--border)", background: "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%)" }}
                >
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl" style={{ background: "rgba(139, 92, 246, 0.2)" }}>
                            <Sparkles size={24} className="text-purple-500" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold">{plugin.name}</h2>
                            <div className="flex items-center gap-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
                                <span>by {plugin.author}</span>
                                {plugin.isPublic && (
                                    <span className="px-1.5 py-0.5 rounded" style={{ background: "rgba(139, 92, 246, 0.2)", color: "#8b5cf6" }}>
                                        Public
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 rounded-xl hover:bg-[var(--background)] transition-all">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-5 space-y-4">
                    {plugin.description && (
                        <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                            {plugin.description}
                        </p>
                    )}

                    {/* Config Details */}
                    <div className="space-y-3">
                        <h3 className="text-sm font-medium">Konfigürasyon</h3>

                        <div className="grid grid-cols-2 gap-2">
                            {plugin.config.character && (
                                <div className="p-3 rounded-xl" style={{ background: "var(--background)" }}>
                                    <div className="flex items-center gap-2 text-xs mb-1" style={{ color: "var(--foreground-muted)" }}>
                                        <Users size={12} /> Karakter
                                    </div>
                                    <div className="text-sm font-medium">
                                        {plugin.config.character.isVariable ? "🔄 Değişken" : plugin.config.character.name}
                                    </div>
                                </div>
                            )}

                            {plugin.config.location && (
                                <div className="p-3 rounded-xl" style={{ background: "var(--background)" }}>
                                    <div className="flex items-center gap-2 text-xs mb-1" style={{ color: "var(--foreground-muted)" }}>
                                        <MapPin size={12} /> Lokasyon
                                    </div>
                                    <div className="text-sm font-medium">{plugin.config.location.name}</div>
                                </div>
                            )}

                            {plugin.config.timeOfDay && (
                                <div className="p-3 rounded-xl" style={{ background: "var(--background)" }}>
                                    <div className="flex items-center gap-2 text-xs mb-1" style={{ color: "var(--foreground-muted)" }}>
                                        <Clock size={12} /> Zaman
                                    </div>
                                    <div className="text-sm font-medium">{plugin.config.timeOfDay}</div>
                                </div>
                            )}

                            {plugin.config.style && (
                                <div className="p-3 rounded-xl" style={{ background: "var(--background)" }}>
                                    <div className="flex items-center gap-2 text-xs mb-1" style={{ color: "var(--foreground-muted)" }}>
                                        <Palette size={12} /> Stil
                                    </div>
                                    <div className="text-sm font-medium">{plugin.config.style}</div>
                                </div>
                            )}
                        </div>

                        {plugin.config.cameraAngles && plugin.config.cameraAngles.length > 0 && (
                            <div className="p-3 rounded-xl" style={{ background: "var(--background)" }}>
                                <div className="flex items-center gap-2 text-xs mb-2" style={{ color: "var(--foreground-muted)" }}>
                                    <Camera size={12} /> Kamera Açıları
                                </div>
                                <div className="flex flex-wrap gap-1">
                                    {plugin.config.cameraAngles.map((angle, i) => (
                                        <span key={i} className="px-2 py-1 text-xs rounded" style={{ background: "var(--card)" }}>
                                            {angle}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {plugin.config.promptTemplate && (
                            <div className="p-3 rounded-xl" style={{ background: "var(--background)" }}>
                                <div className="text-xs mb-2" style={{ color: "var(--foreground-muted)" }}>
                                    Prompt Şablonu
                                </div>
                                <code className="text-xs font-mono block" style={{ color: "var(--accent)" }}>
                                    {plugin.config.promptTemplate}
                                </code>
                            </div>
                        )}
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 p-4 border-t" style={{ borderColor: "var(--border)" }}>
                    <button
                        onClick={handleDownload}
                        className="flex items-center gap-2 px-4 py-2.5 text-sm rounded-xl hover:bg-[var(--background)] transition-colors"
                        style={{ border: "1px solid var(--border)" }}
                    >
                        <FileJson size={16} />
                        JSON İndir
                    </button>

                    {onDelete && (
                        <button
                            onClick={() => { onDelete(plugin.id); onClose(); }}
                            className="px-4 py-2.5 text-sm rounded-xl hover:bg-red-500/20 text-red-400 transition-colors"
                        >
                            Sil
                        </button>
                    )}

                    <div className="flex-1" />

                    {onUse && (
                        <button
                            onClick={() => { onUse(plugin); onClose(); }}
                            className="px-6 py-2.5 text-sm font-medium rounded-xl transition-colors flex items-center gap-2"
                            style={{ background: "var(--accent)", color: "var(--background)" }}
                        >
                            <Sparkles size={16} />
                            Kullan
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
