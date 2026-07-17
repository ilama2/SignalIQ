import { Card, CardContent } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { StockPrice } from "@/components/ui/StockPrice";
import { Badge } from "@/components/ui/Badge";
import { mockCompanies } from "@/data/mock";
import { Search } from "lucide-react";

export function Companies() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Companies</h1>
        <p className="text-sm text-text-secondary">Explore Saudi market companies</p>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted" />
        <Input placeholder="Search by name or symbol..." className="pl-9" />
      </div>

      <Card>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Company
                  </th>
                  <th className="pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Symbol
                  </th>
                  <th className="pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Sector
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Price
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Change
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Volume
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {mockCompanies.map((company) => (
                  <tr
                    key={company.id}
                    className="cursor-pointer transition-colors hover:bg-surface-hover"
                  >
                    <td className="py-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                          {company.symbol.slice(0, 2)}
                        </div>
                        <span className="text-sm font-medium text-text-primary">
                          {company.companyName}
                        </span>
                      </div>
                    </td>
                    <td className="py-3">
                      <span className="text-sm text-text-secondary">
                        {company.symbol}
                      </span>
                    </td>
                    <td className="py-3">
                      <Badge>{company.sector}</Badge>
                    </td>
                    <td className="py-3 text-right">
                      <span className="text-sm font-medium text-text-primary">
                        {company.price.toFixed(2)}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <StockPrice
                        price={company.price}
                        change={company.change}
                        changePercent={company.changePercent}
                        size="sm"
                      />
                    </td>
                    <td className="py-3 text-right">
                      <span className="text-sm text-text-secondary">
                        {(company.volume / 1e6).toFixed(1)}M
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
