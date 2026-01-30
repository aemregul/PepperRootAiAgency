"use client";

import { X, AlertTriangle } from "lucide-react";

interface ConfirmDeleteModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    itemName: string;
    itemType: string; // "karakter", "proje", "lokasyon", etc.
}

export function ConfirmDeleteModal({
    isOpen,
    onClose,
    onConfirm,
    itemName,
    itemType
}: ConfirmDeleteModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="relative w-full max-w-sm rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div className="p-5 text-center">
                    <div
                        className="w-14 h-14 mx-auto mb-4 rounded-full flex items-center justify-center"
                        style={{ background: "rgba(239, 68, 68, 0.1)" }}
                    >
                        <AlertTriangle size={28} className="text-red-500" />
                    </div>

                    <h3 className="text-lg font-semibold mb-2">Silmek istediğinize emin misiniz?</h3>
                    <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                        <span className="font-medium" style={{ color: "var(--foreground)" }}>
                            {itemName}
                        </span>
                        {" "}adlı {itemType} çöp kutusuna taşınacak.
                    </p>
                    <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                        3 gün içinde geri yükleyebilirsiniz.
                    </p>
                </div>

                {/* Actions */}
                <div className="flex gap-3 p-4 pt-0">
                    <button
                        onClick={onClose}
                        className="flex-1 px-4 py-2.5 text-sm font-medium rounded-xl transition-colors"
                        style={{
                            background: "var(--background)",
                            color: "var(--foreground)"
                        }}
                    >
                        Vazgeç
                    </button>
                    <button
                        onClick={() => {
                            onConfirm();
                            onClose();
                        }}
                        className="flex-1 px-4 py-2.5 text-sm font-medium rounded-xl transition-colors bg-red-500 hover:bg-red-600 text-white"
                    >
                        Çöp Kutusuna Taşı
                    </button>
                </div>
            </div>
        </div>
    );
}
