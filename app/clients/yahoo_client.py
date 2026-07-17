"""
Yahoo Finance Client

Responsible only for communicating with Yahoo Finance.
"""

from typing import Dict
from datetime import datetime, timezone
import yfinance as yf
import pandas as pd


class YahooClient:
    """Wrapper around yfinance."""

    def __init__(self):
        pass

    def get_stock(self, ticker: str) -> yf.Ticker:
        """
        Return a Yahoo Finance stock object.

        Example:
            stock = client.get_stock("2222.SR")
        """
        return yf.Ticker(ticker)

    def get_profile(self, ticker: str) -> Dict:
        """
        Get company profile.
        """
        stock = self.get_stock(ticker)
        return stock.info

    def get_prices(
        self,
        ticker: str,
        period: str = "5y",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """
        Download historical prices.
        """
        stock = self.get_stock(ticker)

        return stock.history(
            period=period,
            interval=interval,
            auto_adjust=True,
        )

    def get_income_statement(self, ticker: str) -> pd.DataFrame:
        """
        Annual income statement.
        """
        stock = self.get_stock(ticker)
        return stock.financials

    def get_balance_sheet(self, ticker: str) -> pd.DataFrame:
        """
        Annual balance sheet.
        """
        stock = self.get_stock(ticker)
        return stock.balance_sheet

    def get_cashflow(self, ticker: str) -> pd.DataFrame:
        """
        Annual cash flow statement.
        """
        stock = self.get_stock(ticker)
        return stock.cashflow

    def get_financials(self, ticker: str) -> Dict:
        """
        Return all financial statements.
        """
        return {
            "income": self.get_income_statement(ticker),
            "balance": self.get_balance_sheet(ticker),
            "cashflow": self.get_cashflow(ticker),
        }

    def get_market_info(self, ticker: str) -> Dict:
        """
        Return selected market information.
        """
        info = self.get_profile(ticker)

        return {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "currency": info.get("currency"),
        }

    def get_quote(self, ticker: str) -> Dict:
        """
        Return a normalized quote similar to the Sahmk response.
        """
        info = self.get_profile(ticker)

        previous = info.get("regularMarketPreviousClose")
        current = info.get("currentPrice")

        if previous is not None and current is not None:
            change = round(current - previous, 2)
            change_percent = round((change / previous) * 100, 2)
        else:
            change = None
            change_percent = None

        market_time = info.get("regularMarketTime")

        return {
            "symbol": ticker.replace(".SR", ""),
            "name": None,                       # Yahoo doesn't provide Arabic name
            "name_en": info.get("longName"),

            "price": current,
            "change": change,
            "change_percent": change_percent,

            "open": info.get("regularMarketOpen"),
            "high": info.get("regularMarketDayHigh"),
            "low": info.get("regularMarketDayLow"),
            "previous_close": previous,

            "volume": info.get("regularMarketVolume"),
            "value": None,                      # Not available from Yahoo

            "bid": info.get("bid"),
            "ask": info.get("ask"),
            "bid_size": None,
            "ask_size": None,

            "liquidity": {
                "inflow_value": None,
                "inflow_volume": None,
                "inflow_trades": None,
                "outflow_value": None,
                "outflow_volume": None,
                "outflow_trades": None,
                "net_value": None,
            },

            "updated_at": (
                datetime.fromtimestamp(
                    market_time,
                    tz=timezone.utc,
                ).isoformat()
                if market_time
                else None
            ),

            "is_delayed": True,
        }