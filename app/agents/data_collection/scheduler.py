"""
SignalIQ - Data Collection Scheduler

Runs the data collection pipeline automatically.
"""

import time

import schedule
from loguru import logger

from app.agents.data_collection.pipeline import DataCollectionPipeline


def run_pipeline():
    """Execute one data collection cycle."""

    try:
        logger.info("Starting scheduled data collection...")

        pipeline = DataCollectionPipeline()

        pipeline.run()

        logger.success("Data collection finished.")

    except Exception as e:
        logger.exception(
            f"Data collection failed: {e}"
        )


# ==========================================================
# Schedule
# ==========================================================

# Every day at 5:00 PM
schedule.every().day.at("17:00").do(run_pipeline)

# Optional:
# schedule.every().hour.do(run_pipeline)
# schedule.every(30).minutes.do(run_pipeline)

logger.info("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(100000)