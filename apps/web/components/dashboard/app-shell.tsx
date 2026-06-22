"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { CrocGuidePanel } from "@/components/dashboard/croc-guide-panel";
import { Sidebar } from "@/components/dashboard/sidebar";
import { getCurrentAccount } from "@/lib/api-client";
import type { AccountUserResponse } from "@/types/api";

interface AppShellControls {
  account: AccountUserResponse | null;
  isAccountLoading: boolean;
  openGuide: () => void;
  openSidebar: () => void;
}

interface AppShellProps {
  children: (controls: AppShellControls) => ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);
  const [account, setAccount] = useState<AccountUserResponse | null>(null);
  const [isAccountLoading, setIsAccountLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    getCurrentAccount(controller.signal)
      .then(setAccount)
      .catch(() => {
        if (!controller.signal.aborted) {
          setAccount(null);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsAccountLoading(false);
        }
      });

    return () => controller.abort();
  }, []);

  return (
    <div className="min-h-screen bg-croc-emerald lg:flex">
      <Sidebar account={account} isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="min-w-0 flex-1 bg-croc-cream p-4 md:p-6 lg:rounded-l-[28px] lg:p-7">
        {children({
          account,
          isAccountLoading,
          openGuide: () => setIsGuideOpen(true),
          openSidebar: () => setIsSidebarOpen(true)
        })}
      </main>
      <CrocGuidePanel isOpen={isGuideOpen} onClose={() => setIsGuideOpen(false)} />
    </div>
  );
}
