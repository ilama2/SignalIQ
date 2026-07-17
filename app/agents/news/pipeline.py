"""
SignalIQ - News Analysis Pipeline

Runs the News Agent for all Saudi-listed companies and saves
one structured JSON report per company.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from loguru import logger

from .news import NewsAgent


class NewsPipeline:
    """
    Run news analysis for every company in the company universe.

    Responsibilities:
    - Read the Saudi companies CSV file.
    - Normalize company symbols.
    - Skip already processed companies when requested.
    - Run NewsAgent for each company.
    - Save reports as JSON.
    - Continue processing when one company fails.
    """

    def __init__(
        self,
        agent: NewsAgent | None = None,
        company_file: str | Path = "Data/saudi_companies.csv",
        output_dir: str | Path = "Data/analysis/news",
        skip_existing: bool = True,
    ) -> None:
        """
        Initialize the news-analysis pipeline.

        Args:
            agent:
                Optional configured NewsAgent instance.

            company_file:
                CSV file containing Saudi company symbols.

            output_dir:
                Directory where news reports will be saved.

            skip_existing:
                Skip companies that already have a saved report.
        """

        self.agent = agent or NewsAgent()

        self.company_file = Path(company_file)
        self.output_dir = Path(output_dir)
        self.skip_existing = skip_existing

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # Public API
    # ==========================================================

    def run(self) -> dict[str, int]:
        """
        Run news analysis for all companies.

        Returns:
            Pipeline execution statistics.
        """

        companies = self._load_companies()

        total_companies = len(companies)

        stats = {
            "total": total_companies,
            "completed": 0,
            "skipped": 0,
            "failed": 0,
        }

        logger.info(
            "Starting News Analysis Pipeline for {} companies.",
            total_companies,
        )

        for index, row in companies.iterrows():
            symbol = self._extract_symbol(row)

            if not symbol:
                stats["failed"] += 1

                logger.warning(
                    "Skipping row {} because no valid symbol was found.",
                    index,
                )
                continue

            output_file = self._output_file(symbol)

            if self.skip_existing and output_file.exists():
                stats["skipped"] += 1

                logger.info(
                    "[{}/{}] {} skipped: report already exists.",
                    index + 1,
                    total_companies,
                    symbol,
                )
                continue

            logger.info(
                "[{}/{}] Processing {}.",
                index + 1,
                total_companies,
                symbol,
            )

            try:
                report = self.agent.run(symbol)

                self._save_report(
                    report=report,
                    output_file=output_file,
                )

                stats["completed"] += 1

                logger.success(
                    "[{}/{}] {} completed with score {} and rating {}.",
                    index + 1,
                    total_companies,
                    symbol,
                    report.score.score,
                    report.score.rating,
                )

            except Exception as exc:
                stats["failed"] += 1

                logger.exception(
                    "[{}/{}] {} failed: {}",
                    index + 1,
                    total_companies,
                    symbol,
                    exc,
                )

        logger.success(
            "News Analysis Pipeline finished. "
            "Total: {} | Completed: {} | Skipped: {} | Failed: {}",
            stats["total"],
            stats["completed"],
            stats["skipped"],
            stats["failed"],
        )

        return stats

    def run_symbol(
        self,
        symbol: str,
        overwrite: bool = True,
    ) -> Path:
        """
        Run news analysis for one company.

        Args:
            symbol:
                Saudi Exchange company symbol.

            overwrite:
                Whether to replace an existing report.

        Returns:
            Path to the saved report.
        """

        cleaned_symbol = self._clean_symbol(symbol)
        output_file = self._output_file(cleaned_symbol)

        if output_file.exists() and not overwrite:
            logger.info(
                "{} skipped: report already exists.",
                cleaned_symbol,
            )

            return output_file

        report = self.agent.run(cleaned_symbol)

        self._save_report(
            report=report,
            output_file=output_file,
        )

        logger.success(
            "{} news report saved to {}.",
            cleaned_symbol,
            output_file,
        )

        return output_file

    # ==========================================================
    # Company Loading
    # ==========================================================

    def _load_companies(self) -> pd.DataFrame:
        """
        Load and validate the company CSV file.
        """

        if not self.company_file.exists():
            raise FileNotFoundError(
                f"Company file not found: {self.company_file}"
            )

        companies = pd.read_csv(
            self.company_file,
            dtype={"symbol": str},
        )

        if companies.empty:
            raise ValueError(
                f"Company file is empty: {self.company_file}"
            )

        if "symbol" not in companies.columns:
            raise ValueError(
                "Company file must contain a 'symbol' column."
            )

        return companies

    @classmethod
    def _extract_symbol(
        cls,
        row: pd.Series,
    ) -> str | None:
        """
        Extract and normalize a symbol from one CSV row.
        """

        value = row.get("symbol")

        if pd.isna(value):
            return None

        try:
            return cls._clean_symbol(str(value))

        except ValueError:
            return None

    # ==========================================================
    # Report Saving
    # ==========================================================

    @staticmethod
    def _save_report(
        report,
        output_file: Path,
    ) -> None:
        """
        Save a Pydantic NewsReport as formatted JSON.
        """

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_file = output_file.with_suffix(".json.tmp")

        report_data = report.model_dump(
            mode="json"
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report_data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_file.replace(output_file)

    def _output_file(
        self,
        symbol: str,
    ) -> Path:
        """
        Return the output path for one company.
        """

        return self.output_dir / f"{symbol}.json"

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _clean_symbol(
        symbol: str,
    ) -> str:
        """
        Normalize company symbols read from CSV files.

        Examples:
            "2222"   -> "2222"
            "2222.0" -> "2222"
            " 2222 " -> "2222"
        """

        cleaned = str(symbol).strip()

        if cleaned.endswith(".0"):
            cleaned = cleaned[:-2]

        if not cleaned:
            raise ValueError(
                "Company symbol cannot be empty."
            )

        return cleaned