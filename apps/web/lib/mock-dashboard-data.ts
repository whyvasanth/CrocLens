import {
  BarChart3,
  Bell,
  ClipboardCheck,
  ChartPie,
  CircleDollarSign,
  Home,
  Landmark,
  LineChart,
  Newspaper,
  NotebookPen,
  PiggyBank,
  Settings,
  ShieldCheck,
  Sparkles,
  UserRound,
  WalletCards
} from "lucide-react";
import type {
  ActionItem,
  AllocationPoint,
  ChatMessage,
  ComparisonAsset,
  GuideInsight,
  MarketSnapshotItem,
  MetricCard,
  PortfolioHistoryPoint,
  ScoreItem,
  SidebarItem
} from "@/types/dashboard";

export const sidebarItems: SidebarItem[] = [
  { label: "Dashboard", href: "/dashboard", icon: Home },
  { label: "Onboarding", href: "/onboarding", icon: UserRound },
  { label: "Portfolio", href: "/portfolio", icon: WalletCards },
  { label: "Compare Assets", href: "/compare-assets", icon: ChartPie },
  { label: "Market News", href: "/market-news", icon: Newspaper },
  { label: "Watchlist", href: "/watchlist", icon: Bell },
  { label: "Action Plans", href: "/action-plans", icon: Sparkles },
  { label: "Journal", href: "/journal", icon: NotebookPen },
  { label: "Retirement", href: "/retirement", icon: PiggyBank },
  { label: "Tax Planner", href: "/tax-planner", icon: ShieldCheck },
  { label: "Metrics", href: "/evaluation-metrics", icon: ClipboardCheck },
  { label: "Settings", href: "/settings", icon: Settings }
];

export const metricCards: MetricCard[] = [
  {
    label: "Net worth",
    value: "$214.8K",
    helper: "Assets minus liabilities",
    trend: "+$4.2K this month",
    direction: "up"
  },
  {
    label: "Total assets",
    value: "$329.4K",
    helper: "Investments, cash, home equity",
    trend: "+2.1% this month",
    direction: "up"
  },
  {
    label: "Total debt",
    value: "$114.6K",
    helper: "Mortgage, loans, cards",
    trend: "-$740 paid down",
    direction: "down"
  }
];

export const portfolioHistory: PortfolioHistoryPoint[] = [
  { month: "Jan", value: 184000 },
  { month: "Feb", value: 188500 },
  { month: "Mar", value: 194000 },
  { month: "Apr", value: 202800 },
  { month: "May", value: 207100 },
  { month: "Jun", value: 214800 }
];

export const allocationData: AllocationPoint[] = [
  { name: "Stocks", value: 29, color: "#0d5c49" },
  { name: "ETFs", value: 24, color: "#7bb7f0" },
  { name: "Real Estate", value: 22, color: "#f6c85f" },
  { name: "Retirement", value: 13, color: "#a8e6b1" },
  { name: "Cash", value: 7, color: "#7d8b86" },
  { name: "Crypto", value: 5, color: "#ee7b72" }
];

export const marketSnapshot: MarketSnapshotItem[] = [
  {
    label: "S&P 500",
    value: "5,297.10",
    change: "+0.84%",
    note: "Broad stocks are slightly higher",
    direction: "up"
  },
  {
    label: "NASDAQ",
    value: "16,688.88",
    change: "+1.25%",
    note: "Tech-heavy stocks are leading today",
    direction: "up"
  },
  {
    label: "Bitcoin",
    value: "$66,421.35",
    change: "-1.90%",
    note: "Crypto is moving more than stocks",
    direction: "down"
  },
  {
    label: "10Y Treasury",
    value: "4.18%",
    change: "Flat",
    note: "Rates affect bonds and mortgages",
    direction: "flat"
  }
];

export const actionItems: ActionItem[] = [
  {
    title: "Review emergency cash target",
    body: "Completed after comparing cash with three months of core expenses.",
    priority: "High",
    isDone: true
  },
  {
    title: "Compare debt interest rates",
    body: "Consider reviewing credit card APR against student loan and mortgage rates.",
    priority: "Medium",
    isDone: false
  },
  {
    title: "Revisit target allocation",
    body: "Your portfolio is diversified, but tech exposure may deserve a beginner-friendly review.",
    priority: "Low",
    isDone: false
  }
];

export const scoreItems: ScoreItem[] = [
  {
    label: "Risk",
    value: 64,
    description: "Moderate because stocks and crypto move more than cash or bonds."
  },
  {
    label: "Liquidity",
    value: 72,
    description: "Healthy because cash and tradable funds are available if needed."
  },
  {
    label: "Diversification",
    value: 78,
    description: "Good mix across public markets, cash, and real estate."
  }
];

export const crocMessages: ChatMessage[] = [
  {
    speaker: "Croc Guide",
    message:
      "Your dashboard looks balanced overall. The main beginner watch-out is high-interest debt versus your cash goals."
  },
  {
    speaker: "You",
    message: "How does the market move affect me?"
  },
  {
    speaker: "Croc Guide",
    message:
      "Based on sample data, broad stock moves matter more to you than crypto today because stocks and ETFs are a larger share."
  }
];

export const comparisonAssets: ComparisonAsset[] = [
  {
    symbol: "VOO",
    name: "S&P 500 ETF",
    price: "$486.20",
    change: "+0.84%",
    direction: "up",
    sparkline: [41, 44, 43, 48, 47, 51, 55, 54, 58]
  },
  {
    symbol: "VTI",
    name: "Total Market ETF",
    price: "$261.81",
    change: "+0.62%",
    direction: "up",
    sparkline: [38, 39, 41, 40, 45, 44, 46, 49, 52]
  },
  {
    symbol: "BTC",
    name: "Bitcoin",
    price: "$66,421",
    change: "-1.90%",
    direction: "down",
    sparkline: [70, 68, 66, 69, 63, 62, 60, 58, 56]
  },
  {
    symbol: "AGG",
    name: "Bond ETF",
    price: "$97.66",
    change: "+0.21%",
    direction: "flat",
    sparkline: [31, 32, 31, 33, 32, 34, 33, 35, 36]
  }
];

export const guideInsights: GuideInsight[] = [
  {
    title: "Croc Insight",
    body: "Your portfolio is diversified across several asset classes.",
    tone: "green"
  },
  {
    title: "Smart Move",
    body: "Consider comparing bond exposure with your time horizon.",
    tone: "gold"
  },
  {
    title: "Croc Alert",
    body: "Volatility is rising. Keep an eye on tech concentration.",
    tone: "blue"
  }
];

export const retirementProgress = {
  current: 42000,
  goal: 52000,
  matchStatus: "On track for estimated employer match",
  contributionRate: "8%"
};

export const sourceFreshness = {
  label: "Sample data",
  detail: "Static mock dataset for Phase 1"
};

export const portfolioSummary = {
  userName: "Maya",
  riskProfile: "Balanced beginner",
  householdTag: "Whole-wealth view",
  confidence: "Medium",
  limitation:
    "This dashboard uses mock data. It is educational and not financial advice.",
  featuredMetricIcon: CircleDollarSign,
  chartIcon: LineChart,
  marketIcon: BarChart3,
  retirementIcon: Landmark
};
