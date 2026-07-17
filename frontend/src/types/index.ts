export interface Company {
  id: string;
  symbol: string;
  companyName: string;
  market: string;
  sector: string;
  industry: string;
  description: string;
  website: string;
  logo: string;
  exchange: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
}

export interface FinancialStatement {
  companyId: string;
  period: string;
  incomeStatement: Record<string, number>;
  balanceSheet: Record<string, number>;
  cashFlow: Record<string, number>;
  financialRatios: Record<string, number>;
}

export interface MarketPrice {
  companyId: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface NewsItem {
  id: string;
  companyId: string;
  title: string;
  source: string;
  publishedDate: string;
  url: string;
  summary: string;
  sentiment: "positive" | "negative" | "neutral";
}

export interface Recommendation {
  companyId: string;
  recommendation: "Strong Buy" | "Buy" | "Hold" | "Sell" | "Strong Sell";
  confidence: number;
  explanation: string;
  generatedAt: string;
}

export interface PortfolioHolding {
  userId: string;
  companyId: string;
  quantity: number;
  averagePrice: number;
  company?: Company;
}

export interface WatchlistItem {
  userId: string;
  companyId: string;
  company?: Company;
}

export interface MarketOverview {
  index: string;
  value: number;
  change: number;
  changePercent: number;
  topGainers: Company[];
  topLosers: Company[];
}
