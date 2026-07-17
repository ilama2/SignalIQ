"""
SignalIQ - Data Collection Pipeline
"""

import time
from pathlib import Path

import pandas as pd
from loguru import logger
from tqdm import tqdm

from app.clients.yahoo_client import YahooClient
from app.clients.sahmk_client import SahmkClient
from app.agents.data_collection.storage import Storage
from app.agents.data_collection.cache import Cache


class DataCollectionPipeline:

    def __init__(self):
        self.yahoo = YahooClient()
        self.sahmk = SahmkClient()

        self.storage = Storage()
        self.cache = Cache()

        self.company_file = Path("Data/saudi_companies.csv")
        self.delay = 10  # seconds between companies

    def run(self):
        companies = pd.read_csv(self.company_file)

        total = len(companies)

        logger.info(f"Found {total} companies")

        success = 0
        failed = 0

        for index, company in enumerate(
            tqdm(companies.itertuples(index=False), total=total),
            start=1,
        ):

            symbol = str(company.symbol)

            logger.info(f"[{index}/{total}] Processing {symbol}")

            try:
                self.collect_company(company)
                success += 1

            except KeyboardInterrupt:
                logger.warning("Pipeline interrupted by user.")
                raise

            except Exception as e:
                failed += 1
                logger.exception(f"{symbol}: {e}")

            if index < total:
                time.sleep(self.delay)

        logger.info("=" * 60)
        logger.success("Data collection completed.")
        logger.info(f"Successful : {success}")
        logger.info(f"Failed     : {failed}")
        logger.info("=" * 60)

    def collect_company(self, company):

        symbol = str(company.symbol)
        ticker = company.ticker

        logger.info(f"{symbol}: Starting collection")

        # =====================================================
        # Company Profile
        # =====================================================

        if self.storage.profile_exists(symbol):

            logger.info(f"{symbol}: Profile already exists")

            if self.cache.profile_expired(symbol):

                logger.info(f"{symbol}: Refreshing profile")

                quote = self.sahmk.get_quote(symbol)

                self.storage.save_profile(
                    symbol=symbol,
                    profile=quote,
                )

                self.cache.update_profile(symbol)

            else:
                logger.info(f"{symbol}: Using cached profile")

        else:

            logger.info(f"{symbol}: Downloading profile")

            quote = self.sahmk.get_quote(symbol)

            self.storage.save_profile(
                symbol=symbol,
                profile=quote,
            )

            self.cache.update_profile(symbol)

        # =====================================================
        # Historical Prices
        # =====================================================

        if self.cache.prices_expired(symbol):

            logger.info(f"{symbol}: Downloading prices")

            prices = self.yahoo.get_prices(ticker)

            self.storage.save_prices(
                symbol=symbol,
                prices=prices,
            )

            self.cache.update_prices(symbol)

        else:
            logger.info(f"{symbol}: Prices are up-to-date")

        # =====================================================
        # Financial Statements
        # =====================================================

        if self.cache.financials_expired(symbol):

            logger.info(f"{symbol}: Downloading financial statements")

            financials = self.yahoo.get_financials(ticker)

            self.storage.save_financials(
                symbol=symbol,
                financials=financials,
            )

            self.cache.update_financials(symbol)

        else:
            logger.info(f"{symbol}: Financial statements are up-to-date")

        logger.success(f"{symbol}: Collection completed")