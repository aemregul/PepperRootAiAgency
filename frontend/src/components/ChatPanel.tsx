"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Paperclip, Loader2, Mic, Smile, MoreHorizontal, ChevronDown, AlertCircle } from "lucide-react";
import { sendMessage, createSession, checkHealth } from "@/lib/api";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    image_url?: string;
}

interface ChatPanelProps {
    sessionId?: string;
    onSessionChange?: (sessionId: string) => void;
    onNewAsset?: (asset: { url: string; type: string }) => void;
}

// Helper to render @mentions with highlighting
function renderContent(content: string | undefined | null) {
    if (!content || typeof content !== 'string') {
        return content ?? '';
    }
    const parts = content.split(/(@\w+)/g);
    return parts.map((part, i) => {
        if (part.startsWith("@")) {
            return (
                <span key={i} className="mention">
                    {part}
                </span>
            );
        }
        return part;
    });
}

export function ChatPanel({ sessionId: initialSessionId, onSessionChange, onNewAsset }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
    const [isConnected, setIsConnected] = useState<boolean | null>(null);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Check backend connection
    useEffect(() => {
        const checkConnection = async () => {
            const healthy = await checkHealth();
            setIsConnected(healthy);
            if (!healthy) {
                setError("Backend bağlantısı kurulamadı. Sunucunun çalıştığından emin olun.");
            }
        };
        checkConnection();
    }, []);

    // Create session if none exists
    useEffect(() => {
        const initSession = async () => {
            if (!sessionId && isConnected) {
                try {
                    const session = await createSession("New Project");
                    setSessionId(session.id);
                    onSessionChange?.(session.id);

                    // Welcome message
                    setMessages([{
                        id: "welcome",
                        role: "assistant",
                        content: "Merhaba! Ben Pepper Root AI asistanınız. Size nasıl yardımcı olabilirim? Görsel, video veya karakter oluşturabilirim.",
                        timestamp: new Date(),
                    }]);
                } catch (err) {
                    console.error("Session creation failed:", err);
                    setError("Oturum oluşturulamadı.");
                }
            }
        };
        initSession();
    }, [isConnected, sessionId, onSessionChange]);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading || !sessionId) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);
        setError(null);

        try {
            const response = await sendMessage(sessionId, input);

            // Backend returns response as MessageResponse object
            const responseContent = typeof response.response === 'string'
                ? response.response
                : response.response?.content ?? 'Yanıt alınamadı';

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: responseContent,
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);

            // Handle generated assets
            if (response.assets && response.assets.length > 0) {
                response.assets.forEach((asset) => {
                    onNewAsset?.({ url: asset.url, type: asset.asset_type });
                });
            }
        } catch (err) {
            console.error("Chat error:", err);
            setError("Mesaj gönderilemedi. Lütfen tekrar deneyin.");

            // Fallback message
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex-1 flex flex-col h-screen">
            {/* Header */}
            <header
                className="h-14 px-4 lg:px-6 flex items-center justify-between border-b shrink-0"
                style={{
                    background: "var(--background-secondary)",
                    borderColor: "var(--border)"
                }}
            >
                <div className="flex items-center gap-3 pl-12 lg:pl-0">
                    <div
                        className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                        style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                    >
                        P
                    </div>
                    <div className="flex items-center gap-1">
                        <span className="font-medium">PepperRoot</span>
                        <span style={{ color: "var(--foreground-muted)" }}>AI Agency</span>
                        <ChevronDown size={16} style={{ color: "var(--foreground-muted)" }} />
                    </div>

                    {/* Connection status */}
                    <div className="ml-2">
                        {isConnected === null ? (
                            <Loader2 className="w-4 h-4 animate-spin" style={{ color: "var(--foreground-muted)" }} />
                        ) : isConnected ? (
                            <div className="w-2 h-2 rounded-full bg-green-500" title="Bağlı" />
                        ) : (
                            <div className="w-2 h-2 rounded-full bg-red-500" title="Bağlantı yok" />
                        )}
                    </div>
                </div>

                <button className="p-2 rounded-lg hover:bg-[var(--card)]">
                    <MoreHorizontal size={20} style={{ color: "var(--foreground-muted)" }} />
                </button>
            </header>

            {/* Error banner */}
            {error && (
                <div
                    className="px-4 py-2 flex items-center gap-2 text-sm"
                    style={{ background: "rgba(239, 68, 68, 0.1)", color: "#ef4444" }}
                >
                    <AlertCircle size={16} />
                    {error}
                </div>
            )}

            {/* Messages */}
            <div
                className="flex-1 overflow-y-auto p-4 lg:p-6"
                style={{ background: "var(--background)" }}
            >
                <div className="max-w-3xl mx-auto space-y-4">
                    {messages.length === 0 && !isLoading && (
                        <div className="text-center py-12" style={{ color: "var(--foreground-muted)" }}>
                            <svg className="w-8 h-8 mx-auto mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ color: "var(--accent)" }}>
                                <path d="M12 2c-1.5 0-3 .5-4 1.5C7 2.5 6 2 5 2c-1 0-2 .5-2.5 1.5" strokeLinecap="round" />
                                <path d="M12 2c1.5 0 3 .5 4 1.5C17 2.5 18 2 19 2c1 0 2 .5 2.5 1.5" strokeLinecap="round" />
                                <path d="M12 2v3M9 22c-2-1-3.5-3-4-5.5-.5-2.5 0-5 1-7s2.5-4 4-5c1.5 1 3 3 4 5s1.5 4.5 1 7c-.5 2.5-2 4.5-4 5.5" strokeLinejoin="round" />
                                <path d="M12 10c.5 1.5.5 3.5 0 5" strokeLinecap="round" />
                            </svg>
                            <p>Merhaba! Bir şeyler yazmaya başlayın.</p>
                        </div>
                    )}

                    {messages.map((msg) => (
                        <div key={msg.id}>
                            {msg.role === "user" ? (
                                <div className="message-bubble message-user">
                                    <p className="text-sm lg:text-[15px] leading-relaxed">
                                        {renderContent(msg.content)}
                                    </p>
                                </div>
                            ) : (
                                <div className="flex gap-3">
                                    <div
                                        className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
                                        style={{ background: "var(--accent)" }}
                                    >
                                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ color: "var(--background)" }}>
                                            <path d="M12 2c-1.5 0-3 .5-4 1.5C7 2.5 6 2 5 2c-1 0-2 .5-2.5 1.5" strokeLinecap="round" />
                                            <path d="M12 2c1.5 0 3 .5 4 1.5C17 2.5 18 2 19 2c1 0 2 .5 2.5 1.5" strokeLinecap="round" />
                                            <path d="M12 2v3M9 22c-2-1-3.5-3-4-5.5-.5-2.5 0-5 1-7s2.5-4 4-5c1.5 1 3 3 4 5s1.5 4.5 1 7c-.5 2.5-2 4.5-4 5.5" strokeLinejoin="round" />
                                        </svg>
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-medium mb-2 text-sm">Pepper AI Assistant</div>
                                        <div className="message-bubble message-ai">
                                            <p className="text-sm lg:text-[15px] leading-relaxed whitespace-pre-wrap">
                                                {renderContent(msg.content)}
                                            </p>

                                            {msg.image_url && (
                                                <img
                                                    src={msg.image_url}
                                                    alt="Generated"
                                                    className="mt-3 rounded-lg max-w-full"
                                                />
                                            )}
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-3">
                            <div
                                className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold"
                                style={{ background: "var(--accent)", color: "var(--background)" }}
                            >
                                P
                            </div>
                            <div className="message-bubble message-ai flex items-center gap-2">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span className="text-sm">Düşünüyor...</span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input */}
            <div
                className="p-3 lg:p-4 shrink-0"
                style={{ background: "var(--background-secondary)" }}
            >
                <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
                    <div className="chat-input flex items-center gap-2 p-2">
                        <button
                            type="button"
                            className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors shrink-0"
                            title="Sesli giriş"
                        >
                            <Mic size={20} style={{ color: "var(--foreground-muted)" }} />
                        </button>

                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isConnected ? "Mesajınızı yazın..." : "Backend bağlantısı bekleniyor..."}
                            className="flex-1 bg-transparent outline-none text-sm lg:text-[15px] px-2"
                            style={{ color: "var(--foreground)" }}
                            disabled={isLoading || !isConnected}
                        />

                        <div className="flex items-center gap-1 shrink-0">
                            <button
                                type="button"
                                className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                                title="Emoji"
                            >
                                <Smile size={20} style={{ color: "var(--foreground-muted)" }} />
                            </button>
                            <button
                                type="button"
                                className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                                title="Dosya ekle"
                            >
                                <Paperclip size={20} style={{ color: "var(--foreground-muted)" }} />
                            </button>
                            <button
                                type="submit"
                                disabled={!input.trim() || isLoading || !isConnected}
                                className="p-2 rounded-lg transition-all duration-200 disabled:opacity-40"
                                style={{
                                    background: input.trim() && isConnected ? "var(--accent)" : "transparent",
                                    color: input.trim() && isConnected ? "var(--background)" : "var(--foreground-muted)"
                                }}
                            >
                                <Send size={18} />
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}
