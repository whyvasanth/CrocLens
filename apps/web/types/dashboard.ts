import type { LucideIcon } from "lucide-react";

export type AssetClass =
  | "Stocks"
  | "ETFs"
  | "Crypto"
  | "Real Estate"
  | "Cash"
  | "Bonds"
  | "Retirement"
  | "Debt";

export type TrendDirection = "up" | "down" | "flat";

export interface SidebarItem {
  label: string;
  href: string;
  icon: LucideIcon;
  isActive?: boolean;
}

export interface MetricCard {
  label: string;
  value: string;
  helper: string;
  trend: string;
  direction: TrendDirection;
}

export interface AllocationPoint {
  name: AssetClass;
  value: number;
  color: string;
}

export interface MarketSnapshotItem {
  label: string;
  value: string;
  change: string;
  note: string;
  direction: TrendDirection;
}

export interface ActionItem {
  title: string;
  body: string;
  priority: "High" | "Medium" | "Low";
  isDone?: boolean;
}

export interface ScoreItem {
  label: string;
  value: number;
  description: string;
}

export interface PortfolioHistoryPoint {
  month: string;
  value: number;
}

export interface ChatMessage {
  speaker: "Croc Guide" | "You";
  message: string;
}

export interface ComparisonAsset {
  symbol: string;
  name: string;
  price: string;
  change: string;
  direction: TrendDirection;
  sparkline: number[];
}

export interface GuideInsight {
  title: string;
  body: string;
  tone: "green" | "gold" | "blue";
}
