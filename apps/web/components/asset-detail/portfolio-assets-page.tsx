"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Banknote,
  Building2,
  Landmark,
  LineChart,
  Pencil,
  Plus,
  RefreshCcw,
  Save,
  Trash2,
  WalletCards
} from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import {
  createHolding,
  createLiability,
  deleteHolding,
  deleteLiability,
  getAssetDetailCards,
  getPortfolioRecords,
  updateHolding,
  updateLiability
} from "@/lib/api-client";
import { formatCurrency } from "@/lib/formatters";
import type {
  AccountUserResponse,
  AssetDetailCardResponse,
  AssetDetailCategory,
  AssetTypeInput,
  HoldingCreateRequest,
  HoldingResponse,
  LiabilityCreateRequest,
  LiabilityResponse,
  LiabilityTypeInput,
  PortfolioRecordsResponse,
  RiskLevel
} from "@/types/api";

const categoryLabel: Record<AssetDetailCategory, string> = {
  stock_etf: "Stock / ETF",
  crypto: "Crypto",
  real_estate: "Real estate",
  debt: "Debt / liability",
  retirement: "Retirement",
  cash: "Cash",
  bond: "Bond / Treasury",
  other: "Other asset"
};

const categoryIcon = {
  stock_etf: LineChart,
  crypto: Activity,
  real_estate: Building2,
  debt: Banknote,
  retirement: Landmark,
  cash: Banknote,
  bond: Landmark,
  other: WalletCards
};

const riskTone: Record<RiskLevel, "green" | "gold" | "coral"> = {
  low: "green",
  medium: "gold",
  high: "coral"
};

const assetTypeOptions: AssetTypeInput[] = [
  "Stocks",
  "ETFs",
  "Mutual Funds",
  "Crypto",
  "Real Estate",
  "Cash",
  "Bonds",
  "Treasuries",
  "Retirement",
  "Other"
];

const liabilityTypeOptions: LiabilityTypeInput[] = [
  "Mortgage",
  "Student loan",
  "Credit card",
  "Auto loan",
  "Personal loan",
  "Other"
];

const inputClass =
  "min-h-10 w-full rounded-lg border border-emerald-900/10 bg-white px-3 text-sm text-croc-ink outline-none transition focus:border-croc-moss";
const labelClass = "mb-1.5 block text-xs font-semibold uppercase text-stone-500";

const emptyHolding: HoldingCreateRequest = {
  symbol: "",
  name: "",
  asset_type: "ETFs",
  account_name: "",
  quantity: 0,
  cost_basis: null,
  market_value: 0,
  as_of_date: null
};

const emptyLiability: LiabilityCreateRequest = {
  name: "",
  liability_type: "Credit card",
  balance: 0,
  interest_rate: null,
  minimum_payment: null,
  due_day: null
};

export function PortfolioAssetsPage() {
  return (
    <AppShell>
      {(controls) => <PortfolioAssetsContent {...controls} />}
    </AppShell>
  );
}

interface PortfolioAssetsContentProps {
  account: AccountUserResponse | null;
  isAccountLoading: boolean;
  openGuide: () => void;
  openSidebar: () => void;
}

