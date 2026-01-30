"use client";

import { useState, useEffect, useCallback } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { AssetsPanel } from "@/components/AssetsPanel";
import { createSession, getSessions } from "@/lib/api";

export default function Home() {
  const [assetsCollapsed, setAssetsCollapsed] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeProjectId, setActiveProjectId] = useState<string>("samsung");
  const [isLoading, setIsLoading] = useState(true);
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

  // Refresh triggers - entity veya asset değiştiğinde artır
  const [entityRefreshKey, setEntityRefreshKey] = useState(0);
  const [assetRefreshKey, setAssetRefreshKey] = useState(0);

  // Session yönetimi
  useEffect(() => {
    const initSession = async () => {
      try {
        const sessions = await getSessions();
        if (sessions.length > 0) {
          setSessionId(sessions[0].id);
        } else {
          const newSession = await createSession("Ana Oturum");
          setSessionId(newSession.id);
        }
      } catch (error) {
        console.error("Session başlatılamadı:", error);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, []);

  // Proje (session) değiştiğinde sessionId'yi güncelle
  const handleProjectChange = (projectId: string) => {
    // projectId aslında backend'deki session.id
    setSessionId(projectId);
    setActiveProjectId(projectId);
  };

  // Chat'te yeni asset oluşturulduğunda AssetsPanel'i refresh et
  const handleNewAsset = useCallback(() => {
    setAssetRefreshKey(prev => prev + 1);
  }, []);

  // Chat'te yeni entity oluşturulduğunda Sidebar'ı refresh et
  const handleEntityChange = useCallback(() => {
    setEntityRefreshKey(prev => prev + 1);
  }, []);

  if (isLoading) {
    return (
      <main className="flex h-screen items-center justify-center" style={{ background: "var(--background)" }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--accent)] mx-auto mb-4"></div>
          <p style={{ color: "var(--foreground-muted)" }}>Yükleniyor...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        activeProjectId={activeProjectId}
        onProjectChange={handleProjectChange}
        sessionId={sessionId}
        refreshKey={entityRefreshKey}
        onSendPrompt={setPendingPrompt}
      />

      {/* Chat Panel */}
      <ChatPanel
        key={`${activeProjectId}-${sessionId}`}
        projectId={activeProjectId}
        sessionId={sessionId || undefined}
        onSessionChange={setSessionId}
        onNewAsset={handleNewAsset}
        onEntityChange={handleEntityChange}
        pendingPrompt={pendingPrompt}
        onPromptConsumed={() => setPendingPrompt(null)}
      />

      {/* Assets Panel */}
      <AssetsPanel
        collapsed={assetsCollapsed}
        onToggle={() => setAssetsCollapsed(!assetsCollapsed)}
        sessionId={sessionId}
        refreshKey={assetRefreshKey}
      />
    </main>
  );
}
