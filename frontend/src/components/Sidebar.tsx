"use client";

import {
    MessageSquare,
    Image as ImageIcon,
    Users,
    Settings,
    Sun,
    Moon,
    Menu,
    X
} from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { useState } from "react";

interface NavItem {
    icon: React.ReactNode;
    label: string;
    href: string;
    active?: boolean;
}

const navItems: NavItem[] = [
    { icon: <MessageSquare size={22} />, label: "Chat", href: "/", active: true },
    { icon: <ImageIcon size={22} />, label: "Assets", href: "/assets" },
    { icon: <Users size={22} />, label: "Karakterler", href: "/characters" },
    { icon: <Settings size={22} />, label: "Ayarlar", href: "/settings" },
];

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
                    className="lg:hidden fixed inset-0 bg-black/50 z-40"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* Sidebar */}
            <aside
                className={`
          fixed lg:relative
          h-screen w-[70px] lg:w-[70px]
          flex flex-col items-center
          py-4 gap-2
          z-50
          transition-transform duration-300
          ${mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
        `}
                style={{ background: "var(--sidebar)" }}
            >
                {/* Close button (mobile) */}
                <button
                    onClick={() => setMobileOpen(false)}
                    className="lg:hidden absolute top-4 right-4"
                >
                    <X size={20} />
                </button>

                {/* Logo */}
                <div className="w-10 h-10 mb-6 flex items-center justify-center text-2xl">
                    🫑
                </div>

                {/* Navigation */}
                <nav className="flex-1 flex flex-col gap-2">
                    {navItems.map((item) => (
                        <a
                            key={item.href}
                            href={item.href}
                            className={`
                w-12 h-12 rounded-xl flex items-center justify-center
                transition-all duration-200
                hover:scale-105
                ${item.active
                                    ? "bg-[var(--accent)] text-[var(--background)]"
                                    : "hover:bg-[var(--card)]"
                                }
              `}
                            title={item.label}
                        >
                            {item.icon}
                        </a>
                    ))}
                </nav>

                {/* Theme toggle */}
                <button
                    onClick={toggleTheme}
                    className="w-12 h-12 rounded-xl flex items-center justify-center hover:bg-[var(--card)] transition-all duration-200"
                    title={theme === "dark" ? "Aydınlık mod" : "Karanlık mod"}
                >
                    {theme === "dark" ? <Sun size={22} /> : <Moon size={22} />}
                </button>

                {/* User avatar */}
                <div
                    className="w-10 h-10 rounded-full flex items-center justify-center mt-4 text-sm font-semibold"
                    style={{ background: "var(--accent)", color: "var(--background)" }}
                >
                    E
                </div>
            </aside>
        </>
    );
}
