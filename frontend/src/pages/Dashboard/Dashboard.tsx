import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { Badge } from "@/components/ui/Badge";
import { StockPrice } from "@/components/ui/StockPrice";
import { mockCompanies, mockNews } from "@/data/mock";

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
        <p className="text-sm text-text-secondary">Market overview and insights</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Tadawul Index" value="12,450.30" change={0.85} />
        <StatCard label="Total Volume" value="182M" change={-2.1} />
        <StatCard label="Top Gainer" value="Bupa Arabia" change={1.98} />
        <StatCard label="Top Loser" value="Al Rajhi Bank" change={-1.42} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Market Movers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockCompanies.slice(0, 5).map((company) => (
                <div
                  key={company.id}
                  className="flex items-center justify-between rounded-lg border border-border p-3"
                >
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                      {company.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-text-primary">
                        {company.companyName}
                      </p>
                      <p className="text-xs text-text-muted">{company.symbol}</p>
                    </div>
                  </div>
                  <StockPrice
                    price={company.price}
                    change={company.change}
                    changePercent={company.changePercent}
                    size="sm"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Latest News</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockNews.slice(0, 4).map((news) => (
                <div
                  key={news.id}
                  className="rounded-lg border border-border p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm font-medium text-text-primary line-clamp-2">
                      {news.title}
                    </p>
                    <Badge
                      variant={
                        news.sentiment === "positive"
                          ? "gain"
                          : news.sentiment === "negative"
                          ? "loss"
                          : "default"
                      }
                    >
                      {news.sentiment}
                    </Badge>
                  </div>
                  <p className="mt-1 text-xs text-text-muted">
                    {news.source} &middot; {news.publishedDate}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
