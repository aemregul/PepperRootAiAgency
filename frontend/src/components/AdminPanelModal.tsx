"use client";

import { useState } from "react";
import { X, Shield, Puzzle, Activity, Database, Zap, Power, TrendingUp, PieChart as PieChartIcon } from "lucide-react";
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

export function AdminPanelModal({ isOpen, onClose }: AdminPanelModalProps) {
    const [activeTab, setActiveTab] = useState<"overview" | "models" | "analytics">("overview");
    const [models, setModels] = useState(initialModels);

    const toggleModel = (modelId: string) => {
        setModels(models.map(model =>
            model.id === modelId ? { ...model, enabled: !model.enabled } : model
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
                        <div className="space-y-3">
                            <p className="text-sm mb-4" style={{ color: "var(--foreground-muted)" }}>
                                AI modellerini açıp kapatarak sistemin hangi servisleri kullanacağını kontrol edin.
                            </p>

                            {models.map((model) => (
                                <div
                                    key={model.id}
                                    className="flex items-center justify-between p-4 rounded-xl transition-all duration-200"
                                    style={{
                                        background: "var(--background)",
                                        opacity: model.enabled ? 1 : 0.6
                                    }}
                                >
                                    <div className="flex items-center gap-4">
                                        <div
                                            className="text-2xl p-2 rounded-lg"
                                            style={{ background: model.enabled ? "rgba(34, 197, 94, 0.2)" : "rgba(107, 114, 128, 0.2)" }}
                                        >
                                            {model.icon}
                                        </div>
                                        <div>
                                            <div className="font-medium flex items-center gap-2">
                                                {model.name}
                                                <span
                                                    className="px-2 py-0.5 text-xs rounded-full"
                                                    style={{
                                                        background: "var(--card)",
                                                        color: "var(--foreground-muted)"
                                                    }}
                                                >
                                                    {model.type}
                                                </span>
                                            </div>
                                            <div className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                                                {model.description}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Toggle Switch */}
                                    <button
                                        onClick={() => toggleModel(model.id)}
                                        className="relative w-14 h-7 rounded-full transition-all duration-300 ease-in-out"
                                        style={{
                                            background: model.enabled ? "var(--accent)" : "rgba(107, 114, 128, 0.4)",
                                            boxShadow: model.enabled ? "0 0 20px rgba(34, 197, 94, 0.3)" : "none"
                                        }}
                                    >
                                        <div
                                            className="absolute top-0.5 w-6 h-6 rounded-full bg-white shadow-lg transition-all duration-300 ease-in-out flex items-center justify-center"
                                            style={{
                                                left: model.enabled ? "30px" : "2px",
                                            }}
                                        >
                                            <Power size={12} style={{ color: model.enabled ? "#22c55e" : "#6b7280" }} />
                                        </div>
                                    </button>
                                </div>
                            ))}
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
            </div>
        </div>
    );
}
