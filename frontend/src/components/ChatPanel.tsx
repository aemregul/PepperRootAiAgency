"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { Send, Paperclip, Loader2, Mic, Smile, MoreHorizontal, ChevronDown, AlertCircle, Sparkles, X, Image, ZoomIn } from "lucide-react";
import { useToast } from "./ToastProvider";
import { sendMessage, createSession, checkHealth, getSessionHistory } from "@/lib/api";

interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
    image_url?: string;
    video_url?: string;
}

interface ChatPanelProps {
    sessionId?: string;
    activeProjectId?: string;  // Aktif proje — asset'ler buraya kaydedilir
    onSessionChange?: (sessionId: string) => void;
    onNewAsset?: (asset: { url: string; type: string }) => void;
    onEntityChange?: () => void;
    pendingPrompt?: string | null;
    onPromptConsumed?: () => void;
}

// Helper to render @mentions, markdown images, links, and VIDEOS
function renderContent(content: string | undefined | null, onImageClick?: (url: string) => void) {
    if (!content || typeof content !== 'string') {
        return content ?? '';
    }

    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    // Combined regex for all patterns
    // 1. Markdown images: ![alt](url)
    // 2. Markdown links: [text](url)
    // 3. @mentions: @word
    // 4. Video URLs (simple detection for standalone URLs ending with video extensions)
    //    Note: This is a basic regex, might need refinement for complex URLs
    const combinedRegex = /!\[([^\]]*)\]\(([^)]+)\)|\[([^\]]+)\]\(([^)]+)\)|@[\w_]+|(https?:\/\/[^\s]+\.(?:mp4|mov|webm)(?:\?[^\s]*)?)/g;

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
                    className="mt-2 mb-2 rounded-lg max-w-full max-h-64 object-contain cursor-pointer hover:opacity-90 hover:shadow-lg transition-all"
                    onClick={() => onImageClick ? onImageClick(url) : window.open(url, '_blank')}
                    onError={(e) => {
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

            // Check if it's a video link inside markdown syntax
            if (url.match(/\.(mp4|mov|webm)(\?.*)?$/i)) {
                elements.push(
                    <div key={key++} className="mt-2 mb-2">
                        <video
                            src={url}
                            controls
                            playsInline
                            className="rounded-lg max-w-full max-h-80 border border-[var(--border)] bg-black/10"
                        />
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-[var(--foreground-muted)]">📹 {text}</span>
                            <a href={url} target="_blank" rel="noopener noreferrer" className="text-xs text-[var(--accent)] hover:underline">
                                (Yeni sekmede aç)
                            </a>
                        </div>
                    </div>
                );
            } else {
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
            }
        } else if (match[0].startsWith('@')) {
            // @mention
            elements.push(
                <span key={key++} className="mention">
                    {match[0]}
                </span>
            );
        } else if (match[5]) {
            // Standalone Video URL
            const url = match[5];
            elements.push(
                <div key={key++} className="mt-2 mb-2">
                    <video
                        src={url}
                        controls
                        playsInline
                        className="rounded-lg max-w-full max-h-80 border border-[var(--border)] bg-black/10"
                    />
                    <div className="flex items-center gap-2 mt-1">
                        <a href={url} target="_blank" rel="noopener noreferrer" className="text-xs text-[var(--accent)] hover:underline">
                            📹 Videoyu İndir / Aç
                        </a>
                    </div>
                </div>
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

export function ChatPanel({ sessionId: initialSessionId, activeProjectId, onSessionChange, onNewAsset, onEntityChange, pendingPrompt, onPromptConsumed }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState<string | null>(initialSessionId || null);
    const [isConnected, setIsConnected] = useState<boolean | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [attachedFile, setAttachedFile] = useState<File | null>(null);
    const [filePreview, setFilePreview] = useState<string | null>(null);
    const [attachedVideoUrl, setAttachedVideoUrl] = useState<string | null>(null);
    const [isDragOver, setIsDragOver] = useState(false);
    const [lightboxImage, setLightboxImage] = useState<string | null>(null);
    const [loadingStatus, setLoadingStatus] = useState<string>("Düşünüyor...");
    const loadingTimerRef = useRef<NodeJS.Timeout | null>(null);
    const [offlineQueue, setOfflineQueue] = useState<{ message: string, timestamp: number }[]>([]);
    const [isOffline, setIsOffline] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const toast = useToast();

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

        // Asset drop (image or video)
        const assetUrl = e.dataTransfer.getData('application/x-asset-url');
        const assetType = e.dataTransfer.getData('application/x-asset-type'); // 'video' | 'image'

        if (assetUrl) {
            // Eğer video ise URL referansı olarak ekle (dosya indirme yapma)
            if (assetType === 'video' || assetUrl.match(/\.(mp4|mov|webm)(\?.*)?$/i)) {
                setAttachedVideoUrl(assetUrl);
                // Clear any image attachment
                setAttachedFile(null);
                setFilePreview(null);

                inputRef.current?.focus();
                toast.success("Video eklendi");
                return;
            }

            // Image ise (eski mantıkla devam - dosyayı indirip attach et)
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
                toast.error("Görsel yüklenemedi");
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
        setAttachedVideoUrl(null);
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
        const hasContent = input.trim() || attachedFile || attachedVideoUrl;
        if (!hasContent || isLoading || !sessionId) return;

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
            content: input || (attachedFile ? "[Referans Görsel]" : ""),
            timestamp: new Date(),
            image_url: filePreview || undefined,
            video_url: attachedVideoUrl || undefined
        };

        setMessages((prev) => [...prev, userMessage]);

        // Append video URL to content for backend if exists
        const contentToSend = attachedVideoUrl
            ? `${input}\n\n[Referans Video](${attachedVideoUrl})`
            : input;

        const currentInput = contentToSend;
        const currentFile = attachedFile;

        setInput("");
        // Reset textarea height after clearing
        if (inputRef.current) {
            inputRef.current.style.height = '24px';
        }
        // Clear draft from localStorage after successful send start
        localStorage.removeItem(DRAFT_KEY);
        removeAttachment(); // Dosyayı temizle
        setIsLoading(true);
        setError(null);

        // Smart loading status based on message content
        const lowerMsg = currentInput.toLowerCase();
        const hasImage = !!currentFile;

        let statusPhases: { text: string; delay: number }[] = [];

        if (lowerMsg.match(/görsel|resim|fotoğraf|image|çiz|oluştur.*görsel|generate.*image|illustration|poster|logo/)) {
            statusPhases = [
                { text: "🎨 Prompt analiz ediliyor...", delay: 0 },
                { text: "🖌️ Görsel oluşturuluyor...", delay: 3000 },
                { text: "✨ Son rötuşlar yapılıyor...", delay: 12000 },
            ];
        } else if (lowerMsg.match(/video|animasyon|klip|sinema|cinematic/)) {
            statusPhases = [
                { text: "🎬 Video senaryosu hazırlanıyor...", delay: 0 },
                { text: "🎥 Video üretiliyor...", delay: 3000 },
                { text: "🎞️ Video işleniyor...", delay: 15000 },
            ];
        } else if (lowerMsg.match(/düzenle|edit|değiştir|kaldır|ekle.*görsel|remove|change/)) {
            statusPhases = [
                { text: "🔍 Görsel analiz ediliyor...", delay: 0 },
                { text: "✏️ Düzenleme yapılıyor...", delay: 3000 },
                { text: "✨ Sonuç hazırlanıyor...", delay: 10000 },
            ];
        } else if (hasImage) {
            statusPhases = [
                { text: "📷 Görsel inceleniyor...", delay: 0 },
                { text: "🧠 Analiz ediliyor...", delay: 2000 },
                { text: "💬 Yanıt hazırlanıyor...", delay: 5000 },
            ];
        } else if (lowerMsg.match(/tanı|kaydet|karakter|entity|lokasyon|mekan/)) {
            statusPhases = [
                { text: "🧠 Bilgi analiz ediliyor...", delay: 0 },
                { text: "💾 Kayıt yapılıyor...", delay: 2000 },
            ];
        } else {
            statusPhases = [
                { text: "💭 Düşünüyor...", delay: 0 },
                { text: "📝 Yanıt yazılıyor...", delay: 4000 },
            ];
        }

        // Set initial status
        setLoadingStatus(statusPhases[0].text);

        // Schedule phase transitions
        const timers: NodeJS.Timeout[] = [];
        statusPhases.slice(1).forEach((phase) => {
            const timer = setTimeout(() => setLoadingStatus(phase.text), phase.delay);
            timers.push(timer);
        });
        loadingTimerRef.current = timers[timers.length - 1] || null;

        // Store timers for cleanup
        const cleanupTimers = () => timers.forEach(t => clearTimeout(t));

        try {
            const response = await sendMessage(sessionId, currentInput, currentFile || undefined, activeProjectId);


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
            setLoadingStatus("Düşünüyor...");
            cleanupTimers();
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
                                            className="w-32 h-32 object-cover rounded-lg mb-2 cursor-pointer hover:opacity-90 hover:shadow-lg transition-all"
                                            onClick={() => setLightboxImage(msg.image_url!)}
                                        />
                                    )}
                                    {msg.video_url && (
                                        <div className="mb-2">
                                            <video
                                                src={msg.video_url}
                                                controls
                                                className="w-48 max-w-full rounded-lg border border-[var(--border)] bg-black/10"
                                            />
                                            <div className="text-xs mt-1 text-[var(--foreground-muted)] flex items-center gap-1">
                                                <span>📹 Video Referansı</span>
                                            </div>
                                        </div>
                                    )}
                                    <div className="text-sm lg:text-[15px] leading-relaxed">
                                        {renderContent(msg.content, setLightboxImage)}
                                    </div>
                                </div>
                            ) : (
                                <div className="flex gap-3">
                                    <span className="text-xl shrink-0">🫑</span>
                                    <div className="flex-1">
                                        <div className="font-medium mb-2 text-sm">Pepper AI Assistant</div>
                                        <div className="message-bubble message-ai">
                                            <div className="text-sm lg:text-[15px] leading-relaxed whitespace-pre-wrap">
                                                {renderContent(msg.content, setLightboxImage)}
                                            </div>

                                            {/* Only show image_url if it's NOT already in content as markdown */}
                                            {msg.image_url && !msg.content?.includes(msg.image_url) && (
                                                <img
                                                    src={msg.image_url}
                                                    alt="Üretilen görsel"
                                                    className="mt-3 rounded-lg max-w-full cursor-pointer hover:opacity-90 hover:shadow-lg transition-all"
                                                    onClick={() => setLightboxImage(msg.image_url!)}
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
                            <div className="message-bubble message-ai">
                                <div className="flex items-center gap-2">
                                    <Loader2 className="w-4 h-4 animate-spin" style={{ color: "var(--accent)" }} />
                                    <span
                                        className="text-sm"
                                        style={{ transition: "opacity 0.3s ease" }}
                                        key={loadingStatus}
                                    >
                                        {loadingStatus}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input — ChatGPT Style */}
            <div
                className="p-3 lg:p-4 shrink-0"
                style={{ background: "var(--background-secondary)" }}
            >
                <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
                    <div
                        className="chat-input rounded-2xl overflow-hidden"
                        style={{
                            background: "var(--card)",
                            border: "1px solid var(--border)",
                        }}
                    >
                        {/* Inline Image Preview — ChatGPT Style */}
                        {filePreview && (
                            <div className="p-3 pb-0">
                                <div className="relative inline-block">
                                    <img
                                        src={filePreview}
                                        alt="Referans görsel"
                                        className="w-36 h-36 object-cover rounded-xl"
                                        style={{ border: "1px solid var(--border)" }}
                                    />
                                    {/* Overlay Buttons */}
                                    <div className="absolute top-1.5 right-1.5 flex items-center gap-1">
                                        <button
                                            type="button"
                                            onClick={() => fileInputRef.current?.click()}
                                            className="p-1.5 rounded-full backdrop-blur-sm transition-colors hover:bg-black/60"
                                            style={{ background: "rgba(0,0,0,0.5)" }}
                                            title="Görseli değiştir"
                                        >
                                            <Paperclip size={13} className="text-white" />
                                        </button>
                                        <button
                                            type="button"
                                            onClick={removeAttachment}
                                            className="p-1.5 rounded-full backdrop-blur-sm transition-colors hover:bg-black/60"
                                            style={{ background: "rgba(0,0,0,0.5)" }}
                                            title="Görseli kaldır"
                                        >
                                            <X size={13} className="text-white" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Inline Video Preview */}
                        {attachedVideoUrl && (
                            <div className="p-3 pb-0">
                                <div className="relative inline-block">
                                    <div
                                        className="w-36 h-24 bg-black rounded-xl overflow-hidden flex items-center justify-center"
                                        style={{ border: "1px solid var(--border)" }}
                                    >
                                        <video
                                            src={attachedVideoUrl}
                                            className="w-full h-full object-cover opacity-80"
                                        />
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <span className="text-white text-xs font-medium bg-black/50 px-2 py-1 rounded">📹 VİDEO</span>
                                        </div>
                                    </div>
                                    <button
                                        type="button"
                                        onClick={removeAttachment}
                                        className="absolute top-1.5 right-1.5 p-1.5 rounded-full backdrop-blur-sm transition-colors hover:bg-black/60"
                                        style={{ background: "rgba(0,0,0,0.5)" }}
                                        title="Videoyu kaldır"
                                    >
                                        <X size={13} className="text-white" />
                                    </button>
                                </div>
                            </div>
                        )}

                        {/* Text Input Row */}
                        <div className="flex items-center gap-2 p-2">
                            <button
                                type="button"
                                onClick={() => fileInputRef.current?.click()}
                                className={`p-2 rounded-lg transition-colors shrink-0 ${attachedFile ? 'bg-[var(--accent)]/20' : 'hover:bg-[var(--background-secondary)]'}`}
                                title="Referans görsel ekle"
                            >
                                <Paperclip size={20} style={{ color: attachedFile ? 'var(--accent)' : 'var(--foreground-muted)' }} />
                            </button>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelect}
                                className="hidden"
                            />

                            <textarea
                                ref={inputRef}
                                value={input}
                                onChange={(e) => {
                                    setInput(e.target.value);
                                    // Auto-resize
                                    e.target.style.height = 'auto';
                                    e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' && !e.shiftKey) {
                                        e.preventDefault();
                                        if (input.trim() || attachedFile || attachedVideoUrl) {
                                            handleSubmit(e as unknown as React.FormEvent);
                                        }
                                    }
                                }}
                                placeholder={isDragOver ? "Buraya bırak..." : isConnected ? "Herhangi bir şey sor" : "Backend bağlantısı bekleniyor..."}
                                className={`flex-1 bg-transparent outline-none text-sm lg:text-[15px] px-1 resize-none ${isDragOver ? 'text-[var(--accent)]' : ''}`}
                                style={{ color: "var(--foreground)", height: '24px', maxHeight: '200px', overflowY: 'auto' }}
                                disabled={isLoading || !isConnected}
                                rows={1}
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
                                    className="p-2 rounded-lg hover:bg-[var(--background-secondary)] transition-colors"
                                    title="Sesli giriş"
                                >
                                    <Mic size={20} style={{ color: "var(--foreground-muted)" }} />
                                </button>
                                <button
                                    type="submit"
                                    disabled={(!input.trim() && !attachedFile && !attachedVideoUrl) || isLoading || !isConnected}
                                    className="p-2 rounded-full transition-all duration-200 disabled:opacity-40"
                                    style={{
                                        background: (input.trim() || attachedFile || attachedVideoUrl) && isConnected ? "var(--accent)" : "var(--foreground-muted)",
                                        color: "var(--background)"
                                    }}
                                >
                                    <Send size={16} />
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>

            {/* Lightbox Modal */}
            {lightboxImage && (
                <div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4"
                    style={{ background: "rgba(0, 0, 0, 0.85)", backdropFilter: "blur(8px)" }}
                    onClick={() => setLightboxImage(null)}
                    onKeyDown={(e) => e.key === 'Escape' && setLightboxImage(null)}
                    tabIndex={0}
                    ref={(el) => el?.focus()}
                >
                    {/* Close Button */}
                    <button
                        onClick={() => setLightboxImage(null)}
                        className="absolute top-4 right-4 p-2 rounded-full transition-colors hover:bg-white/20"
                        style={{ background: "rgba(255,255,255,0.1)" }}
                    >
                        <X size={24} className="text-white" />
                    </button>

                    {/* Open in New Tab */}
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            window.open(lightboxImage!, '_blank');
                        }}
                        className="absolute top-4 right-16 p-2 rounded-full transition-colors hover:bg-white/20"
                        style={{ background: "rgba(255,255,255,0.1)" }}
                        title="Yeni sekmede aç"
                    >
                        <ZoomIn size={24} className="text-white" />
                    </button>

                    {/* Image */}
                    <img
                        src={lightboxImage!}
                        alt="Büyütülmüş görsel"
                        className="max-w-[90vw] max-h-[90vh] object-contain rounded-xl shadow-2xl"
                        onClick={(e) => e.stopPropagation()}
                        style={{ animation: "fadeIn 0.2s ease-out" }}
                    />
                </div>
            )}
        </div>
    );
}
