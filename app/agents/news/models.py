"""
SignalIQ - News Analysis Models

Defines the structured output models used by the News Agent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


# ==========================================================
# Article Source
# ==========================================================

class NewsSourceModel(BaseModel):
    """Information about the article publisher."""

    name: str = "Unknown"
    url: HttpUrl | None = None


# ==========================================================
# Article Sentiment
# ==========================================================

class SentimentModel(BaseModel):
    """Sentiment result for one news article."""

    label: Literal["positive", "neutral", "negative"]

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Model confidence between 0 and 1.",
    )

    score: float = Field(
        ge=-1.0,
        le=1.0,
        description=(
            "Normalized sentiment score where -1 is strongly negative, "
            "0 is neutral, and 1 is strongly positive."
        ),
    )


# ==========================================================
# News Article
# ==========================================================

class NewsArticleModel(BaseModel):
    """Normalized news article returned by the collector."""

    title: str

    description: str | None = None
    content: str | None = None

    url: HttpUrl | None = None
    image_url: HttpUrl | None = None

    source: NewsSourceModel = Field(
        default_factory=NewsSourceModel
    )

    author: str | None = None
    published_at: datetime | None = None

    language: str = "en"

    sentiment: SentimentModel | None = None

    relevance_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Article relevance to the target company.",
    )

    impact_score: float | None = Field(
        default=None,
        ge=-1.0,
        le=1.0,
        description="Estimated impact on the stock.",
    )


# ==========================================================
# News Score
# ==========================================================

class NewsScoreModel(BaseModel):
    """Aggregated investment score derived from company news."""

    score: int = Field(
        ge=0,
        le=100,
        description="Overall news score from 0 to 100.",
    )

    rating: Literal[
        "Strongly Bullish",
        "Bullish",
        "Neutral",
        "Bearish",
        "Strongly Bearish",
    ]

    positive_articles: int = Field(default=0, ge=0)
    neutral_articles: int = Field(default=0, ge=0)
    negative_articles: int = Field(default=0, ge=0)

    average_sentiment: float = Field(
        ge=-1.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)


# ==========================================================
# News Summary
# ==========================================================

class NewsSummaryModel(BaseModel):
    """LLM-generated investment-focused news summary."""

    summary: str

    key_events: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    expected_impact: Literal[
        "Strong Positive",
        "Positive",
        "Neutral",
        "Negative",
        "Strong Negative",
        "Unknown",
    ] = "Unknown"


# ==========================================================
# Complete News Report
# ==========================================================

class NewsReport(BaseModel):
    """Complete output produced by the News Agent."""

    symbol: str
    company_name: str

    generated_at: datetime = Field(
        default_factory=datetime.now
    )

    article_count: int = Field(default=0, ge=0)

    articles: list[NewsArticleModel] = Field(
        default_factory=list
    )

    score: NewsScoreModel

    summary: NewsSummaryModel