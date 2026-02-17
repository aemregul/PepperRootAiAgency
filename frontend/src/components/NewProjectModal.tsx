"use client";

import { useState, useRef, useEffect } from "react";
import { X, FolderPlus, Tag } from "lucide-react";

interface NewProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (name: string, description?: string, category?: string) => void;
}

const CATEGORIES = [
    { value: "reklam", label: "📢 Reklam Kampanyası", color: "#ef4444" },
    { value: "sosyal_medya", label: "📱 Sosyal Medya", color: "#3b82f6" },
    { value: "film", label: "🎬 Film / Video", color: "#a855f7" },
    { value: "kisisel", label: "🎨 Kişisel Proje", color: "#22c55e" },
    { value: "marka", label: "🏷️ Marka / Branding", color: "#f59e0b" },
    { value: "diger", label: "📂 Diğer", color: "#6b7280" },
];

export function NewProjectModal({ isOpen, onClose, onSubmit }: NewProjectModalProps) {
    const [projectName, setProjectName] = useState("");
    const [description, setDescription] = useState("");
    const [category, setCategory] = useState<string>("");
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
        if (!isOpen) {
            setProjectName("");
            setDescription("");
            setCategory("");
        }
    }, [isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (projectName.trim()) {
            onSubmit(
                projectName.trim(),
                description.trim() || undefined,
                category || undefined
            );
            onClose();
        }
    };

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
                className="relative w-full max-w-lg rounded-xl shadow-2xl"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="flex items-center gap-2">
                        <FolderPlus size={20} style={{ color: "var(--accent)" }} />
                        <h2 className="text-lg font-semibold">Yeni Proje</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-lg hover:bg-[var(--background)] transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    {/* Proje Adı */}
                    <div>
                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--foreground-muted)" }}>
                            Proje Adı *
                        </label>
                        <input
                            ref={inputRef}
                            type="text"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="Örn: Nike Yaz Koleksiyonu"
                            className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-all"
                            style={{
                                background: "var(--background)",
                                border: "1px solid var(--border)",
                                color: "var(--foreground)",
                            }}
                        />
                    </div>

                    {/* Açıklama */}
                    <div>
                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--foreground-muted)" }}>
                            Açıklama
                        </label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Bu proje ne hakkında? Asistan bu bilgiyi hatırlayacak..."
                            rows={2}
                            className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-all resize-none"
                            style={{
                                background: "var(--background)",
                                border: "1px solid var(--border)",
                                color: "var(--foreground)",
                            }}
                        />
                    </div>

                    {/* Kategori */}
                    <div>
                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--foreground-muted)" }}>
                            <Tag size={14} className="inline mr-1" />
                            Kategori
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                            {CATEGORIES.map((cat) => (
                                <button
                                    key={cat.value}
                                    type="button"
                                    onClick={() => setCategory(category === cat.value ? "" : cat.value)}
                                    className="px-3 py-2 rounded-lg text-xs font-medium transition-all text-left"
                                    style={{
                                        background: category === cat.value ? `${cat.color}20` : "var(--background)",
                                        border: `1px solid ${category === cat.value ? cat.color : "var(--border)"}`,
                                        color: category === cat.value ? cat.color : "var(--foreground-muted)",
                                    }}
                                >
                                    {cat.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-2 justify-end pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 rounded-lg text-sm transition-colors hover:bg-[var(--background)]"
                            style={{ color: "var(--foreground-muted)" }}
                        >
                            İptal
                        </button>
                        <button
                            type="submit"
                            disabled={!projectName.trim()}
                            className="px-4 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50"
                            style={{
                                background: "var(--accent)",
                                color: "var(--background)",
                            }}
                        >
                            Proje Oluştur
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
