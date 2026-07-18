import {
  useEffect,
  useState,
} from "react";

import {
  Link,
  useParams,
} from "react-router-dom";

import {
  ArrowRight,
  ExternalLink,
  RefreshCw,
  Star,
} from "lucide-react";

import {
  getCompanyDetails,
  type CompanyDetailsResponse,
} from "@/services/api";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/Card";

import { Badge } from "@/components/ui/Badge";
import { StockPrice } from "@/components/ui/StockPrice";
import { Button } from "@/components/ui/Button";

/* =========================================================
   Formatting Functions
========================================================= */

function formatNumber(
  value?: number | null,
  maximumFractionDigits = 2,
): string {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "غير متوفر";
  }

  return new Intl.NumberFormat("ar-SA", {
    maximumFractionDigits,
  }).format(Number(value));
}

function formatLargeNumber(
  value?: number | null,
): string {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "غير متوفر";
  }

  return new Intl.NumberFormat("ar-SA", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(Number(value));
}

function formatConfidence(
  value?: number | null,
): string {
  if (
    value === null ||
    value === undefined
  ) {
    return "غير متوفر";
  }

  const percentage =
    value <= 1
      ? value * 100
      : value;

  return `${formatNumber(percentage, 0)}٪`;
}

function formatDate(
  date?: string | null,
): string {
  if (!date) {
    return "غير متوفر";
  }

  const parsedDate = new Date(date);

  if (Number.isNaN(parsedDate.getTime())) {
    return date;
  }

  return new Intl.DateTimeFormat(
    "ar-SA",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(parsedDate);
}

/* =========================================================
   Recommendation Translation
========================================================= */

function translateRecommendation(
  recommendation?: string | null,
): string {
  switch (
    recommendation
      ?.trim()
      .toLowerCase()
  ) {
    case "strong buy":
      return "شراء قوي";

    case "buy":
      return "شراء";

    case "hold":
      return "احتفاظ";

    case "sell":
      return "بيع";

    case "strong sell":
      return "بيع قوي";

    default:
      return recommendation ?? "غير متوفر";
  }
}

function translateAnalysisItem(
  item: string,
): string {
  const translations: Record<string, string> = {
    "Low Debt":
      "انخفاض مستوى الديون",

    "High Debt":
      "ارتفاع مستوى الديون",

    "Excellent Return on Equity":
      "عائد ممتاز على حقوق المساهمين",

    "High Net Margin":
      "هامش صافي ربح مرتفع",

    "Positive Free Cash Flow":
      "تدفق نقدي حر إيجابي",

    "Negative Free Cash Flow":
      "تدفق نقدي حر سلبي",

    "High Volatility":
      "ارتفاع تذبذب السهم",

    "Large historical maximum drawdown":
      "انخفاض تاريخي كبير في سعر السهم",

    "Strong Revenue Growth":
      "نمو قوي في الإيرادات",

    "Strong Profitability":
      "ربحية قوية",

    "Weak Profitability":
      "ضعف في الربحية",

    "Positive Earnings Growth":
      "نمو إيجابي في الأرباح",

    "Negative Earnings Growth":
      "انخفاض في الأرباح",
  };

  return translations[item] ?? item;
}

function buildArabicSummary(
  company: CompanyDetailsResponse,
): string {
  const score =
    company.final_score !== null &&
    company.final_score !== undefined
      ? formatNumber(company.final_score)
      : "غير متوفر";

  const recommendation =
    translateRecommendation(
      company.recommendation,
    );

  const confidence =
    formatConfidence(
      company.confidence,
    );

  return `حصلت شركة ${company.company_name} على درجة استثمارية قدرها ${score}، وكانت التوصية هي ${recommendation}، بنسبة ثقة تبلغ ${confidence}.`;
}

/* =========================================================
   Loading
========================================================= */

function LoadingState() {
  return (
    <div
      dir="rtl"
      className="space-y-6 text-right"
    >
      <div className="h-28 animate-pulse rounded-2xl bg-surface-hover" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map(
          (item) => (
            <div
              key={item}
              className="h-28 animate-pulse rounded-xl bg-surface-hover"
            />
          ),
        )}
      </div>

      <div className="h-44 animate-pulse rounded-2xl bg-surface-hover" />
    </div>
  );
}

