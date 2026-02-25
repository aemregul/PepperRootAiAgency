"use client";

import { useState, useEffect, useRef } from "react";

interface GenerationProgressCardProps {
    type: "video" | "long_video" | "image";
    prompt?: string;
    duration?: string | number;
    sessionId: string;
    onComplete?: (result: { video_url?: string; message?: string }) => void;
}

export function GenerationProgressCard({
    type,
    prompt,
    duration,
    sessionId,
    onComplete,
}: GenerationProgressCardProps) {
    const [progress, setProgress] = useState(0);
    const [status, setStatus] = useState<"generating" | "complete" | "error">("generating");
    const [resultUrl, setResultUrl] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const simulateRef = useRef<ReturnType<typeof setInterval> | null>(null);
    const targetProgressRef = useRef(0);

    useEffect(() => {
        // WebSocket bağlantısı
        const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.hostname}:8000/api/v1/chat/ws/progress/${sessionId}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("🔌 Progress WS connected");
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === "progress") {
                    targetProgressRef.current = Math.round(data.progress * 100);
                } else if (data.type === "complete") {
                    targetProgressRef.current = 100;
                    setProgress(100);
                    setStatus("complete");
                    setResultUrl(data.result?.video_url || null);
                    onComplete?.(data.result || {});
                } else if (data.type === "error") {
                    setStatus("error");
                }
            } catch { /* ignore */ }
        };

        ws.onerror = () => {
            console.warn("Progress WS error — using simulated progress");
        };

        ws.onclose = () => {
            console.log("🔌 Progress WS closed");
        };

        // Simulated smooth progress animation
        // Moves toward targetProgressRef at a natural pace
        let simulated = 0;
        simulateRef.current = setInterval(() => {
            if (status === "complete" || status === "error") return;

            const target = targetProgressRef.current;
            if (target > simulated) {
                // Jump closer to real target
                simulated = Math.min(target, simulated + 2);
            } else if (simulated < 95) {
                // Slow auto-advance when no WS updates (for non-WS fallback)
                simulated += 0.15;
            }
            setProgress(Math.round(simulated));
        }, 500);

        // Keep-alive ping
        const pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send("ping");
            }
        }, 15000);

        return () => {
            ws.close();
            wsRef.current = null;
            if (simulateRef.current) clearInterval(simulateRef.current);
            clearInterval(pingInterval);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [sessionId]);

    const icon = type === "image" ? "🖼️" : "🎬";
    const label = type === "image" ? "Görsel" : "Video";
    const durationText = duration ? `${duration}s` : "";

    return (
        <div className="mt-3 mb-2 rounded-2xl overflow-hidden" style={{ maxWidth: "360px" }}>
            <div
                className="relative p-5"
                style={{
                    background: type === "image"
                        ? "linear-gradient(135deg, rgba(16,185,129,0.25) 0%, rgba(30,30,60,1) 50%, rgba(139,92,246,0.2) 100%)"
                        : "linear-gradient(135deg, rgba(99,102,241,0.25) 0%, rgba(20,20,40,1) 50%, rgba(139,92,246,0.25) 100%)",
                }}
            >
                {/* Header */}
                <div className="flex items-center gap-2.5 mb-4">
                    <div className="w-9 h-9 rounded-xl flex items-center justify-center"
                        style={{ background: "rgba(255,255,255,0.08)" }}>
                        <span className="text-lg">{icon}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                        <span className="text-sm font-medium text-white/90 block">
                            {label} {status === "complete" ? "Hazır!" : "Üretiliyor"}
                        </span>
                        {durationText && (
                            <span className="text-[11px] text-white/35">{durationText}</span>
                        )}
                    </div>
                </div>

                {/* Progress area */}
                {status === "generating" && (
                    <div className="flex flex-col items-center gap-3">
                        {/* Big percentage */}
                        <div className="text-4xl font-light text-white/90 tabular-nums tracking-tight" style={{ fontVariantNumeric: "tabular-nums" }}>
                            {progress}<span className="text-xl text-white/40">%</span>
                        </div>

                        {/* Progress bar */}
                        <div className="w-full h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.08)" }}>
                            <div
                                className="h-full rounded-full transition-all duration-700 ease-out"
                                style={{
                                    width: `${progress}%`,
                                    background: type === "image"
                                        ? "linear-gradient(90deg, #10b981, #34d399)"
                                        : "linear-gradient(90deg, #6366f1, #a78bfa)",
                                }}
                            />
                        </div>
                    </div>
                )}

                {/* Complete state */}
                {status === "complete" && (
                    <div className="flex items-center justify-center gap-2 py-2">
                        <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center">
                            <span className="text-emerald-400 text-sm">✓</span>
                        </div>
                        <span className="text-sm text-emerald-400 font-medium">Tamamlandı!</span>
                    </div>
                )}

                {/* Error state */}
                {status === "error" && (
                    <div className="flex items-center justify-center gap-2 py-2">
                        <span className="text-sm text-red-400">⚠️ Üretim başarısız</span>
                    </div>
                )}

                {/* Prompt preview */}
                {prompt && (
                    <p className="text-[11px] text-white/25 mt-3 truncate">{prompt}</p>
                )}
            </div>
        </div>
    );
}
