"""
SignalIQ - News Scoring

Converts article-level sentiment and relevance signals into an
aggregated investment-oriented news score.

This module does not collect or summarize news.
"""

from __future__ import annotations

from collections import Counter

from loguru import logger

from .models import (
    NewsArticleModel,
    NewsScoreModel,
    NewsSummaryModel,
)


class NewsScorer:
    """
    Calculate an overall news score for one company.

    The score combines:

    - Article sentiment
    - Sentiment confidence
    - Company relevance
    - Estimated article impact
    - Article recency
    - Summary-level expected impact

    Final score range:

        0   = strongly bearish
        50  = neutral
        100 = strongly bullish
    """

    SUMMARY_IMPACT_ADJUSTMENTS = {
        "Strong Positive": 12.0,
        "Positive": 6.0,
        "Neutral": 0.0,
        "Negative": -6.0,
        "Strong Negative": -12.0,
        "Unknown": 0.0,
    }

    POSITIVE_KEYWORDS = {
        "profit",
        "profits",
        "growth",
        "increase",
        "increased",
        "higher",
        "expansion",
        "contract",
        "agreement",
        "acquisition",
        "dividend",
        "dividends",
        "award",
        "approval",
        "partnership",
        "record",
        "surge",
        "upgrade",
        "investment",
        "launch",
    }

    NEGATIVE_KEYWORDS = {
        "loss",
        "losses",
        "decline",
        "decrease",
        "lower",
        "lawsuit",
        "fine",
        "penalty",
        "downgrade",
        "resignation",
        "investigation",
        "default",
        "debt",
        "warning",
        "suspension",
        "fraud",
        "recall",
        "delay",
        "risk",
    }

    def __init__(
        self,
        neutral_score: float = 50.0,
        minimum_article_weight: float = 0.05,
    ) -> None:
        """
        Initialize the scorer.

        Args:
            neutral_score:
                Starting score before applying news signals.

            minimum_article_weight:
                Minimum weight given to an article.
        """

        if not 0 <= neutral_score <= 100:
            raise ValueError(
                "neutral_score must be between 0 and 100."
            )

        if not 0 <= minimum_article_weight <= 1:
            raise ValueError(
                "minimum_article_weight must be between 0 and 1."
            )

        self.neutral_score = neutral_score
        self.minimum_article_weight = minimum_article_weight

    # ==========================================================
    # Public API
    # ==========================================================

    def score(
        self,
        articles: list[NewsArticleModel],
        summary: NewsSummaryModel | None = None,
    ) -> NewsScoreModel:
        """
        Calculate the aggregated news score.

        Args:
            articles:
                Articles after sentiment analysis.

            summary:
                Optional company-level news summary.

        Returns:
            NewsScoreModel containing the overall score,
            rating, counts, confidence, strengths, and risks.
        """

        if not articles:
            return self._empty_score(summary)

        sentiment_counts = self._count_sentiments(
            articles
        )

        average_sentiment = self._weighted_sentiment(
            articles
        )

        confidence = self._aggregate_confidence(
            articles
        )

        # ------------------------------------------------------
        # Sample-size calibration
        # ------------------------------------------------------

        article_count = len(articles)

        sample_factor = min(
            article_count / 5.0,
            1.0,
        )

        adjusted_sentiment = (
            average_sentiment * sample_factor
        )

        adjusted_confidence = (
            confidence * sample_factor
        )

        # ------------------------------------------------------
        # Base score
        # ------------------------------------------------------

        base_score = self.neutral_score + (
            adjusted_sentiment * 40.0
        )

        impact_adjustment = (
            self._article_impact_adjustment(
                articles
            )
        )

        summary_adjustment = (
            self._summary_adjustment(
                summary
            )
        )

        event_adjustment = (
            self._event_adjustment(
                articles
            )
        )

        # Reduce all adjustments when article coverage is limited.
        impact_adjustment *= sample_factor
        summary_adjustment *= sample_factor
        event_adjustment *= sample_factor

        final_score = (
            base_score
            + impact_adjustment
            + summary_adjustment
            + event_adjustment
        )

        final_score = int(
            round(
                max(
                    0.0,
                    min(final_score, 100.0),
                )
            )
        )

        strengths = self._extract_strengths(
            articles=articles,
            summary=summary,
        )

        risks = self._extract_risks(
            articles=articles,
            summary=summary,
        )

        # ------------------------------------------------------
        # Rating calibration
        # ------------------------------------------------------

        if article_count == 1:
            if final_score >= 55:
                rating = "Bullish"
            elif final_score <= 45:
                rating = "Bearish"
            else:
                rating = "Neutral"

        elif article_count < 3:
            if final_score >= 60:
                rating = "Bullish"
            elif final_score <= 40:
                rating = "Bearish"
            else:
                rating = "Neutral"

        else:
            rating = self._rating(
                final_score
            )

        result = NewsScoreModel(
            score=final_score,
            rating=rating,
            positive_articles=sentiment_counts["positive"],
            neutral_articles=sentiment_counts["neutral"],
            negative_articles=sentiment_counts["negative"],
            average_sentiment=round(
                max(
                    -1.0,
                    min(average_sentiment, 1.0),
                ),
                4,
            ),
            confidence=round(
                adjusted_confidence,
                4,
            ),
            strengths=strengths,
            risks=risks,
        )

        logger.debug(
            "News score calculated: score={}, rating={}, "
            "average_sentiment={}, confidence={}, "
            "article_count={}, sample_factor={}",
            result.score,
            result.rating,
            result.average_sentiment,
            result.confidence,
            article_count,
            sample_factor,
        )

        return result

    # ==========================================================
    # Sentiment Aggregation
    # ==========================================================

    def _weighted_sentiment(
        self,
        articles: list[NewsArticleModel],
    ) -> float:
        """
        Calculate weighted average sentiment.

        Weight is based on:

        - relevance
        - sentiment confidence
        - recency
        """

        weighted_sum = 0.0
        total_weight = 0.0

        for article in articles:
            if article.sentiment is None:
                continue

            weight = self._article_weight(article)

            weighted_sum += (
                article.sentiment.score * weight
            )

            total_weight += weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def _article_weight(
        self,
        article: NewsArticleModel,
    ) -> float:
        """
        Calculate article importance weight.
        """

        relevance = (
            article.relevance_score
            if article.relevance_score is not None
            else 0.5
        )

        confidence = (
            article.sentiment.confidence
            if article.sentiment
            else 0.0
        )

        recency = self._recency_weight(article)

        weight = (
            relevance * 0.45
            + confidence * 0.35
            + recency * 0.20
        )

        return max(
            self.minimum_article_weight,
            min(weight, 1.0),
        )

    @staticmethod
    def _recency_weight(
        article: NewsArticleModel,
    ) -> float:
        """
        Convert article age into a recency weight.

        Approximate weights:

        - 0 to 3 days: 1.00
        - 4 to 7 days: 0.85
        - 8 to 14 days: 0.65
        - 15 to 30 days: 0.40
        - older: 0.20
        """

        if article.published_at is None:
            return 0.4

        from datetime import datetime, timezone

        published_at = article.published_at

        if published_at.tzinfo is None:
            published_at = published_at.replace(
                tzinfo=timezone.utc
            )

        now = datetime.now(timezone.utc)

        age_days = max(
            0,
            (now - published_at).days,
        )

        if age_days <= 3:
            return 1.0

        if age_days <= 7:
            return 0.85

        if age_days <= 14:
            return 0.65

        if age_days <= 30:
            return 0.40

        return 0.20

    @staticmethod
    def _aggregate_confidence(
        articles: list[NewsArticleModel],
    ) -> float:
        """
        Calculate average model confidence.
        """

        confidences = [
            article.sentiment.confidence
            for article in articles
            if article.sentiment is not None
        ]

        if not confidences:
            return 0.0

        average_confidence = (
            sum(confidences) / len(confidences)
        )

        coverage = min(
            len(confidences) / max(len(articles), 1),
            1.0,
        )

        return max(
            0.0,
            min(
                average_confidence * coverage,
                1.0,
            ),
        )

    # ==========================================================
    # Additional Adjustments
    # ==========================================================

    @staticmethod
    def _article_impact_adjustment(
        articles: list[NewsArticleModel],
    ) -> float:
        """
        Apply adjustment from article impact scores.

        The article impact_score field ranges from -1 to 1.
        """

        weighted_impacts: list[float] = []

        for article in articles:
            if article.impact_score is None:
                continue

            relevance = (
                article.relevance_score
                if article.relevance_score is not None
                else 0.5
            )

            weighted_impacts.append(
                article.impact_score * relevance
            )

        if not weighted_impacts:
            return 0.0

        average_impact = (
            sum(weighted_impacts)
            / len(weighted_impacts)
        )

        return average_impact * 8.0

    def _summary_adjustment(
        self,
        summary: NewsSummaryModel | None,
    ) -> float:
        """
        Apply summary-level expected-impact adjustment.
        """

        if summary is None:
            return 0.0

        return self.SUMMARY_IMPACT_ADJUSTMENTS.get(
            summary.expected_impact,
            0.0,
        )

    def _event_adjustment(
        self,
        articles: list[NewsArticleModel],
    ) -> float:
        """
        Apply a small rule-based adjustment for high-impact terms.

        This is intentionally limited so keywords do not overpower
        FinBERT sentiment.
        """

        positive_hits = 0
        negative_hits = 0

        for article in articles:
            text = self._article_text(article)

            positive_hits += sum(
                1
                for keyword in self.POSITIVE_KEYWORDS
                if keyword in text
            )

            negative_hits += sum(
                1
                for keyword in self.NEGATIVE_KEYWORDS
                if keyword in text
            )

        net_hits = positive_hits - negative_hits

        return max(
            -5.0,
            min(net_hits * 0.75, 5.0),
        )

    # ==========================================================
    # Strengths and Risks
    # ==========================================================

    def _extract_strengths(
        self,
        articles: list[NewsArticleModel],
        summary: NewsSummaryModel | None,
    ) -> list[str]:
        """
        Extract concise positive signals.
        """

        strengths: list[str] = []

        if summary:
            strengths.extend(summary.opportunities)

        positive_articles = sorted(
            (
                article
                for article in articles
                if (
                    article.sentiment
                    and article.sentiment.label
                    == "positive"
                )
            ),
            key=self._positive_article_priority,
            reverse=True,
        )

        strengths.extend(
            article.title
            for article in positive_articles[:5]
        )

        return self._unique_strings(
            strengths,
            limit=5,
        )

    def _extract_risks(
        self,
        articles: list[NewsArticleModel],
        summary: NewsSummaryModel | None,
    ) -> list[str]:
        """
        Extract concise negative signals.
        """

        risks: list[str] = []

        if summary:
            risks.extend(summary.risks)

        negative_articles = sorted(
            (
                article
                for article in articles
                if (
                    article.sentiment
                    and article.sentiment.label
                    == "negative"
                )
            ),
            key=self._negative_article_priority,
            reverse=True,
        )

        risks.extend(
            article.title
            for article in negative_articles[:5]
        )

        return self._unique_strings(
            risks,
            limit=5,
        )

    @staticmethod
    def _positive_article_priority(
        article: NewsArticleModel,
    ) -> float:
        """
        Rank positive articles.
        """

        if article.sentiment is None:
            return 0.0

        relevance = article.relevance_score or 0.5

        return (
            article.sentiment.score
            * article.sentiment.confidence
            * relevance
        )

    @staticmethod
    def _negative_article_priority(
        article: NewsArticleModel,
    ) -> float:
        """
        Rank negative articles by severity.
        """

        if article.sentiment is None:
            return 0.0

        relevance = article.relevance_score or 0.5

        return (
            abs(article.sentiment.score)
            * article.sentiment.confidence
            * relevance
        )

    # ==========================================================
    # Counts and Labels
    # ==========================================================

    @staticmethod
    def _count_sentiments(
        articles: list[NewsArticleModel],
    ) -> Counter:
        """
        Count positive, neutral, and negative articles.
        """

        counts = Counter(
            article.sentiment.label
            if article.sentiment
            else "neutral"
            for article in articles
        )

        return Counter(
            {
                "positive": counts.get("positive", 0),
                "neutral": counts.get("neutral", 0),
                "negative": counts.get("negative", 0),
            }
        )

    @staticmethod
    def _rating(
        score: int,
    ) -> str:
        """
        Convert numeric score into news rating.
        """

        if score >= 80:
            return "Strongly Bullish"

        if score >= 62:
            return "Bullish"

        if score >= 42:
            return "Neutral"

        if score >= 22:
            return "Bearish"

        return "Strongly Bearish"

    # ==========================================================
    # Helpers
    # ==========================================================

    def _empty_score(
        self,
        summary: NewsSummaryModel | None,
    ) -> NewsScoreModel:
        """
        Return a safe neutral score when no articles exist.
        """

        adjustment = self._summary_adjustment(summary)

        score = int(
            round(
                max(
                    0,
                    min(
                        self.neutral_score + adjustment,
                        100,
                    ),
                )
            )
        )

        return NewsScoreModel(
            score=score,
            rating=self._rating(score),
            positive_articles=0,
            neutral_articles=0,
            negative_articles=0,
            average_sentiment=0.0,
            confidence=0.0,
            strengths=(
                summary.opportunities[:5]
                if summary
                else []
            ),
            risks=(
                summary.risks[:5]
                if summary
                else []
            ),
        )

    @staticmethod
    def _article_text(
        article: NewsArticleModel,
    ) -> str:
        """
        Combine article fields for keyword detection.
        """

        parts = [
            article.title,
            article.description or "",
            article.content or "",
        ]

        return " ".join(parts).lower()

    @staticmethod
    def _unique_strings(
        values: list[str],
        limit: int,
    ) -> list[str]:
        """
        Remove duplicate and empty strings while preserving order.
        """

        unique_values: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned = str(value).strip()

            if not cleaned:
                continue

            normalized = cleaned.lower()

            if normalized in seen:
                continue

            seen.add(normalized)
            unique_values.append(cleaned)

            if len(unique_values) >= limit:
                break

        return unique_values