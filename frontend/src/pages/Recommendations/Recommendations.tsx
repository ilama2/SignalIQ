import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  getRecommendations,
  type Recommendation,
} from "@/services/api";

type RecommendationVariant =
  | "buy"
  | "hold"
  | "sell";

type RecommendationSectionProps = {
  title: string;
  description: string;
  recommendations: Recommendation[];
  variant: RecommendationVariant;
};

const sectionStyles = {
  buy: {
    container:
      "border-emerald-500/20 bg-emerald-500/[0.04]",
    badge:
      "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
    score:
      "text-emerald-600 dark:text-emerald-400",
    bar: "bg-emerald-500",
    rank:
      "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
  },

  hold: {
    container:
      "border-amber-500/20 bg-amber-500/[0.04]",
    badge:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    score:
      "text-amber-600 dark:text-amber-400",
    bar: "bg-amber-500",
    rank:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400",
  },

  sell: {
    container:
      "border-red-500/20 bg-red-500/[0.04]",
    badge:
      "bg-red-500/10 text-red-600 dark:text-red-400",
    score:
      "text-red-600 dark:text-red-400",
    bar: "bg-red-500",
    rank:
      "bg-red-500/10 text-red-600 dark:text-red-400",
  },
};

function formatConfidence(
  confidence: number,
): string {
  const percentage =
    confidence <= 1
      ? confidence * 100
      : confidence;

  return `${percentage.toFixed(0)}٪`;
}

function formatPrice(
  company: Recommendation,
): string | null {
  const price = company.current_price;

  if (
    price === null ||
    price === undefined ||
    Number.isNaN(Number(price))
  ) {
    return null;
  }

  return new Intl.NumberFormat("ar-SA", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(price));
}

