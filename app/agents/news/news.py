"""
SignalIQ - News Analysis Agent

Coordinates the complete company-news analysis workflow.

Workflow:
    Company profile
        ↓
    News collection
        ↓
    Sentiment analysis
        ↓
    Investment-focused summarization
        ↓
    News scoring
        ↓
    Structured NewsReport
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from loguru import logger

from .collector import NewsCollector
from .models import NewsReport
from .scoring import NewsScorer
from .sentiment import NewsSentimentAnalyzer
from .summarizer import NewsSummarizer
from .models import NewsReport

class NewsAgent:
    """
    Perform complete news analysis for one company.

    Responsibilities:
    - Load the stored company profile.
    - Extract a display name for the final report.
    - Extract an English search name for NewsAPI.
    - Collect recent company news.
    - Analyze article-level sentiment.
    - Generate an investment-focused summary.
    - Calculate an aggregated news score.
    - Return a validated NewsReport.
    """

    def __init__(
        self,
        collector: NewsCollector | None = None,
        sentiment_analyzer: NewsSentimentAnalyzer | None = None,
        summarizer: NewsSummarizer | None = None,
        scorer: NewsScorer | None = None,
        llm: Callable[[str], Any] | None = None,
        profile_dir: str | Path = "Data/profiles",
        max_articles: int = 20,
    ) -> None:
        """
        Initialize the News Agent.

        Args:
            collector:
                Optional custom NewsCollector.

            sentiment_analyzer:
                Optional custom NewsSentimentAnalyzer.

            summarizer:
                Optional custom NewsSummarizer.

            scorer:
                Optional custom NewsScorer.

            llm:
                Optional callable passed to NewsSummarizer.

            profile_dir:
                Directory containing company profile JSON files.

            max_articles:
                Maximum number of news articles collected per company.
        """

        if max_articles <= 0:
            raise ValueError(
                "max_articles must be greater than zero."
            )

        self.profile_dir = Path(profile_dir)

        self.collector = collector or NewsCollector(
            max_articles=max_articles,
        )

        self.sentiment_analyzer = (
            sentiment_analyzer
            or NewsSentimentAnalyzer()
        )

        self.summarizer = (
            summarizer
            or NewsSummarizer(llm=llm)
        )

        self.scorer = scorer or NewsScorer()

    # ==========================================================
    # Load Company Profile
    # ==========================================================

    def load_profile(
        self,
        symbol: str,
    ) -> dict[str, Any]:
        """
        Load the stored company profile.

        Args:
            symbol:
                Saudi Exchange company symbol.

        Returns:
            Company profile dictionary.

        Raises:
            FileNotFoundError:
                When the profile file does not exist.

            ValueError:
                When the profile is empty or invalid.
        """

        symbol = self._clean_symbol(symbol)

        profile_file = self.profile_dir / f"{symbol}.json"

        if not profile_file.exists():
            raise FileNotFoundError(
                f"Company profile not found for {symbol}: "
                f"{profile_file}"
            )

        try:
            with profile_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                profile = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid profile JSON for {symbol}: "
                f"{profile_file}"
            ) from exc

        except OSError as exc:
            raise OSError(
                f"Unable to read profile for {symbol}: "
                f"{profile_file}"
            ) from exc

        if not isinstance(profile, dict):
            raise ValueError(
                f"Profile for {symbol} must be a JSON object."
            )

        if not profile:
            raise ValueError(
                f"Profile for {symbol} is empty."
            )

        return profile

    # ==========================================================
    # Company Information
    # ==========================================================

    def get_company_name(
        self,
        symbol: str,
        profile: dict[str, Any],
    ) -> str:
        """
        Extract the display name used in the final report.

        Arabic names are prioritized so the generated SignalIQ
        report can continue displaying Arabic company names.
        """

        possible_names = (
            profile.get("arabicName"),
            profile.get("arabic_name"),
            profile.get("nameAr"),
            profile.get("name_ar"),
            profile.get("companyNameAr"),
            profile.get("company_name_ar"),
            profile.get("displayName"),
            profile.get("companyName"),
            profile.get("company_name"),
            profile.get("name"),
            profile.get("englishName"),
            profile.get("english_name"),
            profile.get("longName"),
            profile.get("shortName"),
        )

        for name in possible_names:
            cleaned_name = self._clean_optional_string(name)

            if cleaned_name:
                return cleaned_name

        logger.warning(
            "No display company name found in profile for {}. "
            "Using the symbol.",
            symbol,
        )

        return symbol

    def get_news_search_name(
        self,
        symbol: str,
        profile: dict[str, Any],
    ) -> str:
        """
        Return an English company name suitable for news searches.
        """

        # Prefer curated names for companies whose official profile name
        # is not commonly used in news articles.
        known_names = {
            "2222": "Saudi Aramco",
        }

        if symbol in known_names:
            return known_names[symbol]

        possible_names = (
            profile.get("name_en"),
            profile.get("english_name"),
            profile.get("longName"),
            profile.get("shortName"),
            profile.get("name"),
        )


        for name in possible_names:
            cleaned_name = self._clean_optional_string(name)

            if (
                cleaned_name
                and self._contains_latin_characters(cleaned_name)
            ):
                return cleaned_name

        logger.warning(
            "No English company name found for {}. "
            "Using the symbol.",
            symbol,
        )

        return symbol

    def get_company_aliases(
        self,
        profile: dict[str, Any],
        display_name: str,
        search_name: str,
    ) -> list[str]:
        """
        Extract alternative company names.

        Aliases may include:
        - Arabic company name
        - English company name
        - Short name
        - Trading name
        - Display name
        """

        possible_aliases = (
            profile.get("arabicName"),
            profile.get("arabic_name"),
            profile.get("nameAr"),
            profile.get("name_ar"),
            profile.get("companyNameAr"),
            profile.get("company_name_ar"),
            profile.get("englishName"),
            profile.get("english_name"),
            profile.get("companyNameEn"),
            profile.get("company_name_en"),
            profile.get("nameEn"),
            profile.get("name_en"),
            profile.get("shortName"),
            profile.get("longName"),
            profile.get("tradingName"),
            profile.get("displayName"),
            profile.get("companyName"),
            profile.get("company_name"),
            profile.get("name"),
        )

        aliases: list[str] = []

        excluded_names = {
            display_name.casefold(),
            search_name.casefold(),
        }

        for alias in possible_aliases:
            cleaned_alias = self._clean_optional_string(alias)

            if not cleaned_alias:
                continue

            if cleaned_alias.casefold() in excluded_names:
                continue

            aliases.append(cleaned_alias)

        # Add a useful short alias for Saudi Aramco.
        if search_name.casefold() == "saudi aramco":
            aliases.append("Aramco")

        return self._unique_strings(aliases)

    # ==========================================================
    # Analysis
    # ==========================================================

    def analyze(
        self,
        symbol: str,
        search_name: str | None = None,
    ) -> NewsReport:
        """
        Run the full news-analysis workflow for one company.

        Args:
            symbol:
                Saudi Exchange company symbol.

        Returns:
            Complete validated NewsReport.
        """

        symbol = self._clean_symbol(symbol)

        logger.info(
            "Starting news analysis for {}.",
            symbol,
        )

        # ------------------------------------------------------
        # Load profile
        # ------------------------------------------------------

        profile = self.load_profile(symbol)

        # Used in the final report and summary.
        company_name = self.get_company_name(
            symbol=symbol,
            profile=profile,
        )

        # Used only for NewsAPI search and English-language rules.
        if search_name:
            search_name = self._clean_optional_string(
                search_name
            )

        else:
            search_name = self.get_news_search_name(
                symbol=symbol,
                profile=profile,
        )

        if not search_name:
            search_name = symbol

        aliases = self.get_company_aliases(
            profile=profile,
            display_name=company_name,
            search_name=search_name,
        )

        logger.info(
            "Company {} | display name='{}' | "
            "news search name='{}'",
            symbol,
            company_name,
            search_name,
        )

        logger.debug(
            "News aliases for {}: {}",
            symbol,
            aliases,
        )

        # ------------------------------------------------------
        # Collect articles
        # ------------------------------------------------------

        articles = self.collector.collect(
            symbol=symbol,
            company_name=search_name,
            aliases=aliases,
        )

        logger.info(
            "Collected {} relevant news articles for {}.",
            len(articles),
            symbol,
        )

        if not articles:
            logger.warning(
                "No relevant news articles found for {} "
                "using search name '{}'.",
                symbol,
                search_name,
            )

        # ------------------------------------------------------
        # Sentiment analysis
        # ------------------------------------------------------

        analyzed_articles = (
            self.sentiment_analyzer.analyze_articles(
                articles
            )
        )

        logger.debug(
            "Sentiment analysis completed for {} articles.",
            len(analyzed_articles),
        )

        # ------------------------------------------------------
        # Company-perspective sentiment adjustment
        # ------------------------------------------------------

        analyzed_articles = self.adjust_company_sentiment(
            articles=analyzed_articles,
            company_name=search_name,
        )

        logger.debug(
            "Company-perspective sentiment adjustment "
            "completed for {} articles.",
            len(analyzed_articles),
        )

        # ------------------------------------------------------
        # Summarization
        # ------------------------------------------------------

        summary = self.summarizer.summarize(
            symbol=symbol,
            company_name=company_name,
            articles=analyzed_articles,
        )

        # ------------------------------------------------------
        # Scoring
        # ------------------------------------------------------

        score = self.scorer.score(
            articles=analyzed_articles,
            summary=summary,
        )

        # ------------------------------------------------------
        # Build report
        # ------------------------------------------------------

        report = NewsReport(
            symbol=symbol,
            company_name=company_name,
            article_count=len(analyzed_articles),
            articles=analyzed_articles,
            score=score,
            summary=summary,
        )

        logger.success(
            "{} news analysis completed: "
            "score={}, rating={}, articles={}",
            symbol,
            report.score.score,
            report.score.rating,
            report.article_count,
        )

        return report

    def adjust_company_sentiment(
        self,
        articles: list[NewsReport],
        company_name: str,
    ) -> list[NewsReport]:
        """
        Adjust generic sentiment from the company's perspective.

        A general sentiment model may classify a headline as positive
        because it contains positive language about another company.

        Example:
            "Meta surpasses Saudi Aramco"

        This may be positive for Meta, but it is negative or unfavorable
        from Saudi Aramco's perspective.
        """

        company = company_name.strip().casefold()

        if not company:
            return articles

        negative_patterns = (
            f"surpasses {company}",
            f"surpassed {company}",
            f"overtakes {company}",
            f"overtook {company}",
            f"beats {company}",
            f"beat {company}",
            f"passes {company}",
            f"passed {company}",
            f"ahead of {company}",
            f"replaces {company}",
            f"replaced {company}",
            f"{company} falls behind",
            f"{company} fell behind",
            f"{company} loses",
            f"{company} lost",
            f"{company} declines",
            f"{company} declined",
            f"{company} drops",
            f"{company} dropped",
            f"{company} falls",
            f"{company} fell",
            f"{company} misses",
            f"{company} missed",
            f"{company} cuts",
            f"{company} cut",
            f"{company} warns",
            f"{company} warned",
        )

        positive_patterns = (
            f"{company} surpasses",
            f"{company} surpassed",
            f"{company} overtakes",
            f"{company} overtook",
            f"{company} beats",
            f"{company} beat",
            f"{company} passes",
            f"{company} passed",
            f"{company} leads",
            f"{company} led",
            f"{company} rises",
            f"{company} rose",
            f"{company} gains",
            f"{company} gained",
            f"{company} grows",
            f"{company} grew",
            f"{company} wins",
            f"{company} won",
            f"{company} expands",
            f"{company} expanded",
            f"{company} reports record",
            f"{company} posts record",
        )

        for article in articles:
            if article.sentiment is None:
                continue

            title = article.title.casefold()

            description = (
                article.description.casefold()
                if article.description
                else ""
            )

            # Give the title priority because it usually expresses
            # the main event and affected company.
            text = f"{title} {description}"

            matched_negative_pattern = next(
                (
                    pattern
                    for pattern in negative_patterns
                    if pattern in text
                ),
                None,
            )

            matched_positive_pattern = next(
                (
                    pattern
                    for pattern in positive_patterns
                    if pattern in text
                ),
                None,
            )

            if matched_negative_pattern:
                original_label = article.sentiment.label
                original_score = article.sentiment.score

                article.sentiment.label = "negative"
                article.sentiment.score = -abs(
                    float(article.sentiment.score)
                )

                logger.debug(
                    "Adjusted sentiment for '{}' from {} ({}) "
                    "to negative ({}) using pattern '{}'.",
                    article.title,
                    original_label,
                    original_score,
                    article.sentiment.score,
                    matched_negative_pattern,
                )

            elif matched_positive_pattern:
                original_label = article.sentiment.label
                original_score = article.sentiment.score

                article.sentiment.label = "positive"
                article.sentiment.score = abs(
                    float(article.sentiment.score)
                )

                logger.debug(
                    "Adjusted sentiment for '{}' from {} ({}) "
                    "to positive ({}) using pattern '{}'.",
                    article.title,
                    original_label,
                    original_score,
                    article.sentiment.score,
                    matched_positive_pattern,
                )

        return articles

    # ==========================================================
    # Public Run Method
    # ==========================================================

    def run(
        self,
        symbol: str,
    ) -> NewsReport:
        """
        Public entry point used by the News Pipeline.
        """

        symbol = self._clean_symbol(symbol)

        try:
            return self.analyze(symbol)

        except Exception as exc:
            logger.exception(
                "News analysis failed for {}: {}",
                symbol,
                exc,
            )

            raise

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _clean_symbol(
        symbol: str,
    ) -> str:
        """
        Normalize a Saudi Exchange symbol.

        Removes the decimal suffix that may appear when pandas
        reads integer symbols as floating-point values.
        """

        cleaned_symbol = str(symbol).strip()

        if cleaned_symbol.endswith(".0"):
            cleaned_symbol = cleaned_symbol[:-2]

        if not cleaned_symbol:
            raise ValueError(
                "symbol cannot be empty."
            )

        return cleaned_symbol

    @staticmethod
    def _clean_optional_string(
        value: Any,
    ) -> str | None:
        """
        Convert an optional profile value into a clean string.
        """

        if value is None:
            return None

        cleaned_value = " ".join(
            str(value).strip().split()
        )

        if not cleaned_value:
            return None

        return cleaned_value

    @staticmethod
    def _contains_latin_characters(
        value: str,
    ) -> bool:
        """
        Check whether a string contains Latin alphabet characters.
        """

        return any(
            ("a" <= character.lower() <= "z")
            for character in value
        )

    @staticmethod
    def _unique_strings(
        values: list[str],
    ) -> list[str]:
        """
        Remove duplicate strings while preserving order.
        """

        unique_values: list[str] = []
        seen: set[str] = set()

        for value in values:
            cleaned_value = " ".join(
                str(value).strip().split()
            )

            if not cleaned_value:
                continue

            normalized_value = cleaned_value.casefold()

            if normalized_value in seen:
                continue

            seen.add(normalized_value)
            unique_values.append(cleaned_value)

        return unique_values