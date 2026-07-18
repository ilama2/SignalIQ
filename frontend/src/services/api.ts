const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";

/* =========================================================
   Recommendations
========================================================= */

export interface Recommendation {
  symbol: string;
  company_name: string;
  final_score: number;
  recommendation: string;
  confidence: number;

  current_price?: number | null;
  currency?: string;
  summary?: string;
}

export interface RecommendationsResponse {
  count: number;
  recommendations: Recommendation[];
}

/* =========================================================
   Companies List
========================================================= */

export interface CompanyListItem {
  symbol: string;
  company_name: string;
  company_name_en?: string | null;

  exchange?: string | null;
  sector?: string | null;

  current_price?: number | null;
  change?: number | null;
  change_percent?: number | null;

  volume?: number | null;
  trading_value?: number | null;

  recommendation?: string | null;
  final_score?: number | null;
  confidence?: number | null;

  updated_at?: string | null;
  is_delayed?: boolean;

  currency?: string;
}

export interface CompaniesResponse {
  count: number;
  companies: CompanyListItem[];
}

/* =========================================================
   Company Details
========================================================= */

export interface CompanyLiquidity {
  inflow_value?: number | null;
  inflow_volume?: number | null;
  inflow_trades?: number | null;

  outflow_value?: number | null;
  outflow_volume?: number | null;
  outflow_trades?: number | null;

  net_value?: number | null;
}

export interface CompanyNews {
  id?: string;
  title: string;
  source?: string;
  published_date?: string;
  url?: string;
  sentiment?: string;
}

export interface CompanyDetailsResponse {
  symbol: string;
  company_name: string;
  company_name_en?: string | null;

  exchange?: string | null;
  sector?: string | null;
  industry?: string | null;
  website?: string | null;
  description?: string | null;
  employees?: number | null;

  current_price?: number | null;
  change?: number | null;
  change_percent?: number | null;

  open?: number | null;
  high?: number | null;
  low?: number | null;
  previous_close?: number | null;

  volume?: number | null;
  trading_value?: number | null;

  bid?: number | null;
  ask?: number | null;
  bid_size?: number | null;
  ask_size?: number | null;

  liquidity?: CompanyLiquidity;

  market_cap?: number | null;
  pe_ratio?: number | null;
  pb_ratio?: number | null;
  dividend_yield?: number | null;

  final_score?: number | null;
  recommendation?: string | null;
  confidence?: number | null;

  summary?: string | null;
  strengths?: string[];
  risks?: string[];

  news?: CompanyNews[];

  updated_at?: string | null;
  is_delayed?: boolean;

  currency?: string;
}
/* =========================================================
   News
========================================================= */

export interface NewsItem {
    id: string;
  
    symbol?: string | null;
    company_name?: string | null;
  
    title: string;
    source?: string | null;
    published_date?: string | null;
    url?: string | null;
    sentiment?: string | null;
  }
  
  export interface NewsResponse {
    count: number;
    news: NewsItem[];
  }

/* =========================================================
   Shared Fetch Function
========================================================= */

async function fetchApi<T>(
  endpoint: string,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${endpoint}`,
    {
      headers: {
        Accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    let errorMessage =
      `حدث خطأ أثناء تحميل البيانات. رمز الخطأ: ${response.status}`;

    try {
      const errorData =
        (await response.json()) as {
          detail?: string;
          message?: string;
        };

      if (errorData.detail) {
        errorMessage = errorData.detail;
      } else if (errorData.message) {
        errorMessage = errorData.message;
      }
    } catch {
      // The server response was not JSON.
    }

    throw new Error(errorMessage);
  }

  return (await response.json()) as T;
}

/* =========================================================
   API Functions
========================================================= */

export function getRecommendations():
  Promise<RecommendationsResponse> {
  return fetchApi<RecommendationsResponse>(
    "/api/recommendations",
  );
}

export function getCompanies():
  Promise<CompaniesResponse> {
  return fetchApi<CompaniesResponse>(
    "/api/companies",
  );
}

export function getCompanyDetails(
  symbol: string,
): Promise<CompanyDetailsResponse> {
  return fetchApi<CompanyDetailsResponse>(
    `/api/companies/${encodeURIComponent(symbol)}`,
  );
}

export function getNews(
    limit = 20,
  ): Promise<NewsResponse> {
    const safeLimit = Math.max(
      1,
      Math.min(
        100,
        Math.trunc(limit),
      ),
    );
  
    return fetchApi<NewsResponse>(
      `/api/news?limit=${safeLimit}`,
    );
  }