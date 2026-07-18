import { useEffect, useMemo, useState } from "react";

import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/Card";

import { StatCard } from "@/components/ui/StatCard";
import { Badge } from "@/components/ui/Badge";
import { StockPrice } from "@/components/ui/StockPrice";

import {
  getCompanies,
  getRecommendations,
  type CompanyListItem,
  type Recommendation,
} from "@/services/api";

export function Dashboard() {
  const [companies, setCompanies] = useState<
    CompanyListItem[]
  >([]);

  const [recommendations, setRecommendations] =
    useState<Recommendation[]>([]);

  const [isLoading, setIsLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  async function loadDashboard() {
    try {
      setIsLoading(true);
      setError(null);

      const [
        companiesResponse,
        recommendationsResponse,
      ] = await Promise.all([
        getCompanies(),
        getRecommendations(),
      ]);

      setCompanies(
        companiesResponse.companies ?? [],
      );

      setRecommendations(
        recommendationsResponse.recommendations ??
          [],
      );
    } catch (requestError) {
      const message =
        requestError instanceof Error
          ? requestError.message
          : "تعذر تحميل بيانات لوحة التحكم.";

      setError(message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboard();
  }, []);

  const totalVolume = useMemo(() => {
    return companies.reduce(
      (total, company) =>
        total + (company.volume ?? 0),
      0,
    );
  }, [companies]);

  const sortedByChange = useMemo(() => {
    return [...companies].sort(
      (firstCompany, secondCompany) =>
        (secondCompany.change_percent ?? 0) -
        (firstCompany.change_percent ?? 0),
    );
  }, [companies]);

  const topGainer =
    sortedByChange.length > 0
      ? sortedByChange[0]
      : null;

  const topLoser =
    sortedByChange.length > 0
      ? sortedByChange[
          sortedByChange.length - 1
        ]
      : null;

  const marketMovers = useMemo(() => {
    return [...companies]
      .sort(
        (firstCompany, secondCompany) =>
          Math.abs(
            secondCompany.change_percent ?? 0,
          ) -
          Math.abs(
            firstCompany.change_percent ?? 0,
          ),
      )
      .slice(0, 5);
  }, [companies]);

  const topRecommendations = useMemo(() => {
    return [...recommendations]
      .sort(
        (firstRecommendation, secondRecommendation) =>
          (secondRecommendation.final_score ??
            0) -
          (firstRecommendation.final_score ??
            0),
      )
      .slice(0, 4);
  }, [recommendations]);

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (error) {
    return (
      <div className="flex min-h-[420px] items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent>
            <div className="py-8 text-center">
              <h2 className="text-lg font-semibold text-text-primary">
                تعذر تحميل لوحة التحكم
              </h2>

              <p className="mt-2 text-sm text-text-secondary">
                {error}
              </p>

              <button
                type="button"
                onClick={() =>
                  void loadDashboard()
                }
                className="mt-5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition hover:opacity-90"
              >
                إعادة المحاولة
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Dashboard
        </h1>

        <p className="text-sm text-text-secondary">
          Market overview and AI investment
          insights
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          label="Tracked Companies"
          value={formatNumber(
            companies.length,
          )}
          change={0}
        />

        <StatCard
          label="Total Volume"
          value={formatCompactNumber(
            totalVolume,
          )}
          change={0}
        />

        <StatCard
          label="Top Gainer"
          value={
            topGainer?.company_name ??
            "غير متوفر"
          }
          change={
            topGainer?.change_percent ?? 0
          }
        />

        <StatCard
          label="Top Loser"
          value={
            topLoser?.company_name ??
            "غير متوفر"
          }
          change={
            topLoser?.change_percent ?? 0
          }
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>
              Market Movers
            </CardTitle>
          </CardHeader>

          <CardContent>
            {marketMovers.length === 0 ? (
              <EmptyState message="لا توجد بيانات شركات متاحة." />
            ) : (
              <div className="space-y-3">
                {marketMovers.map(
                  (company) => (
                    <div
                      key={company.symbol}
                      className="flex items-center justify-between rounded-lg border border-border p-3"
                    >
                      <div className="flex min-w-0 items-center gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                          {company.symbol.slice(
                            0,
                            2,
                          )}
                        </div>

                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-text-primary">
                            {
                              company.company_name
                            }
                          </p>

                          <p className="text-xs text-text-muted">
                            {company.symbol}
                          </p>
                        </div>
                      </div>

                      <StockPrice
                        price={
                          company.current_price ??
                          0
                        }
                        change={
                          company.change ?? 0
                        }
                        changePercent={
                          company.change_percent ??
                          0
                        }
                        size="sm"
                      />
                    </div>
                  ),
                )}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Top AI Recommendations
            </CardTitle>
          </CardHeader>

          <CardContent>
            {topRecommendations.length ===
            0 ? (
              <EmptyState message="لا توجد توصيات استثمارية متاحة." />
            ) : (
              <div className="space-y-3">
                {topRecommendations.map(
                  (recommendation) => (
                    <div
                      key={
                        recommendation.symbol
                      }
                      className="rounded-lg border border-border p-3"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-text-primary">
                            {
                              recommendation.company_name
                            }
                          </p>

                          <p className="mt-1 text-xs text-text-muted">
                            {
                              recommendation.symbol
                            }
                            {" · "}
                            Score:{" "}
                            {formatScore(
                              recommendation.final_score,
                            )}
                          </p>
                        </div>

                        <Badge
                          variant={getRecommendationVariant(
                            recommendation.recommendation,
                          )}
                        >
                          {translateRecommendation(
                            recommendation.recommendation,
                          )}
                        </Badge>
                      </div>

                      <div className="mt-3 flex items-center justify-between text-xs">
                        <span className="text-text-muted">
                          Confidence
                        </span>

                        <span className="font-medium text-text-primary">
                          {formatConfidence(
                            recommendation.confidence,
                          )}
                        </span>
                      </div>

                      {recommendation.summary && (
                        <p className="mt-2 line-clamp-2 text-xs leading-5 text-text-secondary">
                          {
                            recommendation.summary
                          }
                        </p>
                      )}
                    </div>
                  ),
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div>
        <div className="h-8 w-40 animate-pulse rounded bg-surface-hover" />
        <div className="mt-2 h-4 w-64 animate-pulse rounded bg-surface-hover" />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({
          length: 4,
        }).map((_, index) => (
          <div
            key={index}
            className="h-28 animate-pulse rounded-xl border border-border bg-surface-hover"
          />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {Array.from({
          length: 2,
        }).map((_, index) => (
          <div
            key={index}
            className="h-96 animate-pulse rounded-xl border border-border bg-surface-hover"
          />
        ))}
      </div>
    </div>
  );
}

function EmptyState({
  message,
}: {
  message: string;
}) {
  return (
    <div className="flex min-h-48 items-center justify-center rounded-lg border border-dashed border-border">
      <p className="text-sm text-text-muted">
        {message}
      </p>
    </div>
  );
}

function formatNumber(
  value: number,
): string {
  return new Intl.NumberFormat(
    "en-US",
  ).format(value);
}

function formatCompactNumber(
  value: number,
): string {
  if (!Number.isFinite(value)) {
    return "0";
  }

  return new Intl.NumberFormat(
    "en-US",
    {
      notation: "compact",
      maximumFractionDigits: 1,
    },
  ).format(value);
}

function formatScore(
  score: number | null | undefined,
): string {
  if (
    score === null ||
    score === undefined ||
    !Number.isFinite(score)
  ) {
    return "N/A";
  }

  return `${score.toFixed(1)}/100`;
}

function formatConfidence(
  confidence: number | null | undefined,
): string {
  if (
    confidence === null ||
    confidence === undefined ||
    !Number.isFinite(confidence)
  ) {
    return "N/A";
  }

  const normalizedConfidence =
    confidence <= 1
      ? confidence * 100
      : confidence;

  return `${normalizedConfidence.toFixed(
    0,
  )}%`;
}

function translateRecommendation(
  recommendation:
    | string
    | null
    | undefined,
): string {
  const normalized =
    recommendation
      ?.trim()
      .toLowerCase() ?? "";

  if (
    normalized === "strong buy" ||
    normalized === "strong_buy"
  ) {
    return "شراء قوي";
  }

  if (normalized === "buy") {
    return "شراء";
  }

  if (normalized === "hold") {
    return "احتفاظ";
  }

  if (normalized === "sell") {
    return "بيع";
  }

  if (
    normalized === "strong sell" ||
    normalized === "strong_sell"
  ) {
    return "بيع قوي";
  }

  return recommendation || "غير متوفر";
}

function getRecommendationVariant(
  recommendation:
    | string
    | null
    | undefined,
): "gain" | "loss" | "default" {
  const normalized =
    recommendation
      ?.trim()
      .toLowerCase() ?? "";

  if (
    normalized.includes("buy")
  ) {
    return "gain";
  }

  if (
    normalized.includes("sell")
  ) {
    return "loss";
  }

  return "default";
}