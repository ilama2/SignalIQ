import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { mockNews } from "@/data/mock";
import { ExternalLink } from "lucide-react";

export function News() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">News</h1>
        <p className="text-sm text-text-secondary">
          Latest market news and sentiment analysis
        </p>
      </div>

      <div className="space-y-4">
        {mockNews.map((article) => (
          <Card key={article.id}>
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <CardTitle className="text-base leading-snug">
                    {article.title}
                  </CardTitle>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs text-text-muted">
                      {article.source}
                    </span>
                    <span className="text-text-muted">&middot;</span>
                    <span className="text-xs text-text-muted">
                      {article.publishedDate}
                    </span>
                  </div>
                </div>
                <Badge
                  variant={
                    article.sentiment === "positive"
                      ? "gain"
                      : article.sentiment === "negative"
                      ? "loss"
                      : "default"
                  }
                >
                  {article.sentiment}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-text-secondary leading-relaxed">
                {article.summary}
              </p>
              <a
                href={article.url}
                className="mt-3 inline-flex items-center gap-1 text-sm text-primary hover:text-primary-hover"
              >
                <ExternalLink className="h-3 w-3" />
                Read more
              </a>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
