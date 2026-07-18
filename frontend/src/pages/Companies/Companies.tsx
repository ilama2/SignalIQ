import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useNavigate,
} from "react-router-dom";

import {
  AlertCircle,
  RefreshCw,
  Search,
} from "lucide-react";

import {
  Card,
  CardContent,
} from "@/components/ui/Card";

import { Input } from "@/components/ui/Input";
import { StockPrice } from "@/components/ui/StockPrice";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

import {
  getCompanies,
  type CompanyListItem,
} from "@/services/api";


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


function getRecommendationVariant(
  recommendation?: string | null,
): "default" | "info" {
  const normalized =
    recommendation
      ?.trim()
      .toLowerCase();

  if (
    normalized === "buy" ||
    normalized === "strong buy"
  ) {
    return "info";
  }

  return "default";
}


function LoadingRows() {
  return (
    <>
      {Array.from({
        length: 8,
      }).map((_, index) => (
        <tr
          key={index}
          className="border-b border-border"
        >
          <td className="py-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 animate-pulse rounded-lg bg-surface-hover" />

              <div className="h-4 w-36 animate-pulse rounded bg-surface-hover" />
            </div>
          </td>

          <td className="py-4">
            <div className="h-4 w-16 animate-pulse rounded bg-surface-hover" />
          </td>

          <td className="py-4">
            <div className="h-6 w-20 animate-pulse rounded bg-surface-hover" />
          </td>

          <td className="py-4">
            <div className="mr-auto h-4 w-16 animate-pulse rounded bg-surface-hover" />
          </td>

          <td className="py-4">
            <div className="mr-auto h-4 w-20 animate-pulse rounded bg-surface-hover" />
          </td>

          <td className="py-4">
            <div className="mr-auto h-4 w-20 animate-pulse rounded bg-surface-hover" />
          </td>
        </tr>
      ))}
    </>
  );
}


