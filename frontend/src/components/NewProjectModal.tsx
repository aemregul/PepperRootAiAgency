"use client";

import { useState, useRef, useEffect } from "react";
import { X, FolderPlus } from "lucide-react";

interface NewProjectModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (name: string) => void;
}

export function NewProjectModal({ isOpen, onClose, onSubmit }: NewProjectModalProps) {
    const [projectName, setProjectName] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
        if (!isOpen) {
            setProjectName("");
        }
    }, [isOpen]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (projectName.trim()) {
            onSubmit(projectName.trim());
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
                className="relative w-full max-w-md rounded-xl shadow-2xl"
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
                <form onSubmit={handleSubmit} className="p-4">
                    <div className="mb-4">
                        <label className="block text-sm font-medium mb-2" style={{ color: "var(--foreground-muted)" }}>
                            Proje Adı
                        </label>
                        <input
                            ref={inputRef}
                            type="text"
                            value={projectName}
                            onChange={(e) => setProjectName(e.target.value)}
                            placeholder="Örn: Samsung Reklam Kampanyası"
                            className="w-full px-3 py-2 rounded-lg text-sm outline-none transition-all"
                            style={{
                                background: "var(--background)",
                                border: "1px solid var(--border)",
                                color: "var(--foreground)",
                            }}
                        />
                    </div>

                    <div className="flex gap-2 justify-end">
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
                            Oluştur
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
