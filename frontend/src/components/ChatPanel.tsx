"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Loader2 } from "lucide-react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    image_url?: string;
}

interface ChatPanelProps {
    onNewAsset?: (asset: { url: string; type: string }) => void;
}

export function ChatPanel({ onNewAsset }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "assistant",
            content: "Merhaba! Ben Pepper Root AI asistanınız. Size nasıl yardımcı olabilirim? Görsel, video veya karakter oluşturabilirim. 🫑",
            timestamp: new Date(),
        },
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            // TODO: Backend API çağrısı
            // Şimdilik mock response
            await new Promise((resolve) => setTimeout(resolve, 1500));

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "Bu özellik yakında aktif olacak! Backend API'ye bağlanmak için geliştirme devam ediyor.",
                timestamp: new Date(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
            console.error("Chat error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex-1 flex flex-col h-screen lg:h-screen">
            {/* Header */}
            <header
                className="h-14 px-4 lg:px-6 flex items-center justify-between border-b shrink-0"
                style={{
                    background: "var(--background-secondary)",
                    borderColor: "var(--border)"
                }}
            >
                <div className="flex items-center gap-3">
                    <span className="text-lg font-semibold pl-12 lg:pl-0">
                        Yeni Proje
                    </span>
                </div>
            </header>

            {/* Messages */}
            <div
                className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4"
                style={{ background: "var(--background)" }}
            >
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                        <div
                            className={`
                max-w-[85%] lg:max-w-[70%] p-3 lg:p-4 rounded-2xl
                ${msg.role === "user"
                                    ? "rounded-br-md"
                                    : "rounded-bl-md glass"
                                }
              `}
                            style={{
                                background: msg.role === "user"
                                    ? "var(--accent)"
                                    : "var(--ai-bubble)",
                                color: msg.role === "user"
                                    ? "var(--background)"
                                    : "var(--foreground)",
                            }}
                        >
                            <p className="text-sm lg:text-base leading-relaxed whitespace-pre-wrap">
                                {msg.content}
                            </p>
                            {msg.image_url && (
                                <img
                                    src={msg.image_url}
                                    alt="Generated"
                                    className="mt-3 rounded-lg max-w-full"
                                />
                            )}
                            <span
                                className="text-xs mt-2 block opacity-60"
                            >
                                {msg.timestamp.toLocaleTimeString("tr-TR", {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                })}
                            </span>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div
                            className="p-4 rounded-2xl rounded-bl-md glass"
                            style={{ background: "var(--ai-bubble)" }}
                        >
                            <Loader2 className="w-5 h-5 animate-spin" />
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form
                onSubmit={handleSubmit}
                className="p-3 lg:p-4 border-t shrink-0"
                style={{
                    background: "var(--background-secondary)",
                    borderColor: "var(--border)"
                }}
            >
                <div
                    className="flex items-center gap-2 lg:gap-3 p-2 lg:p-3 rounded-xl"
                    style={{ background: "var(--background)" }}
                >
                    <button
                        type="button"
                        className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors shrink-0"
                        title="Dosya ekle"
                    >
                        <Paperclip size={20} style={{ color: "var(--foreground-muted)" }} />
                    </button>

                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Mesajınızı yazın..."
                        className="flex-1 bg-transparent outline-none text-sm lg:text-base"
                        style={{ color: "var(--foreground)" }}
                        disabled={isLoading}
                    />

                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="p-2 lg:p-3 rounded-lg transition-all duration-200 disabled:opacity-50 shrink-0"
                        style={{
                            background: "var(--accent)",
                            color: "var(--background)"
                        }}
                    >
                        <Send size={18} />
                    </button>
                </div>
            </form>
        </div>
    );
}