export function Companies() {
  const navigate = useNavigate();

  const [
    companies,
    setCompanies,
  ] = useState<CompanyListItem[]>([]);

  const [
    searchText,
    setSearchText,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(null);


  async function loadCompanies() {
    try {
      setLoading(true);
      setError(null);

      const response =
        await getCompanies();

      setCompanies(
        response.companies,
      );
    } catch (caughtError) {
      setCompanies([]);

      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "تعذر تحميل بيانات الشركات.",
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    void loadCompanies();
  }, []);


  const filteredCompanies =
    useMemo(() => {
      const normalizedSearch =
        searchText
          .trim()
          .toLowerCase();

      if (!normalizedSearch) {
        return companies;
      }

      return companies.filter(
        (company) => {
          const searchableValues = [
            company.symbol,
            company.company_name,
            company.company_name_en,
            company.sector,
            company.recommendation,
          ];

          return searchableValues.some(
            (value) =>
              value
                ?.toLowerCase()
                .includes(
                  normalizedSearch,
                ),
          );
        },
      );
    }, [
      companies,
      searchText,
    ]);


  function openCompany(
    symbol: string,
  ) {
    navigate(
      `/companies/${encodeURIComponent(symbol)}`,
    );
  }


  return (
    <div
      dir="rtl"
      className="space-y-6 text-right"
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">
            الشركات
          </h1>

          <p className="mt-1 text-sm text-text-secondary">
            استعرض شركات السوق السعودي وبيانات التداول والتوصيات الاستثمارية.
          </p>
        </div>

        {!loading && !error && (
          <div className="rounded-xl border border-border bg-surface px-4 py-3">
            <p className="text-xs text-text-muted">
              عدد الشركات
            </p>

            <p className="mt-1 text-xl font-bold text-text-primary">
              {formatNumber(
                filteredCompanies.length,
                0,
              )}
            </p>
          </div>
        )}
      </div>

      <div className="relative max-w-md">
        <Search className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />

        <Input
          value={searchText}
          onChange={(event) =>
            setSearchText(
              event.target.value,
            )
          }
          placeholder="ابحث باسم الشركة أو الرمز..."
          className="pr-9"
          disabled={loading}
        />
      </div>

      {error && (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-red-500/20 bg-red-500/5 p-8 text-center">
          <AlertCircle className="h-8 w-8 text-red-600" />

          <h2 className="mt-3 font-bold text-red-600">
            تعذر تحميل الشركات
          </h2>

          <p className="mt-2 max-w-lg text-sm text-text-muted">
            {error}
          </p>

          <Button
            className="mt-5"
            onClick={() =>
              void loadCompanies()
            }
          >
            <RefreshCw className="h-4 w-4" />
            إعادة المحاولة
          </Button>
        </div>
      )}

      {!error && (
        <Card>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[850px]">
                <thead>
                  <tr className="border-b border-border">
                    <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">
                      الشركة
                    </th>

                    <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">
                      الرمز
                    </th>

                    <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-text-muted">
                      التوصية
                    </th>

                    <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-text-muted">
                      السعر
                    </th>

                    <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-text-muted">
                      التغير
                    </th>

                    <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-text-muted">
                      حجم التداول
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-border">
                  {loading ? (
                    <LoadingRows />
                  ) : (
                    filteredCompanies.map(
                      (company) => (
                        <tr
                          key={company.symbol}
                          role="button"
                          tabIndex={0}
                          onClick={() =>
                            openCompany(
                              company.symbol,
                            )
                          }
                          onKeyDown={(
                            event,
                          ) => {
                            if (
                              event.key ===
                                "Enter" ||
                              event.key ===
                                " "
                            ) {
                              event.preventDefault();

                              openCompany(
                                company.symbol,
                              );
                            }
                          }}
                          className="cursor-pointer transition-colors hover:bg-surface-hover focus:bg-surface-hover focus:outline-none"
                        >
                          <td className="py-4">
                            <div className="flex items-center gap-3">
                              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                                {company.symbol.slice(
                                  0,
                                  2,
                                )}
                              </div>

                              <div>
                                <p className="text-sm font-medium text-text-primary">
                                  {
                                    company.company_name
                                  }
                                </p>

                                {company.company_name_en && (
                                  <p
                                    dir="ltr"
                                    className="mt-1 max-w-60 truncate text-right text-xs text-text-muted"
                                  >
                                    {
                                      company.company_name_en
                                    }
                                  </p>
                                )}

                                {company.is_delayed && (
                                  <p className="mt-1 text-xs text-amber-600">
                                    بيانات متأخرة
                                  </p>
                                )}
                              </div>
                            </div>
                          </td>

                          <td className="py-4">
                            <span
                              dir="ltr"
                              className="text-sm font-medium text-text-secondary"
                            >
                              {company.symbol}
                            </span>
                          </td>

                          <td className="py-4">
                            {company.recommendation ? (
                              <Badge
                                variant={getRecommendationVariant(
                                  company.recommendation,
                                )}
                              >
                                {translateRecommendation(
                                  company.recommendation,
                                )}
                              </Badge>
                            ) : (
                              <span className="text-sm text-text-muted">
                                غير متوفر
                              </span>
                            )}
                          </td>

                          <td className="py-4 text-left">
                            <span
                              dir="ltr"
                              className="text-sm font-medium text-text-primary"
                            >
                              {company.current_price !==
                                null &&
                              company.current_price !==
                                undefined
                                ? `${formatNumber(
                                    company.current_price,
                                  )} ${
                                    company.currency ??
                                    "ر.س"
                                  }`
                                : "غير متوفر"}
                            </span>
                          </td>

                          <td className="py-4 text-left">
                            {company.current_price !==
                              null &&
                            company.current_price !==
                              undefined ? (
                              <div
                                dir="ltr"
                                className="inline-block text-right"
                              >
                                <StockPrice
                                  price={
                                    company.current_price
                                  }
                                  change={
                                    company.change ??
                                    0
                                  }
                                  changePercent={
                                    company.change_percent ??
                                    0
                                  }
                                  size="sm"
                                />
                              </div>
                            ) : (
                              <span className="text-sm text-text-muted">
                                غير متوفر
                              </span>
                            )}
                          </td>

                          <td className="py-4 text-left">
                            <span className="text-sm text-text-secondary">
                              {formatLargeNumber(
                                company.volume,
                              )}
                            </span>
                          </td>
                        </tr>
                      ),
                    )
                  )}
                </tbody>
              </table>

              {!loading &&
                filteredCompanies.length ===
                  0 && (
                  <div className="flex min-h-52 flex-col items-center justify-center text-center">
                    <Search className="h-8 w-8 text-text-muted" />

                    <p className="mt-3 font-medium text-text-primary">
                      لا توجد شركات مطابقة
                    </p>

                    <p className="mt-1 text-sm text-text-muted">
                      جرّب البحث باسم أو رمز مختلف.
                    </p>
                  </div>
                )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}