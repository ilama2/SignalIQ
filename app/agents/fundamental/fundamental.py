"""
SignalIQ - Fundamental Analysis Agent

Coordinates the complete fundamental analysis workflow.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from loguru import logger

from .models import (
    FinancialRatiosModel,
    FundamentalReport,
    ScoreModel,
    ValuationModel,
)
from .ratios import FinancialRatios
from .scoring import FundamentalScorer
from .valuation import Valuation


class FundamentalAgent:
    """
    Performs complete fundamental analysis.
    """

    def __init__(self):

        self.financial_dir = Path("Data/financials")
        self.profile_dir = Path("Data/profiles")
        self.price_dir = Path("Data/prices")

    # =====================================================
    # Load Financial Statements
    # =====================================================

    def load_financials(self, symbol: str) -> dict:

        income = pd.read_csv(
            self.financial_dir / f"{symbol}_income.csv",
            index_col=0,
        )

        balance = pd.read_csv(
            self.financial_dir / f"{symbol}_balance.csv",
            index_col=0,
        )

        cashflow = pd.read_csv(
            self.financial_dir / f"{symbol}_cashflow.csv",
            index_col=0,
        )

        return {
            "income": income,
            "balance": balance,
            "cashflow": cashflow,
        }

    # =====================================================
    # Load Profile
    # =====================================================

    def load_profile(self, symbol: str) -> dict:

        with open(
            self.profile_dir / f"{symbol}.json",
            encoding="utf-8",
        ) as f:
            return json.load(f)

    # =====================================================
    # Load Latest Stock Price
    # =====================================================

    def load_current_price(self, symbol: str) -> float:

        prices = pd.read_csv(
            self.price_dir / f"{symbol}.csv"
        )

        return float(prices["Close"].iloc[-1])

    # =====================================================
    # Analyze
    # =====================================================

    def analyze(self, symbol: str) -> FundamentalReport:

        logger.info(f"Analyzing {symbol}")

        financials = self.load_financials(symbol)
        profile = self.load_profile(symbol)

        # -----------------------------------------------------
        # Financial Ratios
        # -----------------------------------------------------

        ratios = FinancialRatios.calculate_all(financials)

        # -----------------------------------------------------
        # Current Market Price
        # -----------------------------------------------------

        current_price = self.load_current_price(symbol)

        # -----------------------------------------------------
        # EPS
        # -----------------------------------------------------

        income = financials["income"]
        latest = income.columns[0]

        shares_outstanding = profile.get(
            "sharesOutstanding",
            profile.get("shares_outstanding", 0),
        )

        if "Diluted EPS" in income.index:

            eps = float(
                income.loc["Diluted EPS", latest]
            )

        else:

            net_income = float(
                income.loc["Net Income", latest]
            )

            eps = (
                net_income / shares_outstanding
                if shares_outstanding > 0
                else 0.0
            )

        # -----------------------------------------------------
        # Valuation
        # -----------------------------------------------------

        valuation_engine = Valuation()

        valuation = valuation_engine.calculate(
            current_price=current_price,
            eps=eps,
            free_cash_flow=ratios["free_cash_flow"],
            growth_rate=max(
                ratios["revenue_growth"],
                0.03,
            ),
            shares_outstanding=shares_outstanding,
        )

        # -----------------------------------------------------
        # Score
        # -----------------------------------------------------

        score = FundamentalScorer().score_company(
            ratios
        )

        # -----------------------------------------------------
        # Build Report
        # -----------------------------------------------------

        report = FundamentalReport(
            symbol=symbol,
            company_name=profile.get(
                "companyName",
                profile.get("name", symbol),
            ),
            sector=profile.get(
                "sector",
                "Unknown",
            ),
            ratios=FinancialRatiosModel(
                **ratios
            ),
            valuation=ValuationModel(
                **valuation
            ),
            score=ScoreModel(
                **score
            ),
        )

        return report

    # =====================================================
    # Run
    # =====================================================

    def run(self, symbol: str) -> FundamentalReport:

        logger.info(
            f"Starting analysis for {symbol}"
        )

        report = self.analyze(symbol)

        logger.success(
            f"{symbol} analysis completed"
        )

        return report