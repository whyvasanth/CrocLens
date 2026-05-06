"use client";

import { useEffect, useState } from "react";
import { Download, RefreshCw, ShieldCheck, Trash2 } from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import {
  deleteDataPreview,
  getDataExport,
  getPrivacySettings,
  getSecurityStatus,
  updatePrivacySettings
} from "@/lib/api-client";
import type {
  DataExportResponse,
  DeleteDataResponse,
  PrivacySettingsResponse,
  SecurityStatusResponse
} from "@/types/api";

export function SettingsPrivacyPage() {
  const [security, setSecurity] = useState<SecurityStatusResponse | null>(null);
  const [privacy, setPrivacy] = useState<PrivacySettingsResponse | null>(null);
  const [exportPreview, setExportPreview] = useState<DataExportResponse | null>(null);
  const [deletePreview, setDeletePreview] = useState<DeleteDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function loadSettings(signal?: AbortSignal) {
    setIsLoading(true);
    setError(null);
    try {
      const [securityResponse, privacyResponse] = await Promise.all([
        getSecurityStatus(signal),
        getPrivacySettings(signal)
      ]);
      setSecurity(securityResponse);
      setPrivacy(privacyResponse);
    } catch (caught) {
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError("CrocLens could not load security settings.");
    } finally {
      if (!signal?.aborted) setIsLoading(false);
    }
  }

  useEffect(() => {
    const controller = new AbortController();
    void loadSettings(controller.signal);
    return () => controller.abort();
  }, []);

  async function toggleSetting(key: keyof PrivacySettingsResponse) {
    if (!privacy || typeof privacy[key] !== "boolean") return;
    const next = {
      beginner_mode_enabled: privacy.beginner_mode_enabled,
      store_assistant_history: privacy.store_assistant_history,
      allow_product_analytics: privacy.allow_product_analytics,
      allow_external_integrations: privacy.allow_external_integrations,
      data_retention_days: privacy.data_retention_days,
      [key]: !privacy[key]
    };
    setPrivacy(await updatePrivacySettings(next));
  }

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Manage privacy controls, export/delete previews, and MVP security status."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Settings"
          />

          {error ? (
            <Card className="border-rose-200 bg-rose-50">
              <div className="flex items-center justify-between gap-4">
                <p className="text-sm font-semibold text-rose-900">{error}</p>
                <button
                  className="inline-flex min-h-10 items-center gap-2 rounded-lg bg-white px-4 text-sm font-semibold text-rose-900"
                  onClick={() => void loadSettings()}
                  suppressHydrationWarning
                  type="button"
                >
                  <RefreshCw className="h-4 w-4" />
                  Retry
                </button>
              </div>
            </Card>
          ) : null}

          <div className="grid gap-5 lg:grid-cols-[minmax(0,1.1fr)_minmax(340px,0.9fr)]">
            <Card>
              <SectionTitle
                eyebrow="Privacy controls"
                title={isLoading ? "Loading controls" : "User data preferences"}
                action={<Pill tone="green">MVP preview</Pill>}
              />
              <div className="space-y-3">
                {privacy ? (
                  [
                    ["beginner_mode_enabled", "Beginner mode"],
                    ["store_assistant_history", "Store assistant history"],
                    ["allow_product_analytics", "Product analytics"],
                    ["allow_external_integrations", "External integrations"]
                  ].map(([key, label]) => (
                    <label
                      className="flex min-h-12 items-center justify-between gap-3 rounded-lg border border-emerald-900/10 px-4"
                      key={key}
                    >
                      <span className="text-sm font-semibold text-croc-ink">{label}</span>
                      <input
                        checked={Boolean(privacy[key as keyof PrivacySettingsResponse])}
                        className="h-5 w-5 accent-croc-moss"
                        onChange={() => void toggleSetting(key as keyof PrivacySettingsResponse)}
                        type="checkbox"
                      />
                    </label>
                  ))
                ) : (
                  <p className="text-sm text-stone-600">Loading privacy settings...</p>
                )}
              </div>
              <p className="mt-4 text-sm leading-6 text-stone-600">{privacy?.explanation}</p>
            </Card>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Security status" title="Current controls" />
                <div className="space-y-3 text-sm leading-6 text-stone-600">
                  <p>{security?.authentication_status}</p>
                  <p>Rate limit: {security?.rate_limit_per_minute ?? "--"} requests per minute.</p>
                  <div className="flex flex-wrap gap-2">
                    {security?.security_headers_enabled.map((header) => (
                      <Pill key={header} tone="blue">{header}</Pill>
                    ))}
                  </div>
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Data rights" title="Export and delete" />
                <div className="grid gap-3 sm:grid-cols-2">
                  <button
                    className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                    onClick={async () => setExportPreview(await getDataExport())}
                    suppressHydrationWarning
                    type="button"
                  >
                    <Download className="h-4 w-4" />
                    Export preview
                  </button>
                  <button
                    className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-rose-100 px-4 text-sm font-semibold text-rose-900"
                    onClick={async () => setDeletePreview(await deleteDataPreview())}
                    suppressHydrationWarning
                    type="button"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete preview
                  </button>
                </div>
                <div className="mt-4 space-y-3 text-sm leading-6 text-stone-600">
                  {exportPreview ? (
                    <p>
                      Export `{exportPreview.export_id}` covers {exportPreview.sections.length} sections.
                    </p>
                  ) : null}
                  {deletePreview ? (
                    <p>{deletePreview.explanation}</p>
                  ) : null}
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Guardrails" title="Prompt injection safety" />
                <div className="space-y-2">
                  {security?.prompt_injection_guardrails.map((guardrail) => (
                    <div className="flex gap-3 rounded-lg bg-croc-cream p-3" key={guardrail}>
                      <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-croc-moss" />
                      <p className="text-sm leading-6 text-stone-600">{guardrail}</p>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}
    </AppShell>
  );
}