function RecommendationSection({
  title,
  description,
  recommendations,
  variant,
}: RecommendationSectionProps) {
  const styles = sectionStyles[variant];

  return (
    <section
      className={`overflow-hidden rounded-2xl border ${styles.container}`}
    >
      <header className="flex items-start justify-between gap-4 border-b border-border/60 p-5">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-lg font-semibold text-foreground">
              {title}
            </h2>

            <span
              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${styles.badge}`}
            >
              {recommendations.length} شركات
            </span>
          </div>

          <p className="mt-1 text-sm text-muted-foreground">
            {description}
          </p>
        </div>
      </header>

      {recommendations.length === 0 ? (
        <div className="p-8 text-center text-sm text-muted-foreground">
          لا توجد توصيات متاحة ضمن هذا التصنيف.
        </div>
      ) : (
        <div className="divide-y divide-border/60">
          {recommendations.map(
            (company, index) => {
              const formattedPrice =
                formatPrice(company);

              return (
                <Link
                  key={company.symbol}
                  to={`/companies/${company.symbol}`}
                  className="group block p-4 transition-colors hover:bg-background/70"
                >
                  <div className="flex items-center gap-4">
                    <div
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${styles.rank}`}
                    >
                      {index + 1}
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-4">
                        <div className="min-w-0">
                          <p className="truncate font-semibold text-foreground transition-colors group-hover:text-primary">
                            {company.company_name ||
                              company.symbol}
                          </p>

                          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                            <span className="font-medium">
                              {company.symbol}
                            </span>

                            <span>•</span>

                            <span>
                              نسبة الثقة:{" "}
                              {formatConfidence(
                                company.confidence,
                              )}
                            </span>
                          </div>
                        </div>

                        <div className="shrink-0 text-left">
                          <p
                            className={`text-xl font-bold ${styles.score}`}
                          >
                            {company.final_score.toFixed(
                              2,
                            )}
                          </p>

                          {formattedPrice ? (
                            <p className="mt-1 text-xs font-medium text-muted-foreground">
                              السعر الحالي:{" "}
                              {formattedPrice}{" "}
                              {company.currency ??
                                "ر.س"}
                            </p>
                          ) : (
                            <p className="mt-1 text-xs text-muted-foreground">
                              السعر غير متوفر
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted">
                        <div
                          className={`h-full rounded-full ${styles.bar}`}
                          style={{
                            width: `${Math.min(
                              Math.max(
                                company.final_score,
                                0,
                              ),
                              100,
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </Link>
              );
            },
          )}
        </div>
      )}
    </section>
  );
}

function LoadingSkeleton() {
  return (
    <div className="grid gap-6 xl:grid-cols-3">
      {[1, 2, 3].map((section) => (
        <div
          key={section}
          className="animate-pulse overflow-hidden rounded-2xl border border-border bg-card"
        >
          <div className="border-b border-border p-5">
            <div className="h-5 w-32 rounded bg-muted" />
            <div className="mt-3 h-3 w-48 rounded bg-muted" />
          </div>

          <div className="space-y-5 p-5">
            {[1, 2, 3, 4, 5].map(
              (row) => (
                <div
                  key={row}
                  className="flex items-center gap-4"
                >
                  <div className="h-10 w-10 rounded-xl bg-muted" />

                  <div className="flex-1">
                    <div className="h-4 w-2/3 rounded bg-muted" />

                    <div className="mt-2 h-3 w-1/3 rounded bg-muted" />
                  </div>

                  <div className="h-6 w-14 rounded bg-muted" />
                </div>
              ),
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export function Recommendations() {
  const [
    recommendations,
    setRecommendations,
  ] = useState<Recommendation[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  useEffect(() => {
    async function loadRecommendations() {
      try {
        setLoading(true);
        setError(null);

        const response =
          await getRecommendations();

        setRecommendations(
          response.recommendations,
        );
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "تعذر تحميل التوصيات.",
        );
      } finally {
        setLoading(false);
      }
    }

    void loadRecommendations();
  }, []);

  const sections = useMemo(() => {
    const buy = recommendations
      .filter(
        (company) =>
          company.recommendation
            .trim()
            .toLowerCase() === "buy",
      )
      .sort(
        (a, b) =>
          b.final_score -
          a.final_score,
      )
      .slice(0, 5);

    const hold = recommendations
      .filter(
        (company) =>
          company.recommendation
            .trim()
            .toLowerCase() === "hold",
      )
      .sort(
        (a, b) =>
          b.final_score -
          a.final_score,
      )
      .slice(0, 5);

    const sell = recommendations
      .filter((company) => {
        const recommendation =
          company.recommendation
            .trim()
            .toLowerCase();

        return (
          recommendation === "sell" ||
          recommendation ===
            "strong sell"
        );
      })
      .sort(
        (a, b) =>
          a.final_score -
          b.final_score,
      )
      .slice(0, 5);

    return {
      buy,
      hold,
      sell,
    };
  }, [recommendations]);

  const counts = useMemo(() => {
    return recommendations.reduce(
      (result, company) => {
        const recommendation =
          company.recommendation
            .trim()
            .toLowerCase();

        if (recommendation === "buy") {
          result.buy += 1;
        } else if (
          recommendation === "hold"
        ) {
          result.hold += 1;
        } else if (
          recommendation === "sell" ||
          recommendation ===
            "strong sell"
        ) {
          result.sell += 1;
        }

        return result;
      },
      {
        buy: 0,
        hold: 0,
        sell: 0,
      },
    );
  }, [recommendations]);

  if (loading) {
    return (
      <div
        dir="rtl"
        className="space-y-8 p-6 text-right lg:p-8"
      >
        <div>
          <div className="h-8 w-72 animate-pulse rounded bg-muted" />

          <div className="mt-3 h-4 w-96 max-w-full animate-pulse rounded bg-muted" />
        </div>

        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div
        dir="rtl"
        className="p-6 text-right lg:p-8"
      >
        <div className="rounded-2xl border border-red-500/20 bg-red-500/5 p-6">
          <h2 className="font-semibold text-red-600 dark:text-red-400">
            تعذر تحميل التوصيات
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            {error}
          </p>

          <button
            type="button"
            onClick={() =>
              window.location.reload()
            }
            className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      dir="rtl"
      className="space-y-8 p-6 text-right lg:p-8"
    >
      <header>
        <p className="text-sm font-medium text-primary">
          تحليلات SignalIQ للسوق
        </p>

        <div className="mt-2 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">
              توصيات الاستثمار
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">
              أفضل الفرص الاستثمارية وأبرز
              إشارات المخاطر الناتجة عن تحليلات
              الوكلاء ونظام الإشراف.
            </p>
          </div>

          <div className="text-sm text-muted-foreground">
            تم تحليل{" "}
            <span className="font-semibold text-foreground">
              {recommendations.length}
            </span>{" "}
            شركة
          </div>
        </div>
      </header>

      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/[0.04] p-5">
          <p className="text-sm font-medium text-muted-foreground">
            توصيات الشراء
          </p>

          <p className="mt-2 text-3xl font-bold text-emerald-600 dark:text-emerald-400">
            {counts.buy}
          </p>
        </div>

        <div className="rounded-2xl border border-amber-500/20 bg-amber-500/[0.04] p-5">
          <p className="text-sm font-medium text-muted-foreground">
            توصيات الاحتفاظ
          </p>

          <p className="mt-2 text-3xl font-bold text-amber-600 dark:text-amber-400">
            {counts.hold}
          </p>
        </div>

        <div className="rounded-2xl border border-red-500/20 bg-red-500/[0.04] p-5">
          <p className="text-sm font-medium text-muted-foreground">
            توصيات البيع
          </p>

          <p className="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">
            {counts.sell}
          </p>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-3">
        <RecommendationSection
          title="أفضل 5 للشراء"
          description="الشركات التي حصلت على أعلى درجات الشراء."
          recommendations={sections.buy}
          variant="buy"
        />

        <RecommendationSection
          title="أفضل 5 للاحتفاظ"
          description="أعلى الشركات المصنفة ضمن توصية الاحتفاظ."
          recommendations={sections.hold}
          variant="hold"
        />

        <RecommendationSection
          title="أعلى 5 توصيات للبيع"
          description="الشركات التي حصلت على أضعف الدرجات الاستثمارية."
          recommendations={sections.sell}
          variant="sell"
        />
      </div>
    </div>
  );
}