"use client";

import { useState } from "react";
import { X, Puzzle, Plus, Users, MapPin, Camera, Palette, Clock, ChevronDown, Check, Sparkles, Share2 } from "lucide-react";

interface CreativePluginModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (plugin: CreativePlugin) => void;
    editPlugin?: CreativePlugin | null;
}

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
            isVariable: boolean; // Kullanıcı kendi karakterini koyabilir
        };
        location?: {
            id: string;
            name: string;
            settings: string; // "aydınlatma", "mobilya stili" vb.
        };
        timeOfDay?: string; // "sabah", "öğle", "akşam", "gece"
        cameraAngles?: string[];
        style?: string;
        promptTemplate?: string;
    };
    createdAt: Date;
    downloads: number;
    rating: number;
}

// Mock data
const mockCharacters = [
    { id: "emre", name: "@character_emre" },
    { id: "ayse", name: "@character_ayse" },
    { id: "variable", name: "🔄 Değişken (Kullanıcı seçer)" },
];

const mockLocations = [
    { id: "mutfak", name: "Modern Mutfak" },
    { id: "ofis", name: "Minimalist Ofis" },
    { id: "outdoor", name: "Outdoor - Park" },
];

const timeOptions = ["Sabah", "Öğle", "Gün Batımı", "Gece"];

const cameraOptions = [
    "Yakın Çekim (Close-up)",
    "Orta Plan (Medium Shot)",
    "Geniş Açı (Wide Shot)",
    "Kuş Bakışı (Bird's Eye)",
    "Alt Açı (Low Angle)",
    "Omuz Çekimi (Over Shoulder)",
];

const styleOptions = [
    "Sinematik",
    "Minimalist",
    "Sıcak Tonlar",
    "Soğuk Tonlar",
    "Editorial",
    "Commercial",
];

