"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Paperclip, Loader2, Mic, Smile, MoreHorizontal, ChevronDown, AlertCircle, Sparkles, X, Image } from "lucide-react";
import { sendMessage, createSession, checkHealth, getSessionHistory } from "@/lib/api";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    image_url?: string;
}

interface ChatPanelProps {
    sessionId?: string;
    projectId?: string;
    onSessionChange?: (sessionId: string) => void;
    onNewAsset?: (asset: { url: string; type: string }) => void;
    onEntityChange?: () => void;
    pendingPrompt?: string | null;
    onPromptConsumed?: () => void;
}

// Helper to render @mentions, markdown images, and links
function renderContent(content: string | undefined | null) {
    if (!content || typeof content !== 'string') {
        return content ?? '';
    }

    // Markdown görsellerini ve linkleri parse et
    // ![alt](url) formatındaki görselleri bul
    // [text](url) formatındaki linkleri bul
    // @mention formatındaki tag'leri bul

    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    // Combined regex for all patterns
    // 1. Markdown images: ![alt](url)
    // 2. Markdown links: [text](url)
    // 3. @mentions: @word
    const combinedRegex = /!\[([^\]]*)\]\(([^)]+)\)|\[([^\]]+)\]\(([^)]+)\)|@[\w_]+/g;

    let match;
    let key = 0;

    while ((match = combinedRegex.exec(content)) !== null) {
        // Add text before the match
        if (match.index > lastIndex) {
            elements.push(content.slice(lastIndex, match.index));
        }

        if (match[0].startsWith('![')) {
            // Markdown image: ![alt](url)
            const alt = match[1] || 'Görsel';
            const url = match[2];
            elements.push(
                <img
                    key={key++}
                    src={url}
                    alt={alt}
                    className="mt-2 mb-2 rounded-lg max-w-full max-h-64 object-contain cursor-pointer hover:opacity-90 transition-opacity"
                    onClick={() => window.open(url, '_blank')}
                    onError={(e) => {
                        // Görsel yüklenemezse link olarak göster
                        const target = e.currentTarget;
                        target.style.display = 'none';
                        const fallback = document.createElement('a');
                        fallback.href = url;
                        fallback.target = '_blank';
                        fallback.textContent = `🔗 ${alt}`;
                        fallback.className = 'text-[var(--accent)] underline';
                        target.parentNode?.insertBefore(fallback, target);
                    }}
                />
            );
        } else if (match[0].startsWith('[')) {
            // Markdown link: [text](url)
            const text = match[3];
            const url = match[4];
            elements.push(
                <a
                    key={key++}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--accent)] underline hover:opacity-80"
                >
                    {text}
                </a>
            );
        } else if (match[0].startsWith('@')) {
            // @mention
            elements.push(
                <span key={key++} className="mention">
                    {match[0]}
                </span>
            );
        }

        lastIndex = match.index + match[0].length;
    }

    // Add remaining text after last match
    if (lastIndex < content.length) {
        elements.push(content.slice(lastIndex));
    }

    return elements.length > 0 ? elements : content;
}

