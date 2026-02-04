"use client";

import { useState, useEffect, useRef } from "react";
import {
    getEntities, deleteEntity, Entity, createSession, getSessions, deleteSession, updateSession,
    getCreativePlugins, createCreativePlugin, deleteCreativePlugin, CreativePluginData,
    getTrashItems, restoreTrashItem, permanentDeleteTrashItem, TrashItemData
} from "@/lib/api";
import {
    ChevronDown,
    ChevronRight,
    FolderOpen,
    Brain,
    Users,
    MapPin,
    Shirt,
    Search,
    Plus,
    Sun,
    Moon,
    Menu,
    X,
    Settings,
    Shield,
    User,
    Puzzle,
    Trash2,
    Store,
    Pencil,
    Grid3x3,
    LogOut
} from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { useAuth } from "@/contexts/AuthContext";
import { SettingsModal } from "./SettingsModal";
import { SearchModal } from "./SearchModal";
import { NewProjectModal } from "./NewProjectModal";
import { AdminPanelModal } from "./AdminPanelModal";
import { ConfirmDeleteModal } from "./ConfirmDeleteModal";
import { TrashModal, TrashItem } from "./TrashModal";
import { SavePluginModal, PluginDetailModal, CreativePlugin } from "./CreativePluginModal";
import { useToast } from "./ToastProvider";
import { PluginMarketplaceModal } from "./PluginMarketplaceModal";
import { GridGeneratorModal } from "./GridGeneratorModal";
import { useKeyboardShortcuts, SHORTCUTS } from "@/hooks/useKeyboardShortcuts";

interface SidebarItem {
    id: string;
    name: string;
    type: "project" | "character" | "location" | "wardrobe";
}

// Mock data
const mockProjects = [
    { id: "1", name: "Samsung Ad Campaign", active: false },
    { id: "2", name: "Modern Kitchen Promo", active: true },
];

const mockCharacters = [
    { id: "c1", name: "@character_emre" },
    { id: "c2", name: "@character_ahmet" },
    { id: "c3", name: "@character_ayse" },
];

const mockLocations = [
    { id: "l1", name: "@location_kitchen" },
    { id: "l2", name: "@location_office" },
];

const mockWardrobe = [
    { id: "w1", name: "@costume_black_jacket" },
    { id: "w2", name: "@costume_chef_outfit" },
    { id: "w3", name: "@object_modern_tv" },
    { id: "w4", name: "@object_smartphone" },
];

const mockCreativePlugins: CreativePlugin[] = [
    {
        id: "p1",
        name: "Mutfak Reklamı Seti",
        description: "Modern mutfak arka planı ile profesyonel görsel üretimi",
        author: "Ben",
        isPublic: false,
        config: {
            character: { id: "variable", name: "Değişken", isVariable: true },
            location: { id: "mutfak", name: "Modern Mutfak", settings: "" },
            timeOfDay: "Gün Batımı",
            cameraAngles: ["Orta Plan (Medium Shot)", "Yakın Çekim (Close-up)"],
            style: "Sıcak Tonlar"
        },
        createdAt: new Date(),
        downloads: 0,
        rating: 0
    },
    {
        id: "p2",
        name: "Outdoor Fashion",
        description: "Dış mekan moda çekimi için hazır şablon",
        author: "Ben",
        isPublic: true,
        config: {
            character: { id: "variable", name: "Değişken", isVariable: true },
            location: { id: "outdoor", name: "Outdoor - Park", settings: "" },
            timeOfDay: "Sabah",
            cameraAngles: ["Geniş Açı (Wide Shot)", "Orta Plan (Medium Shot)"],
            style: "Editorial"
        },
        createdAt: new Date(),
        downloads: 45,
        rating: 4.5
    },
];

interface CollapsibleSectionProps {
    title: string;
    icon: React.ReactNode;
    items: { id: string; name: string }[];
    defaultOpen?: boolean;
    onDelete?: (id: string) => void;
}

