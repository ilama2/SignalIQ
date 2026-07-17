from pathlib import Path
import pandas as pd
from loguru import logger

from .fundamental import FundamentalAgent


class FundamentalPipeline:

    def __init__(self):
        self.agent = FundamentalAgent()
        self.csv = Path("Data/saudi_companies.csv")
        self.output = Path("Data/analysis/fundamental")
        self.output.mkdir(parents=True, exist_ok=True)

    def run(self):

        companies = pd.read_csv(self.csv)

        for _, row in companies.iterrows():

            symbol = str(row["symbol"])

            try:

                report = self.agent.run(symbol)

                with open(
                    self.output / f"{symbol}.json",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(report.model_dump_json(indent=4))

                logger.success(f"{symbol} completed")

            except Exception as e:
                logger.exception(f"{symbol}: {e}")