"use client";

import { useState } from "react";
import { X, Trash2, RotateCcw, Clock, AlertCircle } from "lucide-react";

export interface TrashItem {
    id: string;
    name: string;
    type: "proje" | "karakter" | "lokasyon" | "wardrobe" | "plugin";
    deletedAt: Date;
    originalData: any;
}

interface TrashModalProps {
    isOpen: boolean;
    onClose: () => void;
    items: TrashItem[];
    onRestore: (item: TrashItem) => void;
    onPermanentDelete: (id: string) => void;
}

function getTimeRemaining(deletedAt: Date): string {
    const now = new Date();
    const deleteTime = new Date(deletedAt);
    deleteTime.setDate(deleteTime.getDate() + 3); // 3 gün sonra silinecek

    const diff = deleteTime.getTime() - now.getTime();
    if (diff <= 0) return "Siliniyor...";

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;

    if (days > 0) {
        return `${days} gün ${remainingHours} saat`;
    }
    return `${hours} saat`;
}

function getTypeLabel(type: TrashItem["type"]): string {
    const labels = {
        proje: "Proje",
        karakter: "Karakter",
        lokasyon: "Lokasyon",
        wardrobe: "Kıyafet",
        plugin: "Plugin"
    };
    return labels[type];
}

function getTypeColor(type: TrashItem["type"]): string {
    const colors = {
        proje: "#22c55e",
        karakter: "#8b5cf6",
        lokasyon: "#3b82f6",
        wardrobe: "#f59e0b",
        plugin: "#ec4899"
    };
    return colors[type];
}

export function TrashModal({
    isOpen,
    onClose,
    items,
    onRestore,
    onPermanentDelete
}: TrashModalProps) {
    const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-md"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="relative w-full max-w-lg max-h-[80vh] rounded-2xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-5 border-b"
                    style={{
                        borderColor: "var(--border)",
                        background: "linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, transparent 100%)"
                    }}
                >
                    <div className="flex items-center gap-3">
                        <div
                            className="p-2 rounded-xl"
                            style={{ background: "rgba(239, 68, 68, 0.2)" }}
                        >
                            <Trash2 size={24} className="text-red-500" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Çöp Kutusu</h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                {items.length} öğe • 3 gün sonra kalıcı silinir
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-xl hover:bg-[var(--background)] transition-all duration-200"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4 overflow-y-auto max-h-[calc(80vh-120px)]">
                    {items.length === 0 ? (
                        <div className="text-center py-12">
                            <Trash2 size={48} className="mx-auto mb-3 opacity-20" />
                            <p style={{ color: "var(--foreground-muted)" }}>
                                Çöp kutusu boş
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {items.map((item) => (
                                <div
                                    key={item.id}
                                    className="flex items-center justify-between p-3 rounded-xl transition-all"
                                    style={{ background: "var(--background)" }}
                                >
                                    <div className="flex items-center gap-3 flex-1 min-w-0">
                                        <div
                                            className="w-2 h-2 rounded-full shrink-0"
                                            style={{ background: getTypeColor(item.type) }}
                                        />
                                        <div className="flex-1 min-w-0">
                                            <div className="font-medium truncate">{item.name}</div>
                                            <div className="flex items-center gap-2 text-xs" style={{ color: "var(--foreground-muted)" }}>
                                                <span
                                                    className="px-1.5 py-0.5 rounded"
                                                    style={{ background: "var(--card)" }}
                                                >
                                                    {getTypeLabel(item.type)}
                                                </span>
                                                <span className="flex items-center gap-1">
                                                    <Clock size={10} />
                                                    {getTimeRemaining(item.deletedAt)}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-1 shrink-0">
                                        {/* Restore button */}
                                        <button
                                            onClick={() => onRestore(item)}
                                            className="p-2 rounded-lg hover:bg-green-500/20 transition-colors"
                                            title="Geri Yükle"
                                        >
                                            <RotateCcw size={16} className="text-green-500" />
                                        </button>

                                        {/* Permanent delete button */}
                                        {confirmDelete === item.id ? (
                                            <div className="flex items-center gap-1">
                                                <button
                                                    onClick={() => {
                                                        onPermanentDelete(item.id);
                                                        setConfirmDelete(null);
                                                    }}
                                                    className="px-2 py-1 text-xs rounded bg-red-500 text-white hover:bg-red-600 transition-colors"
                                                >
                                                    Sil
                                                </button>
                                                <button
                                                    onClick={() => setConfirmDelete(null)}
                                                    className="px-2 py-1 text-xs rounded hover:bg-[var(--card)] transition-colors"
                                                >
                                                    İptal
                                                </button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => setConfirmDelete(item.id)}
                                                className="p-2 rounded-lg hover:bg-red-500/20 transition-colors"
                                                title="Kalıcı Sil"
                                            >
                                                <Trash2 size={16} className="text-red-400" />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer info */}
                {items.length > 0 && (
                    <div
                        className="px-4 py-3 border-t flex items-center gap-2 text-xs"
                        style={{ borderColor: "var(--border)", color: "var(--foreground-muted)" }}
                    >
                        <AlertCircle size={14} />
                        <span>Öğeler 3 gün sonra otomatik olarak kalıcı silinir.</span>
                    </div>
                )}
            </div>
        </div>
    );
}
