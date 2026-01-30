"use client";

import { X, Moon, Sun, Palette, Bell, Lock, Info } from "lucide-react";
import { useTheme } from "./ThemeProvider";

interface SettingsModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
    const { theme, toggleTheme } = useTheme();

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
                    <h2 className="text-lg font-semibold">Ayarlar</h2>
                    <button
                        onClick={onClose}
                        className="p-1 rounded-lg hover:bg-[var(--background)] transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-4 space-y-4">
                    {/* Appearance */}
                    <div>
                        <div className="flex items-center gap-2 text-sm font-medium mb-3" style={{ color: "var(--foreground-muted)" }}>
                            <Palette size={16} />
                            <span>Görünüm</span>
                        </div>

                        {/* Theme Toggle */}
                        <div className="flex items-center justify-between p-3 rounded-lg" style={{ background: "var(--background)" }}>
                            <div className="flex items-center gap-2">
                                {theme === "dark" ? <Moon size={18} /> : <Sun size={18} />}
                                <span className="text-sm">Tema</span>
                            </div>
                            <button
                                onClick={toggleTheme}
                                className="relative w-14 h-7 rounded-full transition-all duration-300 ease-in-out"
                                style={{
                                    background: theme === "dark" ? "var(--accent)" : "rgba(120, 120, 128, 0.32)",
                                    boxShadow: "inset 0 0 0 1px rgba(0,0,0,0.1)"
                                }}
                            >
                                <div
                                    className="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-lg transition-all duration-300 ease-in-out"
                                    style={{
                                        left: theme === "dark" ? "30px" : "2px",
                                        boxShadow: "0 2px 4px rgba(0,0,0,0.2), 0 0 0 1px rgba(0,0,0,0.05)"
                                    }}
                                />
                            </button>
                        </div>
                        <p className="text-xs mt-1 px-1" style={{ color: "var(--foreground-muted)" }}>
                            {theme === "dark" ? "Koyu tema aktif" : "Açık tema aktif"}
                        </p>
                    </div>

                    {/* Notifications - Coming Soon */}
                    <div className="opacity-50">
                        <div className="flex items-center gap-2 text-sm font-medium mb-3" style={{ color: "var(--foreground-muted)" }}>
                            <Bell size={16} />
                            <span>Bildirimler</span>
                            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "var(--background)" }}>Yakında</span>
                        </div>
                    </div>

                    {/* Privacy - Coming Soon */}
                    <div className="opacity-50">
                        <div className="flex items-center gap-2 text-sm font-medium mb-3" style={{ color: "var(--foreground-muted)" }}>
                            <Lock size={16} />
                            <span>Gizlilik</span>
                            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "var(--background)" }}>Yakında</span>
                        </div>
                    </div>

                    {/* About */}
                    <div>
                        <div className="flex items-center gap-2 text-sm font-medium mb-3" style={{ color: "var(--foreground-muted)" }}>
                            <Info size={16} />
                            <span>Hakkında</span>
                        </div>
                        <div className="p-3 rounded-lg text-sm" style={{ background: "var(--background)", color: "var(--foreground-muted)" }}>
                            <p><strong>Pepper Root AI Agency</strong></p>
                            <p className="text-xs mt-1">Versiyon 1.0.0</p>
                            <p className="text-xs mt-1">Yapay zeka destekli görsel üretim platformu</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