/* =========================================================
   Component
========================================================= */

export function CompanyDetails() {
  const { symbol } =
    useParams<{ symbol: string }>();

  const [
    company,
    setCompany,
  ] =
    useState<CompanyDetailsResponse | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  async function loadCompany() {
    if (!symbol) {
      setError(
        "لم يتم تحديد رمز الشركة.",
      );

      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data =
        await getCompanyDetails(
          symbol,
        );

      setCompany(data);
    } catch (caughtError) {
      setCompany(null);

      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "تعذر تحميل بيانات الشركة.",
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadCompany();
  }, [symbol]);

  if (loading) {
    return <LoadingState />;
  }

  if (error || !company) {
    return (
      <div
        dir="rtl"
        className="flex min-h-64 items-center justify-center text-right"
      >
        <div className="w-full max-w-md rounded-2xl border border-red-500/20 bg-red-500/5 p-8 text-center">
          <h2 className="font-bold text-red-600">
            تعذر تحميل الشركة
          </h2>

          <p className="mt-2 text-sm text-text-muted">
            {error ??
              "الشركة غير موجودة."}
          </p>

          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <Button
              onClick={() =>
                void loadCompany()
              }
            >
              <RefreshCw className="h-4 w-4" />
              إعادة المحاولة
            </Button>

            <Link to="/companies">
              <Button variant="secondary">
                العودة إلى الشركات
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      dir="rtl"
      className="space-y-6 text-right"
    >
      {/* Back Link */}

      <Link
        to="/companies"
        className="inline-flex items-center gap-2 text-sm text-text-muted transition-colors hover:text-primary"
      >
        <ArrowRight className="h-4 w-4" />
        العودة إلى الشركات
      </Link>

      {/* Company Header */}

      <section className="flex flex-col gap-5 rounded-2xl border border-border bg-surface p-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex items-start gap-4">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-xl bg-surface-hover text-xl font-bold text-text-primary">
            {company.symbol.slice(0, 2)}
          </div>

          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              {company.company_name}
            </h1>

            {company.company_name_en && (
              <p
                dir="ltr"
                className="mt-1 text-right text-sm text-text-muted"
              >
                {company.company_name_en}
              </p>
            )}

            <div className="mt-2 flex flex-wrap items-center gap-2">
              <span
                dir="ltr"
                className="text-sm font-medium text-text-muted"
              >
                {company.symbol}
              </span>

              <Badge variant="info">
                {company.exchange ??
                  "تداول"}
              </Badge>

              {company.recommendation && (
                <Badge>
                  {translateRecommendation(
                    company.recommendation,
                  )}
                </Badge>
              )}

              {company.is_delayed && (
                <Badge>
                  بيانات متأخرة
                </Badge>
              )}
            </div>

            {company.updated_at && (
              <p className="mt-3 text-xs text-text-muted">
                آخر تحديث:{" "}
                {formatDate(
                  company.updated_at,
                )}
              </p>
            )}
          </div>
        </div>

        <Button
          variant="secondary"
          size="sm"
        >
          <Star className="h-4 w-4" />
          إضافة للمراقبة
        </Button>
      </section>

      {/* Main Summary Cards */}

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="p-4">
          <p className="text-xs text-text-muted">
            السعر الحالي
          </p>

          {company.current_price !==
          null &&
          company.current_price !==
            undefined ? (
            <div
              dir="ltr"
              className="mt-2 text-right"
            >
              <StockPrice
                price={
                  company.current_price
                }
                change={
                  company.change ?? 0
                }
                changePercent={
                  company.change_percent ??
                  0
                }
                size="lg"
              />
            </div>
          ) : (
            <p className="mt-2 text-xl font-bold text-text-primary">
              غير متوفر
            </p>
          )}

          <p className="mt-1 text-xs text-text-muted">
            العملة:{" "}
            {company.currency ?? "ر.س"}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted">
            حجم التداول
          </p>

          <p className="mt-2 text-2xl font-bold text-text-primary">
            {formatLargeNumber(
              company.volume,
            )}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted">
            قيمة التداول
          </p>

          <p className="mt-2 text-2xl font-bold text-text-primary">
            {company.trading_value !==
            null &&
            company.trading_value !==
              undefined
              ? `${formatLargeNumber(
                  company.trading_value,
                )} ${
                  company.currency ??
                  "ر.س"
                }`
              : "غير متوفر"}
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-xs text-text-muted">
            درجة التوصية
          </p>

          <p className="mt-2 text-2xl font-bold text-primary">
            {formatNumber(
              company.final_score,
            )}
          </p>

          <p className="mt-1 text-xs text-text-muted">
            الثقة:{" "}
            {formatConfidence(
              company.confidence,
            )}
          </p>
        </Card>
      </section>

      {/* Daily Price Cards */}

      <section>
        <h2 className="mb-3 text-lg font-bold text-text-primary">
          حركة السعر اليومية
        </h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Card className="p-4">
            <p className="text-xs text-text-muted">
              سعر الافتتاح
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {company.open !== null &&
              company.open !== undefined
                ? `${formatNumber(
                    company.open,
                  )} ${
                    company.currency ??
                    "ر.س"
                  }`
                : "غير متوفر"}
            </p>
          </Card>

          <Card className="p-4">
            <p className="text-xs text-text-muted">
              أعلى سعر
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {company.high !== null &&
              company.high !== undefined
                ? `${formatNumber(
                    company.high,
                  )} ${
                    company.currency ??
                    "ر.س"
                  }`
                : "غير متوفر"}
            </p>
          </Card>

          <Card className="p-4">
            <p className="text-xs text-text-muted">
              أقل سعر
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {company.low !== null &&
              company.low !== undefined
                ? `${formatNumber(
                    company.low,
                  )} ${
                    company.currency ??
                    "ر.س"
                  }`
                : "غير متوفر"}
            </p>
          </Card>

          <Card className="p-4">
            <p className="text-xs text-text-muted">
              الإغلاق السابق
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {company.previous_close !==
              null &&
              company.previous_close !==
                undefined
                ? `${formatNumber(
                    company.previous_close,
                  )} ${
                    company.currency ??
                    "ر.س"
                  }`
                : "غير متوفر"}
            </p>
          </Card>
        </div>
      </section>

      {/* Bid and Ask */}

      <section>
        <h2 className="mb-3 text-lg font-bold text-text-primary">
          العرض والطلب
        </h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Card className="p-4">
            <p className="text-xs text-text-muted">
              أفضل طلب
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {company.bid !== null &&
              company.bid !== undefined
                ? `${formatNumber(
                    company.bid,
                  )} ${
                    company.currency ??
                    "ر.س"
                  }`
                : "غير متوفر"}
            </p>
          </Card>

          <Card className="p-4">
            <p className="text-xs text-text-muted">
              كمية الطلب
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {formatLargeNumber(
                company.bid_size,
              )}
            </p>
          </Card>

          <Card className="p-4">
            <p className="text-xs text-text-muted">
              أفضل عرض
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {company.ask !== null &&
              company.ask !== undefined
                ? `${formatNumber(
                    company.ask,
                  )} ${
                    company.currency ??
                    "ر.س"
                  }`
                : "غير متوفر"}
            </p>
          </Card>

          <Card className="p-4">
            <p className="text-xs text-text-muted">
              كمية العرض
            </p>

            <p className="mt-2 text-xl font-bold text-text-primary">
              {formatLargeNumber(
                company.ask_size,
              )}
            </p>
          </Card>
        </div>
      </section>

      {/* Liquidity */}

      {company.liquidity && (
        <section>
          <h2 className="mb-3 text-lg font-bold text-text-primary">
            السيولة
          </h2>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <Card className="p-4">
              <p className="text-xs text-text-muted">
                قيمة التدفقات الداخلة
              </p>

              <p className="mt-2 text-xl font-bold text-emerald-600">
                {company.liquidity
                  .inflow_value !==
                  null &&
                company.liquidity
                  .inflow_value !==
                  undefined
                  ? `${formatLargeNumber(
                      company.liquidity
                        .inflow_value,
                    )} ${
                      company.currency ??
                      "ر.س"
                    }`
                  : "غير متوفر"}
              </p>
            </Card>

            <Card className="p-4">
              <p className="text-xs text-text-muted">
                قيمة التدفقات الخارجة
              </p>

              <p className="mt-2 text-xl font-bold text-red-600">
                {company.liquidity
                  .outflow_value !==
                  null &&
                company.liquidity
                  .outflow_value !==
                  undefined
                  ? `${formatLargeNumber(
                      company.liquidity
                        .outflow_value,
                    )} ${
                      company.currency ??
                      "ر.س"
                    }`
                  : "غير متوفر"}
              </p>
            </Card>

            <Card className="p-4">
              <p className="text-xs text-text-muted">
                صافي السيولة
              </p>

              <p className="mt-2 text-xl font-bold text-primary">
                {company.liquidity
                  .net_value !== null &&
                company.liquidity
                  .net_value !==
                  undefined
                  ? `${formatLargeNumber(
                      company.liquidity
                        .net_value,
                    )} ${
                      company.currency ??
                      "ر.س"
                    }`
                  : "غير متوفر"}
              </p>
            </Card>
          </div>
        </section>
      )}

      {/* About */}

      <Card>
        <CardHeader>
          <CardTitle>
            نبذة عن الشركة
          </CardTitle>
        </CardHeader>

        <CardContent>
          <p className="text-sm leading-7 text-text-secondary">
            {company.description ??
              "لا تتوفر نبذة عن الشركة حاليًا."}
          </p>

          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-2 text-sm text-primary hover:text-primary-hover"
            >
              <ExternalLink className="h-4 w-4" />
              زيارة موقع الشركة
            </a>
          )}
        </CardContent>
      </Card>

      {/* Analysis */}

      <Card>
        <CardHeader>
          <CardTitle>
            ملخص التحليل
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-5">
          <p className="text-sm leading-7 text-text-secondary">
            {buildArabicSummary(
              company,
            )}
          </p>

          {company.strengths &&
            company.strengths.length >
              0 && (
              <div>
                <h3 className="mb-2 text-sm font-semibold text-emerald-600">
                  نقاط القوة
                </h3>

                <div className="space-y-2">
                  {company.strengths.map(
                    (
                      strength,
                      index,
                    ) => (
                      <div
                        key={`${strength}-${index}`}
                        className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-sm text-text-secondary"
                      >
                        {translateAnalysisItem(
                          strength,
                        )}
                      </div>
                    ),
                  )}
                </div>
              </div>
            )}

          {company.risks &&
            company.risks.length >
              0 && (
              <div>
                <h3 className="mb-2 text-sm font-semibold text-red-600">
                  المخاطر
                </h3>

                <div className="space-y-2">
                  {company.risks.map(
                    (
                      risk,
                      index,
                    ) => (
                      <div
                        key={`${risk}-${index}`}
                        className="rounded-lg border border-red-500/20 bg-red-500/5 p-3 text-sm text-text-secondary"
                      >
                        {translateAnalysisItem(
                          risk,
                        )}
                      </div>
                    ),
                  )}
                </div>
              </div>
            )}
        </CardContent>
      </Card>

      {/* News */}

      {company.news &&
        company.news.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>
                الأخبار المتعلقة بالشركة
              </CardTitle>
            </CardHeader>

            <CardContent>
              <div className="space-y-3">
                {company.news.map(
                  (news, index) => (
                    <article
                      key={
                        news.id ??
                        `${news.title}-${index}`
                      }
                      className="rounded-xl border border-border p-4"
                    >
                      {news.url ? (
                        <a
                          href={news.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-medium text-text-primary transition-colors hover:text-primary"
                        >
                          {news.title}
                        </a>
                      ) : (
                        <p className="font-medium text-text-primary">
                          {news.title}
                        </p>
                      )}

                      <div className="mt-2 flex flex-wrap gap-2 text-xs text-text-muted">
                        {news.source && (
                          <span>
                            {news.source}
                          </span>
                        )}

                        {news.source &&
                          news.published_date && (
                            <span>•</span>
                          )}

                        {news.published_date && (
                          <span>
                            {
                              news.published_date
                            }
                          </span>
                        )}
                      </div>
                    </article>
                  ),
                )}
              </div>
            </CardContent>
          </Card>
        )}
    </div>
  );
}