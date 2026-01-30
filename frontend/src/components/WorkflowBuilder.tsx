"use client";

import { useState, useRef, DragEvent } from "react";
import { X, Play, Save, Trash2, Plus, GripVertical, Image, User, MapPin, Palette, Settings, Zap } from "lucide-react";

interface WorkflowNode {
    id: string;
    type: "character" | "location" | "style" | "effect" | "output";
    label: string;
    icon: string;
    config: Record<string, string>;
    x: number;
    y: number;
}

interface WorkflowBuilderProps {
    isOpen: boolean;
    onClose: () => void;
    characters: { id: string; name: string }[];
    locations: { id: string; name: string }[];
    onExecute: (workflow: WorkflowNode[]) => void;
}

const nodeTypes = [
    { type: "character", label: "Karakter", icon: "👤", color: "#8b5cf6" },
    { type: "location", label: "Lokasyon", icon: "📍", color: "#3b82f6" },
    { type: "style", label: "Stil", icon: "🎨", color: "#f59e0b" },
    { type: "effect", label: "Efekt", icon: "✨", color: "#ec4899" },
    { type: "output", label: "Çıktı", icon: "🖼️", color: "#22c55e" },
];

const styleOptions = [
    "Cinematic", "Editorial", "Commercial", "Portrait", "Documentary", "Minimalist"
];

const effectOptions = [
    "Golden Hour", "Blue Hour", "Dramatic", "Soft Light", "High Contrast", "Vintage"
];

