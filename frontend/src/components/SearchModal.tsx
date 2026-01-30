"use client";

import { useState, useEffect, useRef } from "react";
import { X, Search as SearchIcon, User, MapPin, Image, Video, FileText } from "lucide-react";

interface SearchModalProps {
    isOpen: boolean;
    onClose: () => void;
}

interface SearchResult {
    id: string;
    type: "character" | "location" | "asset" | "project";
    name: string;
    description?: string;
}

// Mock search results - will be replaced with real API
const mockResults: SearchResult[] = [
    { id: "c1", type: "character", name: "@character_emre", description: "Ana karakter" },
    { id: "c2", type: "character", name: "@character_ahmet", description: "Yardımcı karakter" },
    { id: "l1", type: "location", name: "@location_kitchen", description: "Modern mutfak" },
    { id: "l2", type: "location", name: "@location_office", description: "Ofis mekanı" },
    { id: "a1", type: "asset", name: "kitchen_scene_01.png", description: "Görsel" },
    { id: "p1", type: "project", name: "Samsung Ad Campaign", description: "Proje" },
];

export function SearchModal({ isOpen, onClose }: SearchModalProps) {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const inputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen]);

    useEffect(() => {
        if (query.length > 0) {
            const filtered = mockResults.filter(
                (item) =>
                    item.name.toLowerCase().includes(query.toLowerCase()) ||
                    item.description?.toLowerCase().includes(query.toLowerCase())
            );
            setResults(filtered);
        } else {
            setResults([]);
        }
    }, [query]);

    const getIcon = (type: string) => {
        switch (type) {
            case "character":
                return <User size={16} className="text-blue-400" />;
            case "location":
                return <MapPin size={16} className="text-green-400" />;
            case "asset":
                return <Image size={16} className="text-purple-400" />;
            case "project":
                return <FileText size={16} className="text-orange-400" />;
            default:
                return null;
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="relative w-full max-w-lg rounded-xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Search Input */}
                <div className="flex items-center gap-3 p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    <SearchIcon size={20} style={{ color: "var(--foreground-muted)" }} />
                    <input
                        ref={inputRef}
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Karakter, lokasyon veya asset ara..."
                        className="flex-1 bg-transparent outline-none text-sm"
                        style={{ color: "var(--foreground)" }}
                    />
                    <button
                        onClick={onClose}
                        className="p-1 rounded hover:bg-[var(--background)] transition-colors"
                    >
                        <X size={18} style={{ color: "var(--foreground-muted)" }} />
                    </button>
                </div>

                {/* Results */}
                <div className="max-h-[300px] overflow-y-auto">
                    {query.length === 0 ? (
                        <div className="p-4 text-center text-sm" style={{ color: "var(--foreground-muted)" }}>
                            Aramaya başlamak için yazın...
                        </div>
                    ) : results.length === 0 ? (
                        <div className="p-4 text-center text-sm" style={{ color: "var(--foreground-muted)" }}>
                            "{query}" için sonuç bulunamadı
                        </div>
                    ) : (
                        <div className="p-2">
                            {results.map((result) => (
                                <button
                                    key={result.id}
                                    className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-[var(--background)] transition-colors text-left"
                                    onClick={() => {
                                        // TODO: Navigate to result
                                        onClose();
                                    }}
                                >
                                    {getIcon(result.type)}
                                    <div>
                                        <div className="text-sm font-medium">{result.name}</div>
                                        {result.description && (
                                            <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                                {result.description}
                                            </div>
                                        )}
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Keyboard shortcut hint */}
                <div className="p-2 border-t text-center" style={{ borderColor: "var(--border)" }}>
                    <span className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                        ESC ile kapat
                    </span>
                </div>
            </div>
        </div>
    );
}
