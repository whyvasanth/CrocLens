import Link from "next/link";
import {
  ArrowRight,
  Banknote,
  BarChart3,
  Database,
  LockKeyhole,
  MessageCircle,
  PiggyBank,
  ShieldCheck,
  Sparkles,
  WalletCards
} from "lucide-react";
import { Card, Pill } from "@/components/dashboard/ui";

const benefits = [
  {
    icon: WalletCards,
    title: "One whole-money view",
    body: "Bring investments, cash, retirement, property, and debts into one beginner-friendly dashboard."
  },
  {
    icon: BarChart3,
    title: "Clear data labels",
    body: "Every market surface shows whether data is demo, cached, stale, unavailable, or provider-backed."
  },
  {
    icon: MessageCircle,
    title: "Croc Guide explanations",
    body: "Ask simple questions and get educational summaries with limitations and safe next steps."
  }
];

const categories = [
  "Stocks",
  "ETFs",
  "Crypto",
  "Real estate",
  "Cash",
  "Bonds",
  "Treasuries",
  "401(k) / IRA",
  "Mortgages",
  "Student loans",
  "Credit cards"
];

const previewStats = [
  { label: "Assets", value: "$329.4K", icon: WalletCards },
  { label: "Liabilities", value: "$114.6K", icon: Banknote },
  { label: "Retirement", value: "87% on track", icon: PiggyBank },
  { label: "Data status", value: "Demo data", icon: Database }
];

