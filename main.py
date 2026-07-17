"""
SignalIQ - Main Investment Pipeline

Automatically runs:
1. Data Collection
2. Fundamental Analysis
3. Technical Analysis
4. News Analysis
5. Risk Analysis
6. Supervisor Recommendations
7. Portfolio Construction
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from loguru import logger

from app.agents.data_collection.pipeline import DataCollectionPipeline
from app.agents.fundamental.pipeline import FundamentalPipeline
from app.agents.technical.pipeline import TechnicalPipeline
from app.agents.news.pipeline import NewsPipeline
from app.agents.risk import RiskAgent
from app.agents.supervisor import SupervisorAgent
from app.agents.portfolio import PortfolioAgent


COMPANIES_FILE = Path("data/saudi_companies.csv")

RISK_DIR = Path("data/analysis/risk")
SUPERVISOR_DIR = Path("data/analysis/supervisor")


def clean_symbol(value: Any) -> str:
    """
    Convert values such as 2222.0 into 2222.
    """

    symbol = str(value).strip()

    if symbol.endswith(".0"):
        symbol = symbol[:-2]

    return symbol


def load_symbols() -> list[str]:
    """
    Load all company symbols from the companies CSV.
    """

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

    return symbols


def run_batch_pipeline(
    name: str,
    pipeline: Any,
) -> None:
    """
    Run a pipeline that processes all companies.

    An error is logged without stopping the complete workflow.
    """

    logger.info(
        "Starting {}.",
        name,
    )

    try:
        pipeline.run()

        logger.success(
            "{} completed.",
            name,
        )

    except Exception as exc:
        logger.exception(
            "{} failed: {}",
            name,
            exc,
        )


def run_risk_and_supervisor(
    symbols: list[str],
) -> list[str]:
    """
    Generate risk and supervisor reports for every company.

    Returns:
        Symbols that successfully produced Supervisor reports.
    """

    RISK_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SUPERVISOR_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    risk_agent = RiskAgent()
    supervisor_agent = SupervisorAgent()

    successful_symbols: list[str] = []

    for index, symbol in enumerate(
        symbols,
        start=1,
    ):
        logger.info(
            "[{}/{}] Processing {}",
            index,
            len(symbols),
            symbol,
        )

        risk_file = RISK_DIR / f"{symbol}.json"
        supervisor_file = (
            SUPERVISOR_DIR / f"{symbol}.json"
        )

        try:
            # Generate risk report only when missing.
            if risk_file.exists():
                logger.info(
                    "Using cached risk report for {}.",
                    symbol,
                )
            else:
                risk_agent.run(
                    symbol=symbol,
                    save=True,
                )

            # Generate Supervisor report only when missing.
            if supervisor_file.exists():
                logger.info(
                    "Using cached Supervisor report for {}.",
                    symbol,
                )
            else:
                supervisor_agent.run(
                    symbol=symbol,
                    save=True,
                )

            successful_symbols.append(
                symbol
            )

        except Exception as exc:
            logger.exception(
                "Risk or Supervisor failed for {}: {}",
                symbol,
                exc,
            )

    return successful_symbols


def print_recommendations(
    symbols: list[str],
) -> None:
    """
    Print final Supervisor recommendations ordered by score.
    """

    recommendations: list[dict[str, Any]] = []

    for symbol in symbols:
        report_file = (
            SUPERVISOR_DIR / f"{symbol}.json"
        )

        if not report_file.exists():
            continue

        try:
            report = pd.read_json(
                report_file,
                typ="series",
            ).to_dict()

        except Exception as exc:
            logger.warning(
                "Could not read Supervisor report {}: {}",
                report_file,
                exc,
            )

            continue

        recommendations.append(
            report
        )

    recommendations.sort(
        key=lambda report: float(
            report.get(
                "final_score",
                0,
            )
        ),
        reverse=True,
    )

    print()
    print("=" * 90)
    print("SIGNALIQ FINAL INVESTMENT RECOMMENDATIONS")
    print("=" * 90)

    print(
        f"{'Symbol':<10}"
        f"{'Company':<35}"
        f"{'Score':<12}"
        f"{'Recommendation':<18}"
        f"{'Confidence':<12}"
    )

    print("-" * 90)

    for report in recommendations:
        symbol = str(
            report.get(
                "symbol",
                "",
            )
        )

        company_name = str(
            report.get(
                "company_name",
                symbol,
            )
        )[:32]

        score = float(
            report.get(
                "final_score",
                0,
            )
        )

        recommendation = str(
            report.get(
                "recommendation",
                "Unknown",
            )
        )

        confidence = float(
            report.get(
                "confidence",
                0,
            )
        )

        print(
            f"{symbol:<10}"
            f"{company_name:<35}"
            f"{score:<12.2f}"
            f"{recommendation:<18}"
            f"{confidence:<12.2f}"
        )

    print("=" * 90)


def main() -> None:
    """
    Run the complete SignalIQ workflow.
    """

    logger.info(
        "Starting complete SignalIQ pipeline."
    )

    symbols = load_symbols()

    logger.info(
        "{} unique company symbols loaded.",
        len(symbols),
    )

    # These pipelines already process all available companies.
    #run_batch_pipeline(
     #   name="Data Collection Agent",
      #  pipeline=DataCollectionPipeline(),
    #)

    #run_batch_pipeline(
     #   name="Fundamental Agent",
      #  pipeline=FundamentalPipeline(),
    #)

    #run_batch_pipeline(
        #name="Technical Agent",
        #pipeline=TechnicalPipeline(),
    #)

    #run_batch_pipeline(
        #name="News Agent",
        #pipeline=NewsPipeline(),
    #)

    successful_symbols = (
        run_risk_and_supervisor(
            symbols
        )
    )

    print_recommendations(
        successful_symbols
    )

    logger.info(
        "Building final portfolio."
    )

    try:
        portfolio = PortfolioAgent(
            max_positions=10,
            max_weight=0.20,
            minimum_score=55,
        ).run(
            symbols=successful_symbols,
            portfolio_value=100_000,
            save=True,
        )

        print()
        print("=" * 90)
        print("FINAL PORTFOLIO")
        print("=" * 90)

        for position in portfolio.get(
            "positions",
            [],
        ):
            print(
                f"{position['symbol']:<10}"
                f"{str(position['company_name'])[:32]:<35}"
                f"{position['weight_percent']:>7.2f}%  "
                f"SAR {position['allocation_sar']:>12,.2f}"
            )

        print("-" * 90)

        print(
            f"Portfolio score: "
            f"{portfolio.get('portfolio_score', 0)}"
        )

        print(
            f"Portfolio risk: "
            f"{portfolio.get('portfolio_risk_level', 'unknown')}"
        )

        print(
            f"Cash allocation: SAR "
            f"{portfolio.get('cash_allocation_sar', 0):,.2f}"
        )

        print("=" * 90)

    except Exception as exc:
        logger.exception(
            "Portfolio Agent failed: {}",
            exc,
        )

    logger.success(
        "Complete SignalIQ pipeline finished."
    )


if __name__ == "__main__":
    main()