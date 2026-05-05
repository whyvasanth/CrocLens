"use client";

import { FormEvent, useState } from "react";
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  Landmark,
  Loader2,
  PiggyBank,
  ShieldCheck,
  WalletCards
} from "lucide-react";
import { AppShell } from "@/components/dashboard/app-shell";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { submitOnboardingProfile } from "@/lib/api-client";
import type {
  EmployerMatchStatus,
  IncomeRange,
  InvestmentExperience,
  ManualAssetEntry,
  OnboardingProfileRequest,
  OnboardingProfileResponse,
  PrimaryGoal,
  RiskToleranceInput,
  TimeHorizon
} from "@/types/api";

const fieldClass =
  "min-h-11 w-full rounded-lg border border-emerald-900/10 bg-white px-3 text-sm text-croc-ink outline-none transition focus:border-croc-moss";

const optionClass =
  "flex min-h-11 items-center gap-3 rounded-lg border border-emerald-900/10 bg-white px-3 text-sm font-semibold text-croc-ink";

const labelClass = "mb-2 block text-sm font-semibold text-croc-ink";

const experienceOptions: Array<{ label: string; value: InvestmentExperience }> = [
  { label: "New to investing", value: "new" },
  { label: "I know some basics", value: "some" },
  { label: "Comfortable with investing", value: "experienced" }
];

const goalOptions: Array<{ label: string; value: PrimaryGoal }> = [
  { label: "Learn money basics", value: "learn" },
  { label: "Build wealth", value: "build_wealth" },
  { label: "Plan for retirement", value: "retirement" },
  { label: "Pay down debt", value: "debt_payoff" },
  { label: "Buy a home", value: "home" },
  { label: "Build emergency fund", value: "emergency_fund" }
];

const riskOptions: Array<{ label: string; value: RiskToleranceInput }> = [
  { label: "Low", value: "low" },
  { label: "Medium", value: "medium" },
  { label: "High", value: "high" }
];

const horizonOptions: Array<{ label: string; value: TimeHorizon }> = [
  { label: "Less than 3 years", value: "short" },
  { label: "3 to 10 years", value: "medium" },
  { label: "10+ years", value: "long" }
];

const incomeOptions: Array<{ label: string; value: IncomeRange }> = [
  { label: "Under $50k", value: "under_50k" },
  { label: "$50k to $100k", value: "50k_100k" },
  { label: "$100k to $200k", value: "100k_200k" },
  { label: "Over $200k", value: "over_200k" },
  { label: "Prefer not to say", value: "prefer_not" }
];

const employerMatchOptions: Array<{ label: string; value: EmployerMatchStatus }> = [
  { label: "Yes", value: "yes" },
  { label: "No", value: "no" },
  { label: "Not sure", value: "not_sure" },
  { label: "Not applicable", value: "not_applicable" }
];

const initialManualAssets: ManualAssetEntry[] = [
  { asset_class: "Cash", label: "Emergency savings", estimated_value: 4500 },
  { asset_class: "Retirement", label: "401(k)", estimated_value: 12000 }
];

const initialProfile: OnboardingProfileRequest = {
  investment_experience: "new",
  primary_goal: "debt_payoff",
  risk_tolerance: "medium",
  time_horizon: "medium",
  income_range: "50k_100k",
  emergency_cash_months: 2,
  has_retirement_account: true,
  employer_match: "not_sure",
  retirement_contribution_percent: 4,
  has_mortgage: false,
  has_student_loans: true,
  has_credit_card_debt: true,
  has_high_interest_debt: true,
  manual_assets: initialManualAssets
};

function BooleanField({
  checked,
  label,
  onChange
}: {
  checked: boolean;
  label: string;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className={optionClass}>
      <input
        checked={checked}
        className="h-4 w-4 accent-croc-moss"
        onChange={(event) => onChange(event.target.checked)}
        suppressHydrationWarning
        type="checkbox"
      />
      {label}
    </label>
  );
}

