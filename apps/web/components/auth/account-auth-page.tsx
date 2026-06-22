"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ArrowRight, CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { Card, Pill, SectionTitle } from "@/components/dashboard/ui";
import { createAccount, loginAccount } from "@/lib/api-client";
import type {
  AccountSessionResponse,
  EmployerMatchStatus,
  IncomeRange,
  InvestmentExperience,
  ManualAssetEntry,
  OnboardingProfileRequest,
  PrimaryGoal,
  RiskToleranceInput,
  TimeHorizon
} from "@/types/api";

const fieldClass =
  "min-h-11 w-full rounded-lg border border-emerald-900/10 bg-white px-3 text-sm text-croc-ink outline-none transition focus:border-croc-moss";
const labelClass = "mb-2 block text-sm font-semibold text-croc-ink";
const optionClass =
  "flex min-h-11 items-center gap-3 rounded-lg border border-emerald-900/10 bg-white px-3 text-sm font-semibold text-croc-ink";

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
  manual_assets: []
};

interface AccountAuthPageProps {
  mode: "login" | "signup";
}

function saveSession(session: AccountSessionResponse) {
  window.localStorage.setItem(
    "croclens_session",
    JSON.stringify({
      token: session.session_token,
      user: session.user,
      saved_at: new Date().toISOString()
    })
  );
}

