"""
SignalIQ - Run News Analysis Pipeline
"""

from __future__ import annotations

import argparse

from loguru import logger

from .pipeline import NewsPipeline


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run the SignalIQ News Analysis Pipeline."
    )

    parser.add_argument(
        "--symbol",
        type=str,
        help="Run news analysis for a single company symbol.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing report when using --symbol.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run news analysis for all companies.",
    )

    return parser.parse_args()


def main() -> None:
    """
    Entry point.
    """

    args = parse_args()

    pipeline = NewsPipeline()

    if args.symbol:
        logger.info(
            "Running News Agent for symbol: {}",
            args.symbol,
        )

        pipeline.run_symbol(
            symbol=args.symbol,
            overwrite=args.overwrite,
        )

        return

    logger.info(
        "Running News Analysis Pipeline for all companies."
    )

    stats = pipeline.run()

    logger.success(
        "Completed: {} | Skipped: {} | Failed: {}",
        stats["completed"],
        stats["skipped"],
        stats["failed"],
    )


if __name__ == "__main__":
    main()