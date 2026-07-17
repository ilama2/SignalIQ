"""
Run the Risk Agent for all Saudi companies.
"""

from pathlib import Path

import pandas as pd
from loguru import logger

from app.agents.risk import RiskAgent


COMPANIES_FILE = Path("Data/saudi_companies.csv")
OUTPUT_DIR = Path("Data/analysis/risk")


def clean_symbol(value: object) -> str:
    """Convert CSV symbols such as 2222.0 into 2222."""
    symbol = str(value).strip()

    if symbol.endswith(".0"):
        symbol = symbol[:-2]

    return symbol


def main() -> None:
    if not COMPANIES_FILE.exists():
        raise FileNotFoundError(
            f"Companies file not found: {COMPANIES_FILE}"
        )

    companies = pd.read_csv(
        COMPANIES_FILE,
        dtype={"symbol": str},
    )

    if "symbol" not in companies.columns:
        raise ValueError(
            "saudi_companies.csv must contain a 'symbol' column."
        )

    symbols = (
        companies["symbol"]
        .dropna()
        .map(clean_symbol)
        .loc[lambda values: values != ""]
        .drop_duplicates()
        .tolist()
    )

    agent = RiskAgent()

    successful = 0
    failed = 0
    skipped = 0
    failures: list[dict[str, str]] = []

    logger.info(
        "Starting Risk Agent for {} companies.",
        len(symbols),
    )

    for index, symbol in enumerate(
        symbols,
        start=1,
    ):
        output_file = OUTPUT_DIR / f"{symbol}.json"

        logger.info(
            "[{}/{}] Processing {}",
            index,
            len(symbols),
            symbol,
        )

        # Skip reports that were already generated.
        if output_file.exists():
            logger.info(
                "Skipping {} because the risk report already exists.",
                symbol,
            )

            skipped += 1
            continue

        try:
            report = agent.run(
                symbol=symbol,
                save=True,
            )

            successful += 1

            logger.success(
                "{} completed: risk_score={}, risk_level={}",
                symbol,
                report.get("risk_score"),
                report.get("risk_level"),
            )

        except Exception as exc:
            failed += 1

            failures.append(
                {
                    "symbol": symbol,
                    "error": str(exc),
                }
            )

            logger.exception(
                "Risk analysis failed for {}: {}",
                symbol,
                exc,
            )

    logger.info("=" * 60)
    logger.info("Risk Agent batch completed.")
    logger.info("Total companies: {}", len(symbols))
    logger.info("Successful: {}", successful)
    logger.info("Skipped: {}", skipped)
    logger.info("Failed: {}", failed)

    if failures:
        failures_file = OUTPUT_DIR / "failures.csv"

        pd.DataFrame(failures).to_csv(
            failures_file,
            index=False,
        )

        logger.warning(
            "Failure details saved to {}.",
            failures_file,
        )


if __name__ == "__main__":
    main()