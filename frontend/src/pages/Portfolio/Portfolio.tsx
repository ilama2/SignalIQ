import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { mockPortfolio } from "@/data/mock";

export function Portfolio() {
  const totalValue = mockPortfolio.reduce((sum, holding) => {
    if (!holding.company) return sum;
    return sum + holding.company.price * holding.quantity;
  }, 0);

  const totalCost = mockPortfolio.reduce(
    (sum, holding) => sum + holding.averagePrice * holding.quantity,
    0
  );

  const totalPnL = totalValue - totalCost;
  const totalPnLPercent = (totalPnL / totalCost) * 100;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Portfolio</h1>
        <p className="text-sm text-text-secondary">Track your investment holdings</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Portfolio Value" value={`$${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} />
        <StatCard label="Total Cost" value={`$${totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`} />
        <StatCard label="Total P&L" value={`$${totalPnL.toFixed(2)}`} change={totalPnLPercent} />
        <StatCard label="Holdings" value={mockPortfolio.length} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Holdings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="pb-3 text-left text-xs font-medium text-text-muted uppercase tracking-wider">
                    Company
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Qty
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Avg Price
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Current
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    Value
                  </th>
                  <th className="pb-3 text-right text-xs font-medium text-text-muted uppercase tracking-wider">
                    P&L
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {mockPortfolio.map((holding) => {
                  const company = holding.company;
                  if (!company) return null;
                  const value = company.price * holding.quantity;
                  const cost = holding.averagePrice * holding.quantity;
                  const pnl = value - cost;
                  const pnlPercent = (pnl / cost) * 100;

                  return (
                    <tr
                      key={holding.companyId}
                      className="transition-colors hover:bg-surface-hover"
                    >
                      <td className="py-3">
                        <div className="flex items-center gap-3">
                          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                            {company.symbol.slice(0, 2)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-text-primary">
                              {company.companyName}
                            </p>
                            <p className="text-xs text-text-muted">
                              {company.symbol}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 text-right text-sm text-text-primary">
                        {holding.quantity}
                      </td>
                      <td className="py-3 text-right text-sm text-text-primary">
                        {holding.averagePrice.toFixed(2)}
                      </td>
                      <td className="py-3 text-right text-sm text-text-primary">
                        {company.price.toFixed(2)}
                      </td>
                      <td className="py-3 text-right text-sm font-medium text-text-primary">
                        ${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className="py-3 text-right">
                        <span
                          className={
                            pnl >= 0 ? "text-sm font-medium text-gain" : "text-sm font-medium text-loss"
                          }
                        >
                          {pnl >= 0 ? "+" : ""}
                          ${pnl.toFixed(2)} ({pnlPercent >= 0 ? "+" : ""}
                          {pnlPercent.toFixed(2)}%)
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
