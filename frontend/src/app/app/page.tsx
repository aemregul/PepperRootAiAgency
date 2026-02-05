"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { AssetsPanel } from "@/components/AssetsPanel";
import { NewProjectModal } from "@/components/NewProjectModal";
import { createSession, getSessions } from "@/lib/api";
import { FolderPlus, Sparkles } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();

  const [assetsCollapsed, setAssetsCollapsed] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeProjectId, setActiveProjectId] = useState<string>("samsung");
  const [isLoading, setIsLoading] = useState(true);
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [newProjectModalOpen, setNewProjectModalOpen] = useState(false);

  // Refresh triggers - entity veya asset değiştiğinde artır
  const [entityRefreshKey, setEntityRefreshKey] = useState(0);
  const [assetRefreshKey, setAssetRefreshKey] = useState(0);

  // Proje sayısı kontrolü için
  const [hasNoProjects, setHasNoProjects] = useState(false);

  // Auth kontrolü - giriş yapmamışsa login'e yönlendir
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [authLoading, user, router]);

  // Session yönetimi
  useEffect(() => {
    const initSession = async () => {
      try {
        const sessions = await getSessions();
        if (sessions.length > 0) {
          setSessionId(sessions[0].id);
          setHasNoProjects(false);
        } else {
          setSessionId(null);
          setHasNoProjects(true);
        }
      } catch (error) {
        console.error("Session başlatılamadı:", error);
        setHasNoProjects(true);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, [entityRefreshKey]); // entityRefreshKey değiştiğinde projeleri yeniden kontrol et

  // Proje (session) değiştiğinde sessionId'yi güncelle
  const handleProjectChange = (projectId: string) => {
    // projectId aslında backend'deki session.id
    setSessionId(projectId);
    setActiveProjectId(projectId);
    setHasNoProjects(false);
  };

  // Chat'te yeni asset oluşturulduğunda AssetsPanel'i refresh et
  const handleNewAsset = useCallback(() => {
    setAssetRefreshKey(prev => prev + 1);
  }, []);

  // Chat'te yeni entity oluşturulduğunda Sidebar'ı refresh et
  const handleEntityChange = useCallback(() => {
    setEntityRefreshKey(prev => prev + 1);
  }, []);

  // Proje silindiğinde
  const handleProjectDelete = useCallback(() => {
    setSessionId(null);
    setHasNoProjects(true);
    setEntityRefreshKey(prev => prev + 1); // Projeleri yeniden kontrol et
  }, []);

  // Yeni proje oluştur
  const handleCreateProject = async (name: string) => {
    setIsCreatingProject(true);
    try {
      const newSession = await createSession(name);
      setSessionId(newSession.id);
      setActiveProjectId(newSession.id);
      setHasNoProjects(false);
      setEntityRefreshKey(prev => prev + 1); // Sidebar'ı güncelle
    } catch (error) {
      console.error("Proje oluşturulamadı:", error);
    } finally {
      setIsCreatingProject(false);
    }
  };

  // Auth veya data yükleniyorsa loading göster
  if (authLoading || isLoading) {
    return (
      <main className="flex h-screen items-center justify-center" style={{ background: "var(--background)" }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[var(--accent)] mx-auto mb-4"></div>
          <p style={{ color: "var(--foreground-muted)" }}>Yükleniyor...</p>
        </div>
      </main>
    );
  }

  // Giriş yapmamışsa boş döndür (zaten /login'e yönlendiriliyor)
  if (!user) {
    return null;
  }

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        activeProjectId={activeProjectId}
        onProjectChange={handleProjectChange}
        onProjectDelete={handleProjectDelete}
        sessionId={sessionId}
        refreshKey={entityRefreshKey}
        onSendPrompt={setPendingPrompt}
      />

      {/* Proje yoksa "Proje Oluştur" ekranı, varsa Chat Panel */}
      {!sessionId || hasNoProjects ? (
        <div className="flex-1 flex items-center justify-center" style={{ background: "var(--background)" }}>
          <div className="text-center max-w-md px-6">
            {/* Icon */}
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
              style={{
                background: "linear-gradient(135deg, var(--accent) 0%, rgba(139, 92, 246, 0.8) 100%)",
                boxShadow: "0 10px 40px rgba(139, 92, 246, 0.3)"
              }}
            >
              <Sparkles size={40} className="text-white" />
            </div>

            {/* Title */}
            <h1 className="text-2xl font-bold mb-3" style={{ color: "var(--foreground)" }}>
              Pepper Root'a Hoş Geldiniz
            </h1>

            {/* Description */}
            <p className="mb-8" style={{ color: "var(--foreground-muted)" }}>
              AI destekli görsel ve video üretimi için yeni bir proje oluşturun.
              Karakterler, mekanlar ve yaratıcı pluginler ile çalışmaya başlayın.
            </p>

            {/* Create Project Button */}
            <button
              onClick={() => setNewProjectModalOpen(true)}
              disabled={isCreatingProject}
              className="inline-flex items-center gap-3 px-8 py-4 rounded-xl font-medium text-lg transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                background: "var(--accent)",
                color: "var(--background)",
                boxShadow: "0 4px 20px rgba(139, 92, 246, 0.4)"
              }}
            >
              {isCreatingProject ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-current"></div>
                  Oluşturuluyor...
                </>
              ) : (
                <>
                  <FolderPlus size={24} />
                  Yeni Proje Oluştur
                </>
              )}
            </button>

            {/* Tips */}
            <div className="mt-8 p-4 rounded-lg" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
              <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                💡 <strong>İpucu:</strong> Sol menüdeki "+" butonuyla da yeni proje oluşturabilirsiniz.
              </p>
            </div>
          </div>
        </div>
      ) : (
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
      )}

      {/* Assets Panel */}
      <AssetsPanel
        collapsed={assetsCollapsed}
        onToggle={() => setAssetsCollapsed(!assetsCollapsed)}
        sessionId={sessionId}
        refreshKey={assetRefreshKey}
        onWardrobeSave={handleEntityChange}
      />

      {/* New Project Modal */}
      <NewProjectModal
        isOpen={newProjectModalOpen}
        onClose={() => setNewProjectModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </main>
  );
}
