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

// Delete Entity
export async function deleteEntity(entityId: string): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}${API_PREFIX}/entities/${entityId}`, {
            method: 'DELETE',
        });
        return response.ok;
    } catch {
        return false;
    }
}

// ============== ADMIN APIs ==============

// AI Models
export interface AIModel {
    id: string;
    name: string;
    display_name: string;
    model_type: string;
    provider: string;
    description?: string;
    icon: string;
    is_enabled: boolean;
}

export async function getAIModels(): Promise<AIModel[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/models`);
    if (!response.ok) throw new Error('Failed to fetch AI models');
    return response.json();
}

export async function toggleAIModel(modelId: string, isEnabled: boolean): Promise<AIModel> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/models/${modelId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_enabled: isEnabled }),
    });
    if (!response.ok) throw new Error('Failed to toggle AI model');
    return response.json();
}

// Installed Plugins
export interface InstalledPlugin {
    id: string;
    plugin_id: string;
    name: string;
    description?: string;
    icon: string;
    category: string;
    is_enabled: boolean;
}

export async function getInstalledPlugins(): Promise<InstalledPlugin[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/plugins/installed`);
    if (!response.ok) throw new Error('Failed to fetch installed plugins');
    return response.json();
}

export async function installPlugin(plugin: {
    plugin_id: string;
    name: string;
    description?: string;
    icon: string;
    category: string;
    api_key?: string;
}): Promise<InstalledPlugin> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/plugins/install`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(plugin),
    });
    if (!response.ok) throw new Error('Failed to install plugin');
    return response.json();
}

export async function uninstallPlugin(pluginId: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/plugins/${pluginId}`, {
        method: 'DELETE',
    });
    return response.ok;
}

// User Settings
export interface UserSettings {
    id: string;
    theme: string;
    language: string;
    notifications_enabled: boolean;
    auto_save: boolean;
    default_model: string;
}

export async function getUserSettings(): Promise<UserSettings> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/settings`);
    if (!response.ok) throw new Error('Failed to fetch user settings');
    return response.json();
}

export async function updateUserSettings(settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/settings`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
    });
    if (!response.ok) throw new Error('Failed to update user settings');
    return response.json();
}

// Usage Stats
export interface UsageStats {
    date: string;
    api_calls: number;
    images_generated: number;
    videos_generated: number;
}

export async function getUsageStats(days: number = 7): Promise<UsageStats[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/stats/usage?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch usage stats');
    return response.json();
}

export interface OverviewStats {
    total_sessions: number;
    total_assets: number;
    total_messages: number;
    active_models: number;
}

export async function getOverviewStats(): Promise<OverviewStats> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/stats/overview`);
    if (!response.ok) throw new Error('Failed to fetch overview stats');
    return response.json();
}

// Creative Plugins
export interface CreativePluginData {
    id: string;
    name: string;
    description?: string;
    icon: string;
    color: string;
    system_prompt?: string;
    is_public: boolean;
    usage_count: number;
}

export async function getCreativePlugins(sessionId?: string): Promise<CreativePluginData[]> {
    const url = sessionId
        ? `${API_BASE_URL}${API_PREFIX}/admin/creative-plugins?session_id=${sessionId}`
        : `${API_BASE_URL}${API_PREFIX}/admin/creative-plugins`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch creative plugins');
    return response.json();
}

export async function createCreativePlugin(plugin: {
    name: string;
    description?: string;
    icon?: string;
    color?: string;
    system_prompt?: string;
    is_public?: boolean;
}, sessionId?: string): Promise<CreativePluginData> {
    const url = sessionId
        ? `${API_BASE_URL}${API_PREFIX}/admin/creative-plugins?session_id=${sessionId}`
        : `${API_BASE_URL}${API_PREFIX}/admin/creative-plugins`;
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(plugin),
    });
    if (!response.ok) throw new Error('Failed to create creative plugin');
    return response.json();
}

export async function deleteCreativePlugin(pluginId: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/creative-plugins/${pluginId}`, {
        method: 'DELETE',
    });
    return response.ok;
}

// Trash
export interface TrashItemData {
    id: string;
    item_type: string;
    item_id: string;
    item_name: string;
    deleted_at: string;
    expires_at: string;
}

export async function getTrashItems(): Promise<TrashItemData[]> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/trash`);
    if (!response.ok) throw new Error('Failed to fetch trash items');
    return response.json();
}

export async function restoreTrashItem(itemId: string): Promise<{ success: boolean; original_data: unknown }> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/trash/${itemId}/restore`, {
        method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to restore item');
    return response.json();
}

export async function permanentDeleteTrashItem(itemId: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/admin/trash/${itemId}`, {
        method: 'DELETE',
    });
    return response.ok;
}

// Delete Session (Project)
export async function deleteSession(sessionId: string): Promise<boolean> {
    const response = await fetch(`${API_BASE_URL}${API_PREFIX}/sessions/${sessionId}`, {
        method: 'DELETE',
    });
    return response.ok;
}

