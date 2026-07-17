"""
SignalIQ - Storage Module

Responsible for saving collected data.
"""

from pathlib import Path
import json

import pandas as pd


class Storage:
    """Handles saving all collected data."""

    def __init__(self):

        self.base_dir = Path("Data")

        self.profile_dir = self.base_dir / "profiles"
        self.price_dir = self.base_dir / "prices"
        self.financial_dir = self.base_dir / "financials"

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.price_dir.mkdir(parents=True, exist_ok=True)
        self.financial_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Profile
    # ---------------------------------------------------------

    def save_profile(
        self,
        symbol: str,
        profile: dict
    ):

        path = self.profile_dir / f"{symbol}.json"

        with open(path, "w", encoding="utf-8") as f:

            json.dump(
                profile,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ---------------------------------------------------------
    # Prices
    # ---------------------------------------------------------

    def save_prices(
        self,
        symbol: str,
        prices: pd.DataFrame
    ):

        path = self.price_dir / f"{symbol}.csv"

        prices.to_csv(path)

    # ---------------------------------------------------------
    # Financial Statements
    # ---------------------------------------------------------

    def save_financials(
        self,
        symbol: str,
        financials: dict
    ):

        financials["income"].to_csv(
            self.financial_dir / f"{symbol}_income.csv"
        )

        financials["balance"].to_csv(
            self.financial_dir / f"{symbol}_balance.csv"
        )

        financials["cashflow"].to_csv(
            self.financial_dir / f"{symbol}_cashflow.csv"
        )

    # ---------------------------------------------------------
    # Save Everything
    # ---------------------------------------------------------

    def save(
        self,
        symbol: str,
        profile: dict,
        prices: pd.DataFrame,
        financials: dict,
    ):

        self.save_profile(symbol, profile)

        self.save_prices(symbol, prices)

        self.save_financials(symbol, financials)

    def profile_exists(self, symbol: str) -> bool:
        return (Path("Data/profiles") / f"{symbol}.json").exists()

    def prices_exists(self, symbol: str) -> bool:
        return (Path("Data/prices") / f"{symbol}.csv").exists()

    def financials_exists(self, symbol: str) -> bool:
        return (Path("Data/financials") / f"{symbol}.json").exists()


