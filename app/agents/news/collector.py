"""
SignalIQ - News Collector

Collects, normalizes, filters, and deduplicates company news.

This module is responsible only for news collection.
It does not perform sentiment analysis, summarization, or scoring.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from loguru import logger
from pydantic import ValidationError

from app.clients.news_client import NewsClient

from .models import NewsArticleModel, NewsSourceModel


class NewsCollector:
    """
    Collect and normalize news articles for a company.

    Responsibilities:
    - Request articles from the news API client.
    - Normalize different API response formats.
    - Remove duplicate articles.
    - Filter irrelevant articles.
    - Return validated NewsArticleModel objects.
    """

    def __init__(
        self,
        client: NewsClient | None = None,
        max_articles: int = 20,
        default_language: str = "en",
    ) -> None:
        """
        Initialize the news collector.

        Args:
            client:
                Optional NewsClient instance. A default client is created
                when one is not provided.

            max_articles:
                Maximum number of articles returned for one company.

            default_language:
                Default language used when the article does not specify one.
        """

        if max_articles <= 0:
            raise ValueError("max_articles must be greater than zero.")

        self.client = client or NewsClient()
        self.max_articles = max_articles
        self.default_language = default_language

    # ==========================================================
    # Public API
    # ==========================================================

    def collect(
        self,
        symbol: str,
        company_name: str,
        aliases: list[str] | None = None,
    ) -> list[NewsArticleModel]:
        """
        Collect, normalize, deduplicate, and filter company news.

        Returns:
            A list of normalized and relevant NewsArticleModel objects.
        """

        symbol = str(symbol).strip()
        company_name = str(company_name).strip()
        aliases = aliases or []

        if not symbol:
            raise ValueError("symbol cannot be empty.")

        if not company_name:
            raise ValueError("company_name cannot be empty.")

        logger.info(
            "Collecting news for {} using search name '{}'.",
            symbol,
            company_name,
        )

        # ----------------------------------------------------------
        # 1. Fetch raw articles from NewsAPI
        # ----------------------------------------------------------

        try:
            raw_articles = self.client.get_company_news(
                company_name=company_name,
                page_size=self.max_articles,
            )

        except Exception as exc:
            logger.exception(
                "Failed to fetch news for {} using '{}': {}",
                symbol,
                company_name,
                exc,
            )
            raise

        if not isinstance(raw_articles, list):
            logger.warning(
                "News client returned an invalid response type for {}: {}",
                symbol,
                type(raw_articles).__name__,
            )
            return []

        logger.info(
            "Raw articles returned for '{}': {}",
            company_name,
            len(raw_articles),
        )

        for raw_article in raw_articles[:5]:
            if isinstance(raw_article, dict):
                logger.debug(
                    "Raw article title: {}",
                    raw_article.get("title"),
                )

        # ----------------------------------------------------------
        # 2. Build relevance terms
        # ----------------------------------------------------------

        search_terms = [
            company_name,
            *aliases,
        ]

        # Known useful aliases.
        if company_name.casefold() == "saudi aramco":
            search_terms.extend(
                [
                    "Aramco",
                    "Saudi Arabian Oil Company",
                ]
            )

        search_terms = self._unique_strings(search_terms)

        logger.debug(
            "Relevance terms for {}: {}",
            symbol,
            search_terms,
        )

        # ----------------------------------------------------------
        # 3. Normalize, filter, and deduplicate
        # ----------------------------------------------------------

        collected_articles: list[NewsArticleModel] = []

        seen_titles: set[str] = set()
        seen_urls: set[str] = set()

        normalization_failures = 0
        irrelevant_count = 0
        duplicate_count = 0

        for raw_article in raw_articles:
            if not isinstance(raw_article, dict):
                normalization_failures += 1
                logger.debug(
                    "Skipping non-dictionary article response: {}",
                    type(raw_article).__name__,
                )
                continue

            try:
                article = self._normalize_article(
                    raw_article,
                )

            except Exception as exc:
                normalization_failures += 1
                logger.debug(
                    "Unable to normalize article '{}': {}",
                    raw_article.get("title"),
                    exc,
                )
                continue

            if article is None:
                normalization_failures += 1
                continue

            # ------------------------------------------------------
            # Relevance filtering
            # ------------------------------------------------------

            title_text = article.title.casefold()
            description_text = (article.description or "").casefold()
            content_text = (article.content or "").casefold()

            normalized_terms = [
                term.strip().casefold()
                for term in search_terms
                if term and len(term.strip()) >= 3
            ]

            title_matches = [
                term
                for term in normalized_terms
                if term in title_text
            ]

            description_matches = [
                term
                for term in normalized_terms
                if term in description_text
            ]

            content_matches = [
                term
                for term in normalized_terms
                if term in content_text
            ]

            relevance_score = 0.0

            if title_matches:
                relevance_score += 0.70

            if description_matches:
                relevance_score += 0.20

            if content_matches:
                relevance_score += 0.10

            article.relevance_score = round(relevance_score, 4)

            # Require a direct company mention in the headline.
            if not title_matches:
                irrelevant_count += 1

                logger.debug(
                    "Skipping article because company is not in title: {}",
                    article.title,
                )

                continue

            if article.relevance_score < 0.70:
                irrelevant_count += 1

                logger.debug(
                    "Skipping low-relevance article '{}' with score={}.",
                    article.title,
                    article.relevance_score,
                )

                continue            

            # ------------------------------------------------------
            # Duplicate filtering
            # ------------------------------------------------------

            normalized_title = " ".join(
                article.title.casefold().split()
            )

            normalized_url = (
                str(article.url).strip().casefold()
                if article.url
                else ""
            )

            if normalized_title in seen_titles:
                duplicate_count += 1

                logger.debug(
                    "Skipping duplicate title: {}",
                    article.title,
                )
                continue

            if normalized_url and normalized_url in seen_urls:
                duplicate_count += 1

                logger.debug(
                    "Skipping duplicate URL: {}",
                    article.url,
                )
                continue

            seen_titles.add(normalized_title)

            if normalized_url:
                seen_urls.add(normalized_url)

            collected_articles.append(article)

            if len(collected_articles) >= self.max_articles:
                break

        # ----------------------------------------------------------
        # 4. Final logging
        # ----------------------------------------------------------

        logger.info(
            "News collection completed for {}: "
            "raw={}, accepted={}, irrelevant={}, duplicates={}, "
            "normalization_failures={}",
            symbol,
            len(raw_articles),
            len(collected_articles),
            irrelevant_count,
            duplicate_count,
            normalization_failures,
        )

        logger.info(
            "Articles remaining after collector filtering: {}",
            len(collected_articles),
        )

        return collected_articles

    # ==========================================================
    # API Search
    # ==========================================================

    def _search(
        self,
        query: str,
    ) -> list[dict[str, Any]]:
        """
        Search for news using the configured NewsClient.

        This method supports several common NewsClient method names so the
        collector remains compatible with different client implementations.
        """

        if hasattr(self.client, "search_news"):
            response = self.client.search_news(
                query=query,
                limit=self.max_articles,
            )

        elif hasattr(self.client, "search"):
            response = self.client.search(
                query=query,
                limit=self.max_articles,
            )

        elif hasattr(self.client, "get_news"):
            response = self.client.get_news(
                query=query,
                limit=self.max_articles,
            )

        else:
            raise AttributeError(
                "NewsClient must implement search_news(), search(), "
                "or get_news()."
            )

        return self._extract_articles_from_response(response)

    @staticmethod
    def _extract_articles_from_response(
        response: Any,
    ) -> list[dict[str, Any]]:
        """
        Extract an article list from common news API response formats.
        """

        if response is None:
            return []

        if isinstance(response, list):
            return [
                item
                for item in response
                if isinstance(item, dict)
            ]

        if not isinstance(response, dict):
            logger.warning(
                "Unsupported news response type: {}",
                type(response).__name__,
            )
            return []

        possible_keys = (
            "articles",
            "news",
            "results",
            "data",
            "items",
        )

        for key in possible_keys:
            value = response.get(key)

            if isinstance(value, list):
                return [
                    item
                    for item in value
                    if isinstance(item, dict)
                ]

            if isinstance(value, dict):
                nested_articles = value.get("articles")

                if isinstance(nested_articles, list):
                    return [
                        item
                        for item in nested_articles
                        if isinstance(item, dict)
                    ]

        return []

    # ==========================================================
    # Normalization
    # ==========================================================

    def _normalize_articles(
        self,
        raw_articles: list[dict[str, Any]],
    ) -> list[NewsArticleModel]:
        """
        Convert raw API articles into NewsArticleModel objects.
        """

        normalized: list[NewsArticleModel] = []

        for raw_article in raw_articles:
            try:
                article = self._normalize_article(raw_article)

                if article is not None:
                    normalized.append(article)

            except ValidationError as exc:
                logger.debug(
                    "Skipping invalid article: {}",
                    exc,
                )

            except Exception as exc:
                logger.debug(
                    "Failed to normalize article: {}",
                    exc,
                )

        return normalized

    def _normalize_article(
        self,
        article: dict[str, Any],
    ) -> NewsArticleModel | None:
        """
        Normalize one raw article.

        Supports common field names returned by:
        - NewsAPI
        - GNews
        - Finnhub
        - Yahoo Finance
        - Custom news services
        """

        title = self._first_non_empty(
            article.get("title"),
            article.get("headline"),
            article.get("name"),
        )

        if not title:
            return None

        description = self._first_non_empty(
            article.get("description"),
            article.get("summary"),
            article.get("snippet"),
            article.get("excerpt"),
        )

        content = self._first_non_empty(
            article.get("content"),
            article.get("body"),
            article.get("text"),
        )

        url = self._clean_url(
            self._first_non_empty(
                article.get("url"),
                article.get("link"),
                article.get("article_url"),
                article.get("web_url"),
            )
        )

        image_url = self._clean_url(
            self._first_non_empty(
                article.get("image_url"),
                article.get("image"),
                article.get("urlToImage"),
                article.get("thumbnail"),
                article.get("banner_image"),
            )
        )

        source = self._normalize_source(
            article.get("source"),
            article,
            url,
        )

        published_at = self._parse_datetime(
            self._first_non_empty(
                article.get("published_at"),
                article.get("publishedAt"),
                article.get("published"),
                article.get("datetime"),
                article.get("date"),
                article.get("created_at"),
                article.get("providerPublishTime"),
            )
        )

        author = self._first_non_empty(
            article.get("author"),
            article.get("byline"),
            article.get("creator"),
        )

        language = self._first_non_empty(
            article.get("language"),
            article.get("lang"),
            self.default_language,
        )

        return NewsArticleModel(
            title=str(title).strip(),
            description=self._clean_text(description),
            content=self._clean_text(content),
            url=url,
            image_url=image_url,
            source=source,
            author=str(author).strip() if author else None,
            published_at=published_at,
            language=str(language).lower().strip(),
        )

    def _normalize_source(
        self,
        source_value: Any,
        article: dict[str, Any],
        article_url: str | None,
    ) -> NewsSourceModel:
        """
        Normalize article publisher information.
        """

        source_name: str | None = None
        source_url: str | None = None

        if isinstance(source_value, dict):
            source_name = self._first_non_empty(
                source_value.get("name"),
                source_value.get("title"),
                source_value.get("domain"),
            )

            source_url = self._first_non_empty(
                source_value.get("url"),
                source_value.get("homepage"),
            )

        elif isinstance(source_value, str):
            source_name = source_value

        source_name = self._first_non_empty(
            source_name,
            article.get("publisher"),
            article.get("provider"),
            article.get("site"),
        )

        source_url = self._clean_url(source_url)

        if not source_name and article_url:
            source_name = self._extract_domain(article_url)

        return NewsSourceModel(
            name=str(source_name).strip()
            if source_name
            else "Unknown",
            url=source_url,
        )

    # ==========================================================
    # Relevance Filtering
    # ==========================================================

    def _filter_relevant_articles(
        self,
        articles: list[NewsArticleModel],
        symbol: str,
        company_name: str,
        aliases: list[str],
    ) -> list[NewsArticleModel]:
        """
        Remove articles that do not appear relevant to the company.

        The calculated relevance score is stored inside each article.
        """

        company_terms = self._company_terms(
            symbol=symbol,
            company_name=company_name,
            aliases=aliases,
        )

        relevant_articles: list[NewsArticleModel] = []

        for article in articles:
            relevance_score = self._calculate_relevance(
                article=article,
                company_terms=company_terms,
            )

            article.relevance_score = relevance_score

            if relevance_score >= 0.25:
                relevant_articles.append(article)

        return relevant_articles

    @staticmethod
    def _calculate_relevance(
        article: NewsArticleModel,
        company_terms: list[str],
    ) -> float:
        """
        Calculate a simple rule-based article relevance score.

        Title matches receive more weight than description or content matches.
        """

        title = article.title.lower()
        description = (article.description or "").lower()
        content = (article.content or "").lower()

        title_matches = sum(
            1 for term in company_terms if term in title
        )

        description_matches = sum(
            1 for term in company_terms if term in description
        )

        content_matches = sum(
            1 for term in company_terms if term in content
        )

        relevance = (
            title_matches * 0.60
            + description_matches * 0.25
            + content_matches * 0.15
        )

        return round(min(relevance, 1.0), 4)

    # ==========================================================
    # Deduplication
    # ==========================================================

    @staticmethod
    def _deduplicate(
        articles: list[NewsArticleModel],
    ) -> list[NewsArticleModel]:
        """
        Remove duplicate articles using normalized URLs and titles.
        """

        unique_articles: list[NewsArticleModel] = []

        seen_urls: set[str] = set()
        seen_titles: set[str] = set()

        for article in articles:
            normalized_title = NewsCollector._normalize_title(
                article.title
            )

            normalized_url = (
                str(article.url).rstrip("/")
                if article.url
                else None
            )

            if normalized_url and normalized_url in seen_urls:
                continue

            if normalized_title in seen_titles:
                continue

            if normalized_url:
                seen_urls.add(normalized_url)

            seen_titles.add(normalized_title)
            unique_articles.append(article)

        return unique_articles

    # ==========================================================
    # Search Terms
    # ==========================================================

    @staticmethod
    def _build_search_terms(
        symbol: str,
        company_name: str,
        aliases: list[str] | None,
    ) -> list[str]:
        """
        Build news search queries for the company.
        """

        search_terms = [
            company_name,
            f'"{company_name}" stock',
            f'"{company_name}" Saudi',
        ]

        if symbol:
            search_terms.append(
                f'"{company_name}" {symbol}'
            )

        for alias in aliases or []:
            cleaned_alias = alias.strip()

            if cleaned_alias:
                search_terms.append(cleaned_alias)

        # Preserve order while removing duplicates.
        return list(dict.fromkeys(search_terms))

    @staticmethod
    def _company_terms(
        symbol: str,
        company_name: str,
        aliases: list[str],
    ) -> list[str]:
        """
        Create normalized company terms used for relevance filtering.
        """

        terms = [
            company_name.lower().strip(),
            symbol.lower().strip(),
        ]

        terms.extend(
            alias.lower().strip()
            for alias in aliases
            if alias.strip()
        )

        company_words = [
            word
            for word in company_name.lower().split()
            if len(word) >= 4
        ]

        terms.extend(company_words)

        return list(
            dict.fromkeys(
                term for term in terms if term
            )
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _article_sort_key(
        article: NewsArticleModel,
    ) -> datetime:
        """
        Return a timezone-aware date for article sorting.
        """

        published_at = article.published_at

        if published_at is None:
            return datetime.min.replace(tzinfo=timezone.utc)

        if published_at.tzinfo is None:
            return published_at.replace(tzinfo=timezone.utc)

        return published_at

    @staticmethod
    def _parse_datetime(
        value: Any,
    ) -> datetime | None:
        """
        Parse common datetime representations.
        """

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, (int, float)):
            timestamp = float(value)

            # Millisecond Unix timestamps are usually greater than 10^12.
            if timestamp > 10_000_000_000:
                timestamp /= 1000

            try:
                return datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc,
                )
            except (ValueError, OSError, OverflowError):
                return None

        if not isinstance(value, str):
            return None

        value = value.strip()

        if not value:
            return None

        normalized_value = value.replace("Z", "+00:00")

        try:
            return datetime.fromisoformat(normalized_value)
        except ValueError:
            pass

        known_formats = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%d %b %Y %H:%M:%S",
        )

        for date_format in known_formats:
            try:
                parsed = datetime.strptime(
                    value,
                    date_format,
                )

                if parsed.tzinfo is None:
                    parsed = parsed.replace(
                        tzinfo=timezone.utc
                    )

                return parsed

            except ValueError:
                continue

        logger.debug(
            "Unable to parse article datetime: {}",
            value,
        )

        return None

    @staticmethod
    def _first_non_empty(
        *values: Any,
    ) -> Any:
        """
        Return the first value that is not None or empty.
        """

        for value in values:
            if value is None:
                continue

            if isinstance(value, str):
                if value.strip():
                    return value
                continue

            return value

        return None

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str | None:
        """
        Normalize whitespace in article text.
        """

        if value is None:
            return None

        text = str(value).strip()

        if not text:
            return None

        return " ".join(text.split())

    @staticmethod
    def _clean_url(
        value: Any,
    ) -> str | None:
        """
        Return a valid HTTP URL or None.
        """

        if value is None:
            return None

        url = str(value).strip()

        if not url:
            return None

        if not url.startswith(("http://", "https://")):
            return None

        return url

    @staticmethod
    def _extract_domain(
        url: str,
    ) -> str:
        """
        Extract a readable domain from an article URL.
        """

        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain or "Unknown"

    @staticmethod
    def _normalize_title(
        title: str,
    ) -> str:
        """
        Normalize article titles for duplicate detection.
        """

        normalized = title.lower().strip()

        punctuation = ".,:;!?-'\"()[]{}|"

        for character in punctuation:
            normalized = normalized.replace(character, " ")

        return " ".join(normalized.split())

    
    @staticmethod
    def _unique_strings(
        values: list[str],
    ) -> list[str]:
        """
        Remove duplicate strings while preserving their order.
        """

        unique_values: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned_value = " ".join(
                str(value).strip().split()
            )

            if not cleaned_value:
                continue

            normalized_value = cleaned_value.casefold()

            if normalized_value in seen:
                continue

            seen.add(normalized_value)
            unique_values.append(cleaned_value)

        return unique_values