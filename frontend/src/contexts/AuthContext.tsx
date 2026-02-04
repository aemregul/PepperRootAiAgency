'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
    id: string;
    email: string;
    full_name: string | null;
    avatar_url: string | null;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    isLoading: boolean;
    rememberMe: boolean;
    setRememberMe: (value: boolean) => void;
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, fullName?: string) => Promise<void>;
    loginWithGoogle: () => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Storage helpers - use localStorage or sessionStorage based on rememberMe preference
const getStorage = () => {
    if (typeof window === 'undefined') return null;
    const remember = localStorage.getItem('rememberMe') === 'true';
    return remember ? localStorage : sessionStorage;
};

const getToken = () => {
    if (typeof window === 'undefined') return null;
    // Check both storages - localStorage has priority if rememberMe is set
    return localStorage.getItem('token') || sessionStorage.getItem('token');
};

const setToken = (token: string, remember: boolean) => {
    if (typeof window === 'undefined') return;
    // Clear from both first
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
    // Then save to appropriate storage
    if (remember) {
        localStorage.setItem('token', token);
        localStorage.setItem('rememberMe', 'true');
    } else {
        sessionStorage.setItem('token', token);
        localStorage.setItem('rememberMe', 'false');
    }
};

const clearToken = () => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
};

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [token, setTokenState] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [rememberMe, setRememberMeState] = useState(true); // Default to true

    // Load rememberMe preference on mount
    useEffect(() => {
        const savedPreference = localStorage.getItem('rememberMe');
        if (savedPreference !== null) {
            setRememberMeState(savedPreference === 'true');
        }
    }, []);

    // Check for existing token on mount
    useEffect(() => {
        const storedToken = getToken();
        if (storedToken) {
            setTokenState(storedToken);
            fetchUser(storedToken);
        } else {
            setIsLoading(false);
        }
    }, []);

    const setRememberMe = (value: boolean) => {
        setRememberMeState(value);
        localStorage.setItem('rememberMe', value.toString());
    };

    const fetchUser = async (accessToken: string) => {
        try {
            const response = await fetch(`${API_URL}/api/v1/auth/me`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
            });

            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
            } else {
                // Token invalid, clear it
                clearToken();
                setTokenState(null);
            }
        } catch (error) {
            console.error('Failed to fetch user:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (email: string, password: string) => {
        const response = await fetch(`${API_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        setToken(data.access_token, rememberMe);
        setTokenState(data.access_token);
        setUser(data.user);
    };

    const register = async (email: string, password: string, fullName?: string) => {
        const response = await fetch(`${API_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, full_name: fullName }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Registration failed');
        }

        const data = await response.json();
        setToken(data.access_token, rememberMe);
        setTokenState(data.access_token);
        setUser(data.user);
    };

    const loginWithGoogle = () => {
        // Save rememberMe preference before redirect
        localStorage.setItem('rememberMe', rememberMe.toString());
        window.location.href = `${API_URL}/api/v1/auth/google`;
    };

    const logout = () => {
        clearToken();
        setTokenState(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{
            user,
            token,
            isLoading,
            rememberMe,
            setRememberMe,
            login,
            register,
            loginWithGoogle,
            logout,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