export function AccountAuthPage({ mode }: AccountAuthPageProps) {
  const router = useRouter();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [profile, setProfile] = useState<OnboardingProfileRequest>(initialProfile);
  const [session, setSession] = useState<AccountSessionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isSignup = mode === "signup";

  const updateProfile = <TKey extends keyof OnboardingProfileRequest>(
    key: TKey,
    value: OnboardingProfileRequest[TKey]
  ) => setProfile((current) => ({ ...current, [key]: value }));

  const updateManualAsset = (index: number, value: ManualAssetEntry) => {
    setProfile((current) => ({
      ...current,
      manual_assets: current.manual_assets.map((asset, assetIndex) => (assetIndex === index ? value : asset))
    }));
  };

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = isSignup
        ? await createAccount({
            display_name: displayName,
            email,
            password,
            onboarding_profile: profile
          })
        : await loginAccount({ email, password });

      saveSession(response);
      setSession(response);

      if (!isSignup) {
        router.push(response.next_path);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "CrocLens could not complete this account step.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen bg-croc-cream px-4 py-6 md:px-6">
      <div className="mx-auto grid max-w-[1180px] gap-5 lg:grid-cols-[minmax(0,0.95fr)_minmax(440px,1.05fr)]">
        <section className="rounded-lg bg-[radial-gradient(circle_at_top_left,#0b7a5c,#052f28_60%,#03231e)] p-6 text-white shadow-card">
          <Link href="/dashboard" className="flex items-center gap-3" aria-label="CrocLens dashboard">
            <span className="grid h-12 w-12 place-items-center rounded-lg bg-croc-lime text-2xl font-bold text-white">
              C
            </span>
            <span>
              <span className="block text-2xl font-bold">CrocLens</span>
              <span className="block text-sm text-emerald-100">See your money clearly.</span>
            </span>
          </Link>

          <div className="mt-12 max-w-md">
            <Pill tone="green">{isSignup ? "Create account" : "Welcome back"}</Pill>
            <h1 className="mt-5 text-4xl font-bold leading-tight">
              {isSignup ? "Build your beginner wealth profile as you sign up." : "Log in to your CrocLens dashboard."}
            </h1>
            <p className="mt-4 text-sm leading-6 text-emerald-50">
              {isSignup
                ? "CrocLens collects goals, risk comfort, retirement context, debt, and manual assets during account creation so there is no separate onboarding page."
                : "This MVP login uses persisted local authentication. Production auth will add Cognito, email verification, password reset, and secure cookie sessions."}
            </p>
          </div>

          <div className="mt-8 space-y-3">
            {[
              "Beginner mode is enabled by default.",
              "Account setup includes risk profile context.",
              "This is educational software, not financial advice.",
              "No paid auth provider is required for local development."
            ].map((item) => (
              <div className="flex gap-3 rounded-lg border border-white/10 bg-white/10 p-3" key={item}>
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-200" />
                <p className="text-sm leading-6 text-emerald-50">{item}</p>
              </div>
            ))}
          </div>
        </section>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <Card>
            <SectionTitle
              eyebrow={isSignup ? "Account" : "Login"}
              title={isSignup ? "Create your account" : "Log in"}
              action={<Pill tone="blue">Local auth</Pill>}
            />
            <div className="grid gap-4 md:grid-cols-2">
              {isSignup ? (
                <label className="md:col-span-2">
                  <span className={labelClass}>Name</span>
                  <input
                    className={fieldClass}
                    onChange={(event) => setDisplayName(event.target.value)}
                    suppressHydrationWarning
                    value={displayName}
                  />
                </label>
              ) : null}
              <label>
                <span className={labelClass}>Email</span>
                <input
                  className={fieldClass}
                  onChange={(event) => setEmail(event.target.value)}
                  suppressHydrationWarning
                  type="email"
                  value={email}
                />
              </label>
              <label>
                <span className={labelClass}>Password</span>
                <input
                  className={fieldClass}
                  onChange={(event) => setPassword(event.target.value)}
                  suppressHydrationWarning
                  type="password"
                  value={password}
                />
              </label>
            </div>
          </Card>

          {isSignup ? (
            <>
              <Card>
                <SectionTitle eyebrow="Profile" title="Goals and investing comfort" />
                <div className="grid gap-4 md:grid-cols-2">
                  <SelectField
                    label="Experience"
                    value={profile.investment_experience}
                    onChange={(value) => updateProfile("investment_experience", value as InvestmentExperience)}
                    options={[
                      ["new", "New to investing"],
                      ["some", "I know some basics"],
                      ["experienced", "Comfortable with investing"]
                    ]}
                  />
                  <SelectField
                    label="Primary goal"
                    value={profile.primary_goal}
                    onChange={(value) => updateProfile("primary_goal", value as PrimaryGoal)}
                    options={[
                      ["learn", "Learn money basics"],
                      ["build_wealth", "Build wealth"],
                      ["retirement", "Plan for retirement"],
                      ["debt_payoff", "Pay down debt"],
                      ["home", "Buy a home"],
                      ["emergency_fund", "Build emergency fund"]
                    ]}
                  />
                  <SelectField
                    label="Risk tolerance"
                    value={profile.risk_tolerance}
                    onChange={(value) => updateProfile("risk_tolerance", value as RiskToleranceInput)}
                    options={[
                      ["low", "Low"],
                      ["medium", "Medium"],
                      ["high", "High"]
                    ]}
                  />
                  <SelectField
                    label="Time horizon"
                    value={profile.time_horizon}
                    onChange={(value) => updateProfile("time_horizon", value as TimeHorizon)}
                    options={[
                      ["short", "Less than 3 years"],
                      ["medium", "3 to 10 years"],
                      ["long", "10+ years"]
                    ]}
                  />
                </div>
              </Card>

              <Card>
                <SectionTitle eyebrow="Money context" title="Cash, retirement, and debt" />
                <div className="grid gap-4 md:grid-cols-2">
                  <SelectField
                    label="Income range"
                    value={profile.income_range}
                    onChange={(value) => updateProfile("income_range", value as IncomeRange)}
                    options={[
                      ["under_50k", "Under $50k"],
                      ["50k_100k", "$50k to $100k"],
                      ["100k_200k", "$100k to $200k"],
                      ["over_200k", "Over $200k"],
                      ["prefer_not", "Prefer not to say"]
                    ]}
                  />
                  <NumberField
                    label="Emergency cash months"
                    max={36}
                    value={profile.emergency_cash_months}
                    onChange={(value) => updateProfile("emergency_cash_months", value)}
                  />
                  <SelectField
                    label="Employer match"
                    value={profile.employer_match}
                    onChange={(value) => updateProfile("employer_match", value as EmployerMatchStatus)}
                    options={[
                      ["yes", "Yes"],
                      ["no", "No"],
                      ["not_sure", "Not sure"],
                      ["not_applicable", "Not applicable"]
                    ]}
                  />
                  <NumberField
                    label="Retirement contribution %"
                    max={100}
                    value={profile.retirement_contribution_percent ?? 0}
                    onChange={(value) => updateProfile("retirement_contribution_percent", value)}
                  />
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  <BooleanField checked={profile.has_retirement_account} label="I have a retirement account" onChange={(value) => updateProfile("has_retirement_account", value)} />
                  <BooleanField checked={profile.has_mortgage} label="I have a mortgage" onChange={(value) => updateProfile("has_mortgage", value)} />
                  <BooleanField checked={profile.has_student_loans} label="I have student loans" onChange={(value) => updateProfile("has_student_loans", value)} />
                  <BooleanField checked={profile.has_credit_card_debt} label="I have credit card debt" onChange={(value) => updateProfile("has_credit_card_debt", value)} />
                  <BooleanField checked={profile.has_high_interest_debt} label="Some debt is high interest" onChange={(value) => updateProfile("has_high_interest_debt", value)} />
                </div>
              </Card>

              <Card>
                <SectionTitle
                  eyebrow="Manual assets"
                  title="Seed your first dashboard"
                  action={
                    <button
                      className="inline-flex min-h-9 items-center rounded-lg bg-croc-mint px-3 text-sm font-semibold text-croc-moss"
                      onClick={() =>
                        updateProfile("manual_assets", [
                          ...profile.manual_assets,
                          { asset_class: "Stocks", label: "New asset", estimated_value: 0 }
                        ])
                      }
                      suppressHydrationWarning
                      type="button"
                    >
                      Add asset
                    </button>
                  }
                />
                <div className="space-y-3">
                  {profile.manual_assets.map((asset, index) => (
                    <div className="grid gap-3 rounded-lg bg-croc-cream p-3 md:grid-cols-[1fr_1.4fr_1fr]" key={`${asset.label}-${index}`}>
                      <TextField label="Class" value={asset.asset_class} onChange={(value) => updateManualAsset(index, { ...asset, asset_class: value })} />
                      <TextField label="Label" value={asset.label} onChange={(value) => updateManualAsset(index, { ...asset, label: value })} />
                      <NumberField label="Value" value={asset.estimated_value} onChange={(value) => updateManualAsset(index, { ...asset, estimated_value: value })} />
                    </div>
                  ))}
                </div>
              </Card>
            </>
          ) : null}

          {error ? <p className="rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">{error}</p> : null}

          {session?.onboarding_profile ? (
            <Card>
              <SectionTitle
                eyebrow="Profile created"
                title={session.onboarding_profile.risk_profile}
                action={<Pill tone="green">{session.onboarding_profile.confidence} confidence</Pill>}
              />
              <p className="text-sm leading-6 text-stone-600">{session.onboarding_profile.summary}</p>
              <button
                className="mt-4 inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white"
                onClick={() => router.push(session.next_path)}
                suppressHydrationWarning
                type="button"
              >
                Go to dashboard
                <ArrowRight className="h-4 w-4" />
              </button>
            </Card>
          ) : null}

          <Card>
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div className="flex gap-3">
                <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-croc-moss" />
                <p className="text-sm leading-6 text-stone-600">
                  Local account flow for development. Production will use Cognito, verified tokens, and secure cookie sessions.
                </p>
              </div>
              <button
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-croc-emerald px-4 text-sm font-semibold text-white transition hover:bg-croc-moss"
                disabled={isSubmitting}
                suppressHydrationWarning
                type="submit"
              >
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
                {isSignup ? "Create account" : "Log in"}
              </button>
            </div>
            <p className="mt-4 text-sm text-stone-600">
              {isSignup ? (
                <>
                  Already have an account? <Link className="font-semibold text-croc-moss" href="/login">Log in</Link>
                </>
              ) : (
                <>
                  New to CrocLens? <Link className="font-semibold text-croc-moss" href="/signup">Create account</Link>
                </>
              )}
            </p>
          </Card>
        </form>
      </div>
    </main>
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
  options: Array<[string, string]>;
  value: string;
}) {
  return (
    <label>
      <span className={labelClass}>{label}</span>
      <select className={fieldClass} onChange={(event) => onChange(event.target.value)} suppressHydrationWarning value={value}>
        {options.map(([optionValue, optionLabel]) => (
          <option key={optionValue} value={optionValue}>{optionLabel}</option>
        ))}
      </select>
    </label>
  );
}

function TextField({ label, onChange, value }: { label: string; onChange: (value: string) => void; value: string }) {
  return (
    <label>
      <span className={labelClass}>{label}</span>
      <input className={fieldClass} onChange={(event) => onChange(event.target.value)} suppressHydrationWarning value={value} />
    </label>
  );
}

function NumberField({
  label,
  max,
  onChange,
  value
}: {
  label: string;
  max?: number;
  onChange: (value: number) => void;
  value: number;
}) {
  return (
    <label>
      <span className={labelClass}>{label}</span>
      <input
        className={fieldClass}
        max={max}
        min={0}
        onChange={(event) => onChange(Number(event.target.value))}
        suppressHydrationWarning
        type="number"
        value={value}
      />
    </label>
  );
}

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
