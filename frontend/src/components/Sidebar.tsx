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
    Puzzle
} from "lucide-react";
import { useTheme } from "./ThemeProvider";

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
}

function CollapsibleSection({ title, icon, items, defaultOpen = false }: CollapsibleSectionProps) {
    const [open, setOpen] = useState(defaultOpen);

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
                            className="flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg hover:bg-[var(--card)] cursor-pointer transition-colors"
                            style={{ color: "var(--foreground-muted)" }}
                        >
                            <span className="w-1.5 h-1.5 rounded-full" style={{ background: "var(--accent)" }} />
                            <span className="truncate">{item.name}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export function Sidebar() {
    const { theme, toggleTheme } = useTheme();
    const [mobileOpen, setMobileOpen] = useState(false);

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

                    {mockProjects.map((project) => (
                        <div
                            key={project.id}
                            className={`px-3 py-2 text-sm rounded-lg cursor-pointer transition-colors ${project.active ? "bg-[var(--card)]" : "hover:bg-[var(--card)]"
                                }`}
                        >
                            {project.name}
                        </div>
                    ))}

                    <button
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
                        items={mockCharacters}
                        defaultOpen={true}
                    />

                    {/* Locations */}
                    <CollapsibleSection
                        title="Locations"
                        icon={<MapPin size={16} />}
                        items={mockLocations}
                        defaultOpen={true}
                    />

                    {/* Wardrobe */}
                    <CollapsibleSection
                        title="Wardrobe"
                        icon={<Shirt size={16} />}
                        items={mockWardrobe}
                        defaultOpen={false}
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
                    <button className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-1">
                        <Search size={16} style={{ color: "var(--foreground-muted)" }} />
                        <span style={{ color: "var(--foreground-muted)" }}>Search</span>
                    </button>



                    {/* Settings */}
                    <button className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-1">
                        <Settings size={16} style={{ color: "var(--foreground-muted)" }} />
                        <span style={{ color: "var(--foreground-muted)" }}>Settings</span>
                    </button>

                    {/* Admin Panel */}
                    <button className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-[var(--card)] mb-2">
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
        </>
    );
}
