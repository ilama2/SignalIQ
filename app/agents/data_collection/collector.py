"""
SignalIQ - Data Collection Agent

Entry point for the data collection process.
"""

from loguru import logger

from app.agents.data_collection.pipeline import DataCollectionPipeline


class DataCollector:
    """Runs the complete data collection pipeline."""

    def __init__(self):
        self.pipeline = DataCollectionPipeline()

    def run(self):
        logger.info("=" * 60)
        logger.info("Starting Data Collection Agent")

        try:
            self.pipeline.run()

            logger.success("Data Collection completed successfully.")

        except KeyboardInterrupt:
            logger.warning("Data Collection interrupted by user.")

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")

        finally:
            logger.info("Data Collection Agent finished.")
            logger.info("=" * 60)


def main():
    collector = DataCollector()
    collector.run()


if __name__ == "__main__":
    main()