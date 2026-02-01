'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const token = searchParams.get('token');

        if (token) {
            // Save token from Google OAuth callback
            localStorage.setItem('token', token);
            router.push('/app');
        } else {
            // No token, redirect to login
            router.push('/login');
        }
    }, [searchParams, router]);

    return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center">
            <div className="text-center">
                <div className="text-5xl mb-4 animate-pulse">🫑</div>
                <p className="text-gray-400">Giriş yapılıyor...</p>
            </div>
        </div>
    );
}
