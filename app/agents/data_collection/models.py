"""
SignalIQ - Data Models
"""

from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict


class CompanyProfile(BaseModel):
    """Company profile information."""

    symbol: str
    ticker: str

    company_name: str | None = None

    sector: str | None = None
    industry: str | None = None

    website: str | None = None

    employees: int | None = None

    market: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class MarketInfo(BaseModel):
    """Market information."""

    market_cap: float | None = None

    pe_ratio: float | None = None

    price_to_book: float | None = None

    shares_outstanding: float | None = None

    dividend_yield: float | None = None

    beta: float | None = None

    currency: str | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FinancialStatements(BaseModel):
    """Financial statements."""

    income: Any

    balance: Any

    cashflow: Any

    model_config = ConfigDict(arbitrary_types_allowed=True)


class CompanyData(BaseModel):
    """
    Complete company data collected by the Data Collection Agent.
    """

    profile: CompanyProfile

    prices: Any

    financials: FinancialStatements

    market_info: MarketInfo

    model_config = ConfigDict(arbitrary_types_allowed=True)