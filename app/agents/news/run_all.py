"""
Run the News Agent for all Saudi companies.

Usage:
    uv run python -m app.agents.news.run_all

Overwrite existing reports:
    uv run python -m app.agents.news.run_all --overwrite

Limit the run for testing:
    uv run python -m app.agents.news.run_all --limit 10
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
from loguru import logger

from app.agents.news.pipeline import NewsPipeline


DEFAULT_COMPANIES_FILE = Path(
    "data/saudi_companies.csv"
)


def clean_symbol(value: object) -> str:
    """
    Convert a company symbol into a clean string.

    Examples:
        2222.0 -> "2222"
        "1120" -> "1120"
    """

    if pd.isna(value):
        return ""

    symbol = str(value).strip()

    if symbol.endswith(".0"):
        symbol = symbol[:-2]

    return symbol


def load_symbols(
    csv_path: Path,
    symbol_column: str = "symbol",
) -> list[str]:
    """
    Read unique company symbols from the CSV file.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Companies file not found: {csv_path}"
        )

    dataframe = pd.read_csv(
        csv_path,
        dtype={symbol_column: str},
    )

    if symbol_column not in dataframe.columns:
        raise ValueError(
            f"Column '{symbol_column}' was not found in "
            f"{csv_path}. Available columns: "
            f"{list(dataframe.columns)}"
        )

    symbols = [
        clean_symbol(value)
        for value in dataframe[symbol_column]
    ]

    # Remove empty and duplicate symbols while
    # preserving their original order.
    unique_symbols = list(
        dict.fromkeys(
            symbol
            for symbol in symbols
            if symbol
        )
    )

    return unique_symbols


def run_all_companies(
    csv_path: Path,
    overwrite: bool = False,
    limit: int | None = None,
    delay_seconds: float = 1.0,
) -> None:
    """
    Run the news pipeline for all company symbols.
    """

    symbols = load_symbols(csv_path)

    if limit is not None:
        symbols = symbols[:limit]

    pipeline = NewsPipeline()

    total = len(symbols)
    successful = 0
    failed = 0
    skipped = 0
    failures: list[tuple[str, str]] = []

    logger.info(
        "Starting news collection for {} companies.",
        total,
    )

    for index, symbol in enumerate(
        symbols,
        start=1,
    ):
        logger.info(
            "[{}/{}] Processing company {}.",
            index,
            total,
            symbol,
        )

        try:
            result = pipeline.run_symbol(
                symbol=symbol,
                overwrite=overwrite,
            )

            # Some pipeline implementations return None
            # when an existing report is skipped.
            if result is None:
                skipped += 1

                logger.info(
                    "[{}/{}] Skipped {}.",
                    index,
                    total,
                    symbol,
                )
            else:
                successful += 1

                logger.success(
                    "[{}/{}] Completed {}.",
                    index,
                    total,
                    symbol,
                )

        except Exception as error:
            failed += 1
            failures.append(
                (
                    symbol,
                    str(error),
                )
            )

            logger.exception(
                "[{}/{}] Failed {}: {}",
                index,
                total,
                symbol,
                error,
            )

        # Avoid sending requests too quickly to NewsAPI.
        if delay_seconds > 0 and index < total:
            time.sleep(delay_seconds)

    logger.info(
        "News batch completed: total={}, successful={}, "
        "skipped={}, failed={}",
        total,
        successful,
        skipped,
        failed,
    )

    if failures:
        logger.warning("Failed company symbols:")

        for symbol, error in failures:
            logger.warning(
                "{}: {}",
                symbol,
                error,
            )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Run the News Agent for all companies "
            "in saudi_companies.csv."
        )
    )

    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_COMPANIES_FILE,
        help=(
            "Path to the companies CSV file. "
            "Default: data/saudi_companies.csv"
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate reports that already exist.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only process the first N companies.",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help=(
            "Delay between companies in seconds. "
            "Default: 1.0"
        ),
    )

    return parser.parse_args()


def main() -> None:
    """
    CLI entry point.
    """

    args = parse_arguments()

    run_all_companies(
        csv_path=args.csv,
        overwrite=args.overwrite,
        limit=args.limit,
        delay_seconds=args.delay,
    )


if __name__ == "__main__":
    main()