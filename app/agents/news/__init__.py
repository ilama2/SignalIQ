"""
SignalIQ News Agent

Provides a complete company news analysis pipeline including:

- News collection
- Sentiment analysis
- News summarization
- News scoring
- Pipeline execution
"""

from .collector import NewsCollector
from .models import (
    NewsArticleModel,
    NewsReport,
    NewsScoreModel,
    NewsSourceModel,
    NewsSummaryModel,
    SentimentModel,
)
from .news import NewsAgent
from .pipeline import NewsPipeline
from .scoring import NewsScorer
from .sentiment import NewsSentimentAnalyzer
from .summarizer import NewsSummarizer

__all__ = [
    # Main API
    "NewsAgent",
    "NewsPipeline",

    # Components
    "NewsCollector",
    "NewsSentimentAnalyzer",
    "NewsSummarizer",
    "NewsScorer",

    # Models
    "NewsArticleModel",
    "NewsReport",
    "NewsScoreModel",
    "NewsSourceModel",
    "NewsSummaryModel",
    "SentimentModel",
]