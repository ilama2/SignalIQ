"""
SignalIQ - News Summarizer

Produces an investment-focused summary from analyzed news articles.

This module does not collect articles or calculate the final news score.
It summarizes the main events, opportunities, risks, and expected impact.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from loguru import logger
from pydantic import ValidationError
from .prompts import news_summary_prompt
from .models import (
    NewsArticleModel,
    NewsSummaryModel,
)


class NewsSummarizer:
    """
    Summarize company news for investment analysis.

    The summarizer supports two modes:

    1. LLM mode:
       Pass an LLM callable that accepts a prompt and returns text.

    2. Rule-based fallback:
       If no LLM is supplied, the summarizer generates a deterministic
       summary from article titles and sentiment results.
    """

    def __init__(
        self,
        llm: Callable[[str], Any] | None = None,
        max_articles: int = 12,
        max_text_length: int = 12_000,
    ) -> None:
        """
        Initialize the news summarizer.

        Args:
            llm:
                Optional callable used to invoke an LLM.

                The callable should accept a string prompt and return:
                - a string,
                - a dictionary,
                - or an object containing a ``content`` attribute.

            max_articles:
                Maximum number of articles included in the prompt.

            max_text_length:
                Maximum combined character length sent to the LLM.
        """

        if max_articles <= 0:
            raise ValueError(
                "max_articles must be greater than zero."
            )

        if max_text_length <= 0:
            raise ValueError(
                "max_text_length must be greater than zero."
            )

        self.llm = llm
        self.max_articles = max_articles
        self.max_text_length = max_text_length

    # ==========================================================
    # Public API
    # ==========================================================

    def summarize(
        self,
        symbol: str,
        company_name: str,
        articles: list[NewsArticleModel],
    ) -> NewsSummaryModel:
        """
        Generate an investment-focused summary.

        Args:
            symbol:
                Saudi Exchange company symbol.

            company_name:
                Company name.

            articles:
                News articles, preferably after sentiment analysis.

        Returns:
            NewsSummaryModel containing:
            - overall summary
            - key events
            - opportunities
            - risks
            - expected impact
        """

        symbol = str(symbol).strip()
        company_name = company_name.strip()

        if not symbol:
            raise ValueError("symbol cannot be empty.")

        if not company_name:
            raise ValueError("company_name cannot be empty.")

        if not articles:
            return self._empty_summary(
                company_name=company_name,
            )

        selected_articles = self._select_articles(
            articles
        )

        if self.llm is None:
            logger.info(
                "No LLM configured. Using rule-based summary for {}.",
                symbol,
            )

            return self._rule_based_summary(
                company_name=company_name,
                articles=selected_articles,
            )

        try:
            prompt = self._build_prompt(
                symbol=symbol,
                company_name=company_name,
                articles=selected_articles,
            )

            raw_response = self.llm(prompt)

            response_text = self._extract_response_text(
                raw_response
            )

            parsed_summary = self._parse_llm_response(
                response_text
            )

            logger.success(
                "News summary generated for {}.",
                symbol,
            )

            return parsed_summary

        except Exception as exc:
            logger.warning(
                "LLM summarization failed for {}: {}. "
                "Using rule-based fallback.",
                symbol,
                exc,
            )

            return self._rule_based_summary(
                company_name=company_name,
                articles=selected_articles,
            )

    # ==========================================================
    # Article Selection
    # ==========================================================

    def _select_articles(
        self,
        articles: list[NewsArticleModel],
    ) -> list[NewsArticleModel]:
        """
        Select the most useful articles for summarization.

        Priority:
        1. Higher relevance
        2. More recent publication date
        3. Stronger sentiment confidence
        """

        sorted_articles = sorted(
            articles,
            key=self._article_priority,
            reverse=True,
        )

        return sorted_articles[: self.max_articles]

    @staticmethod
    def _article_priority(
        article: NewsArticleModel,
    ) -> tuple[float, float, float]:
        """
        Return an article-ranking tuple.
        """

        relevance = article.relevance_score or 0.0

        timestamp = (
            article.published_at.timestamp()
            if article.published_at
            else 0.0
        )

        sentiment_confidence = (
            article.sentiment.confidence
            if article.sentiment
            else 0.0
        )

        return (
            relevance,
            timestamp,
            sentiment_confidence,
        )

    # ==========================================================
    # Prompt Construction
    # ==========================================================

    def _build_prompt(
        self,
        symbol: str,
        company_name: str,
        articles: list[NewsArticleModel],
    ) -> str:
        article_text = self._format_articles(articles)

        return news_summary_prompt(
            symbol=symbol,
            company_name=company_name,
            articles=article_text,
        )

    # ==========================================================
    # LLM Response Parsing
    # ==========================================================

    def _parse_llm_response(
        self,
        response_text: str,
    ) -> NewsSummaryModel:
        """
        Parse and validate the LLM JSON response.
        """

        cleaned_response = self._clean_json_text(
            response_text
        )

        try:
            data = json.loads(cleaned_response)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM response is not valid JSON."
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "LLM summary must return a JSON object."
            )

        data["summary"] = str(
            data.get(
                "summary",
                "No summary was generated.",
            )
        ).strip()

        data["key_events"] = self._safe_string_list(
            data.get("key_events")
        )

        data["opportunities"] = self._safe_string_list(
            data.get("opportunities")
        )

        data["risks"] = self._safe_string_list(
            data.get("risks")
        )

        data["expected_impact"] = (
            self._normalize_expected_impact(
                data.get("expected_impact")
            )
        )

        try:
            return NewsSummaryModel(**data)

        except ValidationError as exc:
            raise ValueError(
                "LLM response did not match NewsSummaryModel."
            ) from exc

    @staticmethod
    def _extract_response_text(
        response: Any,
    ) -> str:
        """
        Extract text from common LLM response formats.
        """

        if response is None:
            raise ValueError(
                "The LLM returned an empty response."
            )

        if isinstance(response, str):
            return response

        if isinstance(response, dict):
            if "content" in response:
                return str(response["content"])

            if "text" in response:
                return str(response["text"])

            return json.dumps(
                response,
                ensure_ascii=False,
            )

        content = getattr(
            response,
            "content",
            None,
        )

        if content is not None:
            return str(content)

        text = getattr(
            response,
            "text",
            None,
        )

        if text is not None:
            return str(text)

        return str(response)

    @staticmethod
    def _clean_json_text(
        text: str,
    ) -> str:
        """
        Remove common Markdown wrappers from JSON.
        """

        cleaned = text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]

        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    # ==========================================================
    # Rule-Based Fallback
    # ==========================================================

    def _rule_based_summary(
        self,
        company_name: str,
        articles: list[NewsArticleModel],
    ) -> NewsSummaryModel:
        """
        Generate a summary without an LLM.

        This fallback allows the pipeline to continue when:
        - no LLM is configured,
        - an API call fails,
        - or the LLM returns invalid output.
        """

        positive_articles = [
            article
            for article in articles
            if (
                article.sentiment
                and article.sentiment.label == "positive"
            )
        ]

        negative_articles = [
            article
            for article in articles
            if (
                article.sentiment
                and article.sentiment.label == "negative"
            )
        ]

        neutral_articles = [
            article
            for article in articles
            if (
                not article.sentiment
                or article.sentiment.label == "neutral"
            )
        ]

        sentiment_scores = [
            article.sentiment.score
            for article in articles
            if article.sentiment
        ]

        average_sentiment = (
            sum(sentiment_scores)
            / max(len(sentiment_scores), 1)
        )

        expected_impact = self._impact_from_score(
            average_sentiment
        )

        key_events = [
            article.title
            for article in articles[:5]
        ]

        opportunities = [
            article.title
            for article in positive_articles[:3]
        ]

        risks = [
            article.title
            for article in negative_articles[:3]
        ]

        # ------------------------------------------------------
        # Limited coverage: only one article
        # ------------------------------------------------------

        if len(articles) == 1:
            article = articles[0]

            sentiment_label = (
                article.sentiment.label
                if article.sentiment
                else "neutral"
            )

            if sentiment_label == "negative":
                summary = (
                    f"Limited recent coverage for {company_name} "
                    "shows a negative signal based on one article."
                )
                expected_impact = "Negative"

            elif sentiment_label == "positive":
                summary = (
                    f"Limited recent coverage for {company_name} "
                    "shows a positive signal based on one article."
                )
                expected_impact = "Positive"

            else:
                summary = (
                    f"Limited recent coverage for {company_name} "
                    "does not show a clear directional signal."
                )
                expected_impact = "Neutral"

        # ------------------------------------------------------
        # Multiple articles
        # ------------------------------------------------------

        elif average_sentiment >= 0.35:
            summary = (
                f"Recent news coverage for {company_name} is "
                f"predominantly positive. "
                f"{len(positive_articles)} article(s) were positive, "
                f"{len(neutral_articles)} neutral, and "
                f"{len(negative_articles)} negative."
            )

        elif average_sentiment <= -0.35:
            summary = (
                f"Recent news coverage for {company_name} is "
                f"predominantly negative. "
                f"{len(negative_articles)} article(s) highlighted "
                f"potential concerns, compared with "
                f"{len(positive_articles)} positive article(s)."
            )

        else:
            summary = (
                f"Recent news coverage for {company_name} is mixed "
                f"or neutral. The available articles include "
                f"{len(positive_articles)} positive, "
                f"{len(neutral_articles)} neutral, and "
                f"{len(negative_articles)} negative article(s)."
            )

        return NewsSummaryModel(
            summary=summary,
            key_events=key_events,
            opportunities=opportunities,
            risks=risks,
            expected_impact=expected_impact,
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _impact_from_score(
        score: float,
    ) -> str:
        """
        Convert average sentiment into expected impact.
        """

        if score >= 0.70:
            return "Strong Positive"

        if score >= 0.20:
            return "Positive"

        if score <= -0.70:
            return "Strong Negative"

        if score <= -0.20:
            return "Negative"

        return "Neutral"

    @staticmethod
    def _normalize_expected_impact(
        value: Any,
    ) -> str:
        """
        Normalize LLM impact labels.
        """

        normalized = str(
            value or "Unknown"
        ).strip().lower()

        mapping = {
            "strong positive": "Strong Positive",
            "strongly positive": "Strong Positive",
            "very positive": "Strong Positive",
            "positive": "Positive",
            "neutral": "Neutral",
            "mixed": "Neutral",
            "negative": "Negative",
            "strong negative": "Strong Negative",
            "strongly negative": "Strong Negative",
            "very negative": "Strong Negative",
            "unknown": "Unknown",
        }

        return mapping.get(
            normalized,
            "Unknown",
        )

    @staticmethod
    def _safe_string_list(
        value: Any,
    ) -> list[str]:
        """
        Convert an arbitrary value into a clean string list.
        """

        if value is None:
            return []

        if isinstance(value, str):
            cleaned = value.strip()

            return [cleaned] if cleaned else []

        if not isinstance(value, list):
            return []

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    @staticmethod
    def _empty_summary(
        company_name: str,
    ) -> NewsSummaryModel:
        """
        Return a safe summary when no articles are available.
        """

        return NewsSummaryModel(
            summary=(
                f"No relevant recent news articles were found "
                f"for {company_name}."
            ),
            key_events=[],
            opportunities=[],
            risks=[],
            expected_impact="Unknown",
        )