export function ChatPanel({ sessionId: initialSessionId, onSessionChange, onNewAsset, onEntityChange, pendingPrompt, onPromptConsumed }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
    const [isConnected, setIsConnected] = useState<boolean | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [attachedFile, setAttachedFile] = useState<File | null>(null);
    const [filePreview, setFilePreview] = useState<string | null>(null);
    const [isDragOver, setIsDragOver] = useState(false);
    const [offlineQueue, setOfflineQueue] = useState<{ message: string, timestamp: number }[]>([]);
    const [isOffline, setIsOffline] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // === AUTO-SAVE DRAFT TO LOCALSTORAGE ===
    const DRAFT_KEY = `pepper_draft_${initialSessionId || 'default'}`;

    // Load draft from localStorage on mount
    useEffect(() => {
        if (typeof window === 'undefined') return;
        const savedDraft = localStorage.getItem(DRAFT_KEY);
        if (savedDraft && !input) {
            setInput(savedDraft);
        }
    }, [initialSessionId]);

    // Save draft to localStorage on input change (debounced)
    useEffect(() => {
        if (typeof window === 'undefined') return;
        const timer = setTimeout(() => {
            if (input.trim()) {
                localStorage.setItem(DRAFT_KEY, input);
            } else {
                localStorage.removeItem(DRAFT_KEY);
            }
        }, 500); // 500ms debounce
        return () => clearTimeout(timer);
    }, [input, DRAFT_KEY]);

    // === OFFLINE DETECTION ===
    useEffect(() => {
        if (typeof window === 'undefined') return;

        const handleOnline = () => {
            setIsOffline(false);
            // Retry queued messages when back online
            if (offlineQueue.length > 0) {
                offlineQueue.forEach((item) => {
                    // Re-add to input for user to send
                    setInput(item.message);
                });
                setOfflineQueue([]);
                localStorage.removeItem('pepper_offline_queue');
            }
        };

        const handleOffline = () => {
            setIsOffline(true);
        };

        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);

        // Load any saved offline queue
        const savedQueue = localStorage.getItem('pepper_offline_queue');
        if (savedQueue) {
            try {
                setOfflineQueue(JSON.parse(savedQueue));
            } catch (e) {
                console.error('Failed to parse offline queue');
            }
        }

        return () => {
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, []);

    // Handle entity and asset drag & drop
    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.types.includes('application/x-entity-tag') ||
            e.dataTransfer.types.includes('application/x-asset-url')) {
            setIsDragOver(true);
            e.dataTransfer.dropEffect = 'copy';
        }
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);
    };

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragOver(false);

        // Entity tag drop (karakterler, mekanlar)
        const entityTag = e.dataTransfer.getData('application/x-entity-tag');
        if (entityTag) {
            setInput((prev) => {
                const newValue = prev.trim() ? `${prev} ${entityTag}` : entityTag;
                return newValue;
            });
            inputRef.current?.focus();
            return;
        }

        // Asset image drop (referans görsel olarak)
        const assetUrl = e.dataTransfer.getData('application/x-asset-url');
        if (assetUrl) {
            try {
                // URL'den dosya oluştur
                const response = await fetch(assetUrl);
                const blob = await response.blob();
                const file = new File([blob], 'reference_image.png', { type: blob.type });

                // Dosyayı referans görsel olarak ekle
                setAttachedFile(file);
                const previewUrl = URL.createObjectURL(file);
                setFilePreview(previewUrl);

                // Focus input
                inputRef.current?.focus();
            } catch (error) {
                console.error('Error loading dropped image:', error);
            }
            return;
        }
    };

    // Handle file selection
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            if (file.type.startsWith('image/')) {
                setAttachedFile(file);
                const reader = new FileReader();
                reader.onload = (e) => {
                    setFilePreview(e.target?.result as string);
                };
                reader.readAsDataURL(file);
            } else {
                setError('Sadece resim dosyaları destekleniyor.');
            }
        }
    };

    const removeAttachment = () => {
        setAttachedFile(null);
        setFilePreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

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

    // initialSessionId değiştiğinde veya ilk yüklemede mesaj geçmişini yükle
    useEffect(() => {
        const loadHistory = async () => {
            if (!initialSessionId) return;

            // SessionId'yi güncelle
            setSessionId(initialSessionId);
            setIsLoading(true);

            try {
                // Backend'den mesaj geçmişini yükle
                const history = await getSessionHistory(initialSessionId);
                const formattedMessages: Message[] = history.map((msg: {
                    id: string;
                    role: string;
                    content: string;
                    created_at: string;
                    metadata_?: { images?: { url: string }[]; has_reference_image?: boolean };
                }) => ({
                    id: msg.id,
                    role: msg.role as 'user' | 'assistant',
                    content: msg.content,
                    timestamp: new Date(msg.created_at),
                    // Metadata'dan image_url al (assistant mesajları için images[0], user için has_reference_image)
                    image_url: msg.metadata_?.images?.[0]?.url,
                }));
                setMessages(formattedMessages);
            } catch (err) {
                console.error('Mesaj geçmişi yüklenemedi:', err);
                setMessages([]);
            } finally {
                setIsLoading(false);
            }
        };
        loadHistory();
    }, [initialSessionId]);

    // Workflow'dan gelen prompt'u otomatik gönder
    useEffect(() => {
        if (pendingPrompt && sessionId && !isLoading) {
            setInput(pendingPrompt);
            onPromptConsumed?.();
            // Küçük bir gecikmeyle formu submit et
            setTimeout(() => {
                const form = document.querySelector('form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
            }, 100);
        }
    }, [pendingPrompt, sessionId, isLoading, onPromptConsumed]);

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, scrollToBottom]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading || !sessionId) return;

        // If offline, queue the message
        if (isOffline || !navigator.onLine) {
            const queueItem = { message: input, timestamp: Date.now() };
            const newQueue = [...offlineQueue, queueItem];
            setOfflineQueue(newQueue);
            localStorage.setItem('pepper_offline_queue', JSON.stringify(newQueue));
            setError("Çevrimdışısınız. Mesaj bağlantı geldiğinde gönderilecek.");
            return;
        }

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date(),
            image_url: filePreview || undefined,
        };

        setMessages((prev) => [...prev, userMessage]);

        const currentInput = input;
        const currentFile = attachedFile;

        setInput("");
        // Clear draft from localStorage after successful send start
        localStorage.removeItem(DRAFT_KEY);
        removeAttachment(); // Dosyayı temizle
        setIsLoading(true);
        setError(null);

        try {
            const response = await sendMessage(sessionId, currentInput, currentFile || undefined);


            // Backend returns response as MessageResponse object
            const responseContent = typeof response.response === 'string'
                ? response.response
                : response.response?.content ?? 'Yanıt alınamadı';

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: responseContent,
                timestamp: new Date(),
                // Response'daki ilk image asset'ini mesaja ekle
                image_url: response.assets?.find((a: { asset_type: string; url: string }) => a.asset_type === 'image')?.url,
            };

            setMessages((prev) => [...prev, assistantMessage]);

            // Handle generated assets - trigger refresh
            if (response.assets && response.assets.length > 0) {
                response.assets.forEach((asset: { url: string; asset_type: string }) => {
                    onNewAsset?.({ url: asset.url, type: asset.asset_type });
                });
            }

            // Handle created entities - trigger sidebar refresh
            if (response.entities_created && response.entities_created.length > 0) {
                onEntityChange?.();
            }
        } catch (err) {
            console.error("Chat error:", err);
            // Save failed message back to draft for retry
            localStorage.setItem(DRAFT_KEY, currentInput);
            setError("Mesaj gönderilemedi. Mesajınız kaydedildi, tekrar deneyin.");

            // Fallback message
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "Üzgünüm, bir hata oluştu. Mesajınız kaydedildi, lütfen tekrar deneyin.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div
            className={`flex-1 flex flex-col h-screen ${isDragOver ? 'ring-2 ring-[var(--accent)] ring-inset' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
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
                        ) : isConnected && !isOffline ? (
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

            {/* Offline banner */}
            {isOffline && (
                <div
                    className="px-4 py-2 flex items-center gap-2 text-sm"
                    style={{ background: "rgba(234, 179, 8, 0.1)", color: "#eab308" }}
                >
                    <AlertCircle size={16} />
                    Çevrimdışı - İnternet bağlantınız yok. Mesajlar bağlantı geldiğinde gönderilecek.
                </div>
            )}

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
                        <div className="flex flex-col items-center justify-center py-16">
                            {/* Logo & Title */}
                            <div className="text-4xl mb-4">🫑</div>
                            <h2 className="text-2xl font-bold mb-2">Pepper Root AI</h2>
                            <p className="text-sm mb-8" style={{ color: "var(--foreground-muted)" }}>
                                Yapay zeka destekli görsel üretim asistanın
                            </p>

                            {/* Quick Actions */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md">
                                <button
                                    onClick={() => setInput("Profesyonel bir stüdyo ortamında, yumuşak aydınlatma altında, 30'lu yaşlarında karizmatik bir iş insanı portresi oluştur. Modern ve minimal bir arka plan kullan.")}
                                    className="p-4 rounded-xl text-left transition-all hover:scale-[1.02]"
                                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                >
                                    <span className="text-lg mb-2 block">🎨</span>
                                    <span className="text-sm font-medium">Görsel Oluştur</span>
                                    <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                        Profesyonel görsel üret
                                    </p>
                                </button>
                                <button
                                    onClick={() => setInput("Yeni bir ana karakter oluşturmak istiyorum. İsmi Ayşe olsun, 28 yaşında, profesyonel bir iç mimar. Kısa kahverengi saçları, yeşil gözleri ve modern, şık bir giyim tarzı var. @karakter_ayse olarak kaydet.")}
                                    className="p-4 rounded-xl text-left transition-all hover:scale-[1.02]"
                                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                >
                                    <span className="text-lg mb-2 block">👤</span>
                                    <span className="text-sm font-medium">Karakter Ekle</span>
                                    <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                        Detaylı karakter profili
                                    </p>
                                </button>
                                <button
                                    onClick={() => setInput("Yeni bir mekan oluşturmak istiyorum: Lüks bir penthouse dairesi, geniş pencerelerden şehir manzarası görünen, minimalist dekorasyonlu, beyaz ve gri tonlarında modern bir oturma odası. @lokasyon_penthouse olarak kaydet.")}
                                    className="p-4 rounded-xl text-left transition-all hover:scale-[1.02]"
                                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                >
                                    <span className="text-lg mb-2 block">📍</span>
                                    <span className="text-sm font-medium">Lokasyon Ekle</span>
                                    <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                        Atmosferik mekan tanımla
                                    </p>
                                </button>
                                <button
                                    onClick={() => setInput("Merhaba! Tüm yeteneklerini ve yapabileceklerini detaylı olarak açıkla. Görsel üretimi, karakter yönetimi, video oluşturma ve diğer özelliklerini anlat.")}
                                    className="p-4 rounded-xl text-left transition-all hover:scale-[1.02]"
                                    style={{ background: "var(--card)", border: "1px solid var(--border)" }}
                                >
                                    <span className="text-lg mb-2 block">💡</span>
                                    <span className="text-sm font-medium">Ne Yapabilirim?</span>
                                    <p className="text-xs mt-1" style={{ color: "var(--foreground-muted)" }}>
                                        Tüm özellikleri keşfet
                                    </p>
                                </button>
                            </div>
                        </div>
                    )}

                    {messages.map((msg) => (
                        <div key={msg.id}>
                            {msg.role === "user" ? (
                                <div className="message-bubble message-user">
                                    {msg.image_url && (
                                        <img
                                            src={msg.image_url}
                                            alt="Referans görsel"
                                            className="w-32 h-32 object-cover rounded-lg mb-2"
                                        />
                                    )}
                                    <p className="text-sm lg:text-[15px] leading-relaxed">
                                        {renderContent(msg.content)}
                                    </p>
                                </div>
                            ) : (
                                <div className="flex gap-3">
                                    <span className="text-xl shrink-0">🫑</span>
                                    <div className="flex-1">
                                        <div className="font-medium mb-2 text-sm">Pepper AI Assistant</div>
                                        <div className="message-bubble message-ai">
                                            <p className="text-sm lg:text-[15px] leading-relaxed whitespace-pre-wrap">
                                                {renderContent(msg.content)}
                                            </p>

                                            {/* Only show image_url if it's NOT already in content as markdown */}
                                            {msg.image_url && !msg.content?.includes(msg.image_url) && (
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
                            <span className="text-xl shrink-0">🫑</span>
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
                    {/* File Preview */}
                    {filePreview && (
                        <div className="mb-2 p-2 rounded-lg flex items-center gap-3" style={{ background: "var(--card)" }}>
                            <div className="relative">
                                <img
                                    src={filePreview}
                                    alt="Referans görsel"
                                    className="w-16 h-16 object-cover rounded-lg"
                                />
                                <button
                                    type="button"
                                    onClick={removeAttachment}
                                    className="absolute -top-2 -right-2 p-1 rounded-full bg-red-500 text-white hover:bg-red-600 transition-colors"
                                >
                                    <X size={12} />
                                </button>
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center gap-2 text-sm font-medium">
                                    <Image size={14} style={{ color: "var(--accent)" }} />
                                    Referans Görsel
                                </div>
                                <p className="text-xs mt-0.5 truncate" style={{ color: "var(--foreground-muted)" }}>
                                    {attachedFile?.name}
                                </p>
                            </div>
                        </div>
                    )}

                    <div className="chat-input flex items-center gap-2 p-2">
                        <button
                            type="button"
                            className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors shrink-0"
                            title="Sesli giriş"
                        >
                            <Mic size={20} style={{ color: "var(--foreground-muted)" }} />
                        </button>

                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={isDragOver ? "Buraya bırak..." : isConnected ? "Mesajınızı yazın..." : "Backend bağlantısı bekleniyor..."}
                            className={`flex-1 bg-transparent outline-none text-sm lg:text-[15px] px-2 ${isDragOver ? 'text-[var(--accent)]' : ''}`}
                            style={{ color: "var(--foreground)" }}
                            disabled={isLoading || !isConnected}
                        />

                        <div className="flex items-center gap-1 shrink-0">
                            {/* Plugin Yap Button */}
                            <button
                                type="button"
                                onClick={() => {
                                    const pluginMessage = "Plugin oluşturma modunu başlat. Şu ana kadar bu sohbette kullandığım karakter, lokasyon, zaman, kamera açıları ve stil ayarlarını analiz et ve bana uygun bir Creative Plugin önerisi sun.";
                                    setInput(pluginMessage);
                                }}
                                className="p-2 rounded-lg transition-all hover:shadow-md"
                                style={{
                                    background: "linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(168, 85, 247, 0.15) 100%)",
                                    border: "1px solid rgba(139, 92, 246, 0.3)"
                                }}
                                title="Bu sohbetten otomatik plugin oluştur"
                            >
                                <Sparkles size={18} className="text-purple-400" />
                            </button>
                            <button
                                type="button"
                                className="p-2 rounded-lg hover:bg-[var(--card)] transition-colors"
                                title="Emoji"
                            >
                                <Smile size={20} style={{ color: "var(--foreground-muted)" }} />
                            </button>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelect}
                                className="hidden"
                            />
                            <button
                                type="button"
                                onClick={() => fileInputRef.current?.click()}
                                className={`p-2 rounded-lg transition-colors ${attachedFile ? 'bg-[var(--accent)]/20' : 'hover:bg-[var(--card)]'}`}
                                title="Referans görsel ekle"
                            >
                                <Paperclip size={20} style={{ color: attachedFile ? 'var(--accent)' : 'var(--foreground-muted)' }} />
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
