"use client";

import { useState } from "react";
import { X, Shield, Puzzle, Activity, Database, Zap, Power, TrendingUp, PieChart as PieChartIcon, Store, Download, Star, Key, Plus, Check, ExternalLink } from "lucide-react";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, BarChart, Bar, Legend
} from "recharts";

interface AdminPanelModalProps {
    isOpen: boolean;
    onClose: () => void;
}

// Mock API usage data (last 7 days)
const usageData = [
    { day: "Pzt", calls: 45, images: 32, videos: 8 },
    { day: "Sal", calls: 62, images: 48, videos: 12 },
    { day: "Çar", calls: 78, images: 55, videos: 15 },
    { day: "Per", calls: 95, images: 72, videos: 18 },
    { day: "Cum", calls: 120, images: 85, videos: 22 },
    { day: "Cmt", calls: 88, images: 60, videos: 20 },
    { day: "Paz", calls: 75, images: 52, videos: 16 },
];

// Model distribution data
const modelDistribution = [
    { name: "Claude", value: 45, color: "#8b5cf6" },
    { name: "fal.ai", value: 35, color: "#22c55e" },
    { name: "Minimax", value: 15, color: "#3b82f6" },
    { name: "Diğer", value: 5, color: "#6b7280" },
];

// AI Models that can be toggled
const initialModels = [
    { id: "claude", name: "Claude Sonnet 4", type: "LLM", description: "Metin ve sohbet", enabled: true, icon: "🧠" },
    { id: "gpt4", name: "GPT-4o", type: "LLM", description: "OpenAI modeli", enabled: false, icon: "💬" },
    { id: "falai", name: "fal.ai", type: "Görsel", description: "Görsel üretimi", enabled: true, icon: "🖼️" },
    { id: "minimax", name: "Minimax", type: "Video", description: "Video üretimi", enabled: true, icon: "🎬" },
    { id: "kling", name: "Kling 2.5", type: "Video", description: "Yüksek kalite video", enabled: false, icon: "🎥" },
    { id: "runway", name: "Runway ML", type: "Video", description: "AI video düzenleme", enabled: false, icon: "✂️" },
];

// Stats
const stats = {
    totalCalls: 563,
    totalImages: 404,
    totalVideos: 111,
    successRate: 98.5,
};

// Marketplace Plugins
const marketplacePlugins = [
    { id: "midjourney", name: "Midjourney", author: "Midjourney Inc.", description: "Yüksek kaliteli AI görsel üretimi", rating: 4.9, downloads: 15420, icon: "🎨", category: "Görsel", installed: false },
    { id: "runway", name: "Runway ML", author: "Runway", description: "AI video düzenleme ve üretim", rating: 4.7, downloads: 8930, icon: "✂️", category: "Video", installed: false },
    { id: "suno", name: "Suno AI", author: "Suno Labs", description: "AI müzik ve ses üretimi", rating: 4.8, downloads: 12100, icon: "🎵", category: "Ses", installed: false },
    { id: "elevenlabs", name: "ElevenLabs", author: "ElevenLabs", description: "Gerçekçi AI seslendirme", rating: 4.9, downloads: 20500, icon: "🎤", category: "Ses", installed: false },
    { id: "leonardo", name: "Leonardo AI", author: "Leonardo", description: "Oyun ve konsept görsel üretimi", rating: 4.6, downloads: 7200, icon: "🎮", category: "Görsel", installed: false },
    { id: "pika", name: "Pika Labs", author: "Pika", description: "Kısa video ve animasyon", rating: 4.5, downloads: 5800, icon: "📹", category: "Video", installed: false },
];

// Installed Plugins
const initialInstalledPlugins = [
    { id: "falai", name: "fal.ai", description: "Hızlı görsel üretimi", icon: "🖼️", category: "Görsel", hasApiKey: true, enabled: true },
    { id: "minimax", name: "Minimax Video", description: "AI video üretimi", icon: "🎬", category: "Video", hasApiKey: true, enabled: true },
];