function CollapsibleSection({ title, icon, items, defaultOpen = false, onDelete }: CollapsibleSectionProps) {
    const [open, setOpen] = useState(defaultOpen);
    const [hoveredId, setHoveredId] = useState<string | null>(null);

    const handleDragStart = (e: React.DragEvent, item: { id: string; name: string }) => {
        e.dataTransfer.setData('text/plain', item.name);
        e.dataTransfer.setData('application/x-entity-tag', item.name);
        e.dataTransfer.effectAllowed = 'copy';
    };

    return (
        <div className="mb-1">
            <button
                onClick={() => setOpen(!open)}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--card)] rounded-lg transition-colors"
            >
                {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                {icon}
                <span className="font-medium">{title}</span>
            </button>

            {open && (
                <div className="ml-4 mt-1 space-y-0.5">
                    {items.map((item) => (
                        <div
                            key={item.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, item)}
                            className="flex items-center justify-between group px-3 py-1.5 text-sm rounded-lg hover:bg-[var(--card)] cursor-grab active:cursor-grabbing transition-colors"
                            style={{ color: "var(--foreground-muted)" }}
                            onMouseEnter={() => setHoveredId(item.id)}
                            onMouseLeave={() => setHoveredId(null)}
                        >
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: "var(--accent)" }} />
                                <span className="truncate">{item.name}</span>
                            </div>
                            {onDelete && hoveredId === item.id && (
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onDelete(item.id);
                                    }}
                                    className="p-1 rounded hover:bg-red-500/20 transition-colors"
                                    title="Sil"
                                >
                                    <Trash2 size={14} className="text-red-400" />
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

interface SidebarProps {
    activeProjectId?: string;
    onProjectChange?: (projectId: string) => void;
    onProjectDelete?: () => void;  // Proje silindiğinde çağrılır
    sessionId?: string | null;
    refreshKey?: number;
    onSendPrompt?: (prompt: string) => void;
}

export function Sidebar({ activeProjectId, onProjectChange, onProjectDelete, sessionId, refreshKey, onSendPrompt }: SidebarProps) {
    const { theme, toggleTheme } = useTheme();
    const { user, logout } = useAuth();
    const toast = useToast();
    const [mobileOpen, setMobileOpen] = useState(false);
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [searchOpen, setSearchOpen] = useState(false);
    const [newProjectOpen, setNewProjectOpen] = useState(false);
    const [adminOpen, setAdminOpen] = useState(false);
    const [trashOpen, setTrashOpen] = useState(false);
    const [gridGeneratorOpen, setGridGeneratorOpen] = useState(false);
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const [projects, setProjects] = useState<{ id: string; name: string; active: boolean }[]>([]);
    const [isLoadingEntities, setIsLoadingEntities] = useState(false);
    const [isLoadingProjects, setIsLoadingProjects] = useState(false);
    const [entitySearchQuery, setEntitySearchQuery] = useState("");

    // Keyboard shortcuts
    useKeyboardShortcuts({
        shortcuts: [
            { ...SHORTCUTS.SEARCH, action: () => setSearchOpen(true) },
            { ...SHORTCUTS.NEW_PROJECT, action: () => setNewProjectOpen(true) },
            { ...SHORTCUTS.SETTINGS, action: () => setSettingsOpen(true) },
            { ...SHORTCUTS.GRID, action: () => setGridGeneratorOpen(true) },
            { ...SHORTCUTS.ADMIN, action: () => setAdminOpen(true) },
            {
                ...SHORTCUTS.ESCAPE,
                action: () => {
                    // Close any open modal
                    if (searchOpen) setSearchOpen(false);
                    else if (settingsOpen) setSettingsOpen(false);
                    else if (newProjectOpen) setNewProjectOpen(false);
                    else if (adminOpen) setAdminOpen(false);
                    else if (trashOpen) setTrashOpen(false);
                    else if (gridGeneratorOpen) setGridGeneratorOpen(false);
                    else if (userMenuOpen) setUserMenuOpen(false);
                }
            },
        ],
    });

    // Proje ismi düzenleme state'leri
    const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
    const [editingProjectName, setEditingProjectName] = useState("");
    const editInputRef = useRef<HTMLInputElement>(null);

    // Proje ismi düzenleme fonksiyonları
    const startEditingProject = (projectId: string, currentName: string) => {
        setEditingProjectId(projectId);
        setEditingProjectName(currentName);
        setTimeout(() => editInputRef.current?.focus(), 0);
    };

    const cancelEditingProject = () => {
        setEditingProjectId(null);
        setEditingProjectName("");
    };

    const saveProjectName = async (projectId: string) => {
        const trimmedName = editingProjectName.trim();
        if (trimmedName && trimmedName !== projects.find(p => p.id === projectId)?.name) {
            try {
                await updateSession(projectId, trimmedName);
                setProjects(projects.map(p =>
                    p.id === projectId ? { ...p, name: trimmedName } : p
                ));
            } catch (error) {
                console.error('Proje adı güncellenemedi:', error);
            }
        }
        cancelEditingProject();
    };

    // Entity states - API'den gelecek
    const [characters, setCharacters] = useState<{ id: string; name: string }[]>([]);
    const [locations, setLocations] = useState<{ id: string; name: string }[]>([]);
    const [wardrobe, setWardrobe] = useState<{ id: string; name: string }[]>([]);
    const [creativePlugins, setCreativePlugins] = useState<CreativePlugin[]>([]);

    // Filtrelenmiş entity'ler (arama için)
    const filteredCharacters = characters.filter(c =>
        c.name.toLowerCase().includes(entitySearchQuery.toLowerCase())
    );
    const filteredLocations = locations.filter(l =>
        l.name.toLowerCase().includes(entitySearchQuery.toLowerCase())
    );
    const filteredWardrobe = wardrobe.filter(w =>
        w.name.toLowerCase().includes(entitySearchQuery.toLowerCase())
    );

    // Backend'den projeleri yükle
    useEffect(() => {
        const fetchProjects = async () => {
            setIsLoadingProjects(true);
            try {
                const sessions = await getSessions();
                const projectList = sessions.map(s => ({
                    id: s.id,
                    name: s.title,
                    active: sessionId === s.id
                }));
                setProjects(projectList);
            } catch (error) {
                console.error('Proje yükleme hatası:', error);
                setProjects([]);
            } finally {
                setIsLoadingProjects(false);
            }
        };

        fetchProjects();
    }, [sessionId, refreshKey]);

    // Backend'den creative plugins'i yükle
    useEffect(() => {
        const fetchCreativePlugins = async () => {
            if (!sessionId) return;
            try {
                const plugins = await getCreativePlugins(sessionId);
                const pluginList: CreativePlugin[] = plugins.map((p: CreativePluginData) => ({
                    id: p.id,
                    name: p.name,
                    description: p.description || '',
                    author: 'Ben',
                    isPublic: p.is_public,
                    config: {},
                    createdAt: new Date(),
                    downloads: p.usage_count,
                    rating: 0
                }));
                setCreativePlugins(pluginList);
            } catch (error) {
                console.error('Creative plugins yükleme hatası:', error);
                setCreativePlugins([]);
            }
        };

        fetchCreativePlugins();
    }, [sessionId, refreshKey]);

    // API'den entity'leri çek
    useEffect(() => {
        const fetchEntities = async () => {
            if (!sessionId) return;

            setIsLoadingEntities(true);
            try {
                const entities = await getEntities(sessionId);

                // Entity'leri türlerine göre ayır
                const chars = entities
                    .filter((e: Entity) => e.entity_type === 'character')
                    .map((e: Entity) => ({ id: e.id, name: e.tag || e.name }));
                const locs = entities
                    .filter((e: Entity) => e.entity_type === 'location')
                    .map((e: Entity) => ({ id: e.id, name: e.tag || e.name }));
                const ward = entities
                    .filter((e: Entity) => e.entity_type === 'wardrobe')
                    .map((e: Entity) => ({ id: e.id, name: e.tag || e.name }));

                setCharacters(chars);
                setLocations(locs);
                setWardrobe(ward);
            } catch (error) {
                console.error('Entity yükleme hatası:', error);
                // Hata durumunda boş göster
                setCharacters([]);
                setLocations([]);
                setWardrobe([]);
            } finally {
                setIsLoadingEntities(false);
            }
        };

        fetchEntities();
    }, [sessionId, refreshKey]);
    const [selectedPlugin, setSelectedPlugin] = useState<CreativePlugin | null>(null);
    const [pluginDetailOpen, setPluginDetailOpen] = useState(false);
    const [marketplaceOpen, setMarketplaceOpen] = useState(false);

    // Trash state - backend'den yükle
    const [trashItems, setTrashItems] = useState<TrashItem[]>([]);

    // Backend'den trash items'ları yükle
    useEffect(() => {
        const fetchTrashItems = async () => {
            try {
                const items = await getTrashItems();
                const trashList: TrashItem[] = items.map((i: TrashItemData) => ({
                    id: i.id,
                    name: i.item_name,
                    type: i.item_type as TrashItem["type"],
                    deletedAt: new Date(i.deleted_at),
                    originalData: {}
                }));
                setTrashItems(trashList);
            } catch (error) {
                console.error('Trash yükleme hatası:', error);
                setTrashItems([]);
            }
        };

        fetchTrashItems();
    }, [refreshKey]);


    // Delete confirmation state
    const [deleteConfirm, setDeleteConfirm] = useState<{
        isOpen: boolean;
        itemId: string;
        itemName: string;
        itemType: TrashItem["type"];
        onConfirm: () => void;
    } | null>(null);

    // Update projects when activeProjectId changes from parent
    const handleProjectClick = (projectId: string) => {
        setProjects(projects.map(p => ({
            ...p,
            active: p.id === projectId
        })));
        onProjectChange?.(projectId);
    };

    // Move to trash instead of deleting
    const moveToTrash = (id: string, name: string, type: TrashItem["type"], originalData: any) => {
        setTrashItems([...trashItems, {
            id,
            name,
            type,
            deletedAt: new Date(),
            originalData
        }]);
    };

    // Confirm delete handlers - API'ye bağlı
    const confirmDeleteCharacter = (id: string) => {
        const char = characters.find(c => c.id === id);
        if (!char) return;
        setDeleteConfirm({
            isOpen: true,
            itemId: id,
            itemName: char.name,
            itemType: "karakter",
            onConfirm: async () => {
                // Backend'den sil
                const success = await deleteEntity(id);
                if (success) {
                    moveToTrash(id, char.name, "karakter", char);
                    setCharacters(characters.filter(c => c.id !== id));
                    toast.success(`"${char.name}" çöp kutusuna taşındı`);
                } else {
                    toast.error('Karakter silinemedi');
                }
            }
        });
    };

    const confirmDeleteLocation = (id: string) => {
        const loc = locations.find(l => l.id === id);
        if (!loc) return;
        setDeleteConfirm({
            isOpen: true,
            itemId: id,
            itemName: loc.name,
            itemType: "lokasyon",
            onConfirm: async () => {
                const success = await deleteEntity(id);
                if (success) {
                    moveToTrash(id, loc.name, "lokasyon", loc);
                    setLocations(locations.filter(l => l.id !== id));
                    toast.success(`"${loc.name}" çöp kutusuna taşındı`);
                } else {
                    toast.error('Lokasyon silinemedi');
                }
            }
        });
    };

    const confirmDeleteWardrobe = (id: string) => {
        const item = wardrobe.find(w => w.id === id);
        if (!item) return;
        setDeleteConfirm({
            isOpen: true,
            itemId: id,
            itemName: item.name,
            itemType: "wardrobe",
            onConfirm: async () => {
                const success = await deleteEntity(id);
                if (success) {
                    moveToTrash(id, item.name, "wardrobe", item);
                    setWardrobe(wardrobe.filter(w => w.id !== id));
                    toast.success(`"${item.name}" çöp kutusuna taşındı`);
                } else {
                    toast.error('Kıyamet silinemedi');
                }
            }
        });
    };

    const confirmDeleteProject = (id: string) => {
        const proj = projects.find(p => p.id === id);
        if (!proj) return;
        setDeleteConfirm({
            isOpen: true,
            itemId: id,
            itemName: proj.name,
            itemType: "proje",
            onConfirm: async () => {
                try {
                    // Backend'den session'ı sil
                    await deleteSession(id);
                    moveToTrash(id, proj.name, "proje", proj);
                    const remainingProjects = projects.filter(p => p.id !== id);
                    setProjects(remainingProjects);
                    toast.success(`"${proj.name}" çöp kutusuna taşındı`);

                    // Eğer aktif proje silindiyse, ana sayfayı bilgilendir
                    if (proj.active || remainingProjects.length === 0) {
                        onProjectDelete?.();
                    }
                } catch (error) {
                    console.error('Proje silinemedi:', error);
                    toast.error('Proje silinemedi');
                }
            }
        });
    };

    // Restore from trash - backend'e bağlı
    const handleRestore = async (item: TrashItem) => {
        try {
            console.log("=== RESTORE DEBUG ===");
            console.log("TrashItem:", item);
            console.log("item.type:", item.type);
            console.log("Current projects:", projects);

            const result = await restoreTrashItem(item.id);
            console.log("API Result:", result);

            if (result.success && result.restored) {
                const restored = result.restored;
                console.log("Restored object:", restored);

                // UI güncelle - backend'den dönen verilerle
                switch (item.type) {
                    case "karakter":
                    case "character":  // Backend alias
                        console.log("Adding to characters");
                        setCharacters([...characters, {
                            id: restored.id,
                            name: restored.name || item.name
                        }]);
                        break;
                    case "lokasyon":
                    case "location":  // Backend alias
                        console.log("Adding to locations");
                        setLocations([...locations, {
                            id: restored.id,
                            name: restored.name || item.name
                        }]);
                        break;
                    case "wardrobe":
                        console.log("Adding to wardrobe");
                        setWardrobe([...wardrobe, {
                            id: restored.id,
                            name: restored.name || item.name
                        }]);
                        break;
                    case "proje":
                    case "session":  // Backend "session" tip döndürüyor
                        console.log("Adding to projects:", { id: restored.id, name: restored.title || item.name });
                        const newProject = {
                            id: restored.id,
                            name: restored.title || item.name,
                            active: false
                        };
                        setProjects(prevProjects => [...prevProjects, newProject]);
                        break;
                    case "plugin":
                        console.log("Plugin restore - not implemented");
                        break;
                    case "marka":
                    case "brand":  // Backend alias
                        console.log("Adding brand to characters");
                        setCharacters([...characters, {
                            id: restored.id,
                            name: restored.name || item.name
                        }]);
                        break;
                    default:
                        console.log("Unknown type:", item.type);
                }
            } else {
                console.log("result.success:", result.success);
                console.log("result.restored:", result.restored);
            }

            // Çöp kutusundan kaldır
            setTrashItems(trashItems.filter(t => t.id !== item.id));
            toast.success(`"${item.name}" başarıyla geri yüklendi`);
        } catch (error) {
            console.error('Geri yükleme hatası:', error);
            toast.error('Geri yükleme başarısız oldu');
        }
    };

    // Permanent delete - backend'e bağlı
    const handlePermanentDelete = async (id: string) => {
        try {
            await permanentDeleteTrashItem(id);
            setTrashItems(trashItems.filter(t => t.id !== id));
            toast.success('Kalıcı olarak silindi');
        } catch (error) {
            console.error('Kalıcı silme hatası:', error);
            toast.error('Kalıcı silme başarısız oldu');
        }
    };

    // Delete all trash items
    const handleDeleteAll = async () => {
        try {
            for (const item of trashItems) {
                await permanentDeleteTrashItem(item.id);
            }
            setTrashItems([]);
        } catch (error) {
            console.error('Tümünü silme hatası:', error);
        }
    };

    // Delete multiple selected items
    const handleDeleteMultiple = async (ids: string[]) => {
        try {
            for (const id of ids) {
                await permanentDeleteTrashItem(id);
            }
            setTrashItems(trashItems.filter(t => !ids.includes(t.id)));
        } catch (error) {
            console.error('Çoklu silme hatası:', error);
        }
    };

    return (
        <>
            {/* Mobile hamburger button */}
            <button
                onClick={() => setMobileOpen(true)}
                className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg"
                style={{ background: "var(--card)" }}
            >
                <Menu size={24} />
            </button>

            {/* Mobile overlay */}
            {mobileOpen && (
                <div
                    className="lg:hidden fixed inset-0 bg-black/60 z-40"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`
          fixed lg:relative
          h-screen w-[240px]
          flex flex-col
          z-50
          transition-transform duration-300
          ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
          border-r
        `}
                style={{
                    background: "var(--sidebar)",
                    borderColor: "var(--border)"
                }}
            >
                {/* Close button (mobile) */}
                <button
                    onClick={() => setMobileOpen(false)}
                    className="lg:hidden absolute top-4 right-4"
                >
                    <X size={20} />
                </button>

                {/* Logo */}
                <div className="px-4 py-5 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="text-center">
                        <div className="text-lg font-semibold tracking-tight">Pepper Root.</div>
                        <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                            AI Agency
                        </div>
                    </div>
                </div>

                {/* Projects Section */}
                <div className="px-2 py-3 border-b" style={{ borderColor: "var(--border)" }}>
                    <div className="flex items-center justify-between px-2 mb-2">
                        <div className="flex items-center gap-2 text-xs font-semibold uppercase" style={{ color: "var(--foreground-muted)" }}>
                            <FolderOpen size={14} />
                            Projects
                        </div>
                        <button
                            onClick={() => setNewProjectOpen(true)}
                            className="p-1 rounded hover:bg-[var(--card)]"
                        >
                            <Plus size={14} style={{ color: "var(--foreground-muted)" }} />
                        </button>
                    </div>

                    <div className="max-h-40 overflow-y-auto">
                        {projects.map((project) => {
                            const isEditing = editingProjectId === project.id;
                            return (
                                <div
                                    key={project.id}
                                    onClick={() => !isEditing && handleProjectClick(project.id)}
                                    onDoubleClick={(e) => {
                                        e.stopPropagation();
                                        startEditingProject(project.id, project.name);
                                    }}
                                    className={`group flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-all duration-200 ${project.active
                                        ? "bg-[var(--accent)] text-[var(--background)] font-medium"
                                        : "hover:bg-[var(--card)]"
                                        } ${isEditing ? "" : "cursor-pointer"}`}
                                >
                                    {isEditing ? (
                                        <input
                                            ref={editInputRef}
                                            type="text"
                                            value={editingProjectName}
                                            onChange={(e) => setEditingProjectName(e.target.value)}
                                            onBlur={() => saveProjectName(project.id)}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') saveProjectName(project.id);
                                                if (e.key === 'Escape') cancelEditingProject();
                                            }}
                                            onClick={(e) => e.stopPropagation()}
                                            className="flex-1 bg-transparent border-b outline-none text-sm"
                                            style={{
                                                borderColor: project.active ? "var(--background)" : "var(--accent)",
                                                color: "inherit"
                                            }}
                                            autoFocus
                                        />
                                    ) : (
                                        <span className="truncate flex-1">{project.name}</span>
                                    )}

                                    <div className="flex items-center gap-1">
                                        {/* Edit Button */}
                                        {!isEditing && (
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    startEditingProject(project.id, project.name);
                                                }}
                                                className={`p-1 rounded transition-all ${project.active
                                                    ? "opacity-50 hover:opacity-100 hover:bg-white/20"
                                                    : "opacity-0 group-hover:opacity-100 hover:bg-[var(--accent)]/20"
                                                    }`}
                                                title="Yeniden Adlandır"
                                            >
                                                <Pencil size={12} className={project.active ? "" : "text-[var(--accent)]"} />
                                            </button>
                                        )}

                                        {/* Delete Button */}
                                        {!isEditing && (
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    confirmDeleteProject(project.id);
                                                }}
                                                className={`p-1 rounded transition-all ${project.active
                                                    ? "opacity-50 hover:opacity-100 hover:bg-red-500/30"
                                                    : "opacity-0 group-hover:opacity-100 hover:bg-red-500/20"
                                                    }`}
                                                title="Sil"
                                            >
                                                <Trash2 size={14} className={project.active ? "text-red-200" : "text-red-400"} />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <button
                        onClick={() => setNewProjectOpen(true)}
                        className="w-full px-3 py-2 text-sm text-left rounded-lg hover:bg-[var(--card)] transition-colors mt-1"
                        style={{ color: "var(--foreground-muted)" }}
                    >
                        + New Project
                    </button>
                </div>

                {/* Scrollable content */}
                <div className="flex-1 overflow-y-auto px-2 py-2">
                    {/* Entity Arama */}
                    <div className="mb-3 px-1">
                        <div className="relative">
                            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--foreground-muted)]" />
                            <input
                                type="text"
                                placeholder="Entity ara..."
                                value={entitySearchQuery}
                                onChange={(e) => setEntitySearchQuery(e.target.value)}
                                className="w-full pl-8 pr-3 py-1.5 text-xs rounded-lg bg-[var(--card)] border border-[var(--border)] focus:outline-none focus:ring-1 focus:ring-[var(--accent)] transition-all"
                                style={{ color: "var(--foreground)" }}
                            />
                            {entitySearchQuery && (
                                <button
                                    onClick={() => setEntitySearchQuery("")}
                                    className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--foreground-muted)] hover:text-[var(--foreground)]"
                                >
                                    <X size={12} />
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Characters */}
                    <CollapsibleSection
                        title="Characters"
                        icon={<Users size={16} />}
                        items={filteredCharacters}
                        defaultOpen={true}
                        onDelete={confirmDeleteCharacter}
                    />

                    {/* Locations */}
                    <CollapsibleSection
                        title="Locations"
                        icon={<MapPin size={16} />}
                        items={filteredLocations}
                        defaultOpen={true}
                        onDelete={confirmDeleteLocation}
                    />

                    {/* Wardrobe */}
                    <CollapsibleSection
                        title="Wardrobe"
                        icon={<Shirt size={16} />}
                        items={filteredWardrobe}
                        defaultOpen={false}
                        onDelete={confirmDeleteWardrobe}
                    />

                    {/* Creative Plugins Section - sadece plugin varsa göster */}
                    {creativePlugins.length > 0 && (
                        <div className="mt-2">
                            <div className="flex items-center justify-between px-2 py-1.5">
                                <div className="flex items-center gap-2 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                                    <Puzzle size={14} />
                                    <span>Creative Plugins</span>
                                    <span className="text-xs opacity-60">({creativePlugins.length})</span>
                                </div>
                            </div>
                            <div className="space-y-0.5">
                                {creativePlugins.map((plugin) => (
                                    <div
                                        key={plugin.id}
                                        onClick={() => { setSelectedPlugin(plugin); setPluginDetailOpen(true); }}
                                        className="flex items-center justify-between px-3 py-1.5 text-sm rounded-lg hover:bg-[var(--card)] cursor-pointer transition-colors group"
                                        style={{ color: "var(--foreground-muted)" }}
                                    >
                                        <div className="flex items-center gap-2 flex-1 min-w-0">
                                            <span className="w-1.5 h-1.5 rounded-full" style={{ background: plugin.isPublic ? "#8b5cf6" : "var(--accent)" }} />
                                            <span className="truncate">{plugin.name}</span>
                                        </div>
                                        {plugin.isPublic && (
                                            <span className="text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity" style={{ background: "rgba(139, 92, 246, 0.2)", color: "#8b5cf6" }}>
                                                Paylaşıldı
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Bottom section */}
                <div className="p-3 border-t" style={{ borderColor: "var(--border)" }}>
                    {/* Grid Generator - Feature */}
                    <button
                        onClick={() => setGridGeneratorOpen(true)}
                        className="w-full flex items-center gap-2 px-3 py-2.5 text-sm font-medium rounded-lg mb-2 transition-all hover:shadow-lg hover:shadow-emerald-500/20"
                        style={{
                            background: "linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.15) 100%)",
                            color: "#10b981",
                            border: "1px solid rgba(16, 185, 129, 0.3)"
                        }}
                    >
                        <Grid3x3 size={16} />
                        <span>Grid Generator</span>
                    </button>

                    {/* Marketplace - Prominent */}
                    <button
                        onClick={() => setMarketplaceOpen(true)}
                        className="w-full flex items-center gap-2 px-3 py-2.5 text-sm font-medium rounded-lg mb-2 transition-all hover:shadow-lg hover:shadow-purple-500/20"
                        style={{
                            background: "linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.15) 100%)",
                            color: "#a78bfa",
                            border: "1px solid rgba(139, 92, 246, 0.3)"
                        }}
                    >
                        <Store size={16} />
                        <span>Plugin Marketplace</span>
                    </button>

                    {/* Search */}
                    <button
                        onClick={() => setSearchOpen(true)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-1"
                    >
                        <Search size={16} style={{ color: "var(--foreground-muted)" }} />
                        <span style={{ color: "var(--foreground-muted)" }}>Search</span>
                    </button>


                    {/* Settings */}
                    <button
                        onClick={() => setSettingsOpen(true)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-1"
                    >
                        <Settings size={16} style={{ color: "var(--foreground-muted)" }} />
                        <span style={{ color: "var(--foreground-muted)" }}>Settings</span>
                    </button>

                    {/* Trash Bin */}
                    <button
                        onClick={() => setTrashOpen(true)}
                        className="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-1"
                    >
                        <div className="flex items-center gap-2">
                            <Trash2 size={16} style={{ color: "var(--foreground-muted)" }} />
                            <span style={{ color: "var(--foreground-muted)" }}>Çöp Kutusu</span>
                        </div>
                        {trashItems.length > 0 && (
                            <span
                                className="px-1.5 py-0.5 text-xs rounded-full"
                                style={{ background: "rgba(239, 68, 68, 0.2)", color: "#ef4444" }}
                            >
                                {trashItems.length}
                            </span>
                        )}
                    </button>

                    {/* Admin Panel */}
                    <button
                        onClick={() => setAdminOpen(true)}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-2"
                    >
                        <Shield size={16} style={{ color: "var(--foreground-muted)" }} />
                        <span style={{ color: "var(--foreground-muted)" }}>Admin Panel</span>
                    </button>

                    {/* User Profile - En altta */}
                    <div className="relative">
                        <div
                            onClick={() => setUserMenuOpen(!userMenuOpen)}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[var(--card)] cursor-pointer border-t pt-3 mt-2"
                            style={{ borderColor: "var(--border)" }}
                        >
                            <div
                                className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold overflow-hidden"
                                style={{ background: "var(--accent)", color: "var(--background)" }}
                            >
                                {user?.avatar_url ? (
                                    <img src={user.avatar_url} alt={user.full_name || "User"} className="w-full h-full object-cover" />
                                ) : (
                                    <span>{(user?.full_name || user?.email || "U")[0].toUpperCase()}</span>
                                )}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="text-sm font-medium truncate">{user?.full_name || "User"}</div>
                                <div className="text-xs truncate" style={{ color: "var(--foreground-muted)" }}>
                                    {user?.email || "Free Plan"}
                                </div>
                            </div>
                            <ChevronDown
                                size={14}
                                className={`transition-transform ${userMenuOpen ? "rotate-180" : ""}`}
                                style={{ color: "var(--foreground-muted)" }}
                            />
                        </div>

                        {/* User Dropdown Menu */}
                        {userMenuOpen && (
                            <div
                                className="absolute bottom-full left-0 right-0 mb-1 rounded-lg shadow-lg border overflow-hidden"
                                style={{ background: "var(--card)", borderColor: "var(--border)" }}
                            >
                                <div className="p-3 border-b" style={{ borderColor: "var(--border)" }}>
                                    <div className="text-sm font-medium">{user?.full_name || "User"}</div>
                                    <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>
                                        {user?.email}
                                    </div>
                                </div>
                                <button
                                    onClick={() => {
                                        setUserMenuOpen(false);
                                        logout();
                                    }}
                                    className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-red-500/10 transition-colors text-red-400"
                                >
                                    <LogOut size={16} />
                                    Çıkış Yap
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </aside>

            {/* Settings Modal */}
            <SettingsModal
                isOpen={settingsOpen}
                onClose={() => setSettingsOpen(false)}
            />

            {/* Search Modal */}
            <SearchModal
                isOpen={searchOpen}
                onClose={() => setSearchOpen(false)}
                sessionId={sessionId}
            />

            {/* New Project Modal */}
            <NewProjectModal
                isOpen={newProjectOpen}
                onClose={() => setNewProjectOpen(false)}
                onSubmit={async (name) => {
                    try {
                        // Backend'de yeni session oluştur
                        const newSession = await createSession(name);
                        setProjects([...projects, { id: newSession.id, name, active: false }]);
                    } catch (error) {
                        console.error('Proje oluşturulamadı:', error);
                        // Fallback olarak local ekle
                        setProjects([...projects, { id: Date.now().toString(), name, active: false }]);
                    }
                }}
            />

            {/* Admin Panel Modal */}
            <AdminPanelModal
                isOpen={adminOpen}
                onClose={() => setAdminOpen(false)}
            />

            {/* Confirm Delete Modal */}
            <ConfirmDeleteModal
                isOpen={deleteConfirm?.isOpen ?? false}
                onClose={() => setDeleteConfirm(null)}
                onConfirm={() => deleteConfirm?.onConfirm()}
                itemName={deleteConfirm?.itemName ?? ""}
                itemType={deleteConfirm?.itemType ?? "öğe"}
            />


            {/* Trash Modal */}
            <TrashModal
                isOpen={trashOpen}
                onClose={() => setTrashOpen(false)}
                items={trashItems}
                onRestore={handleRestore}
                onPermanentDelete={handlePermanentDelete}
                onDeleteAll={handleDeleteAll}
                onDeleteMultiple={handleDeleteMultiple}
            />

            {/* Plugin Detail Modal */}
            <PluginDetailModal
                isOpen={pluginDetailOpen}
                onClose={() => setPluginDetailOpen(false)}
                plugin={selectedPlugin}
                onDelete={(id) => setCreativePlugins(creativePlugins.filter(p => p.id !== id))}
                onUse={(plugin) => {
                    // Plugin config'ini chat'e gönder
                    if (onSendPrompt && plugin.config) {
                        const parts: string[] = [];

                        // Style varsa ekle
                        if (plugin.config.style) {
                            parts.push(`Stil: ${plugin.config.style}`);
                        }

                        // Camera angles varsa ekle
                        if (plugin.config.cameraAngles && plugin.config.cameraAngles.length > 0) {
                            parts.push(`Açılar: ${plugin.config.cameraAngles.join(", ")}`);
                        }

                        // Time of day varsa ekle
                        if (plugin.config.timeOfDay) {
                            parts.push(`Zaman: ${plugin.config.timeOfDay}`);
                        }

                        // PromptTemplate varsa kullan
                        const prompt = plugin.config.promptTemplate
                            ? `[${plugin.name}] ${plugin.config.promptTemplate}${parts.length > 0 ? ` (${parts.join(", ")})` : ""}`
                            : `[${plugin.name}] ${parts.join(", ")} tarzında görsel üret`;

                        onSendPrompt(prompt);
                    }
                    setPluginDetailOpen(false);
                }}
            />

            {/* Plugin Marketplace Modal */}
            <PluginMarketplaceModal
                isOpen={marketplaceOpen}
                onClose={() => setMarketplaceOpen(false)}
                onInstall={(plugin) => setCreativePlugins([...creativePlugins, plugin])}
                myPlugins={creativePlugins}
            />

            {/* Grid Generator Modal */}
            <GridGeneratorModal
                isOpen={gridGeneratorOpen}
                onClose={() => setGridGeneratorOpen(false)}
            />
        </>
    );
}
