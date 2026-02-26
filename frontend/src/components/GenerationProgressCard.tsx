"use client";

interface GenerationProgressCardProps {
    type: "video" | "long_video" | "image";
    duration?: string | number;
    progress: number; // 0-100 real progress from parent
    status: "generating" | "complete" | "error";
}

export function GenerationProgressCard({
    type,
    duration,
    progress,
    status,
}: GenerationProgressCardProps) {
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
            </div>
        </div>
    );
}
