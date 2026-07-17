"""
SignalIQ - Technical Analysis Agent

Coordinates the complete technical analysis workflow.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from loguru import logger

from .indicators import TechnicalIndicators
from .models import (
    TechnicalIndicatorsModel,
    TechnicalReport,
    TechnicalScoreModel,
)
from .scoring import TechnicalScorer


class TechnicalAgent:
    """
    Performs complete technical analysis.
    """

    def __init__(self):

        self.price_dir = Path("Data/prices")
        self.profile_dir = Path("Data/profiles")

    # =====================================================
    # Load Historical Prices
    # =====================================================

    def load_prices(
        self,
        symbol: str,
    ) -> pd.DataFrame:

        prices = pd.read_csv(
            self.price_dir / f"{symbol}.csv"
        )

        if prices.empty:
            raise ValueError(
                f"No price data found for {symbol}"
            )

        return prices

    # =====================================================
    # Load Company Profile
    # =====================================================

    def load_profile(
        self,
        symbol: str,
    ) -> dict:

        with open(
            self.profile_dir / f"{symbol}.json",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    # =====================================================
    # Analyze
    # =====================================================

    def analyze(
        self,
        symbol: str,
    ) -> TechnicalReport:

        logger.info(f"Analyzing {symbol}")

        prices = self.load_prices(symbol)

        profile = self.load_profile(symbol)

        # ---------------------------------------------
        # Technical Indicators
        # ---------------------------------------------

        indicators = TechnicalIndicators.calculate_all(
            prices
        )

        # ---------------------------------------------
        # Technical Score
        # ---------------------------------------------

        score = TechnicalScorer().score_stock(
            indicators
        )

        # ---------------------------------------------
        # Build Report
        # ---------------------------------------------

        report = TechnicalReport(
            symbol=symbol,
            company_name=profile.get(
                "companyName",
                profile.get("name", symbol),
            ),
            indicators=TechnicalIndicatorsModel(
                **indicators
            ),
            score=TechnicalScoreModel(
                **score
            ),
        )

        return report

    # =====================================================
    # Run
    # =====================================================

    def run(
        self,
        symbol: str,
    ) -> TechnicalReport:

        logger.info(
            f"Starting technical analysis for {symbol}"
        )

        report = self.analyze(symbol)

        logger.success(
            f"{symbol} technical analysis completed"
        )

        return report