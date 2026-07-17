"""
SignalIQ - Financial Ratios

Contains all financial ratio calculations.
"""

from __future__ import annotations

import pandas as pd


class FinancialRatios:

    @staticmethod
    def _value(df: pd.DataFrame, row: str):

        latest = df.columns[0]

        if row not in df.index:
            return 0.0

        value = df.loc[row, latest]

        if pd.isna(value):
            return 0.0

        return float(value)

    # =====================================================
    # Profitability
    # =====================================================

    @classmethod
    def return_on_equity(
        cls,
        income: pd.DataFrame,
        balance: pd.DataFrame,
    ) -> float:

        net_income = cls._value(income, "Net Income")
        equity = cls._value(balance, "Stockholders Equity")

        if equity == 0:
            return 0.0

        return net_income / equity

    @classmethod
    def return_on_assets(
        cls,
        income: pd.DataFrame,
        balance: pd.DataFrame,
    ) -> float:

        net_income = cls._value(income, "Net Income")
        assets = cls._value(balance, "Total Assets")

        if assets == 0:
            return 0.0

        return net_income / assets

    @classmethod
    def net_margin(
        cls,
        income: pd.DataFrame,
    ) -> float:

        revenue = cls._value(income, "Total Revenue")
        net_income = cls._value(income, "Net Income")

        if revenue == 0:
            return 0.0

        return net_income / revenue

    # =====================================================
    # Liquidity
    # =====================================================

    @classmethod
    def current_ratio(
        cls,
        balance: pd.DataFrame,
    ) -> float:

        current_assets = cls._value(balance, "Current Assets")
        current_liabilities = cls._value(balance, "Current Liabilities")

        if current_liabilities == 0:
            return 0.0

        return current_assets / current_liabilities

    @classmethod
    def quick_ratio(
        cls,
        balance: pd.DataFrame,
    ) -> float:

        current_assets = cls._value(balance, "Current Assets")
        inventory = cls._value(balance, "Inventory")
        current_liabilities = cls._value(balance, "Current Liabilities")

        if current_liabilities == 0:
            return 0.0

        return (current_assets - inventory) / current_liabilities

    # =====================================================
    # Leverage
    # =====================================================

    @classmethod
    def debt_ratio(
        cls,
        balance: pd.DataFrame,
    ) -> float:

        liabilities = cls._value(
            balance,
            "Total Liabilities Net Minority Interest",
        )

        assets = cls._value(balance, "Total Assets")

        if assets == 0:
            return 0.0

        return liabilities / assets

    @classmethod
    def debt_to_equity(
        cls,
        balance: pd.DataFrame,
    ) -> float:

        liabilities = cls._value(
            balance,
            "Total Liabilities Net Minority Interest",
        )

        equity = cls._value(
            balance,
            "Stockholders Equity",
        )

        if equity == 0:
            return 0.0

        return liabilities / equity

    # =====================================================
    # Cash Flow
    # =====================================================

    @classmethod
    def free_cash_flow(
        cls,
        cashflow: pd.DataFrame,
    ) -> float:

        operating_cf = cls._value(
            cashflow,
            "Operating Cash Flow",
        )

        capex = abs(
            cls._value(
                cashflow,
                "Capital Expenditure",
            )
        )

        return operating_cf - capex

    # =====================================================
    # Growth
    # =====================================================

    @staticmethod
    def growth(series: pd.Series) -> float:

        if len(series) < 2:
            return 0.0

        latest = float(series.iloc[0])
        previous = float(series.iloc[1])

        if previous == 0:
            return 0.0

        return (latest - previous) / previous

    @classmethod
    def revenue_growth(
        cls,
        income: pd.DataFrame,
    ) -> float:

        if "Total Revenue" not in income.index:
            return 0.0

        return cls.growth(income.loc["Total Revenue"])

    @classmethod
    def net_income_growth(
        cls,
        income: pd.DataFrame,
    ) -> float:

        if "Net Income" not in income.index:
            return 0.0

        return cls.growth(income.loc["Net Income"])

    @classmethod
    def calculate_all(
        cls,
        financials: dict,
    ) -> dict:

        income = financials["income"]
        balance = financials["balance"]
        cashflow = financials["cashflow"]

        return {
            # Profitability
            "roe": cls.return_on_equity(income, balance),
            "roa": cls.return_on_assets(income, balance),
            "gross_margin": cls.gross_margin(income),
            "operating_margin": cls.operating_margin(income),
            "net_margin": cls.net_margin(income),

            # Liquidity
            "current_ratio": cls.current_ratio(balance),
            "quick_ratio": cls.quick_ratio(balance),
            "operating_cash_flow_ratio": cls.operating_cash_flow_ratio(
                cashflow,
                balance,
            ),

            # Leverage
            "debt_ratio": cls.debt_ratio(balance),
            "debt_to_equity": cls.debt_to_equity(balance),
            "equity_multiplier": cls.equity_multiplier(balance),

            # Efficiency
            "asset_turnover": cls.asset_turnover(
                income,
                balance,
            ),

            # Cash Flow
            "free_cash_flow": cls.free_cash_flow(cashflow),
            "cash_conversion_ratio": cls.cash_conversion_ratio(
                income,
                cashflow,
            ),

            # Growth
            "revenue_growth": cls.revenue_growth(income),
            "net_income_growth": cls.net_income_growth(income),
        }
    @classmethod
    def gross_margin(
        cls,
        income: pd.DataFrame,
    ) -> float:

        revenue = cls._value(income, "Total Revenue")
        gross_profit = cls._value(income, "Gross Profit")

        if revenue == 0:
            return 0.0

        return gross_profit / revenue
    
    @classmethod
    def operating_margin(
        cls,
        income: pd.DataFrame,
    ) -> float:

        revenue = cls._value(income, "Total Revenue")
        operating_income = cls._value(income, "Operating Income")

        if revenue == 0:
            return 0.0

        return operating_income / revenue
    
    @classmethod
    def asset_turnover(
        cls,
        income: pd.DataFrame,
        balance: pd.DataFrame,
    ) -> float:

        revenue = cls._value(income, "Total Revenue")
        assets = cls._value(balance, "Total Assets")

        if assets == 0:
            return 0.0

        return revenue / assets
    
    @classmethod
    def equity_multiplier(
        cls,
        balance: pd.DataFrame,
    ) -> float:

        assets = cls._value(balance, "Total Assets")
        equity = cls._value(balance, "Stockholders Equity")

        if equity == 0:
            return 0.0

        return assets / equity
    
    @classmethod
    def operating_cash_flow_ratio(
        cls,
        cashflow: pd.DataFrame,
        balance: pd.DataFrame,
    ) -> float:

        operating_cf = cls._value(
            cashflow,
            "Operating Cash Flow",
        )

        current_liabilities = cls._value(
            balance,
            "Current Liabilities",
        )

        if current_liabilities == 0:
            return 0.0

        return operating_cf / current_liabilities
    
    @classmethod
    def cash_conversion_ratio(
        cls,
        income: pd.DataFrame,
        cashflow: pd.DataFrame,
    ) -> float:

        operating_cf = cls._value(
            cashflow,
            "Operating Cash Flow",
        )

        net_income = cls._value(
            income,
            "Net Income",
        )

        if net_income == 0:
            return 0.0

        return operating_cf / net_income
    
