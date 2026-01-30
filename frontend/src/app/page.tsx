"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { AssetsPanel } from "@/components/AssetsPanel";

export default function Home() {
  const [assetsCollapsed, setAssetsCollapsed] = useState(false);
  const [activeProjectId, setActiveProjectId] = useState<string>("samsung");

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        activeProjectId={activeProjectId}
        onProjectChange={(projectId) => setActiveProjectId(projectId)}
      />

      {/* Chat Panel */}
      <ChatPanel
        key={activeProjectId}  // Force re-mount on project change
        projectId={activeProjectId}
      />

      {/* Assets Panel (Desktop only) */}
      <AssetsPanel
        collapsed={assetsCollapsed}
        onToggle={() => setAssetsCollapsed(!assetsCollapsed)}
      />
    </main>
  );
}
