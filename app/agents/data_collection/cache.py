"""
SignalIQ - Smart Cache

Tracks the last update time for each company and determines
whether data should be downloaded again.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from app.core import settings


class Cache:
    """Manages cache timestamps for collected company data."""

    def __init__(self) -> None:
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================================
    # Internal Helpers
    # ==========================================================

    def _cache_file(self, symbol: str) -> Path:
        return self.cache_dir / f"{symbol}.json"

    def load(self, symbol: str) -> dict[str, Any]:
        """
        Load cache file.

        Returns an empty dictionary if the cache does not exist
        or is corrupted.
        """

        path = self._cache_file(symbol)

        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        except (json.JSONDecodeError, OSError):
            return {}

    def save(self, symbol: str, cache_data: dict[str, Any]) -> None:
        """
        Save cache metadata.
        """

        path = self._cache_file(symbol)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                cache_data,
                f,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # Update Helpers
    # ==========================================================

    def _update(self, symbol: str, key: str) -> None:
        """
        Update a single timestamp.
        """

        data = self.load(symbol)

        data[key] = datetime.now().isoformat()

        self.save(symbol, data)

    def update_profile(self, symbol: str) -> None:
        self._update(symbol, "profile_updated")

    def update_prices(self, symbol: str) -> None:
        self._update(symbol, "prices_updated")

    def update_financials(self, symbol: str) -> None:
        self._update(symbol, "financials_updated")

    def update_all(self, symbol: str) -> None:
        """
        Update all timestamps.
        """

        now = datetime.now().isoformat()

        self.save(
            symbol,
            {
                "profile_updated": now,
                "prices_updated": now,
                "financials_updated": now,
            },
        )

    # ==========================================================
    # Expiration Helpers
    # ==========================================================

    @staticmethod
    def _is_expired(timestamp: str | None, days: int) -> bool:
        """
        Return True if timestamp is missing or older than
        the allowed number of days.
        """

        if not timestamp:
            return True

        last_update = datetime.fromisoformat(timestamp)

        return datetime.now() - last_update >= timedelta(days=days)

    def profile_expired(self, symbol: str) -> bool:

        data = self.load(symbol)

        return self._is_expired(
            data.get("profile_updated"),
            settings.PROFILE_CACHE_DAYS,
        )

    def prices_expired(self, symbol: str) -> bool:

        data = self.load(symbol)

        return self._is_expired(
            data.get("prices_updated"),
            settings.PRICE_CACHE_DAYS,
        )

    def financials_expired(self, symbol: str) -> bool:

        data = self.load(symbol)

        return self._is_expired(
            data.get("financials_updated"),
            settings.FINANCIAL_CACHE_DAYS,
        )