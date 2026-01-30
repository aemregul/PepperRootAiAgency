// API Client for Pepper Root AI Agency Backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

// Types
export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
    image_url?: string;
}

export interface Session {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface Entity {
    id: string;
    type: 'character' | 'location' | 'wardrobe';
    name: string;
    tag: string;
    description?: string;
    reference_images: string[];
}

export interface ChatRequest {
    message: string;
    session_id?: string;
}

export interface MessageResponse {
    id: string;
    session_id: string;
    role: string;
    content: string;
    metadata_?: Record<string, unknown>;
    created_at: string;
}

export interface AssetResponse {
    id?: string;
    asset_type: string;
    url: string;
    prompt?: string;
}

export interface ChatResponse {
    session_id: string;
    message: MessageResponse;
    response: MessageResponse;
    assets: AssetResponse[];
    entities_created: unknown[];
}

export interface ToolCall {
    name: string;
    args: Record<string, unknown>;
    result?: unknown;
}

export interface GeneratedAsset {
    id: string;
    type: 'image' | 'video';
    url: string;
    prompt?: string;
}

// API Functions
export async function createSession(title?: string): Promise<Session> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: title || 'Yeni Oturum' }),
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Failed to create session: ${error}`);
    }

    return response.json();
}

export async function getSessions(): Promise<Session[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/`);

    if (!response.ok) {
        throw new Error('Failed to fetch sessions');
    }

    return response.json();
}

export async function sendMessage(
    sessionId: string,
    message: string
): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            message: message,
        }),
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Failed to send message: ${error}`);
    }

    return response.json();
}

export async function getSessionHistory(sessionId: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/${sessionId}/messages`);

    if (!response.ok) {
        throw new Error('Failed to fetch session history');
    }

    return response.json();
}

// Entity (Character, Location, Wardrobe) APIs
export async function getEntities(sessionId: string): Promise<Entity[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/${sessionId}/entities`);

    if (!response.ok) {
        throw new Error('Failed to fetch entities');
    }

    return response.json();
}

export async function createEntity(
    sessionId: string,
    entity: Omit<Entity, 'id'>
): Promise<Entity> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/${sessionId}/entities`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entity),
    });

    if (!response.ok) {
        throw new Error('Failed to create entity');
    }

    return response.json();
}

// Asset APIs
export async function getAssets(sessionId: string): Promise<GeneratedAsset[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/${sessionId}/assets`);

    if (!response.ok) {
        throw new Error('Failed to fetch assets');
    }

    return response.json();
}

// Health check
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch {
        return false;
    }
}
