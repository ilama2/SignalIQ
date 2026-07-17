import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { mockCompanies } from "@/data/mock";

const mockRecommendations = [
  {
    company: mockCompanies[0],
    recommendation: "Buy" as const,
    confidence: 78,
    explanation: "Strong fundamentals and stable oil revenue growth expected.",
  },
  {
    company: mockCompanies[1],
    recommendation: "Hold" as const,
    confidence: 65,
    explanation: "Stable performance but facing digital transformation headwinds.",
  },
  {
    company: mockCompanies[2],
    recommendation: "Strong Buy" as const,
    confidence: 85,
    explanation: "New product launches and expanding market presence in Asia.",
  },
  {
    company: mockCompanies[3],
    recommendation: "Buy" as const,
    confidence: 72,
    explanation: "Cloud expansion and 5G rollout driving future growth.",
  },
  {
    company: mockCompanies[4],
    recommendation: "Sell" as const,
    confidence: 60,
    explanation: "Interest rate concerns may impact near-term profitability.",
  },
];

function getRecommendationVariant(rec: string) {
  switch (rec) {
    case "Strong Buy":
      return "gain";
    case "Buy":
      return "gain";
    case "Hold":
      return "warning";
    case "Sell":
      return "loss";
    case "Strong Sell":
      return "loss";
    default:
      return "default";
  }
}

export function Recommendations() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Recommendations</h1>
        <p className="text-sm text-text-secondary">
          AI-powered investment recommendations
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mockRecommendations.map((rec) => (
          <Card key={rec.company.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-surface-hover text-xs font-bold text-text-primary">
                    {rec.company.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <CardTitle className="text-base">
                      {rec.company.companyName}
                    </CardTitle>
                    <p className="text-xs text-text-muted">
                      {rec.company.symbol}
                    </p>
                  </div>
                </div>
                <Badge variant={getRecommendationVariant(rec.recommendation)}>
                  {rec.recommendation}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-text-secondary">{rec.explanation}</p>
              <div className="mt-3 flex items-center gap-2">
                <span className="text-xs text-text-muted">Confidence:</span>
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-hover">
                  <div
                    className="h-full rounded-full bg-primary transition-all"
                    style={{ width: `${rec.confidence}%` }}
                  />
                </div>
                <span className="text-xs font-medium text-text-primary">
                  {rec.confidence}%
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
