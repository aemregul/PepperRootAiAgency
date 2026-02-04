"use client";

import { useEffect, useCallback } from 'react';

interface KeyboardShortcut {
    key: string;
    ctrlKey?: boolean;
    metaKey?: boolean;
    shiftKey?: boolean;
    action: () => void;
    description: string;
}

interface UseKeyboardShortcutsOptions {
    shortcuts: KeyboardShortcut[];
    enabled?: boolean;
}

export function useKeyboardShortcuts({ shortcuts, enabled = true }: UseKeyboardShortcutsOptions) {
    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        if (!enabled) return;

        // Ignore shortcuts when typing in input fields
        const target = event.target as HTMLElement;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
            // Allow Escape to work even in input fields
            if (event.key !== 'Escape') {
                return;
            }
        }

        for (const shortcut of shortcuts) {
            const ctrlOrMeta = shortcut.ctrlKey || shortcut.metaKey;
            const keyMatches = event.key.toLowerCase() === shortcut.key.toLowerCase();
            const modifierMatches = ctrlOrMeta
                ? (event.ctrlKey || event.metaKey)
                : (!event.ctrlKey && !event.metaKey);
            const shiftMatches = shortcut.shiftKey ? event.shiftKey : !event.shiftKey;

            if (keyMatches && modifierMatches && shiftMatches) {
                event.preventDefault();
                shortcut.action();
                return;
            }
        }
    }, [shortcuts, enabled]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);
}

// Predefined common shortcuts
export const SHORTCUTS = {
    SEARCH: { key: 'k', metaKey: true, description: 'Arama' },
    NEW_PROJECT: { key: 'n', metaKey: true, description: 'Yeni Proje' },
    SETTINGS: { key: ',', metaKey: true, description: 'Ayarlar' },
    ESCAPE: { key: 'Escape', description: 'Kapat' },
    GRID: { key: 'g', metaKey: true, description: 'Grid Generator' },
    ADMIN: { key: 'a', metaKey: true, shiftKey: true, description: 'Admin Panel' },
} as const;
