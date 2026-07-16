from pathlib import Path
import json

import pandas as pd
import yfinance as yf
from loguru import logger
from tqdm import tqdm


# ==========================
# Directories
# ==========================

BASE_DIR = Path("Data")

COMPANIES_FILE = BASE_DIR / "saudi_companies.csv"

PROFILE_DIR = BASE_DIR / "profiles"
PRICE_DIR = BASE_DIR / "prices"
FINANCIAL_DIR = BASE_DIR / "financials"

PROFILE_DIR.mkdir(parents=True, exist_ok=True)
PRICE_DIR.mkdir(parents=True, exist_ok=True)
FINANCIAL_DIR.mkdir(parents=True, exist_ok=True)

logger.add("logs/data_collection.log")


class DataCollector:

    def __init__(self):
        self.df = pd.read_csv(COMPANIES_FILE)

    def collect_all(self):

        logger.info(f"Found {len(self.df)} companies")

        for company in tqdm(self.df.itertuples(index=False),
                            total=len(self.df)):

            self.collect_company(company)

    def collect_company(self, company):

        ticker = company.ticker
        symbol = str(company.symbol)

        price_file = PRICE_DIR / f"{symbol}.csv"

        # Skip if already downloaded
        if price_file.exists():
            logger.info(f"Skipping {ticker}")
            return

        try:

            stock = yf.Ticker(ticker)

            # ---------------------
            # Company Profile
            # ---------------------

            profile = stock.info

            with open(PROFILE_DIR / f"{symbol}.json",
                      "w",
                      encoding="utf-8") as f:

                json.dump(
                    profile,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            # ---------------------
            # Historical Prices
            # ---------------------

            prices = stock.history(
                period="5y",
                interval="1d",
                auto_adjust=True
            )

            prices.to_csv(price_file)

            # ---------------------
            # Financial Statements
            # ---------------------

            stock.financials.to_csv(
                FINANCIAL_DIR / f"{symbol}_income.csv"
            )

            stock.balance_sheet.to_csv(
                FINANCIAL_DIR / f"{symbol}_balance.csv"
            )

            stock.cashflow.to_csv(
                FINANCIAL_DIR / f"{symbol}_cashflow.csv"
            )

            logger.success(f"{ticker} downloaded")

        except Exception as e:

            logger.error(f"{ticker} -> {e}")


if __name__ == "__main__":

    collector = DataCollector()

    collector.collect_all()