export function OnboardingFlow() {
  const [profile, setProfile] = useState<OnboardingProfileRequest>(initialProfile);
  const [result, setResult] = useState<OnboardingProfileResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const updateProfile = <TKey extends keyof OnboardingProfileRequest>(
    key: TKey,
    value: OnboardingProfileRequest[TKey]
  ) => {
    setProfile((current) => ({ ...current, [key]: value }));
  };

  const updateManualAsset = (index: number, value: ManualAssetEntry) => {
    setProfile((current) => ({
      ...current,
      manual_assets: current.manual_assets.map((asset, assetIndex) => (assetIndex === index ? value : asset))
    }));
  };

  const addManualAsset = () => {
    setProfile((current) => ({
      ...current,
      manual_assets: [
        ...current.manual_assets,
        { asset_class: "Stocks", label: "New asset", estimated_value: 0 }
      ]
    }));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await submitOnboardingProfile(profile);
      setResult(response);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to create onboarding profile.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell>
      {({ openGuide, openSidebar }) => (
        <div className="mx-auto max-w-[1180px] space-y-5">
          <DashboardHeader
            description="Tell CrocLens your goals, comfort level, accounts, and debts so the app can explain money in the right context."
            onAskClick={openGuide}
            onMenuClick={openSidebar}
            title="Onboarding"
          />

          <form className="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(340px,0.75fr)]" onSubmit={handleSubmit}>
            <div className="space-y-5">
              <Card>
                <SectionTitle
                  eyebrow="Step 1"
                  title="Your investing comfort"
                  action={<Pill tone="green">Beginner mode</Pill>}
                />
                <div className="grid gap-4 md:grid-cols-2">
                  <label>
                    <span className={labelClass}>Experience</span>
                    <select
                      className={fieldClass}
                      onChange={(event) => updateProfile("investment_experience", event.target.value as InvestmentExperience)}
                      suppressHydrationWarning
                      value={profile.investment_experience}
                    >
                      {experienceOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span className={labelClass}>Primary goal</span>
                    <select
                      className={fieldClass}
                      onChange={(event) => updateProfile("primary_goal", event.target.value as PrimaryGoal)}
                      suppressHydrationWarning
                      value={profile.primary_goal}
                    >
                      {goalOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span className={labelClass}>Risk tolerance</span>
                    <select
                      className={fieldClass}
                      onChange={(event) => updateProfile("risk_tolerance", event.target.value as RiskToleranceInput)}
                      suppressHydrationWarning
                      value={profile.risk_tolerance}
                    >
                      {riskOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span className={labelClass}>Time horizon</span>
                    <select
                      className={fieldClass}
                      onChange={(event) => updateProfile("time_horizon", event.target.value as TimeHorizon)}
                      suppressHydrationWarning
                      value={profile.time_horizon}
                    >
                      {horizonOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </label>
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Step 2" title="Cash, retirement, and debt context" />
                <div className="grid gap-4 md:grid-cols-2">
                  <label>
                    <span className={labelClass}>Income range</span>
                    <select
                      className={fieldClass}
                      onChange={(event) => updateProfile("income_range", event.target.value as IncomeRange)}
                      suppressHydrationWarning
                      value={profile.income_range}
                    >
                      {incomeOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span className={labelClass}>Emergency cash months</span>
                    <input
                      className={fieldClass}
                      min={0}
                      max={36}
                      onChange={(event) => updateProfile("emergency_cash_months", Number(event.target.value))}
                      suppressHydrationWarning
                      type="number"
                      value={profile.emergency_cash_months}
                    />
                  </label>

                  <label>
                    <span className={labelClass}>Employer match</span>
                    <select
                      className={fieldClass}
                      onChange={(event) => updateProfile("employer_match", event.target.value as EmployerMatchStatus)}
                      suppressHydrationWarning
                      value={profile.employer_match}
                    >
                      {employerMatchOptions.map((option) => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
                  </label>

                  <label>
                    <span className={labelClass}>Retirement contribution %</span>
                    <input
                      className={fieldClass}
                      min={0}
                      max={100}
                      onChange={(event) => updateProfile("retirement_contribution_percent", Number(event.target.value))}
                      suppressHydrationWarning
                      type="number"
                      value={profile.retirement_contribution_percent ?? 0}
                    />
                  </label>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <BooleanField
                    checked={profile.has_retirement_account}
                    label="I have a retirement account"
                    onChange={(value) => updateProfile("has_retirement_account", value)}
                  />
                  <BooleanField
                    checked={profile.has_mortgage}
                    label="I have a mortgage"
                    onChange={(value) => updateProfile("has_mortgage", value)}
                  />
                  <BooleanField
                    checked={profile.has_student_loans}
                    label="I have student loans"
                    onChange={(value) => updateProfile("has_student_loans", value)}
                  />
                  <BooleanField
                    checked={profile.has_credit_card_debt}
                    label="I have credit card debt"
                    onChange={(value) => updateProfile("has_credit_card_debt", value)}
                  />
                  <BooleanField
                    checked={profile.has_high_interest_debt}
                    label="Some debt is high interest"
                    onChange={(value) => updateProfile("has_high_interest_debt", value)}
                  />
                </div>
              </Card>

              <Card>
                <SectionTitle
                  eyebrow="Step 3"
                  title="Manual asset entry"
                  action={
                    <button
                      className="inline-flex min-h-9 items-center rounded-lg bg-croc-mint px-3 text-sm font-semibold text-croc-moss"
                      onClick={addManualAsset}
                      suppressHydrationWarning
                      type="button"
                    >
                      Add asset
                    </button>
                  }
                />
                <div className="space-y-3">
                  {profile.manual_assets.map((asset, index) => (
                    <div className="grid gap-3 rounded-lg border border-emerald-900/10 bg-croc-cream p-3 md:grid-cols-[1fr_1.4fr_1fr]" key={`${asset.label}-${index}`}>
                      <label>
                        <span className={labelClass}>Class</span>
                        <input
                          className={fieldClass}
                          onChange={(event) => updateManualAsset(index, { ...asset, asset_class: event.target.value })}
                          suppressHydrationWarning
                          value={asset.asset_class}
                        />
                      </label>
                      <label>
                        <span className={labelClass}>Label</span>
                        <input
                          className={fieldClass}
                          onChange={(event) => updateManualAsset(index, { ...asset, label: event.target.value })}
                          suppressHydrationWarning
                          value={asset.label}
                        />
                      </label>
                      <label>
                        <span className={labelClass}>Value</span>
                        <input
                          className={fieldClass}
                          min={0}
                          onChange={(event) => updateManualAsset(index, { ...asset, estimated_value: Number(event.target.value) })}
                          suppressHydrationWarning
                          type="number"
                          value={asset.estimated_value}
                        />
                      </label>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <div className="space-y-5">
              <Card>
                <SectionTitle eyebrow="Profile preview" title="How CrocLens will use this" />
                <div className="space-y-3">
                  {[
                    [ClipboardList, "Personalize explanations", "Beginner mode changes how much context each metric gets."],
                    [ShieldCheck, "Tune risk language", "Risk tolerance and time horizon shape safer educational notes."],
                    [PiggyBank, "Prioritize cash and debt", "Cash months and debt flags help CrocLens order action plans."],
                    [Landmark, "Frame retirement", "Employer match status controls which retirement basics appear first."],
                    [WalletCards, "Seed the dashboard", "Manual assets later become holdings when persistence is added."]
                  ].map(([Icon, title, body]) => {
                    const PreviewIcon = Icon as typeof ClipboardList;
                    return (
                      <div className="flex gap-3 rounded-lg border border-emerald-900/10 bg-white p-3" key={String(title)}>
                        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-croc-mint text-croc-moss">
                          <PreviewIcon className="h-5 w-5" />
                        </span>
                        <div>
                          <p className="text-sm font-semibold text-croc-ink">{String(title)}</p>
                          <p className="mt-1 text-xs leading-5 text-stone-500">{String(body)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                <button
                  className="mt-5 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white transition hover:bg-croc-moss"
                  disabled={isSubmitting}
                  suppressHydrationWarning
                  type="submit"
                >
                  {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                  Create risk profile
                </button>
              </Card>

              {error ? (
                <Card className="border-rose-200 bg-rose-50">
                  <div className="flex gap-3 text-rose-900">
                    <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
                    <p className="text-sm leading-6">{error}</p>
                  </div>
                </Card>
              ) : null}

              {result ? (
                <Card>
                  <SectionTitle
                    eyebrow="Generated profile"
                    title={result.risk_profile}
                    action={<Pill tone="green">{result.confidence} confidence</Pill>}
                  />
                  <div className="rounded-lg bg-croc-cream p-4">
                    <p className="text-4xl font-bold text-croc-ink">{result.risk_score}</p>
                    <p className="mt-1 text-sm text-stone-600">Risk profile score out of 100</p>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-stone-600">{result.summary}</p>

                  <div className="mt-5 space-y-3">
                    <p className="text-sm font-semibold text-croc-ink">Recommended first steps</p>
                    {result.recommended_first_steps.map((step) => (
                      <div className="flex gap-3" key={step}>
                        <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-croc-moss" />
                        <p className="text-sm leading-6 text-stone-600">{step}</p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-5 rounded-lg border border-emerald-900/10 bg-white p-3">
                    <p className="text-xs font-semibold uppercase text-croc-moss">Data limitations</p>
                    <p className="mt-2 text-xs leading-5 text-stone-500">
                      {result.data_limitations.join(" ")} {result.educational_disclaimer}
                    </p>
                  </div>
                </Card>
              ) : null}
            </div>
          </form>
        </div>
      )}
    </AppShell>
  );
}
