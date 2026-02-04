"use client";

import React from 'react';
import { Loader2 } from 'lucide-react';

interface LoadingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    loading?: boolean;
    loadingText?: string;
    children: React.ReactNode;
}

export function LoadingButton({
    loading = false,
    loadingText,
    children,
    disabled,
    className = '',
    ...props
}: LoadingButtonProps) {
    return (
        <button
            disabled={disabled || loading}
            className={`relative ${className} ${loading ? 'cursor-wait' : ''}`}
            {...props}
        >
            {loading && (
                <span className="absolute inset-0 flex items-center justify-center">
                    <Loader2 size={16} className="animate-spin" />
                </span>
            )}
            <span className={loading ? 'opacity-0' : ''}>
                {loading && loadingText ? loadingText : children}
            </span>
        </button>
    );
}
