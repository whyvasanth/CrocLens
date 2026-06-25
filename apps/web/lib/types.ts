export interface PricePoint {
  date: string;
  close: number;
}

export interface QuoteResponse {
  symbol: string;
  name: string;
  price: number;
  previous_close: number | null;
  change: number | null;
  change_percent: number | null;
  currency: string;
  day_high: number | null;
  day_low: number | null;
  volume: number | null;
  market_cap: number | null;
  data_as_of: string;
  retrieved_at: string;
  provider: string;
  is_sample_data: boolean;
  data_quality: string;
  data_limitations: string[];
  beginner_explanation: string;
  educational_disclaimer: string;
}

export interface MarketHistoryResponse {
  symbol: string;
  period: string;
  points: PricePoint[];
  provider: string;
  is_sample_data: boolean;
  data_quality: string;
  data_limitations: string[];
  educational_disclaimer: string;
}

export interface DemoHolding {
  symbol: string;
  name: string;
  quantity: number;
  latest_price: number;
  market_value: number;
  allocation_percent: number;
  note: string;
}

export interface DemoPortfolioResponse {
  holdings: DemoHolding[];
  total_value: number;
  is_sample_data: boolean;
  data_quality: string;
  educational_disclaimer: string;
}

export interface GuideResponse {
  symbol: string;
  summary: string;
  observations: string[];
  considerations: string[];
  data_limitations: string[];
  educational_disclaimer: string;
}