const faqs = [
  {
    question: "Is CrocLens a financial advisor?",
    answer: "No. CrocLens is educational software. It helps you understand information and questions to review, but it does not tell you what to buy or sell."
  },
  {
    question: "Can I try it without an account?",
    answer: "Yes. Demo Mode uses clearly labeled sample data and stays separate from real user accounts."
  },
  {
    question: "Does CrocLens require paid APIs?",
    answer: "No. The default path uses manual entry, sample data, yfinance, and public free data sources where available."
  }
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-croc-cream">
      <section className="border-b border-emerald-900/10 bg-white/80">
        <div className="mx-auto flex max-w-[1180px] items-center justify-between gap-4 px-4 py-4 md:px-6">
          <Link className="flex items-center gap-3" href="/" aria-label="CrocLens home">
            <span className="grid h-11 w-11 place-items-center rounded-lg bg-croc-lime text-xl font-bold text-white">
              C
            </span>
            <span>
              <span className="block text-lg font-bold text-croc-ink">CrocLens</span>
              <span className="block text-xs text-stone-600">See your money clearly.</span>
            </span>
          </Link>
          <div className="flex items-center gap-2">
            <Link className="hidden min-h-10 items-center rounded-lg px-3 text-sm font-semibold text-croc-moss sm:inline-flex" href="/login">
              Log in
            </Link>
            <Link className="inline-flex min-h-10 items-center rounded-lg bg-croc-emerald px-3 text-sm font-semibold text-white" href="/signup">
              Create free account
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-[1180px] gap-8 px-4 py-12 md:px-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(420px,1.05fr)] lg:items-center lg:py-16">
        <div>
          <Pill tone="green">Beginner-first wealth intelligence</Pill>
          <h1 className="mt-5 max-w-3xl text-4xl font-bold leading-tight text-croc-ink md:text-6xl">
            CrocLens helps you see your money clearly.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-stone-600">
            A calm AI wealth guide for understanding your portfolio, debts, retirement progress, market context, and next review steps without confusing trading jargon.
          </p>
          <div className="mt-7 flex flex-wrap gap-3">
            <Link className="inline-flex min-h-12 items-center gap-2 rounded-lg bg-croc-emerald px-5 text-sm font-semibold text-white shadow-card" href="/dashboard?demo=1">
              Try Demo
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link className="inline-flex min-h-12 items-center rounded-lg border border-emerald-900/10 bg-white px-5 text-sm font-semibold text-croc-moss shadow-card" href="/signup">
              Create Free Account
            </Link>
          </div>
          <p className="mt-5 text-xs leading-5 text-stone-500">
            Educational information only. CrocLens does not provide personalized financial, legal, or tax advice.
          </p>
        </div>

        <Card className="p-0">
          <div className="rounded-t-lg bg-[radial-gradient(circle_at_top_left,#0b7a5c,#052f28_60%,#03231e)] p-5 text-white">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm text-emerald-100">Demo preview</p>
                <p className="mt-2 text-3xl font-bold">$214,800</p>
                <p className="mt-1 text-sm text-emerald-100">Net worth from sample assets and liabilities</p>
              </div>
              <span className="grid h-14 w-14 place-items-center rounded-lg bg-white/10">
                <Sparkles className="h-7 w-7" />
              </span>
            </div>
          </div>
          <div className="grid gap-3 p-5 sm:grid-cols-2">
            {previewStats.map(({ icon: Icon, label, value }) => (
              <div className="rounded-lg border border-emerald-900/10 bg-croc-cream p-4" key={label}>
                <Icon className="h-5 w-5 text-croc-moss" />
                <p className="mt-3 text-sm text-stone-500">{label}</p>
                <p className="mt-1 text-lg font-bold text-croc-ink">{value}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="mx-auto max-w-[1180px] px-4 pb-12 md:px-6">
        <div className="grid gap-4 md:grid-cols-3">
          {benefits.map(({ body, icon: Icon, title }) => (
            <Card key={title}>
              <Icon className="h-6 w-6 text-croc-moss" />
              <h2 className="mt-4 text-lg font-bold text-croc-ink">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-stone-600">{body}</p>
            </Card>
          ))}
        </div>
      </section>

      <section className="border-y border-emerald-900/10 bg-white/75">
        <div className="mx-auto grid max-w-[1180px] gap-8 px-4 py-10 md:px-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <Pill tone="blue">Supported categories</Pill>
            <h2 className="mt-4 text-2xl font-bold text-croc-ink">Designed for a full financial life.</h2>
            <p className="mt-3 text-sm leading-6 text-stone-600">
              Manual entry comes first for private assets, debts, retirement accounts, and cash. Public market data can be layered in with clear freshness labels.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <span className="rounded-lg border border-emerald-900/10 bg-white px-3 py-2 text-sm font-semibold text-croc-ink" key={category}>
                {category}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-[1180px] gap-5 px-4 py-12 md:px-6 lg:grid-cols-2">
        <Card>
          <ShieldCheck className="h-6 w-6 text-croc-moss" />
          <h2 className="mt-4 text-xl font-bold text-croc-ink">Safety-first by design</h2>
          <p className="mt-3 text-sm leading-6 text-stone-600">
            CrocLens uses safe wording, confidence labels, data limitations, and educational disclaimers. It avoids direct buy or sell instructions and does not promise returns.
          </p>
        </Card>
        <Card>
          <LockKeyhole className="h-6 w-6 text-croc-moss" />
          <h2 className="mt-4 text-xl font-bold text-croc-ink">Private by default</h2>
          <p className="mt-3 text-sm leading-6 text-stone-600">
            CrocLens uses secure cookie sessions and password hashing. Demo data is separate from user accounts, and external provider data is labeled when shown.
          </p>
        </Card>
      </section>

      <section className="mx-auto max-w-[900px] px-4 pb-12 md:px-6">
        <h2 className="text-2xl font-bold text-croc-ink">FAQ</h2>
        <div className="mt-5 space-y-3">
          {faqs.map((faq) => (
            <details className="rounded-lg border border-emerald-900/10 bg-white/90 p-4 shadow-card" key={faq.question}>
              <summary className="cursor-pointer font-semibold text-croc-ink">{faq.question}</summary>
              <p className="mt-3 text-sm leading-6 text-stone-600">{faq.answer}</p>
            </details>
          ))}
        </div>
      </section>

      <footer className="border-t border-emerald-900/10 bg-white/80">
        <div className="mx-auto flex max-w-[1180px] flex-col gap-4 px-4 py-6 text-sm text-stone-600 md:flex-row md:items-center md:justify-between md:px-6">
          <p>CrocLens · See your money clearly.</p>
          <div className="flex flex-wrap gap-4">
            <a className="font-semibold text-croc-moss" href="https://github.com/whyvasanth/CrocLens">GitHub</a>
            <Link className="font-semibold text-croc-moss" href="/market-news">Data Sources</Link>
            <Link className="font-semibold text-croc-moss" href="/settings">Privacy</Link>
            <span>Educational, not financial advice.</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
