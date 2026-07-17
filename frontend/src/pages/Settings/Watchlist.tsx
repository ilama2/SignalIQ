import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { mockWatchlist } from "@/data/mock";
import { Star } from "lucide-react";

export function WatchlistPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Watchlist</h1>
        <p className="text-sm text-text-secondary">
          Companies you are tracking
        </p>
      </div>

      {mockWatchlist.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Star className="h-12 w-12 text-text-muted" />
            <p className="mt-4 text-text-muted">
              No companies in your watchlist yet
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {mockWatchlist.map((item) => {
            const company = item.company;
            if (!company) return null;
            return (
              <Card key={item.companyId}>
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                      {company.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <CardTitle className="text-base">
                        {company.companyName}
                      </CardTitle>
                      <p className="text-xs text-text-muted">{company.symbol}</p>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-baseline justify-between">
                    <span className="text-xl font-bold text-text-primary">
                      {company.price.toFixed(2)}
                    </span>
                    <span
                      className={
                        company.change >= 0
                          ? "text-sm font-medium text-gain"
                          : "text-sm font-medium text-loss"
                      }
                    >
                      {company.change >= 0 ? "+" : ""}
                      {company.changePercent.toFixed(2)}%
                    </span>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
