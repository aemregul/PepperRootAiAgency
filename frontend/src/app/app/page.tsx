"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { AssetsPanel } from "@/components/AssetsPanel";
import { NewProjectModal } from "@/components/NewProjectModal";
import { createSession, getSessions, getMainChatSession } from "@/lib/api";
import { FolderPlus, Sparkles } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function Home() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();

  const [assetsCollapsed, setAssetsCollapsed] = useState(false);

  // === TEK ASISTAN MİMARİSİ ===
  // chatSessionId: ana sohbet session (asla değişmez, user başına 1 tane)
  // activeProjectId: şu an seçili proje (asset + entity container)
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [activeProjectId, setActiveProjectId] = useState<string | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);
  const [pendingInputText, setPendingInputText] = useState<string | null>(null);
  const [installedPlugins, setInstalledPlugins] = useState<Array<{ id: string; name: string; promptText: string }>>([]);
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [newProjectModalOpen, setNewProjectModalOpen] = useState(false);

  // Refresh triggers
  const [entityRefreshKey, setEntityRefreshKey] = useState(0);
  const [assetRefreshKey, setAssetRefreshKey] = useState(0);

  const [hasNoProjects, setHasNoProjects] = useState(false);

  // Auth kontrolü
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [authLoading, user, router]);

  // === ANA CHAT SESSION + PROJE LİSTESİ BAŞLAT ===
  useEffect(() => {
    const init = async () => {
      try {
        // 1. Ana chat session al (yoksa otomatik oluşturulur)
        const mainChat = await getMainChatSession();
        setChatSessionId(mainChat.session_id);

        // 2. Projeleri yükle
        const sessions = await getSessions();
        // main_chat session'ını proje listesinden çıkar
        const projects = sessions.filter(s => s.category !== 'main_chat');

        if (projects.length > 0) {
          setActiveProjectId(projects[0].id);
          setHasNoProjects(false);
        } else {
          setActiveProjectId(null);
          setHasNoProjects(true);
        }
      } catch (error) {
        console.error("Başlatma hatası:", error);
        setHasNoProjects(true);
      } finally {
        setIsLoading(false);
      }
    };

    if (user) init();
  }, [user, entityRefreshKey]);

  // Proje değiştiğinde SADECE activeProjectId güncellenir, chat aynı kalır
  const handleProjectChange = (projectId: string) => {
    setActiveProjectId(projectId);
    setHasNoProjects(false);
  };

  const handleNewAsset = useCallback(() => {
    setAssetRefreshKey(prev => prev + 1);
  }, []);

  const handleEntityChange = useCallback(() => {
    setEntityRefreshKey(prev => prev + 1);
  }, []);

  const handleProjectDelete = useCallback(() => {
    setActiveProjectId(null);
    setHasNoProjects(true);
    setEntityRefreshKey(prev => prev + 1);
  }, []);

  // Asset silindiğinde çöp kutusunu güncelle
  const handleAssetDeleted = useCallback(() => {
    setEntityRefreshKey(prev => prev + 1);  // Sidebar trash'i yeniler
  }, []);

  // Çöp kutusundan asset geri yüklenince media panel'ı güncelle
  const handleAssetRestore = useCallback(() => {
    setAssetRefreshKey(prev => prev + 1);  // AssetsPanel'i yeniler
  }, []);

  const handleCreateProject = async (name: string, description?: string, category?: string) => {
    setIsCreatingProject(true);
    try {
      const newSession = await createSession(name, description, category);
      setActiveProjectId(newSession.id);
      setHasNoProjects(false);
      setEntityRefreshKey(prev => prev + 1);
    } catch (error) {
      console.error("Proje oluşturulamadı:", error);
    } finally {
      setIsCreatingProject(false);
    }
  };

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

  if (!user) return null;

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Sidebar — proje geçişi sadece activeProjectId değiştirir */}
      <Sidebar
        activeProjectId={activeProjectId || ""}
        onProjectChange={handleProjectChange}
        onProjectDelete={handleProjectDelete}
        sessionId={activeProjectId}
        refreshKey={entityRefreshKey}
        onSendPrompt={setPendingPrompt}
        onSetInputText={setPendingInputText}
        onPluginsLoaded={setInstalledPlugins}
        onAssetRestore={handleAssetRestore}
      />

      {/* Chat her zaman görünür (tek sürekli sohbet) */}
      {!chatSessionId || (!activeProjectId && hasNoProjects) ? (
        <div className="flex-1 flex items-center justify-center" style={{ background: "var(--background)" }}>
          <div className="text-center max-w-md px-6">
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6"
              style={{
                background: "linear-gradient(135deg, var(--accent) 0%, rgba(139, 92, 246, 0.8) 100%)",
                boxShadow: "0 10px 40px rgba(139, 92, 246, 0.3)"
              }}
            >
              <Sparkles size={40} className="text-white" />
            </div>
            <h1 className="text-2xl font-bold mb-3" style={{ color: "var(--foreground)" }}>
              Pepper Root&apos;a Hoş Geldiniz
            </h1>
            <p className="mb-8" style={{ color: "var(--foreground-muted)" }}>
              AI destekli görsel ve video üretimi için yeni bir proje oluşturun.
              Tek asistanınız tüm projelerinizde sizi hatırlayacak.
            </p>
            <button
              onClick={() => setNewProjectModalOpen(true)}
              disabled={isCreatingProject}
              className="inline-flex items-center gap-3 px-8 py-4 rounded-xl font-medium text-lg transition-all hover:scale-105 disabled:opacity-50"
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
            <div className="mt-8 p-4 rounded-lg" style={{ background: "var(--card)", border: "1px solid var(--border)" }}>
              <p className="text-sm" style={{ color: "var(--foreground-muted)" }}>
                💡 <strong>İpucu:</strong> Sol menüdeki &quot;+&quot; butonuyla da yeni proje oluşturabilirsiniz.
              </p>
            </div>
          </div>
        </div>
      ) : (
        <ChatPanel
          sessionId={chatSessionId || undefined}
          activeProjectId={activeProjectId || undefined}
          onSessionChange={setChatSessionId}
          onNewAsset={handleNewAsset}
          onEntityChange={handleEntityChange}
          pendingPrompt={pendingPrompt}
          onPromptConsumed={() => setPendingPrompt(null)}
          pendingInputText={pendingInputText}
          onInputTextConsumed={() => setPendingInputText(null)}
          installedPlugins={installedPlugins}
        />
      )}

      {/* Assets Panel — aktif projedeki asset'leri gösterir */}
      <AssetsPanel
        collapsed={assetsCollapsed}
        onToggle={() => setAssetsCollapsed(!assetsCollapsed)}
        sessionId={activeProjectId}
        refreshKey={assetRefreshKey}
        onSaveToImages={handleEntityChange}
        onAssetDeleted={handleAssetDeleted}
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