export function CreativePluginModal({ isOpen, onClose, onSave, editPlugin }: CreativePluginModalProps) {
    const [step, setStep] = useState(1);
    const [name, setName] = useState(editPlugin?.name || "");
    const [description, setDescription] = useState(editPlugin?.description || "");
    const [isPublic, setIsPublic] = useState(editPlugin?.isPublic || false);

    // Config
    const [selectedCharacter, setSelectedCharacter] = useState(editPlugin?.config.character?.id || "variable");
    const [selectedLocation, setSelectedLocation] = useState(editPlugin?.config.location?.id || "");
    const [selectedTime, setSelectedTime] = useState(editPlugin?.config.timeOfDay || "");
    const [selectedAngles, setSelectedAngles] = useState<string[]>(editPlugin?.config.cameraAngles || []);
    const [selectedStyle, setSelectedStyle] = useState(editPlugin?.config.style || "");
    const [promptTemplate, setPromptTemplate] = useState(editPlugin?.config.promptTemplate || "");

    if (!isOpen) return null;

    const toggleAngle = (angle: string) => {
        setSelectedAngles(prev =>
            prev.includes(angle)
                ? prev.filter(a => a !== angle)
                : [...prev, angle]
        );
    };

    const handleSave = () => {
        const plugin: CreativePlugin = {
            id: editPlugin?.id || Date.now().toString(),
            name,
            description,
            author: "Ben",
            isPublic,
            config: {
                character: {
                    id: selectedCharacter,
                    name: mockCharacters.find(c => c.id === selectedCharacter)?.name || "",
                    isVariable: selectedCharacter === "variable"
                },
                location: selectedLocation ? {
                    id: selectedLocation,
                    name: mockLocations.find(l => l.id === selectedLocation)?.name || "",
                    settings: ""
                } : undefined,
                timeOfDay: selectedTime,
                cameraAngles: selectedAngles,
                style: selectedStyle,
                promptTemplate
            },
            createdAt: editPlugin?.createdAt || new Date(),
            downloads: editPlugin?.downloads || 0,
            rating: editPlugin?.rating || 0
        };
        onSave(plugin);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-md"
                onClick={onClose}
            />

            {/* Modal */}
            <div
                className="relative w-full max-w-2xl max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-5 border-b"
                    style={{ borderColor: "var(--border)", background: "linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, transparent 100%)" }}
                >
                    <div className="flex items-center gap-3">
                        <div
                            className="p-2 rounded-xl"
                            style={{ background: "rgba(139, 92, 246, 0.2)" }}
                        >
                            <Sparkles size={24} className="text-purple-500" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">
                                {editPlugin ? "Plugin Düzenle" : "Yeni Creative Plugin"}
                            </h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Kombinasyonunu oluştur ve paylaş
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

                {/* Steps Indicator */}
                <div className="flex items-center justify-center gap-2 p-4 border-b" style={{ borderColor: "var(--border)" }}>
                    {[1, 2, 3].map((s) => (
                        <div key={s} className="flex items-center gap-2">
                            <div
                                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${step >= s ? "bg-purple-500 text-white" : "bg-[var(--background)]"
                                    }`}
                            >
                                {step > s ? <Check size={16} /> : s}
                            </div>
                            {s < 3 && (
                                <div
                                    className="w-12 h-0.5 rounded"
                                    style={{ background: step > s ? "#8b5cf6" : "var(--border)" }}
                                />
                            )}
                        </div>
                    ))}
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(85vh-220px)]">

                    {/* Step 1: Basic Info */}
                    {step === 1 && (
                        <div className="space-y-4">
                            <h3 className="text-lg font-medium mb-4">Temel Bilgiler</h3>

                            <div>
                                <label className="text-sm font-medium mb-2 block">Plugin Adı</label>
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Örn: Mutfak Reklamı Seti"
                                    className="w-full px-4 py-3 rounded-xl text-sm"
                                    style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                                />
                            </div>

                            <div>
                                <label className="text-sm font-medium mb-2 block">Açıklama</label>
                                <textarea
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                    placeholder="Bu plugin ne işe yarar?"
                                    rows={3}
                                    className="w-full px-4 py-3 rounded-xl text-sm resize-none"
                                    style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                                />
                            </div>

                            <div className="flex items-center gap-3 p-4 rounded-xl" style={{ background: "var(--background)" }}>
                                <input
                                    type="checkbox"
                                    id="isPublic"
                                    checked={isPublic}
                                    onChange={(e) => setIsPublic(e.target.checked)}
                                    className="w-5 h-5 rounded accent-purple-500"
                                />
                                <label htmlFor="isPublic" className="flex-1">
                                    <div className="font-medium flex items-center gap-2">
                                        <Share2 size={16} />
                                        Herkese Açık Yap
                                    </div>
                                    <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                        Diğer kullanıcılar bu plugin'i Marketplace'te görebilir
                                    </div>
                                </label>
                            </div>
                        </div>
                    )}

                    {/* Step 2: Character & Location */}
                    {step === 2 && (
                        <div className="space-y-6">
                            <h3 className="text-lg font-medium">Karakter & Lokasyon</h3>

                            {/* Character Selection */}
                            <div>
                                <label className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <Users size={16} />
                                    Karakter
                                </label>
                                <div className="grid grid-cols-1 gap-2">
                                    {mockCharacters.map((char) => (
                                        <button
                                            key={char.id}
                                            onClick={() => setSelectedCharacter(char.id)}
                                            className={`p-3 rounded-xl text-left transition-all ${selectedCharacter === char.id
                                                    ? "ring-2 ring-purple-500"
                                                    : ""
                                                }`}
                                            style={{ background: "var(--background)" }}
                                        >
                                            <div className="flex items-center justify-between">
                                                <span>{char.name}</span>
                                                {selectedCharacter === char.id && (
                                                    <Check size={16} className="text-purple-500" />
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Location Selection */}
                            <div>
                                <label className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <MapPin size={16} />
                                    Lokasyon
                                </label>
                                <div className="grid grid-cols-1 gap-2">
                                    {mockLocations.map((loc) => (
                                        <button
                                            key={loc.id}
                                            onClick={() => setSelectedLocation(loc.id)}
                                            className={`p-3 rounded-xl text-left transition-all ${selectedLocation === loc.id
                                                    ? "ring-2 ring-purple-500"
                                                    : ""
                                                }`}
                                            style={{ background: "var(--background)" }}
                                        >
                                            <div className="flex items-center justify-between">
                                                <span>{loc.name}</span>
                                                {selectedLocation === loc.id && (
                                                    <Check size={16} className="text-purple-500" />
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Time of Day */}
                            <div>
                                <label className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <Clock size={16} />
                                    Zaman
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {timeOptions.map((time) => (
                                        <button
                                            key={time}
                                            onClick={() => setSelectedTime(time)}
                                            className={`px-4 py-2 rounded-lg text-sm transition-all ${selectedTime === time
                                                    ? "bg-purple-500 text-white"
                                                    : ""
                                                }`}
                                            style={selectedTime !== time ? { background: "var(--background)" } : {}}
                                        >
                                            {time}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Step 3: Camera & Style */}
                    {step === 3 && (
                        <div className="space-y-6">
                            <h3 className="text-lg font-medium">Kamera & Stil</h3>

                            {/* Camera Angles */}
                            <div>
                                <label className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <Camera size={16} />
                                    Kamera Açıları (birden fazla seçebilirsin)
                                </label>
                                <div className="grid grid-cols-2 gap-2">
                                    {cameraOptions.map((angle) => (
                                        <button
                                            key={angle}
                                            onClick={() => toggleAngle(angle)}
                                            className={`p-3 rounded-xl text-left text-sm transition-all ${selectedAngles.includes(angle)
                                                    ? "ring-2 ring-purple-500 bg-purple-500/10"
                                                    : ""
                                                }`}
                                            style={!selectedAngles.includes(angle) ? { background: "var(--background)" } : {}}
                                        >
                                            <div className="flex items-center justify-between">
                                                <span>{angle}</span>
                                                {selectedAngles.includes(angle) && (
                                                    <Check size={14} className="text-purple-500" />
                                                )}
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Style */}
                            <div>
                                <label className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <Palette size={16} />
                                    Görsel Stil
                                </label>
                                <div className="flex flex-wrap gap-2">
                                    {styleOptions.map((style) => (
                                        <button
                                            key={style}
                                            onClick={() => setSelectedStyle(style)}
                                            className={`px-4 py-2 rounded-lg text-sm transition-all ${selectedStyle === style
                                                    ? "bg-purple-500 text-white"
                                                    : ""
                                                }`}
                                            style={selectedStyle !== style ? { background: "var(--background)" } : {}}
                                        >
                                            {style}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Prompt Template */}
                            <div>
                                <label className="text-sm font-medium mb-2 block">Prompt Şablonu (opsiyonel)</label>
                                <textarea
                                    value={promptTemplate}
                                    onChange={(e) => setPromptTemplate(e.target.value)}
                                    placeholder="professional photography, {character} in {location}, {time} lighting..."
                                    rows={3}
                                    className="w-full px-4 py-3 rounded-xl text-sm resize-none font-mono"
                                    style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                                />
                                <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                    {"{character}"}, {"{location}"}, {"{time}"} değişkenleri otomatik değiştirilir
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between p-4 border-t" style={{ borderColor: "var(--border)" }}>
                    <button
                        onClick={() => step > 1 ? setStep(step - 1) : onClose()}
                        className="px-4 py-2.5 text-sm rounded-xl hover:bg-[var(--background)] transition-colors"
                    >
                        {step === 1 ? "İptal" : "Geri"}
                    </button>

                    <button
                        onClick={() => step < 3 ? setStep(step + 1) : handleSave()}
                        disabled={step === 1 && !name}
                        className="px-6 py-2.5 text-sm font-medium rounded-xl transition-colors disabled:opacity-50"
                        style={{ background: "var(--accent)", color: "var(--background)" }}
                    >
                        {step < 3 ? "Devam" : "Kaydet"}
                    </button>
                </div>
            </div>
        </div>
    );
}
