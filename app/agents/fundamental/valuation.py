"""
SignalIQ - Valuation Models

Calculates intrinsic value using multiple valuation methods.
"""

from __future__ import annotations


class Valuation:

    # =====================================================
    # Discounted Cash Flow (DCF)
    # =====================================================

    @staticmethod
    def discounted_cash_flow(
        free_cash_flow: float,
        growth_rate: float = 0.08,
        discount_rate: float = 0.10,
        terminal_growth: float = 0.03,
        years: int = 5,
    ) -> float:

        if free_cash_flow <= 0:
            return 0.0

        pv = 0.0
        fcf = free_cash_flow

        for year in range(1, years + 1):

            fcf *= (1 + growth_rate)

            pv += fcf / ((1 + discount_rate) ** year)

        terminal_value = (
            fcf * (1 + terminal_growth)
        ) / (discount_rate - terminal_growth)

        terminal_value /= (1 + discount_rate) ** years

        return pv + terminal_value

    # =====================================================
    # Graham Value
    # =====================================================

    @staticmethod
    def graham_value(
        eps: float,
        growth_rate: float,
    ) -> float:

        if eps <= 0:
            return 0.0

        growth_percent = growth_rate * 100

        return eps * (8.5 + 2 * growth_percent)

    # =====================================================
    # Peter Lynch Value
    # =====================================================

    @staticmethod
    def lynch_value(
        eps: float,
        growth_rate: float,
    ) -> float:

        if eps <= 0:
            return 0.0

        growth_percent = growth_rate * 100

        if growth_percent <= 0:
            return 0.0

        return eps * growth_percent

    # =====================================================
    # Margin of Safety
    # =====================================================

    @staticmethod
    def margin_of_safety(
        intrinsic_value: float,
        current_price: float,
    ) -> float:

        if intrinsic_value <= 0:
            return 0.0

        return (
            intrinsic_value - current_price
        ) / intrinsic_value

    # =====================================================
    # Upside
    # =====================================================

    @staticmethod
    def upside(
        intrinsic_value: float,
        current_price: float,
    ) -> float:

        if current_price <= 0:
            return 0.0

        return (
            intrinsic_value - current_price
        ) / current_price

    # =====================================================
    # Recommendation
    # =====================================================

    @staticmethod
    def recommendation(
        margin_of_safety: float,
    ) -> str:

        if margin_of_safety >= 0.30:
            return "Strong Buy"

        if margin_of_safety >= 0.15:
            return "Buy"

        if margin_of_safety >= 0.05:
            return "Hold"

        if margin_of_safety >= -0.10:
            return "Sell"

        return "Strong Sell"

    # =====================================================
    # Complete Valuation
    # =====================================================

    def calculate(
        self,
        current_price: float,
        eps: float,
        free_cash_flow: float,
        growth_rate: float,
        shares_outstanding: float,
    ):

        # -----------------------------
        # Individual valuation methods
        # -----------------------------

        dcf_total = self.discounted_cash_flow(
            free_cash_flow,
            growth_rate,
        )

        dcf_value = (
            dcf_total / shares_outstanding
            if shares_outstanding > 0
            else 0.0
        )

        graham = self.graham_value(
            eps,
            growth_rate * 100,
        )

        lynch = self.lynch_value(
            eps,
            growth_rate * 100,
        )

        pe = self.pe_value(
            eps,
            15,
        )

        # -----------------------------
        # Average intrinsic value
        # -----------------------------

        values = [
            v
            for v in [dcf_value, graham, lynch, pe]
            if v > 0
        ]

        intrinsic = (
            sum(values) / len(values)
            if values
            else 0.0
        )

        margin = self.margin_of_safety(
            intrinsic,
            current_price,
        )

        return {

            "dcf_value": dcf_value,

            "graham_value": graham,

            "lynch_value": lynch,

            "pe_value": pe,

            "intrinsic_value": intrinsic,

            "current_price": current_price,

            "margin_of_safety": margin,

            "upside": self.upside(
                intrinsic,
                current_price,
            ),

            "recommendation": self.recommendation(
                margin,
            ),
        }
    
    @staticmethod
    def pe_value(
        eps: float,
        target_pe: float = 15,
    ) -> float:

        if eps <= 0:
            return 0.0

        return eps * target_pe

    
