"""
SignalIQ - Fundamental Scoring

Converts financial ratios into an investment score.
"""

from __future__ import annotations


class FundamentalScorer:

    def __init__(self):
        self.score = 0
        self.strengths = []
        self.weaknesses = []

    def score_company(
        self,
        ratios: dict,
    ) -> dict:

        self.score = 0
        self.strengths = []
        self.weaknesses = []

        self._profitability(ratios)
        self._liquidity(ratios)
        self._leverage(ratios)
        self._efficiency(ratios)
        self._growth(ratios)
        self._cashflow(ratios)

        return {
            "score": min(self.score, 100),
            "rating": self._rating(),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }

    def _profitability(self, r):

        # ROE (10)
        roe = r.get("roe", 0)

        if roe >= 0.20:
            self.score += 10
            self.strengths.append("Excellent Return on Equity")
        elif roe >= 0.15:
            self.score += 8
        elif roe >= 0.10:
            self.score += 5
        else:
            self.weaknesses.append("Low Return on Equity")

        # ROA (5)
        roa = r.get("roa", 0)

        if roa >= 0.10:
            self.score += 5
        elif roa >= 0.05:
            self.score += 3
        else:
            self.weaknesses.append("Low Return on Assets")

        # Net Margin (5)
        margin = r.get("net_margin", 0)

        if margin >= 0.20:
            self.score += 5
            self.strengths.append("High Net Margin")
        elif margin >= 0.10:
            self.score += 3

        # Gross Margin (5)
        gross = r.get("gross_margin", 0)

        if gross >= 0.40:
            self.score += 5
        elif gross >= 0.20:
            self.score += 3

        # Operating Margin (10)
        operating = r.get("operating_margin", 0)

        if operating >= 0.20:
            self.score += 10
        elif operating >= 0.10:
            self.score += 5

    # =====================================================
    # Liquidity (20)
    # =====================================================

    def _liquidity(self, r):

        current = r.get("current_ratio", 0)

        if current >= 2:
            self.score += 8
            self.strengths.append("Strong Liquidity")
        elif current >= 1:
            self.score += 5
        else:
            self.weaknesses.append("Weak Liquidity")

        quick = r.get("quick_ratio", 0)

        if quick >= 1:
            self.score += 6
        elif quick >= 0.7:
            self.score += 3

        ocf = r.get("operating_cash_flow_ratio", 0)

        if ocf >= 1:
            self.score += 6
        elif ocf >= 0.5:
            self.score += 3

    # =====================================================
    # Leverage (20)
    # =====================================================

    def _leverage(self, r):

        debt_equity = r.get("debt_to_equity", 0)

        if debt_equity < 0.5:
            self.score += 8
            self.strengths.append("Low Debt")
        elif debt_equity < 1:
            self.score += 5
        else:
            self.weaknesses.append("High Debt")

        debt_ratio = r.get("debt_ratio", 0)

        if debt_ratio < 0.40:
            self.score += 6
        elif debt_ratio < 0.60:
            self.score += 3

        multiplier = r.get("equity_multiplier", 0)

        if multiplier < 2:
            self.score += 6
        elif multiplier < 3:
            self.score += 3

    def _efficiency(self, r):

        turnover = r.get("asset_turnover", 0)

        if turnover >= 1:
            self.score += 5
        elif turnover >= 0.5:
            self.score += 3

        conversion = r.get("cash_conversion_ratio", 0)

        if conversion >= 1:
            self.score += 5
        elif conversion >= 0.8:
            self.score += 3

    def _growth(self, r):

        revenue = r.get("revenue_growth", 0)

        if revenue >= 0.20:
            self.score += 5
            self.strengths.append("Strong Revenue Growth")
        elif revenue >= 0.10:
            self.score += 3
        elif revenue < 0:
            self.weaknesses.append("Revenue Declining")

        income = r.get("net_income_growth", 0)

        if income >= 0.20:
            self.score += 5
            self.strengths.append("Strong Earnings Growth")
        elif income >= 0.10:
            self.score += 3
        elif income < 0:
            self.weaknesses.append("Net Income Declining")


    def _cashflow(self, r):

        fcf = r.get("free_cash_flow", 0)

        if fcf > 0:
            self.score += 5
            self.strengths.append("Positive Free Cash Flow")
        else:
            self.weaknesses.append("Negative Free Cash Flow")

    def _rating(self):

        if self.score >= 85:
            return "Strong Buy"

        if self.score >= 70:
            return "Buy"

        if self.score >= 55:
            return "Hold"

        if self.score >= 40:
            return "Sell"

        return "Strong Sell"