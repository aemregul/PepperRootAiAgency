"use client";

import { useState } from "react";
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
    Trash2
} from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { SettingsModal } from "./SettingsModal";
import { SearchModal } from "./SearchModal";
import { NewProjectModal } from "./NewProjectModal";
import { AdminPanelModal } from "./AdminPanelModal";
import { ConfirmDeleteModal } from "./ConfirmDeleteModal";
import { TrashModal, TrashItem } from "./TrashModal";

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

const mockPlugins = [
    { id: "p1", name: "fal.ai (Görsel)" },
    { id: "p2", name: "Minimax (Video)" },
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
                            className="flex items-center justify-between group px-3 py-1.5 text-sm rounded-lg hover:bg-[var(--card)] cursor-pointer transition-colors"
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
}

export function Sidebar({ activeProjectId, onProjectChange }: SidebarProps) {
    const { theme, toggleTheme } = useTheme();
    const [mobileOpen, setMobileOpen] = useState(false);
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [searchOpen, setSearchOpen] = useState(false);
    const [newProjectOpen, setNewProjectOpen] = useState(false);
    const [adminOpen, setAdminOpen] = useState(false);
    const [trashOpen, setTrashOpen] = useState(false);
    const [projects, setProjects] = useState(mockProjects);

    // Entity states
    const [characters, setCharacters] = useState(mockCharacters);
    const [locations, setLocations] = useState(mockLocations);
    const [wardrobe, setWardrobe] = useState(mockWardrobe);
    const [plugins, setPlugins] = useState(mockPlugins);

    // Trash state
    const [trashItems, setTrashItems] = useState<TrashItem[]>([]);

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

    // Confirm delete handlers
    const confirmDeleteCharacter = (id: string) => {
        const char = characters.find(c => c.id === id);
        if (!char) return;
        setDeleteConfirm({
            isOpen: true,
            itemId: id,
            itemName: char.name,
            itemType: "karakter",
            onConfirm: () => {
                moveToTrash(id, char.name, "karakter", char);
                setCharacters(characters.filter(c => c.id !== id));
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
            onConfirm: () => {
                moveToTrash(id, loc.name, "lokasyon", loc);
                setLocations(locations.filter(l => l.id !== id));
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
            onConfirm: () => {
                moveToTrash(id, item.name, "wardrobe", item);
                setWardrobe(wardrobe.filter(w => w.id !== id));
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
            onConfirm: () => {
                moveToTrash(id, proj.name, "proje", proj);
                setProjects(projects.filter(p => p.id !== id));
            }
        });
    };

    // Restore from trash
    const handleRestore = (item: TrashItem) => {
        switch (item.type) {
            case "karakter":
                setCharacters([...characters, item.originalData]);
                break;
            case "lokasyon":
                setLocations([...locations, item.originalData]);
                break;
            case "wardrobe":
                setWardrobe([...wardrobe, item.originalData]);
                break;
            case "proje":
                setProjects([...projects, item.originalData]);
                break;
            case "plugin":
                setPlugins([...plugins, item.originalData]);
                break;
        }
        setTrashItems(trashItems.filter(t => t.id !== item.id));
    };

    // Permanent delete
    const handlePermanentDelete = (id: string) => {
        setTrashItems(trashItems.filter(t => t.id !== id));
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
                        <button className="p-1 rounded hover:bg-[var(--card)]">
                            <Plus size={14} style={{ color: "var(--foreground-muted)" }} />
                        </button>
                    </div>

                    {projects.map((project) => (
                        <div
                            key={project.id}
                            onClick={() => handleProjectClick(project.id)}
                            className={`group flex items-center justify-between px-3 py-2 text-sm rounded-lg cursor-pointer transition-all duration-200 ${project.active
                                ? "bg-[var(--accent)] text-[var(--background)] font-medium"
                                : "hover:bg-[var(--card)]"
                                }`}
                        >
                            <span className="truncate">{project.name}</span>
                            {!project.active && (
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        confirmDeleteProject(project.id);
                                    }}
                                    className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/20 transition-all"
                                    title="Sil"
                                >
                                    <Trash2 size={14} className="text-red-400" />
                                </button>
                            )}
                        </div>
                    ))}

                    <button
                        onClick={() => setNewProjectOpen(true)}
                        className="w-full px-3 py-2 text-sm text-left rounded-lg hover:bg-[var(--card)] transition-colors"
                        style={{ color: "var(--foreground-muted)" }}
                    >
                        + New Project
                    </button>
                </div>

                {/* Scrollable content */}
                <div className="flex-1 overflow-y-auto px-2 py-2">
                    {/* Characters */}
                    <CollapsibleSection
                        title="Characters"
                        icon={<Users size={16} />}
                        items={characters}
                        defaultOpen={true}
                        onDelete={confirmDeleteCharacter}
                    />

                    {/* Locations */}
                    <CollapsibleSection
                        title="Locations"
                        icon={<MapPin size={16} />}
                        items={locations}
                        defaultOpen={true}
                        onDelete={confirmDeleteLocation}
                    />

                    {/* Wardrobe */}
                    <CollapsibleSection
                        title="Wardrobe"
                        icon={<Shirt size={16} />}
                        items={wardrobe}
                        defaultOpen={false}
                        onDelete={confirmDeleteWardrobe}
                    />

                    {/* Plugins Section */}
                    <div className="mt-2">
                        <div className="flex items-center justify-between px-2 py-1.5">
                            <div className="flex items-center gap-2 text-xs font-medium" style={{ color: "var(--foreground-muted)" }}>
                                <Puzzle size={14} />
                                <span>Plugins</span>
                            </div>
                            <button
                                className="p-1 rounded hover:bg-[var(--card)] transition-colors"
                                title="Yeni Plugin Ekle"
                            >
                                <Plus size={12} style={{ color: "var(--accent)" }} />
                            </button>
                        </div>
                        <div className="space-y-0.5">
                            {mockPlugins.map((plugin) => (
                                <div
                                    key={plugin.id}
                                    className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg hover:bg-[var(--card)] cursor-pointer transition-colors"
                                    style={{ color: "var(--foreground-muted)" }}
                                >
                                    <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--accent)" }} />
                                    <span className="truncate">{plugin.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Bottom section */}
                <div className="p-3 border-t" style={{ borderColor: "var(--border)" }}>
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
                    <div
                        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[var(--card)] cursor-pointer border-t pt-3 mt-2"
                        style={{ borderColor: "var(--border)" }}
                    >
                        <div
                            className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold"
                            style={{ background: "var(--accent)", color: "var(--background)" }}
                        >
                            <User size={16} />
                        </div>
                        <div className="flex-1">
                            <div className="text-sm font-medium">User</div>
                            <div className="text-xs" style={{ color: "var(--foreground-muted)" }}>Free Plan</div>
                        </div>
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
            />

            {/* New Project Modal */}
            <NewProjectModal
                isOpen={newProjectOpen}
                onClose={() => setNewProjectOpen(false)}
                onSubmit={(name) => {
                    setProjects([...projects, { id: Date.now().toString(), name, active: false }]);
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
            />
        </>
    );
}
