"use client";

import { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatPanel } from "@/components/ChatPanel";
import { AssetsPanel } from "@/components/AssetsPanel";

export default function Home() {
  const [assetsCollapsed, setAssetsCollapsed] = useState(false);

  return (
    <main className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Chat Panel */}
      <ChatPanel />

      {/* Assets Panel (Desktop only) */}
      <AssetsPanel
        collapsed={assetsCollapsed}
        onToggle={() => setAssetsCollapsed(!assetsCollapsed)}
      />
    </main>
  );
}
