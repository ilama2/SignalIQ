from app.agents.news.models import NewsArticleModel
from app.agents.news.sentiment import NewsSentimentAnalyzer

article = NewsArticleModel(
    title="Saudi Aramco reports higher quarterly profit",
    description="The company reported stronger earnings and improved cash flow.",
)

analyzer = NewsSentimentAnalyzer()

result = analyzer.analyze_article(article)

print(result.sentiment)