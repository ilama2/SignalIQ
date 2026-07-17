import { useParams } from "react-router-dom";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { StockPrice } from "@/components/ui/StockPrice";
import { Button } from "@/components/ui/Button";
import { mockCompanies, mockNews } from "@/data/mock";
import { Star, ExternalLink } from "lucide-react";

export function CompanyDetails() {
  const { symbol } = useParams<{ symbol: string }>();
  const company = mockCompanies.find((c) => c.symbol === symbol);

  if (!company) {
    return (
      <div className="flex h-64 items-center justify-center">
        <p className="text-text-muted">Company not found</p>
      </div>
    );
  }

  const companyNews = mockNews.filter((n) => n.companyId === company.id);

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-surface-hover text-xl font-bold text-text-primary">
            {company.symbol.slice(0, 2)}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              {company.companyName}
            </h1>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-sm text-text-muted">{company.symbol}</span>
              <Badge>{company.sector}</Badge>
              <Badge variant="info">{company.exchange}</Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm">
            <Star className="h-4 w-4" />
            Watch
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-4">
          <p className="text-xs text-text-muted uppercase">Price</p>
          <StockPrice
            price={company.price}
            change={company.change}
            changePercent={company.changePercent}
            size="lg"
          />
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-muted uppercase">Volume</p>
          <p className="mt-1 text-2xl font-bold text-text-primary">
            {(company.volume / 1e6).toFixed(1)}M
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-muted uppercase">Market Cap</p>
          <p className="mt-1 text-2xl font-bold text-text-primary">
            {(company.marketCap / 1e9).toFixed(0)}B
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-xs text-text-muted uppercase">Industry</p>
          <p className="mt-1 text-2xl font-bold text-text-primary">
            {company.industry}
          </p>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>About</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-text-secondary leading-relaxed">
            {company.description}
          </p>
          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-3 inline-flex items-center gap-1 text-sm text-primary hover:text-primary-hover"
            >
              <ExternalLink className="h-3 w-3" />
              {company.website}
            </a>
          )}
        </CardContent>
      </Card>

      {companyNews.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Related News</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {companyNews.map((news) => (
                <div
                  key={news.id}
                  className="rounded-lg border border-border p-3"
                >
                  <p className="text-sm font-medium text-text-primary">
                    {news.title}
                  </p>
                  <p className="mt-1 text-xs text-text-muted">
                    {news.source} &middot; {news.publishedDate}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