export function WorkflowBuilder({
    isOpen,
    onClose,
    characters,
    locations,
    onExecute
}: WorkflowBuilderProps) {
    const [nodes, setNodes] = useState<WorkflowNode[]>([]);
    const [draggedType, setDraggedType] = useState<string | null>(null);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);
    const canvasRef = useRef<HTMLDivElement>(null);

    if (!isOpen) return null;

    const handleDragStart = (e: DragEvent, type: string) => {
        setDraggedType(type);
        e.dataTransfer.effectAllowed = "copy";
    };

    const handleDragOver = (e: DragEvent) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "copy";
    };

    const handleDrop = (e: DragEvent) => {
        e.preventDefault();
        if (!draggedType || !canvasRef.current) return;

        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left - 75; // Center the node
        const y = e.clientY - rect.top - 30;

        const nodeType = nodeTypes.find(n => n.type === draggedType);
        if (!nodeType) return;

        const newNode: WorkflowNode = {
            id: `node-${Date.now()}`,
            type: draggedType as WorkflowNode["type"],
            label: nodeType.label,
            icon: nodeType.icon,
            config: {},
            x: Math.max(0, Math.min(x, rect.width - 150)),
            y: Math.max(0, Math.min(y, rect.height - 60))
        };

        setNodes([...nodes, newNode]);
        setDraggedType(null);
        setSelectedNode(newNode.id);
    };

    const handleNodeDrag = (e: DragEvent, nodeId: string) => {
        e.preventDefault();
        if (!canvasRef.current) return;

        const rect = canvasRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left - 75;
        const y = e.clientY - rect.top - 30;

        setNodes(nodes.map(node =>
            node.id === nodeId
                ? { ...node, x: Math.max(0, Math.min(x, rect.width - 150)), y: Math.max(0, Math.min(y, rect.height - 60)) }
                : node
        ));
    };

    const deleteNode = (nodeId: string) => {
        setNodes(nodes.filter(n => n.id !== nodeId));
        if (selectedNode === nodeId) setSelectedNode(null);
    };

    const updateNodeConfig = (nodeId: string, key: string, value: string) => {
        setNodes(nodes.map(node =>
            node.id === nodeId
                ? { ...node, config: { ...node.config, [key]: value } }
                : node
        ));
    };

    const executeWorkflow = () => {
        onExecute(nodes);
        onClose();
    };

    const selectedNodeData = nodes.find(n => n.id === selectedNode);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose} />

            <div
                className="relative w-full max-w-5xl h-[80vh] rounded-2xl shadow-2xl overflow-hidden flex"
                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
            >
                {/* Left Panel - Node Types */}
                <div className="w-48 border-r flex flex-col" style={{ borderColor: "var(--border)", background: "var(--background)" }}>
                    <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
                        <h3 className="font-semibold text-sm">Bloklar</h3>
                        <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                            Sürükleyip bırakın
                        </p>
                    </div>

                    <div className="flex-1 p-3 space-y-2 overflow-y-auto">
                        {nodeTypes.map((nodeType) => (
                            <div
                                key={nodeType.type}
                                draggable
                                onDragStart={(e) => handleDragStart(e, nodeType.type)}
                                className="flex items-center gap-2 p-3 rounded-lg cursor-grab active:cursor-grabbing transition-all hover:scale-[1.02]"
                                style={{
                                    background: `${nodeType.color}20`,
                                    border: `1px solid ${nodeType.color}40`
                                }}
                            >
                                <GripVertical size={14} style={{ color: "var(--foreground-muted)" }} />
                                <span className="text-lg">{nodeType.icon}</span>
                                <span className="text-sm font-medium">{nodeType.label}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Center - Canvas */}
                <div className="flex-1 flex flex-col">
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: "var(--border)" }}>
                        <div className="flex items-center gap-3">
                            <Zap size={20} style={{ color: "var(--accent)" }} />
                            <div>
                                <h2 className="font-bold">Workflow Builder</h2>
                                <p className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                    {nodes.length} blok
                                </p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setNodes([])}
                                className="px-3 py-1.5 text-sm rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                            >
                                <Trash2 size={14} className="inline mr-1" />
                                Temizle
                            </button>
                            <button
                                onClick={executeWorkflow}
                                disabled={nodes.length === 0}
                                className="px-4 py-1.5 text-sm rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
                                style={{ background: "var(--accent)", color: "var(--background)" }}
                            >
                                <Play size={14} />
                                Çalıştır
                            </button>
                            <button onClick={onClose} className="p-2 rounded-lg hover:bg-[var(--background)] transition-colors">
                                <X size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Canvas */}
                    <div
                        ref={canvasRef}
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                        className="flex-1 relative overflow-hidden"
                        style={{
                            background: "repeating-linear-gradient(0deg, var(--border) 0px, var(--border) 1px, transparent 1px, transparent 40px), repeating-linear-gradient(90deg, var(--border) 0px, var(--border) 1px, transparent 1px, transparent 40px)",
                            backgroundSize: "40px 40px"
                        }}
                    >
                        {nodes.length === 0 && (
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="text-center" style={{ color: "var(--foreground-muted)" }}>
                                    <Plus size={48} className="mx-auto mb-3 opacity-20" />
                                    <p className="text-sm">Blokları buraya sürükleyin</p>
                                </div>
                            </div>
                        )}

                        {/* Nodes */}
                        {nodes.map((node) => {
                            const nodeType = nodeTypes.find(n => n.type === node.type);
                            return (
                                <div
                                    key={node.id}
                                    draggable
                                    onDrag={(e) => handleNodeDrag(e, node.id)}
                                    onClick={() => setSelectedNode(node.id)}
                                    className={`absolute w-[150px] p-3 rounded-xl cursor-move transition-all ${selectedNode === node.id ? "ring-2 ring-[var(--accent)] shadow-lg" : "shadow"
                                        }`}
                                    style={{
                                        left: node.x,
                                        top: node.y,
                                        background: "var(--card)",
                                        border: `2px solid ${nodeType?.color || "var(--border)"}`
                                    }}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className="text-xl">{node.icon}</span>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                deleteNode(node.id);
                                            }}
                                            className="p-1 rounded hover:bg-red-500/20 transition-colors"
                                        >
                                            <X size={12} className="text-red-400" />
                                        </button>
                                    </div>
                                    <div className="text-sm font-medium">{node.label}</div>
                                    {node.config.value && (
                                        <div className="text-xs mt-1 truncate" style={{ color: "var(--foreground-muted)" }}>
                                            {node.config.value}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Right Panel - Node Config */}
                <div className="w-64 border-l flex flex-col" style={{ borderColor: "var(--border)", background: "var(--background)" }}>
                    <div className="p-4 border-b" style={{ borderColor: "var(--border)" }}>
                        <h3 className="font-semibold text-sm flex items-center gap-2">
                            <Settings size={14} />
                            Blok Ayarları
                        </h3>
                    </div>

                    <div className="flex-1 p-4 overflow-y-auto">
                        {selectedNodeData ? (
                            <div className="space-y-4">
                                <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: "var(--card)" }}>
                                    <span className="text-2xl">{selectedNodeData.icon}</span>
                                    <div>
                                        <div className="font-medium">{selectedNodeData.label}</div>
                                        <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                            {selectedNodeData.type}
                                        </div>
                                    </div>
                                </div>

                                {/* Character Config */}
                                {selectedNodeData.type === "character" && (
                                    <div>
                                        <label className="text-xs font-medium mb-2 block" style={{ color: "var(--foreground-muted)" }}>
                                            Karakter Seç
                                        </label>
                                        <select
                                            value={selectedNodeData.config.value || ""}
                                            onChange={(e) => updateNodeConfig(selectedNodeData.id, "value", e.target.value)}
                                            className="w-full p-2 rounded-lg text-sm"
                                            style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                        >
                                            <option value="">Seçiniz...</option>
                                            {characters.map(c => (
                                                <option key={c.id} value={c.name}>{c.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}

                                {/* Location Config */}
                                {selectedNodeData.type === "location" && (
                                    <div>
                                        <label className="text-xs font-medium mb-2 block" style={{ color: "var(--foreground-muted)" }}>
                                            Lokasyon Seç
                                        </label>
                                        <select
                                            value={selectedNodeData.config.value || ""}
                                            onChange={(e) => updateNodeConfig(selectedNodeData.id, "value", e.target.value)}
                                            className="w-full p-2 rounded-lg text-sm"
                                            style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                        >
                                            <option value="">Seçiniz...</option>
                                            {locations.map(l => (
                                                <option key={l.id} value={l.name}>{l.name}</option>
                                            ))}
                                        </select>
                                    </div>
                                )}

                                {/* Style Config */}
                                {selectedNodeData.type === "style" && (
                                    <div>
                                        <label className="text-xs font-medium mb-2 block" style={{ color: "var(--foreground-muted)" }}>
                                            Stil Seç
                                        </label>
                                        <div className="grid grid-cols-2 gap-2">
                                            {styleOptions.map(style => (
                                                <button
                                                    key={style}
                                                    onClick={() => updateNodeConfig(selectedNodeData.id, "value", style)}
                                                    className={`p-2 text-xs rounded-lg transition-all ${selectedNodeData.config.value === style
                                                        ? "ring-2 ring-[var(--accent)]"
                                                        : ""
                                                        }`}
                                                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                                >
                                                    {style}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Effect Config */}
                                {selectedNodeData.type === "effect" && (
                                    <div>
                                        <label className="text-xs font-medium mb-2 block" style={{ color: "var(--foreground-muted)" }}>
                                            Efekt Seç
                                        </label>
                                        <div className="grid grid-cols-2 gap-2">
                                            {effectOptions.map(effect => (
                                                <button
                                                    key={effect}
                                                    onClick={() => updateNodeConfig(selectedNodeData.id, "value", effect)}
                                                    className={`p-2 text-xs rounded-lg transition-all ${selectedNodeData.config.value === effect
                                                        ? "ring-2 ring-[var(--accent)]"
                                                        : ""
                                                        }`}
                                                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                                >
                                                    {effect}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Output Config */}
                                {selectedNodeData.type === "output" && (
                                    <div className="space-y-3">
                                        <div>
                                            <label className="text-xs font-medium mb-2 block" style={{ color: "var(--foreground-muted)" }}>
                                                Çıktı Formatı
                                            </label>
                                            <select
                                                value={selectedNodeData.config.format || "1:1"}
                                                onChange={(e) => updateNodeConfig(selectedNodeData.id, "format", e.target.value)}
                                                className="w-full p-2 rounded-lg text-sm"
                                                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                            >
                                                <option value="1:1">1:1 (Kare)</option>
                                                <option value="16:9">16:9 (Yatay)</option>
                                                <option value="9:16">9:16 (Dikey)</option>
                                                <option value="4:3">4:3</option>
                                            </select>
                                        </div>
                                        <div>
                                            <label className="text-xs font-medium mb-2 block" style={{ color: "var(--foreground-muted)" }}>
                                                Kalite
                                            </label>
                                            <select
                                                value={selectedNodeData.config.quality || "high"}
                                                onChange={(e) => updateNodeConfig(selectedNodeData.id, "quality", e.target.value)}
                                                className="w-full p-2 rounded-lg text-sm"
                                                style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                            >
                                                <option value="draft">Draft</option>
                                                <option value="standard">Standard</option>
                                                <option value="high">High</option>
                                                <option value="ultra">Ultra</option>
                                            </select>
                                        </div>
                                    </div>
                                )}

                                <button
                                    onClick={() => deleteNode(selectedNodeData.id)}
                                    className="w-full py-2 text-sm rounded-lg text-red-400 hover:bg-red-500/20 transition-colors flex items-center justify-center gap-2"
                                >
                                    <Trash2 size={14} />
                                    Bloğu Sil
                                </button>
                            </div>
                        ) : (
                            <div className="text-center py-8" style={{ color: "var(--foreground-muted)" }}>
                                <Settings size={32} className="mx-auto mb-3 opacity-20" />
                                <p className="text-sm">Bir blok seçin</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
