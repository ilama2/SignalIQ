"""
SignalIQ - News Sentiment Analyzer

Analyzes the financial sentiment of company news articles.

This module is responsible only for sentiment analysis.
It does not collect, summarize, or score company news.
"""

from __future__ import annotations

from collections.abc import Iterable

from loguru import logger

from .models import NewsArticleModel, SentimentModel


class NewsSentimentAnalyzer:
    """
    Analyze financial news sentiment using FinBERT.

    FinBERT labels:
    - positive
    - neutral
    - negative
    """

    MODEL_NAME = "ProsusAI/finbert"

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        max_length: int = 512,
        batch_size: int = 8,
        device: int = -1,
    ) -> None:
        """
        Initialize the sentiment analyzer.

        Args:
            model_name:
                Hugging Face sentiment model.

            max_length:
                Maximum number of tokens processed for each article.

            batch_size:
                Number of articles processed in one batch.

            device:
                Device used by Hugging Face.

                -1 = CPU
                 0 = first CUDA GPU
        """

        if max_length <= 0:
            raise ValueError("max_length must be greater than zero.")

        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero.")

        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.device = device

        self._pipeline = None

    # ==========================================================
    # Model Loading
    # ==========================================================

    def _load_pipeline(self):
        """
        Load the Hugging Face sentiment pipeline lazily.

        The model is loaded only when sentiment analysis is first used.
        """

        if self._pipeline is not None:
            return self._pipeline

        try:
            from transformers import pipeline

            logger.info(
                "Loading sentiment model: {}",
                self.model_name,
            )

            self._pipeline = pipeline(
                task="text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                device=self.device,
            )

            logger.success(
                "Sentiment model loaded successfully."
            )

            return self._pipeline

        except ImportError as exc:
            raise ImportError(
                "The transformers package is required. "
                "Install it using: uv add transformers torch"
            ) from exc

        except Exception as exc:
            logger.exception(
                "Could not load sentiment model: {}",
                exc,
            )

            raise RuntimeError(
                f"Could not load sentiment model "
                f"'{self.model_name}'."
            ) from exc

    # ==========================================================
    # Public API
    # ==========================================================

    def analyze_text(
        self,
        text: str,
    ) -> SentimentModel:
        """
        Analyze sentiment for one text.

        Args:
            text:
                News title, description, or article content.

        Returns:
            Structured sentiment result.
        """

        cleaned_text = self._clean_text(text)

        if not cleaned_text:
            return self._neutral_result()

        model = self._load_pipeline()

        try:
            result = model(
                cleaned_text,
                truncation=True,
                max_length=self.max_length,
            )[0]

            return self._normalize_result(result)

        except Exception as exc:
            logger.warning(
                "Sentiment analysis failed: {}",
                exc,
            )

            return self._neutral_result()

    def analyze_article(
        self,
        article: NewsArticleModel,
    ) -> NewsArticleModel:
        """
        Analyze sentiment for one news article.

        The sentiment result is attached directly to the article.
        """

        text = self._article_text(article)

        article.sentiment = self.analyze_text(text)

        return article

    def analyze_articles(
        self,
        articles: Iterable[NewsArticleModel],
    ) -> list[NewsArticleModel]:
        """
        Analyze sentiment for multiple articles using batch inference.

        Args:
            articles:
                News articles returned by NewsCollector.

        Returns:
            Articles containing sentiment results.
        """

        article_list = list(articles)

        if not article_list:
            return []

        texts = [
            self._article_text(article)
            for article in article_list
        ]

        valid_indices: list[int] = []
        valid_texts: list[str] = []

        for index, text in enumerate(texts):
            cleaned_text = self._clean_text(text)

            if cleaned_text:
                valid_indices.append(index)
                valid_texts.append(cleaned_text)
            else:
                article_list[index].sentiment = (
                    self._neutral_result()
                )

        if not valid_texts:
            return article_list

        model = self._load_pipeline()

        try:
            results = model(
                valid_texts,
                truncation=True,
                max_length=self.max_length,
                batch_size=self.batch_size,
            )

            for article_index, raw_result in zip(
                valid_indices,
                results,
                strict=True,
            ):
                article_list[article_index].sentiment = (
                    self._normalize_result(raw_result)
                )

        except Exception as exc:
            logger.warning(
                "Batch sentiment analysis failed: {}",
                exc,
            )

            # Fall back to one article at a time so one invalid
            # input does not fail the entire company.
            for article_index in valid_indices:
                article_list[article_index].sentiment = (
                    self.analyze_text(
                        texts[article_index]
                    )
                )

        return article_list

    # ==========================================================
    # Result Normalization
    # ==========================================================

    def _normalize_result(
        self,
        result: dict,
    ) -> SentimentModel:
        """
        Convert a Hugging Face result into SentimentModel.
        """

        raw_label = str(
            result.get("label", "neutral")
        ).lower().strip()

        confidence = self._safe_probability(
            result.get("score", 0.0)
        )

        label = self._normalize_label(raw_label)

        signed_score = self._signed_score(
            label=label,
            confidence=confidence,
        )

        return SentimentModel(
            label=label,
            confidence=confidence,
            score=signed_score,
        )

    @staticmethod
    def _normalize_label(
        label: str,
    ) -> str:
        """
        Normalize different model label formats.

        Supports:
        - positive / neutral / negative
        - LABEL_0 / LABEL_1 / LABEL_2

        ProsusAI/finbert usually returns text labels directly.
        """

        normalized = label.lower().strip()

        label_mapping = {
            "positive": "positive",
            "neutral": "neutral",
            "negative": "negative",

            # Common three-class fallback mapping.
            "label_0": "negative",
            "label_1": "neutral",
            "label_2": "positive",
        }

        if normalized not in label_mapping:
            logger.warning(
                "Unknown sentiment label '{}'; "
                "using neutral.",
                label,
            )

            return "neutral"

        return label_mapping[normalized]

    @staticmethod
    def _signed_score(
        label: str,
        confidence: float,
    ) -> float:
        """
        Convert sentiment label and confidence to a -1 to 1 score.

        Examples:
            Positive with confidence 0.90 -> 0.90
            Neutral with confidence 0.85  -> 0.00
            Negative with confidence 0.75 -> -0.75
        """

        if label == "positive":
            return round(confidence, 4)

        if label == "negative":
            return round(-confidence, 4)

        return 0.0

    # ==========================================================
    # Article Text
    # ==========================================================

    @staticmethod
    def _article_text(
        article: NewsArticleModel,
    ) -> str:
        """
        Build the text sent to the sentiment model.

        Title receives priority because it usually contains the
        main financial event.
        """

        parts = [article.title]

        if article.description:
            parts.append(article.description)

        if article.content:
            parts.append(article.content)

        return " ".join(parts)

    @staticmethod
    def _clean_text(
        text: str | None,
    ) -> str:
        """
        Remove unnecessary whitespace from input text.
        """

        if not text:
            return ""

        return " ".join(str(text).split())

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _safe_probability(
        value: object,
    ) -> float:
        """
        Convert a model confidence value safely to 0-1.
        """

        try:
            probability = float(value)
        except (TypeError, ValueError):
            return 0.0

        probability = max(
            0.0,
            min(probability, 1.0),
        )

        return round(probability, 4)

    @staticmethod
    def _neutral_result() -> SentimentModel:
        """
        Return a safe neutral result when no analysis is possible.
        """

        return SentimentModel(
            label="neutral",
            confidence=0.0,
            score=0.0,
        )

