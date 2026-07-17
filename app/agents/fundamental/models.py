"""
SignalIQ - Fundamental Models

Defines the output models used by the Fundamental Agent.
"""

from pydantic import BaseModel, Field


# ==========================================================
# Financial Ratios
# ==========================================================

class FinancialRatiosModel(BaseModel):

    # Profitability
    roe: float = Field(..., description="Return on Equity")
    roa: float = Field(..., description="Return on Assets")
    gross_margin: float
    operating_margin: float
    net_margin: float

    # Liquidity
    current_ratio: float
    quick_ratio: float
    operating_cash_flow_ratio: float

    # Leverage
    debt_ratio: float
    debt_to_equity: float
    equity_multiplier: float

    # Efficiency
    asset_turnover: float
    cash_conversion_ratio: float

    # Cash Flow
    free_cash_flow: float

    # Growth
    revenue_growth: float
    net_income_growth: float


# ==========================================================
# Valuation
# ==========================================================

class ValuationModel(BaseModel):

    dcf_value: float

    graham_value: float

    lynch_value: float

    pe_value: float

    intrinsic_value: float

    current_price: float

    margin_of_safety: float

    upside: float

    recommendation: str


# ==========================================================
# Fundamental Score
# ==========================================================

class ScoreModel(BaseModel):

    score: int

    rating: str

    strengths: list[str]

    weaknesses: list[str]


# ==========================================================
# Complete Fundamental Analysis
# ==========================================================

class FundamentalReport(BaseModel):

    symbol: str

    company_name: str

    sector: str

    ratios: FinancialRatiosModel

    valuation: ValuationModel

    score: ScoreModel