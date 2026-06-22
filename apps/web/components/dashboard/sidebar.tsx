"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePathname } from "next/navigation";
import { ChevronDown, HelpCircle, LogOut, X } from "lucide-react";
import { clsx } from "clsx";
import { logoutAccount } from "@/lib/api-client";
import { sidebarItems } from "@/lib/mock-dashboard-data";
import type { AccountUserResponse } from "@/types/api";

interface SidebarProps {
  account: AccountUserResponse | null;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ account, isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const displayName = account?.display_name ?? "Demo visitor";
  const email = account?.email ?? "Sample data mode";
  const initial = displayName.trim().charAt(0).toUpperCase() || "C";

  async function handleLogout() {
    if (!account) {
      router.push("/login");
      return;
    }

    await logoutAccount();
    router.push("/login");
    router.refresh();
  }

  return (
    <>
      <div
        className={clsx(
          "fixed inset-0 z-30 bg-croc-ink/35 transition-opacity lg:hidden",
          isOpen ? "opacity-100" : "pointer-events-none opacity-0"
        )}
        onClick={onClose}
      />
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-40 flex w-72 flex-col overflow-y-auto bg-[radial-gradient(circle_at_top_left,#0b7a5c,#052f28_55%,#03231e)] px-5 py-5 text-white transition-transform lg:sticky lg:top-0 lg:h-screen lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-3" aria-label="CrocLens dashboard">
            <div className="grid h-12 w-12 place-items-center rounded-lg bg-croc-lime text-2xl">
              C
            </div>
            <div>
              <p className="text-xl font-bold">CrocLens</p>
              <p className="text-xs text-emerald-100">See your money clearly.</p>
            </div>
          </Link>
          <button
            aria-label="Close navigation"
            className="grid h-10 w-10 place-items-center rounded-lg bg-white/10 lg:hidden"
            onClick={onClose}
            suppressHydrationWarning
            type="button"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="mt-7 space-y-1" aria-label="Primary navigation">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <Link
                key={item.label}
                href={item.href}
                onClick={onClose}
                className={clsx(
                  "flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium transition",
                  isActive
                    ? "bg-emerald-400/90 text-white shadow-lg shadow-emerald-950/20"
                    : "text-emerald-50 hover:bg-white/10"
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto space-y-4">
          <div className="rounded-lg border border-white/10 bg-white/10 p-4">
            <div className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-full bg-emerald-300" />
              <p className="text-sm font-semibold">Market is open</p>
            </div>
            <p className="mt-2 text-sm leading-6 text-emerald-50">
              Sample data for Phase 1. Real market freshness arrives later.
            </p>
          </div>

          <button
            className="flex w-full items-center gap-3 rounded-lg border border-white/10 bg-white/10 p-3 text-left"
            suppressHydrationWarning
            type="button"
          >
            <span className="grid h-11 w-11 place-items-center rounded-lg bg-white text-sm font-bold text-croc-emerald">
              {initial}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block text-sm font-semibold">{displayName}</span>
              <span className="block truncate text-xs text-emerald-100">{email}</span>
            </span>
            <ChevronDown className="h-4 w-4 text-emerald-100" />
          </button>

          <div className="space-y-1 border-t border-white/10 pt-3">
            <Link href="/settings" className="flex min-h-9 items-center gap-3 rounded-lg px-3 text-sm text-emerald-50 hover:bg-white/10">
              <HelpCircle className="h-4 w-4" />
              Help Center
            </Link>
            <button
              className="flex min-h-9 w-full items-center gap-3 rounded-lg px-3 text-left text-sm text-emerald-50 hover:bg-white/10"
              onClick={handleLogout}
              suppressHydrationWarning
              type="button"
            >
              <LogOut className="h-4 w-4" />
              {account ? "Log Out" : "Log In"}
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
