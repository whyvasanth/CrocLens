"use client";

import type { ReactNode } from "react";
import { useState } from "react";
import { CrocGuidePanel } from "@/components/dashboard/croc-guide-panel";
import { Sidebar } from "@/components/dashboard/sidebar";

interface AppShellControls {
  openGuide: () => void;
  openSidebar: () => void;
}

interface AppShellProps {
  children: (controls: AppShellControls) => ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  return (
    <div className="min-h-screen bg-croc-emerald lg:flex">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="min-w-0 flex-1 bg-croc-cream p-4 md:p-6 lg:rounded-l-[28px] lg:p-7">
        {children({
          openGuide: () => setIsGuideOpen(true),
          openSidebar: () => setIsSidebarOpen(true)
        })}
      </main>
      <CrocGuidePanel isOpen={isGuideOpen} onClose={() => setIsGuideOpen(false)} />
    </div>
  );
}