export function AdminPanelModal({ isOpen, onClose }: AdminPanelModalProps) {
    const [activeTab, setActiveTab] = useState<"overview" | "models" | "plugins" | "analytics">("overview");
    const [models, setModels] = useState(initialModels);
    const [installedPlugins, setInstalledPlugins] = useState(initialInstalledPlugins);
    const [marketplace, setMarketplace] = useState(marketplacePlugins);
    const [apiKeyModal, setApiKeyModal] = useState<{ isOpen: boolean; plugin: typeof marketplacePlugins[0] | null }>({ isOpen: false, plugin: null });
    const [apiKeyInput, setApiKeyInput] = useState("");

    const toggleModel = (modelId: string) => {
        setModels(models.map(model =>
            model.id === modelId ? { ...model, enabled: !model.enabled } : model
        ));
    };

    const installPlugin = (plugin: typeof marketplacePlugins[0]) => {
        // API Key girişi gerekli
        setApiKeyModal({ isOpen: true, plugin });
    };

    const confirmInstall = () => {
        if (apiKeyModal.plugin && apiKeyInput) {
            // Plugin'i yükle
            setInstalledPlugins([...installedPlugins, {
                id: apiKeyModal.plugin.id,
                name: apiKeyModal.plugin.name,
                description: apiKeyModal.plugin.description,
                icon: apiKeyModal.plugin.icon,
                category: apiKeyModal.plugin.category,
                hasApiKey: true,
                enabled: true
            }]);
            // Marketplace'ten kaldır
            setMarketplace(marketplace.map(p =>
                p.id === apiKeyModal.plugin!.id ? { ...p, installed: true } : p
            ));
            // Modal'ı kapat
            setApiKeyModal({ isOpen: false, plugin: null });
            setApiKeyInput("");
        }
    };

    const uninstallPlugin = (pluginId: string) => {
        setInstalledPlugins(installedPlugins.filter(p => p.id !== pluginId));
        setMarketplace(marketplace.map(p =>
            p.id === pluginId ? { ...p, installed: false } : p
        ));
    };

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
                className="relative w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Header */}
                <div
                    className="flex items-center justify-between p-5 border-b"
                    style={{ borderColor: "var(--border)", background: "linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, transparent 100%)" }}
                >
                    <div className="flex items-center gap-3">
                        <div
                            className="p-2 rounded-xl"
                            style={{ background: "rgba(34, 197, 94, 0.2)" }}
                        >
                            <Shield size={24} style={{ color: "var(--accent)" }} />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold">Admin Panel</h2>
                            <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                Sistem yönetimi ve AI model kontrolü
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

                {/* Tabs */}
                <div className="flex gap-1 p-2 mx-4 mt-4 rounded-xl" style={{ background: "var(--background)" }}>
                    {[
                        { id: "overview", label: "Genel Bakış", icon: Activity },
                        { id: "models", label: "AI Modeller", icon: Puzzle },
                        { id: "plugins", label: "AI Servisleri", icon: Store },
                        { id: "analytics", label: "Analitik", icon: TrendingUp },
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 text-sm rounded-lg transition-all duration-200 ${activeTab === tab.id
                                ? "font-medium shadow-lg"
                                : "opacity-60 hover:opacity-100"
                                }`}
                            style={{
                                background: activeTab === tab.id ? "var(--accent)" : "transparent",
                                color: activeTab === tab.id ? "var(--background)" : "var(--foreground)",
                            }}
                        >
                            <tab.icon size={16} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="p-4 overflow-y-auto max-h-[calc(85vh-180px)]">

                    {/* Overview Tab */}
                    {activeTab === "overview" && (
                        <div className="space-y-4">
                            {/* Stats Grid */}
                            <div className="grid grid-cols-4 gap-3">
                                {[
                                    { label: "Toplam Çağrı", value: stats.totalCalls, icon: Zap, color: "#22c55e" },
                                    { label: "Görseller", value: stats.totalImages, icon: PieChartIcon, color: "#8b5cf6" },
                                    { label: "Videolar", value: stats.totalVideos, icon: TrendingUp, color: "#3b82f6" },
                                    { label: "Başarı Oranı", value: `%${stats.successRate}`, icon: Activity, color: "#f59e0b" },
                                ].map((stat) => (
                                    <div
                                        key={stat.label}
                                        className="p-4 rounded-xl relative overflow-hidden"
                                        style={{ background: "var(--background)" }}
                                    >
                                        <div
                                            className="absolute top-0 right-0 w-16 h-16 rounded-full opacity-20"
                                            style={{ background: stat.color, transform: "translate(30%, -30%)" }}
                                        />
                                        <stat.icon size={20} style={{ color: stat.color }} className="mb-2" />
                                        <div className="text-2xl font-bold">{stat.value}</div>
                                        <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                            {stat.label}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Usage Chart */}
                            <div className="p-4 rounded-xl" style={{ background: "var(--background)" }}>
                                <h3 className="text-sm font-medium mb-4">Son 7 Gün API Kullanımı</h3>
                                <ResponsiveContainer width="100%" height={200}>
                                    <LineChart data={usageData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                        <XAxis dataKey="day" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                                        <YAxis stroke="rgba(255,255,255,0.5)" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{
                                                background: "var(--card)",
                                                border: "1px solid var(--border)",
                                                borderRadius: "8px"
                                            }}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="calls"
                                            stroke="#22c55e"
                                            strokeWidth={2}
                                            dot={{ fill: "#22c55e", strokeWidth: 2 }}
                                            name="API Çağrısı"
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>

                            {/* Active Models Quick View */}
                            <div className="p-4 rounded-xl" style={{ background: "var(--background)" }}>
                                <h3 className="text-sm font-medium mb-3">Aktif Modeller</h3>
                                <div className="flex flex-wrap gap-2">
                                    {models.filter(m => m.enabled).map((model) => (
                                        <span
                                            key={model.id}
                                            className="px-3 py-1.5 rounded-full text-sm flex items-center gap-2"
                                            style={{ background: "rgba(34, 197, 94, 0.2)", color: "#22c55e" }}
                                        >
                                            <span>{model.icon}</span>
                                            {model.name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Models Tab */}
                    {activeTab === "models" && (
                        <div className="flex flex-col items-center justify-center py-16">
                            <div
                                className="p-4 rounded-2xl mb-4"
                                style={{ background: "rgba(34, 197, 94, 0.1)" }}
                            >
                                <Puzzle size={48} style={{ color: "var(--accent)" }} />
                            </div>
                            <h3 className="text-lg font-medium mb-2">AI Model Yönetimi</h3>
                            <p className="text-sm text-center max-w-md" style={{ color: "var(--foreground-muted)" }}>
                                Yeni AI modelleri entegre edildiğinde burada yönetebilirsiniz.
                                Şu an sistem otomatik olarak en uygun modeli seçmektedir.
                            </p>
                            <div className="mt-6 flex gap-2">
                                <span
                                    className="px-3 py-1.5 rounded-full text-sm flex items-center gap-2"
                                    style={{ background: "rgba(34, 197, 94, 0.2)", color: "#22c55e" }}
                                >
                                    🧠 Claude Sonnet 4
                                </span>
                                <span
                                    className="px-3 py-1.5 rounded-full text-sm flex items-center gap-2"
                                    style={{ background: "rgba(34, 197, 94, 0.2)", color: "#22c55e" }}
                                >
                                    🖼️ fal.ai
                                </span>
                                <span
                                    className="px-3 py-1.5 rounded-full text-sm flex items-center gap-2"
                                    style={{ background: "rgba(34, 197, 94, 0.2)", color: "#22c55e" }}
                                >
                                    🎬 Kling 2.5
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Plugins Tab */}
                    {activeTab === "plugins" && (
                        <div className="space-y-6">
                            {/* Installed Plugins */}
                            <div>
                                <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <Check size={16} className="text-green-500" />
                                    Yüklü Pluginler ({installedPlugins.length})
                                </h3>
                                <div className="grid grid-cols-2 gap-3">
                                    {installedPlugins.map((plugin) => (
                                        <div
                                            key={plugin.id}
                                            className="p-4 rounded-xl flex items-center justify-between"
                                            style={{ background: "var(--background)" }}
                                        >
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">{plugin.icon}</span>
                                                <div>
                                                    <div className="font-medium flex items-center gap-2">
                                                        {plugin.name}
                                                        <span className="px-1.5 py-0.5 text-xs rounded" style={{ background: "rgba(34, 197, 94, 0.2)", color: "#22c55e" }}>
                                                            Aktif
                                                        </span>
                                                    </div>
                                                    <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                                        {plugin.category} • {plugin.description}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <button
                                                    className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                                                    title="API Key Düzenle"
                                                >
                                                    <Key size={16} style={{ color: "var(--foreground-muted)" }} />
                                                </button>
                                                <button
                                                    onClick={() => uninstallPlugin(plugin.id)}
                                                    className="px-3 py-1.5 text-xs rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                                                >
                                                    Kaldır
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Marketplace */}
                            <div>
                                <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                                    <Store size={16} style={{ color: "var(--accent)" }} />
                                    Plugin Marketplace
                                </h3>
                                <div className="grid grid-cols-2 gap-3">
                                    {marketplace.filter(p => !p.installed).map((plugin) => (
                                        <div
                                            key={plugin.id}
                                            className="p-4 rounded-xl"
                                            style={{ background: "var(--background)" }}
                                        >
                                            <div className="flex items-start justify-between mb-3">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-2xl">{plugin.icon}</span>
                                                    <div>
                                                        <div className="font-medium">{plugin.name}</div>
                                                        <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                                            by {plugin.author}
                                                        </div>
                                                    </div>
                                                </div>
                                                <span className="px-2 py-0.5 text-xs rounded" style={{ background: "var(--card)" }}>
                                                    {plugin.category}
                                                </span>
                                            </div>
                                            <p className="text-xs mb-3" style={{ color: "var(--foreground-muted)" }}>
                                                {plugin.description}
                                            </p>
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3 text-xs" style={{ color: "var(--foreground-muted)" }}>
                                                    <span className="flex items-center gap-1">
                                                        <Star size={12} className="text-yellow-500" />
                                                        {plugin.rating}
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        <Download size={12} />
                                                        {plugin.downloads.toLocaleString()}
                                                    </span>
                                                </div>
                                                <button
                                                    onClick={() => installPlugin(plugin)}
                                                    className="px-3 py-1.5 text-xs rounded-lg transition-colors flex items-center gap-1"
                                                    style={{ background: "var(--accent)", color: "var(--background)" }}
                                                >
                                                    <Plus size={12} />
                                                    Ekle
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Analytics Tab */}
                    {activeTab === "analytics" && (
                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                {/* Pie Chart - Model Distribution */}
                                <div className="p-4 rounded-xl" style={{ background: "var(--background)" }}>
                                    <h3 className="text-sm font-medium mb-4">Model Kullanım Dağılımı</h3>
                                    <ResponsiveContainer width="100%" height={200}>
                                        <PieChart>
                                            <Pie
                                                data={modelDistribution}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={50}
                                                outerRadius={80}
                                                paddingAngle={5}
                                                dataKey="value"
                                            >
                                                {modelDistribution.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <Tooltip
                                                contentStyle={{
                                                    background: "var(--card)",
                                                    border: "1px solid var(--border)",
                                                    borderRadius: "8px"
                                                }}
                                                formatter={(value: number) => [`%${value}`, ""]}
                                            />
                                        </PieChart>
                                    </ResponsiveContainer>
                                    <div className="flex flex-wrap gap-2 mt-2 justify-center">
                                        {modelDistribution.map((item) => (
                                            <span key={item.name} className="flex items-center gap-1 text-xs">
                                                <span className="w-2 h-2 rounded-full" style={{ background: item.color }} />
                                                {item.name}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Bar Chart - Daily Breakdown */}
                                <div className="p-4 rounded-xl" style={{ background: "var(--background)" }}>
                                    <h3 className="text-sm font-medium mb-4">Günlük Üretim Detayı</h3>
                                    <ResponsiveContainer width="100%" height={200}>
                                        <BarChart data={usageData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                            <XAxis dataKey="day" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                                            <YAxis stroke="rgba(255,255,255,0.5)" fontSize={12} />
                                            <Tooltip
                                                contentStyle={{
                                                    background: "var(--card)",
                                                    border: "1px solid var(--border)",
                                                    borderRadius: "8px"
                                                }}
                                            />
                                            <Bar dataKey="images" fill="#8b5cf6" name="Görsel" radius={[4, 4, 0, 0]} />
                                            <Bar dataKey="videos" fill="#3b82f6" name="Video" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Trend Line */}
                            <div className="p-4 rounded-xl" style={{ background: "var(--background)" }}>
                                <h3 className="text-sm font-medium mb-4">Haftalık Trend</h3>
                                <ResponsiveContainer width="100%" height={150}>
                                    <LineChart data={usageData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                        <XAxis dataKey="day" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                                        <YAxis stroke="rgba(255,255,255,0.5)" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{
                                                background: "var(--card)",
                                                border: "1px solid var(--border)",
                                                borderRadius: "8px"
                                            }}
                                        />
                                        <Legend />
                                        <Line type="monotone" dataKey="images" stroke="#8b5cf6" strokeWidth={2} name="Görsel" />
                                        <Line type="monotone" dataKey="videos" stroke="#3b82f6" strokeWidth={2} name="Video" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}
                </div>

                {/* API Key Modal */}
                {apiKeyModal.isOpen && apiKeyModal.plugin && (
                    <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm rounded-2xl">
                        <div className="w-full max-w-md p-6 rounded-xl" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
                            <div className="flex items-center gap-3 mb-4">
                                <span className="text-3xl">{apiKeyModal.plugin.icon}</span>
                                <div>
                                    <h3 className="font-semibold">{apiKeyModal.plugin.name}</h3>
                                    <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>API Key gerekli</p>
                                </div>
                            </div>
                            <p className="text-sm mb-4" style={{ color: "var(--foreground-muted)" }}>
                                Bu plugin'i kullanmak için API anahtarınızı girin.
                            </p>
                            <input
                                type="password"
                                value={apiKeyInput}
                                onChange={(e) => setApiKeyInput(e.target.value)}
                                placeholder="sk-xxxx..."
                                className="w-full px-4 py-3 rounded-xl text-sm mb-4"
                                style={{ background: "var(--background)", border: "1px solid var(--border)" }}
                            />
                            <div className="flex gap-3">
                                <button
                                    onClick={() => { setApiKeyModal({ isOpen: false, plugin: null }); setApiKeyInput(""); }}
                                    className="flex-1 px-4 py-2.5 text-sm rounded-xl hover:bg-[var(--background)] transition-colors"
                                    style={{ border: "1px solid var(--border)" }}
                                >
                                    İptal
                                </button>
                                <button
                                    onClick={confirmInstall}
                                    disabled={!apiKeyInput}
                                    className="flex-1 px-4 py-2.5 text-sm font-medium rounded-xl transition-colors disabled:opacity-50"
                                    style={{ background: "var(--accent)", color: "var(--background)" }}
                                >
                                    Yükle
                                </button>
                            </div>
                            <a
                                href="#"
                                className="flex items-center justify-center gap-1 text-xs mt-4 hover:underline"
                                style={{ color: "var(--foreground-muted)" }}
                            >
                                API Key nasıl alınır? <ExternalLink size={10} />
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