function PortfolioAssetsContent({
  account,
  isAccountLoading,
  openGuide,
  openSidebar
}: PortfolioAssetsContentProps) {
  const [detailCards, setDetailCards] = useState<AssetDetailCardResponse[]>([]);
  const [records, setRecords] = useState<PortfolioRecordsResponse | null>(null);
  const [holdingDraft, setHoldingDraft] = useState<HoldingCreateRequest>(emptyHolding);
  const [liabilityDraft, setLiabilityDraft] = useState<LiabilityCreateRequest>(emptyLiability);
  const [editingHoldingId, setEditingHoldingId] = useState<string | null>(null);
  const [editingLiabilityId, setEditingLiabilityId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setIsLoading(true);
    setError(null);

    if (isAccountLoading) {
      return () => controller.abort();
    }

    if (!account) {
      setRecords(null);
      getAssetDetailCards(controller.signal)
        .then(setDetailCards)
        .catch((requestError: Error) => {
          if (!controller.signal.aborted) {
            setError(requestError.message);
          }
        })
        .finally(() => {
          if (!controller.signal.aborted) {
            setIsLoading(false);
          }
        });

      return () => controller.abort();
    }

    Promise.all([getPortfolioRecords(controller.signal), getAssetDetailCards(controller.signal)])
      .then(([portfolioRecords, cards]) => {
        setRecords(portfolioRecords);
        setDetailCards(cards);
      })
      .catch((requestError: Error) => {
        if (!controller.signal.aborted) {
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setIsLoading(false);
        }
      });

    return () => controller.abort();
  }, [account, isAccountLoading, refreshKey]);

  async function handleSubmitHolding(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      const request = {
        ...holdingDraft,
        account_name: holdingDraft.account_name || null,
        symbol: holdingDraft.symbol.trim().toUpperCase(),
        name: holdingDraft.name.trim()
      };

      if (editingHoldingId) {
        await updateHolding(editingHoldingId, request);
      } else {
        await createHolding(request);
      }

      resetHoldingForm();
      setRefreshKey((value) => value + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to save holding.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleSubmitLiability(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      if (editingLiabilityId) {
        await updateLiability(editingLiabilityId, liabilityDraft);
      } else {
        await createLiability(liabilityDraft);
      }

      resetLiabilityForm();
      setRefreshKey((value) => value + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to save liability.");
    } finally {
      setIsSaving(false);
    }
  }

  async function removeHolding(holdingId: string) {
    setIsSaving(true);
    setError(null);
    try {
      await deleteHolding(holdingId);
      if (editingHoldingId === holdingId) {
        resetHoldingForm();
      }
      setRefreshKey((value) => value + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to delete holding.");
    } finally {
      setIsSaving(false);
    }
  }

  async function removeLiability(liabilityId: string) {
    setIsSaving(true);
    setError(null);
    try {
      await deleteLiability(liabilityId);
      if (editingLiabilityId === liabilityId) {
        resetLiabilityForm();
      }
      setRefreshKey((value) => value + 1);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to delete liability.");
    } finally {
      setIsSaving(false);
    }
  }

  function startEditingHolding(holding: HoldingResponse) {
    setEditingHoldingId(holding.id);
    setHoldingDraft({
      symbol: holding.symbol,
      name: holding.name,
      asset_type: holding.asset_type as AssetTypeInput,
      account_name: holding.account_name ?? "",
      quantity: holding.quantity,
      cost_basis: holding.cost_basis,
      market_value: holding.market_value,
      as_of_date: holding.as_of_date
    });
  }

  function startEditingLiability(liability: LiabilityResponse) {
    setEditingLiabilityId(liability.id);
    setLiabilityDraft({
      name: liability.name,
      liability_type: liability.liability_type as LiabilityTypeInput,
      balance: liability.balance,
      interest_rate: liability.interest_rate,
      minimum_payment: liability.minimum_payment,
      due_day: liability.due_day
    });
  }

  function resetHoldingForm() {
    setEditingHoldingId(null);
    setHoldingDraft(emptyHolding);
  }

  function resetLiabilityForm() {
    setEditingLiabilityId(null);
    setLiabilityDraft(emptyLiability);
  }

  return (
    <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Track your holdings and liabilities, then open beginner-friendly detail pages for context."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Portfolio"
          />

          {error ? (
            <div className="flex flex-col gap-4 rounded-lg border border-rose-200 bg-rose-50 p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm leading-6 text-rose-800">{error}</p>
              <button
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                onClick={() => setRefreshKey((value) => value + 1)}
                suppressHydrationWarning
                type="button"
              >
                <RefreshCcw className="h-4 w-4" />
                Retry
              </button>
            </div>
          ) : null}

          <Card>
            <SectionTitle
              eyebrow="Portfolio records"
              title="Your tracked wealth records"
              action={
                <Pill tone={account ? "green" : "gold"}>
                  {isAccountLoading || isLoading ? "Loading" : account ? "User-owned data" : "Sign in to edit"}
                </Pill>
              }
            />

            {isLoading ? (
              <div className="grid gap-4 md:grid-cols-3">
                {[0, 1, 2].map((item) => (
                  <div className="h-28 animate-pulse rounded-lg bg-stone-100" key={item} />
                ))}
              </div>
            ) : null}

            {!isLoading && records ? (
              <>
                <div className="grid gap-3 md:grid-cols-3">
                  <SummaryTile label="Assets" value={formatCurrency(records.summary.total_assets)} />
                  <SummaryTile label="Liabilities" value={formatCurrency(records.summary.total_liabilities)} />
                  <SummaryTile label="Net worth" value={formatCurrency(records.summary.net_worth)} />
                </div>

                <div className="mt-5 grid gap-4 xl:grid-cols-2">
                  <section className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
                    <h2 className="text-sm font-bold uppercase text-croc-moss">Holdings</h2>
                    <div className="mt-3 space-y-3">
                      {records.holdings.length ? (
                        records.holdings.map((holding) => (
                          <RecordRow
                            key={holding.id}
                            label={`${holding.symbol} - ${holding.name}`}
                            meta={`${holding.asset_type}${holding.account_name ? ` - ${holding.account_name}` : ""}`}
                            value={formatCurrency(holding.market_value)}
                            onEdit={() => startEditingHolding(holding)}
                            onDelete={() => removeHolding(holding.id)}
                          />
                        ))
                      ) : (
                        <EmptyState text="No holdings yet. Add one to start calculating your own net worth." />
                      )}
                    </div>
                  </section>

                  <section className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
                    <h2 className="text-sm font-bold uppercase text-croc-moss">Liabilities</h2>
                    <div className="mt-3 space-y-3">
                      {records.liabilities.length ? (
                        records.liabilities.map((liability) => (
                          <RecordRow
                            key={liability.id}
                            label={liability.name}
                            meta={liability.liability_type}
                            value={formatCurrency(liability.balance)}
                            onEdit={() => startEditingLiability(liability)}
                            onDelete={() => removeLiability(liability.id)}
                          />
                        ))
                      ) : (
                        <EmptyState text="No debts tracked yet. Add one if you want CrocLens to include it in net worth." />
                      )}
                    </div>
                  </section>
                </div>
              </>
            ) : null}

            {!isLoading && !records ? <SignedOutPortfolioPrompt /> : null}
          </Card>

          {account ? (
          <div className="grid gap-5 xl:grid-cols-2">
            <Card>
              <SectionTitle
                eyebrow={editingHoldingId ? "Edit asset" : "Add asset"}
                title={editingHoldingId ? "Update holding" : "Create a holding"}
              />
              <form className="grid gap-3 md:grid-cols-2" onSubmit={handleSubmitHolding}>
                <TextField label="Symbol" value={holdingDraft.symbol} onChange={(value) => setHoldingDraft({ ...holdingDraft, symbol: value })} />
                <TextField label="Name" value={holdingDraft.name} onChange={(value) => setHoldingDraft({ ...holdingDraft, name: value })} />
                <SelectField
                  label="Asset type"
                  value={holdingDraft.asset_type}
                  onChange={(value) => setHoldingDraft({ ...holdingDraft, asset_type: value as AssetTypeInput })}
                  options={assetTypeOptions}
                />
                <NumberField
                  label="Market value"
                  value={holdingDraft.market_value}
                  onChange={(value) => setHoldingDraft({ ...holdingDraft, market_value: value })}
                />
                <TextField
                  label="Account"
                  value={holdingDraft.account_name ?? ""}
                  onChange={(value) => setHoldingDraft({ ...holdingDraft, account_name: value })}
                />
                <NumberField
                  label="Quantity"
                  value={holdingDraft.quantity}
                  onChange={(value) => setHoldingDraft({ ...holdingDraft, quantity: value })}
                />
                <div className="flex flex-col gap-2 md:col-span-2 sm:flex-row">
                  <button
                    className="inline-flex min-h-10 flex-1 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white disabled:opacity-60"
                    disabled={isSaving}
                    suppressHydrationWarning
                    type="submit"
                  >
                    {editingHoldingId ? <Save className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                    {editingHoldingId ? "Save holding" : "Add holding"}
                  </button>
                  {editingHoldingId ? (
                    <button
                      className="inline-flex min-h-10 items-center justify-center rounded-lg border border-emerald-900/10 bg-white px-4 text-sm font-semibold text-croc-moss transition hover:bg-croc-cream"
                      onClick={resetHoldingForm}
                      suppressHydrationWarning
                      type="button"
                    >
                      Cancel
                    </button>
                  ) : null}
                </div>
              </form>
            </Card>

            <Card>
              <SectionTitle
                eyebrow={editingLiabilityId ? "Edit debt" : "Add debt"}
                title={editingLiabilityId ? "Update liability" : "Create a liability"}
              />
              <form className="grid gap-3 md:grid-cols-2" onSubmit={handleSubmitLiability}>
                <TextField label="Name" value={liabilityDraft.name} onChange={(value) => setLiabilityDraft({ ...liabilityDraft, name: value })} />
                <SelectField
                  label="Type"
                  value={liabilityDraft.liability_type}
                  onChange={(value) => setLiabilityDraft({ ...liabilityDraft, liability_type: value as LiabilityTypeInput })}
                  options={liabilityTypeOptions}
                />
                <NumberField
                  label="Balance"
                  value={liabilityDraft.balance}
                  onChange={(value) => setLiabilityDraft({ ...liabilityDraft, balance: value })}
                />
                <NumberField
                  label="Interest rate"
                  step="0.001"
                  value={liabilityDraft.interest_rate ?? 0}
                  onChange={(value) => setLiabilityDraft({ ...liabilityDraft, interest_rate: value })}
                />
                <div className="flex flex-col gap-2 md:col-span-2 sm:flex-row">
                  <button
                    className="inline-flex min-h-10 flex-1 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white disabled:opacity-60"
                    disabled={isSaving}
                    suppressHydrationWarning
                    type="submit"
                  >
                    {editingLiabilityId ? <Save className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                    {editingLiabilityId ? "Save liability" : "Add liability"}
                  </button>
                  {editingLiabilityId ? (
                    <button
                      className="inline-flex min-h-10 items-center justify-center rounded-lg border border-emerald-900/10 bg-white px-4 text-sm font-semibold text-croc-moss transition hover:bg-croc-cream"
                      onClick={resetLiabilityForm}
                      suppressHydrationWarning
                      type="button"
                    >
                      Cancel
                    </button>
                  ) : null}
                </div>
              </form>
            </Card>
          </div>
          ) : null}

          <Card>
            <SectionTitle
              eyebrow="Learning layer"
              title="Beginner-friendly asset guides"
              action={<Pill tone="blue">Educational context</Pill>}
            />
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {detailCards.map((item) => {
                const Icon = categoryIcon[item.category];
                return (
                  <Link
                    className="group flex min-h-48 flex-col justify-between rounded-lg border border-emerald-900/10 bg-croc-cream p-4 transition hover:-translate-y-0.5 hover:border-croc-moss hover:bg-white"
                    href={`/assets/${item.id}`}
                    key={item.id}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-white text-croc-moss shadow-sm">
                        <Icon className="h-5 w-5" />
                      </span>
                      <Pill tone={riskTone[item.risk_level]}>{item.risk_level} risk</Pill>
                    </div>
                    <div>
                      <div className="mt-5 flex items-end justify-between gap-3">
                        <div>
                          <p className="text-xs font-semibold uppercase text-croc-moss">
                            {categoryLabel[item.category]}
                          </p>
                          <h2 className="mt-1 text-lg font-bold text-croc-ink">{item.name}</h2>
                        </div>
                        <p className="text-base font-bold text-croc-ink">{formatCurrency(item.current_value)}</p>
                      </div>
                      <p className="mt-3 text-sm leading-6 text-stone-600">{item.summary}</p>
                    </div>
                    <span className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-croc-moss">
                      Open detail
                      <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
                    </span>
                  </Link>
                );
              })}
            </div>
          </Card>
    </div>
  );
}

function SummaryTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
      <p className="text-xs font-semibold uppercase text-croc-moss">{label}</p>
      <p className="mt-2 text-2xl font-bold text-croc-ink">{value}</p>
    </div>
  );
}

function SignedOutPortfolioPrompt() {
  return (
    <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4">
      <h2 className="text-base font-bold text-croc-ink">Sign in to track your own holdings and debts</h2>
      <p className="mt-2 max-w-2xl text-sm leading-6 text-stone-600">
        Demo visitors can still read the beginner asset guides below. Create an account or log in when you want
        CrocLens to save portfolio records and calculate your personal net worth.
      </p>
      <div className="mt-4 flex flex-col gap-2 sm:flex-row">
        <Link
          className="inline-flex min-h-10 items-center justify-center rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
          href="/signup"
        >
          Create account
        </Link>
        <Link
          className="inline-flex min-h-10 items-center justify-center rounded-lg border border-emerald-900/10 bg-white px-4 text-sm font-semibold text-croc-moss"
          href="/login"
        >
          Log in
        </Link>
      </div>
    </div>
  );
}

function RecordRow({
  label,
  meta,
  onEdit,
  onDelete,
  value
}: {
  label: string;
  meta: string;
  onEdit: () => void;
  onDelete: () => void;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-white p-3">
      <div className="min-w-0">
        <p className="truncate text-sm font-bold text-croc-ink">{label}</p>
        <p className="truncate text-xs text-stone-500">{meta}</p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <p className="text-sm font-bold text-croc-ink">{value}</p>
        <button
          aria-label={`Edit ${label}`}
          className="grid h-9 w-9 place-items-center rounded-lg text-stone-500 transition hover:bg-emerald-50 hover:text-croc-moss"
          onClick={onEdit}
          suppressHydrationWarning
          type="button"
        >
          <Pencil className="h-4 w-4" />
        </button>
        <button
          aria-label={`Delete ${label}`}
          className="grid h-9 w-9 place-items-center rounded-lg text-stone-500 transition hover:bg-rose-50 hover:text-rose-700"
          onClick={onDelete}
          suppressHydrationWarning
          type="button"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return <p className="rounded-lg bg-white p-3 text-sm leading-6 text-stone-600">{text}</p>;
}

function TextField({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label>
      <span className={labelClass}>{label}</span>
      <input className={inputClass} onChange={(event) => onChange(event.target.value)} suppressHydrationWarning value={value} />
    </label>
  );
}

function NumberField({
  label,
  onChange,
  step = "1",
  value
}: {
  label: string;
  onChange: (value: number) => void;
  step?: string;
  value: number;
}) {
  return (
    <label>
      <span className={labelClass}>{label}</span>
      <input
        className={inputClass}
        min={0}
        onChange={(event) => onChange(Number(event.target.value))}
        step={step}
        suppressHydrationWarning
        type="number"
        value={value}
      />
    </label>
  );
}

function SelectField({
  label,
  onChange,
  options,
  value
}: {
  label: string;
  onChange: (value: string) => void;
  options: string[];
  value: string;
}) {
  return (
    <label>
      <span className={labelClass}>{label}</span>
      <select className={inputClass} onChange={(event) => onChange(event.target.value)} suppressHydrationWarning value={value}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
