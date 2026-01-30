"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Loader2, Mic, Smile, MoreHorizontal, ChevronDown } from "lucide-react";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    image_url?: string;
    status?: "pending" | "done";
}

interface ChatPanelProps {
    onNewAsset?: (asset: { url: string; type: string }) => void;
}

// Helper to render @mentions with highlighting
function renderContent(content: string) {
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

export function ChatPanel({ onNewAsset }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "user",
            content: "@character_emre and @character_ahmet @location_kitchen at night. Create a 3-minute cinematic video.",
            timestamp: new Date(),
        },
        {
            id: "2",
            role: "assistant",
            content: `Understood! I'll create a cinematic video with Emre and Ahmet in a modern kitchen at night. Let me handle the details while you get comfortable. Here's the plan:`,
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
            await new Promise((resolve) => setTimeout(resolve, 1500));

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "I'll get started on that right away. Let me gather the necessary references and begin processing your request.",
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
                </div>

                <button className="p-2 rounded-lg hover:bg-[var(--card)]">
                    <MoreHorizontal size={20} style={{ color: "var(--foreground-muted)" }} />
                </button>
            </header>

            {/* Messages */}
            <div
                className="flex-1 overflow-y-auto p-4 lg:p-6"
                style={{ background: "var(--background)" }}
            >
                <div className="max-w-3xl mx-auto space-y-4">
                    {messages.map((msg) => (
                        <div key={msg.id}>
                            {msg.role === "user" ? (
                                // User message
                                <div className="message-bubble message-user">
                                    <p className="text-sm lg:text-[15px] leading-relaxed">
                                        {renderContent(msg.content)}
                                    </p>
                                </div>
                            ) : (
                                // AI message
                                <div className="flex gap-3">
                                    <div
                                        className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold"
                                        style={{ background: "var(--accent)", color: "var(--background)" }}
                                    >
                                        P
                                    </div>
                                    <div className="flex-1">
                                        <div className="font-medium mb-2 text-sm">Pepper AI Assistant</div>
                                        <div className="message-bubble message-ai">
                                            <p className="text-sm lg:text-[15px] leading-relaxed">
                                                {renderContent(msg.content)}
                                            </p>

                                            {/* Task steps (mock) */}
                                            {msg.id === "2" && (
                                                <div className="mt-4 space-y-2">
                                                    <div className="flex items-center gap-2 text-sm">
                                                        <span>•</span>
                                                        <span>Gathering character references: @character_emre</span>
                                                        <span style={{ color: "var(--accent)" }}>✓</span>
                                                    </div>
                                                    <div className="flex items-center gap-2 text-sm">
                                                        <span>•</span>
                                                        <span>Setting location context: @location_kitchen</span>
                                                        <Loader2 className="w-3 h-3 animate-spin" style={{ color: "var(--foreground-muted)" }} />
                                                    </div>
                                                    <div className="flex items-center gap-2 text-sm" style={{ color: "var(--foreground-muted)" }}>
                                                        <span>•</span>
                                                        <span>Starting video engine...</span>
                                                    </div>
                                                </div>
                                            )}
                                        </div>

                                        {msg.id === "2" && (
                                            <p className="text-sm mt-3" style={{ color: "var(--foreground-muted)" }}>
                                                If I need more detail, I&apos;ll let you know.
                                            </p>
                                        )}
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
                                <span className="text-sm">Thinking...</span>
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
                            title="Voice input"
                        >
                            <Mic size={20} style={{ color: "var(--foreground-muted)" }} />
                        </button>

                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your request..."
                            className="flex-1 bg-transparent outline-none text-sm lg:text-[15px] px-2"
                            style={{ color: "var(--foreground)" }}
                            disabled={isLoading}
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
                                title="Attach file"
                            >
                                <Paperclip size={20} style={{ color: "var(--foreground-muted)" }} />
                            </button>
                            <button
                                type="submit"
                                disabled={!input.trim() || isLoading}
                                className="p-2 rounded-lg transition-all duration-200 disabled:opacity-40"
                                style={{
                                    background: input.trim() ? "var(--accent)" : "transparent",
                                    color: input.trim() ? "var(--background)" : "var(--foreground-muted)"
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
