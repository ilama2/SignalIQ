"""
SignalIQ - Technical Analysis Pipeline

Runs technical analysis for all Saudi companies.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from loguru import logger

from .technical import TechnicalAgent


class TechnicalPipeline:
    """
    Runs the Technical Agent for every company.
    """

    def __init__(self):

        self.agent = TechnicalAgent()

        self.company_file = Path("Data/saudi_companies.csv")

        self.output_dir = Path(
            "Data/analysis/technical"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # =====================================================
    # Run
    # =====================================================

    def run(self):

        companies = pd.read_csv(self.company_file)

        logger.info(
            f"Starting Technical Analysis for {len(companies)} companies..."
        )

        for _, row in companies.iterrows():

            symbol = str(row["symbol"])

            try:

                report = self.agent.run(symbol)

                output_file = (
                    self.output_dir
                    / f"{symbol}.json"
                )

                with open(
                    output_file,
                    "w",
                    encoding="utf-8",
                ) as f:

                    json.dump(
                        report.model_dump(),
                        f,
                        indent=4,
                        ensure_ascii=False,
                    )

                logger.success(
                    f"{symbol} completed"
                )

            except Exception as e:

                logger.exception(
                    f"{symbol}: {e}"
                )

        logger.success(
            "Technical Analysis completed successfully."
        )