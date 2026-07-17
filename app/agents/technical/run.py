"""
Run the Technical Analysis Pipeline.
"""

from app.agents.technical.pipeline import TechnicalPipeline


def main():

    TechnicalPipeline().run()


if __name__ == "__main__":
    main()