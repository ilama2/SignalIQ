"""
SignalIQ - NewsAPI Client

Responsible only for communicating with NewsAPI.

This client:
- Validates configuration.
- Sends requests to NewsAPI.
- Handles HTTP and NewsAPI errors.
- Supports company, market, and general news searches.
- Returns normalized raw article dictionaries.
"""

from __future__ import annotations

from typing import Any

import requests
from loguru import logger

from app.core import settings


class NewsClient:
    """Production-ready client for NewsAPI."""

    def __init__(
        self,
        base_url: str = "https://newsapi.org/v2",
    ) -> None:
        """
        Initialize the NewsAPI client.

        Args:
            base_url:
                NewsAPI base URL.
        """

        self.base_url = base_url.rstrip("/")
        self.api_key = settings.NEWS_API_KEY
        self.timeout = settings.REQUEST_TIMEOUT

        if not self.api_key:
            raise ValueError(
                "NEWS_API_KEY is missing. "
                "Add it to your .env file."
            )

        if not self.timeout or self.timeout <= 0:
            raise ValueError(
                "REQUEST_TIMEOUT must be greater than zero."
            )

        self.session = requests.Session()

    # ==========================================================
    # Internal Request
    # ==========================================================

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send a GET request to NewsAPI.

        Args:
            endpoint:
                NewsAPI endpoint, such as ``everything``.

            params:
                Query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            RuntimeError:
                When the request fails or NewsAPI returns an error.
        """

        endpoint = endpoint.strip("/")

        if not endpoint:
            raise ValueError(
                "NewsAPI endpoint cannot be empty."
            )

        url = f"{self.base_url}/{endpoint}"

        request_params = dict(params or {})
        request_params["apiKey"] = self.api_key

        try:
            response = self.session.get(
                url=url,
                params=request_params,
                timeout=self.timeout,
            )

        except requests.Timeout as exc:
            raise RuntimeError(
                f"NewsAPI request timed out after "
                f"{self.timeout} seconds."
            ) from exc

        except requests.ConnectionError as exc:
            raise RuntimeError(
                "Could not connect to NewsAPI."
            ) from exc

        except requests.RequestException as exc:
            raise RuntimeError(
                f"NewsAPI request failed: {exc}"
            ) from exc

        try:
            response_data = response.json()

        except requests.JSONDecodeError as exc:
            raise RuntimeError(
                "NewsAPI returned an invalid JSON response. "
                f"HTTP status: {response.status_code}"
            ) from exc

        if not response.ok:
            error_code = response_data.get(
                "code",
                "unknown_error",
            )

            error_message = response_data.get(
                "message",
                response.reason,
            )

            raise RuntimeError(
                f"NewsAPI request failed with HTTP "
                f"{response.status_code}: "
                f"{error_code} - {error_message}"
            )

        if response_data.get("status") == "error":
            raise RuntimeError(
                "NewsAPI returned an error: "
                f"{response_data.get('code', 'unknown_error')} - "
                f"{response_data.get('message', 'No message')}"
            )

        return response_data

    # ==========================================================
    # Company News
    # ==========================================================

    def get_company_news(
        self,
        company_name: str,
        language: str = "en",
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Fetch recent news about one company.

        Args:
            company_name:
                Company name used as the search query.

            language:
                NewsAPI language code.

            page_size:
                Maximum number of articles.

        Returns:
            List of raw NewsAPI article dictionaries.
        """

        company_name = self._clean_query(
            company_name
        )

        page_size = self._validate_page_size(
            page_size
        )

        logger.debug(
            "Fetching company news for '{}'.",
            company_name,
        )

        response = self._get(
            endpoint="everything",
            params={
                "q": f'"{company_name}"',
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": page_size,
            },
        )

        articles = self._extract_articles(response)

        logger.info(
            "Fetched {} raw article(s) for '{}'.",
            len(articles),
            company_name,
        )

        return articles

    # ==========================================================
    # Saudi Market News
    # ==========================================================

    def get_market_news(
        self,
        language: str = "en",
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Fetch recent Saudi stock-market news.

        Args:
            language:
                NewsAPI language code.

            page_size:
                Maximum number of articles.

        Returns:
            List of raw article dictionaries.
        """

        page_size = self._validate_page_size(
            page_size
        )

        query = (
            '"Saudi stock market" OR '
            '"Saudi Exchange" OR '
            "Tadawul OR TASI"
        )

        response = self._get(
            endpoint="everything",
            params={
                "q": query,
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": page_size,
            },
        )

        articles = self._extract_articles(response)

        logger.info(
            "Fetched {} Saudi market article(s).",
            len(articles),
        )

        return articles

    # ==========================================================
    # General Search
    # ==========================================================

    def search(
        self,
        query: str,
        language: str = "en",
        page_size: int = 20,
        sort_by: str = "relevancy",
    ) -> list[dict[str, Any]]:
        """
        Search NewsAPI using a custom query.

        Args:
            query:
                NewsAPI search query.

            language:
                NewsAPI language code.

            page_size:
                Maximum number of articles.

            sort_by:
                One of:
                - relevancy
                - popularity
                - publishedAt

        Returns:
            List of raw article dictionaries.
        """

        query = self._clean_query(query)

        page_size = self._validate_page_size(
            page_size
        )

        allowed_sort_values = {
            "relevancy",
            "popularity",
            "publishedAt",
        }

        if sort_by not in allowed_sort_values:
            raise ValueError(
                "sort_by must be one of: "
                "'relevancy', 'popularity', or 'publishedAt'."
            )

        response = self._get(
            endpoint="everything",
            params={
                "q": query,
                "language": language,
                "sortBy": sort_by,
                "pageSize": page_size,
            },
        )

        return self._extract_articles(response)

    def search_news(
        self,
        query: str,
        language: str = "en",
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Compatibility wrapper used by NewsCollector.

        This method allows the collector to call either:

            client.search_news(...)

        or:

            client.search(...)
        """

        return self.search(
            query=query,
            language=language,
            page_size=page_size,
            sort_by="publishedAt",
        )

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _extract_articles(
        response: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Safely extract articles from a NewsAPI response.
        """

        articles = response.get(
            "articles",
            [],
        )

        if not isinstance(articles, list):
            logger.warning(
                "NewsAPI 'articles' field was not a list."
            )

            return []

        return [
            article
            for article in articles
            if isinstance(article, dict)
        ]

    @staticmethod
    def _clean_query(
        query: str,
    ) -> str:
        """
        Validate and normalize a search query.
        """

        cleaned_query = str(query).strip()

        if not cleaned_query:
            raise ValueError(
                "News search query cannot be empty."
            )

        return cleaned_query

    @staticmethod
    def _validate_page_size(
        page_size: int,
    ) -> int:
        """
        Validate NewsAPI page size.

        NewsAPI allows a maximum page size of 100.
        """

        if not isinstance(page_size, int):
            raise TypeError(
                "page_size must be an integer."
            )

        if page_size < 1:
            raise ValueError(
                "page_size must be at least 1."
            )

        return min(page_size, 100)

    def close(self) -> None:
        """
        Close the HTTP session.
        """

        self.session.close()

    def __enter__(self) -> NewsClient:
        """
        Support context-manager usage.
        """

        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        """
        Close the session when leaving a context manager.
        """

        self.close()