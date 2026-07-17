"""
SignalIQ - Risk Management Agent

Evaluates investment risk using:
- Historical price volatility
- Maximum drawdown
- Value at Risk
- Downside volatility
- Fundamental leverage and liquidity

Important:
    risk_score is a safety score.

    High risk_score = safer investment.
    Low risk_score = riskier investment.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger


class RiskAgent:
    """Calculate the investment risk of one Saudi-listed company."""

    def __init__(
        self,
        prices_dir: str | Path = "data/prices",
        fundamental_dir: str | Path = "data/analysis/fundamental",
        output_dir: str | Path = "data/analysis/risk",
        trading_days: int = 252,
    ) -> None:
        self.prices_dir = Path(prices_dir)
        self.fundamental_dir = Path(fundamental_dir)
        self.output_dir = Path(output_dir)
        self.trading_days = trading_days

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # Public API
    # ==========================================================

    def run(
        self,
        symbol: str,
        save: bool = True,
    ) -> dict[str, Any]:
        """
        Generate a risk report for one company.

        Args:
            symbol:
                Saudi Exchange company symbol.

            save:
                Save the report as JSON.

        Returns:
            Risk analysis report.
        """

        symbol = self._clean_symbol(symbol)

        logger.info(
            "Starting risk analysis for {}.",
            symbol,
        )

        prices = self._load_prices(symbol)
        fundamental_report = self._load_json(
            self.fundamental_dir / f"{symbol}.json"
        )

        company_name = self._extract_company_name(
            fundamental_report,
            symbol,
        )

        if prices.empty:
            logger.warning(
                "No usable prices found for {}. "
                "Generating a limited risk report.",
                symbol,
            )

            report = self._build_missing_prices_report(
                symbol=symbol,
                company_name=company_name,
                fundamental_report=fundamental_report,
            )

        else:
            report = self._analyze(
                symbol=symbol,
                company_name=company_name,
                prices=prices,
                fundamental_report=fundamental_report,
            )

        if save:
            self._save_report(
                symbol=symbol,
                report=report,
            )

        logger.success(
            "Risk analysis completed for {}: "
            "risk_level={}, risk_score={}.",
            symbol,
            report["risk_level"],
            report["risk_score"],
        )

        return report

    # ==========================================================
    # Main Analysis
    # ==========================================================

    def _analyze(
        self,
        symbol: str,
        company_name: str,
        prices: pd.DataFrame,
        fundamental_report: dict[str, Any] | None,
    ) -> dict[str, Any]:
        close = self._extract_close(prices)

        returns = close.pct_change().replace(
            [np.inf, -np.inf],
            np.nan,
        ).dropna()

        annualized_volatility = self._annualized_volatility(
            returns
        )

        downside_volatility = self._downside_volatility(
            returns
        )

        max_drawdown = self._maximum_drawdown(
            close
        )

        value_at_risk_95 = self._historical_var(
            returns=returns,
            confidence=0.95,
        )

        conditional_var_95 = self._conditional_var(
            returns=returns,
            confidence=0.95,
        )

        sharpe_ratio = self._sharpe_ratio(
            returns
        )

        leverage_score, leverage_metrics = (
            self._evaluate_fundamental_risk(
                fundamental_report
            )
        )

        market_safety_score = self._calculate_market_safety_score(
            annualized_volatility=annualized_volatility,
            max_drawdown=max_drawdown,
            downside_volatility=downside_volatility,
            value_at_risk_95=value_at_risk_95,
        )

        # Market risk is more important because it comes directly
        # from the company's price history.
        risk_score = (
            market_safety_score * 0.75
            + leverage_score * 0.25
        )

        risk_score = self._clamp(risk_score)
        risk_level = self._get_risk_level(risk_score)

        risks = self._collect_risks(
            annualized_volatility=annualized_volatility,
            downside_volatility=downside_volatility,
            max_drawdown=max_drawdown,
            value_at_risk_95=value_at_risk_95,
            leverage_metrics=leverage_metrics,
        )

        strengths = self._collect_strengths(
            annualized_volatility=annualized_volatility,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            leverage_metrics=leverage_metrics,
        )

        return {
            "symbol": symbol,
            "company_name": company_name,
            "generated_at": datetime.now().isoformat(),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "higher_is_riskier": False,
            "market_safety_score": round(
                market_safety_score,
                2,
            ),
            "fundamental_safety_score": round(
                leverage_score,
                2,
            ),
            "metrics": {
                "observations": int(len(close)),
                "annualized_volatility": self._round_optional(
                    annualized_volatility
                ),
                "downside_volatility": self._round_optional(
                    downside_volatility
                ),
                "max_drawdown": self._round_optional(
                    max_drawdown
                ),
                "value_at_risk_95": self._round_optional(
                    value_at_risk_95
                ),
                "conditional_var_95": self._round_optional(
                    conditional_var_95
                ),
                "sharpe_ratio": self._round_optional(
                    sharpe_ratio
                ),
                **leverage_metrics,
            },
            # Also included at the top level for compatibility
            # with the current Supervisor Agent.
            "volatility": self._round_optional(
                annualized_volatility
            ),
            "max_drawdown": self._round_optional(
                max_drawdown
            ),
            "strengths": strengths,
            "risks": risks,
            "summary": self._build_summary(
                company_name=company_name,
                risk_score=risk_score,
                risk_level=risk_level,
                annualized_volatility=annualized_volatility,
                max_drawdown=max_drawdown,
                risks=risks,
            ),
        }

    # ==========================================================
    # Price Metrics
    # ==========================================================

    def _annualized_volatility(
        self,
        returns: pd.Series,
    ) -> float | None:
        if len(returns) < 2:
            return None

        volatility = (
            returns.std(ddof=1)
            * np.sqrt(self.trading_days)
            * 100
        )

        return self._finite_float(volatility)

    def _downside_volatility(
        self,
        returns: pd.Series,
    ) -> float | None:
        negative_returns = returns[
            returns < 0
        ]

        if len(negative_returns) < 2:
            return None

        value = (
            negative_returns.std(ddof=1)
            * np.sqrt(self.trading_days)
            * 100
        )

        return self._finite_float(value)

    @staticmethod
    def _maximum_drawdown(
        close: pd.Series,
    ) -> float | None:
        if close.empty:
            return None

        rolling_peak = close.cummax()
        drawdown = (
            close / rolling_peak
        ) - 1.0

        value = abs(drawdown.min()) * 100

        return RiskAgent._finite_float(value)

    @staticmethod
    def _historical_var(
        returns: pd.Series,
        confidence: float,
    ) -> float | None:
        if returns.empty:
            return None

        percentile = np.percentile(
            returns,
            (1.0 - confidence) * 100,
        )

        # Positive percentage loss.
        return RiskAgent._finite_float(
            max(0.0, -percentile * 100)
        )

    @staticmethod
    def _conditional_var(
        returns: pd.Series,
        confidence: float,
    ) -> float | None:
        if returns.empty:
            return None

        threshold = np.percentile(
            returns,
            (1.0 - confidence) * 100,
        )

        tail_losses = returns[
            returns <= threshold
        ]

        if tail_losses.empty:
            return None

        return RiskAgent._finite_float(
            max(
                0.0,
                -tail_losses.mean() * 100,
            )
        )

    def _sharpe_ratio(
        self,
        returns: pd.Series,
    ) -> float | None:
        if len(returns) < 2:
            return None

        standard_deviation = returns.std(
            ddof=1
        )

        if (
            standard_deviation is None
            or standard_deviation == 0
            or np.isnan(standard_deviation)
        ):
            return None

        value = (
            returns.mean()
            / standard_deviation
            * np.sqrt(self.trading_days)
        )

        return self._finite_float(value)

    # ==========================================================
    # Scoring
    # ==========================================================

    def _calculate_market_safety_score(
        self,
        annualized_volatility: float | None,
        max_drawdown: float | None,
        downside_volatility: float | None,
        value_at_risk_95: float | None,
    ) -> float:
        volatility_score = self._inverse_score(
            value=annualized_volatility,
            safe=15.0,
            dangerous=60.0,
        )

        drawdown_score = self._inverse_score(
            value=max_drawdown,
            safe=10.0,
            dangerous=60.0,
        )

        downside_score = self._inverse_score(
            value=downside_volatility,
            safe=10.0,
            dangerous=50.0,
        )

        var_score = self._inverse_score(
            value=value_at_risk_95,
            safe=1.0,
            dangerous=6.0,
        )

        return (
            volatility_score * 0.35
            + drawdown_score * 0.35
            + downside_score * 0.20
            + var_score * 0.10
        )

    @staticmethod
    def _inverse_score(
        value: float | None,
        safe: float,
        dangerous: float,
    ) -> float:
        """
        Convert a risk metric to a safety score.

        Values at or below `safe` receive 100.
        Values at or above `dangerous` receive 0.
        """

        if value is None:
            return 50.0

        if value <= safe:
            return 100.0

        if value >= dangerous:
            return 0.0

        position = (
            value - safe
        ) / (
            dangerous - safe
        )

        return 100.0 * (
            1.0 - position
        )

    @staticmethod
    def _get_risk_level(
        risk_score: float,
    ) -> str:
        if risk_score >= 80:
            return "very low"

        if risk_score >= 65:
            return "low"

        if risk_score >= 45:
            return "medium"

        if risk_score >= 25:
            return "high"

        return "very high"

    # ==========================================================
    # Fundamental Risk
    # ==========================================================

    def _evaluate_fundamental_risk(
        self,
        report: dict[str, Any] | None,
    ) -> tuple[float, dict[str, Any]]:
        if not report:
            return 50.0, {
                "debt_to_equity": None,
                "current_ratio": None,
                "interest_coverage": None,
            }

        debt_to_equity = self._find_numeric_value(
            report,
            (
                "debt_to_equity",
                "debtEquity",
                "debt_equity",
            ),
        )

        current_ratio = self._find_numeric_value(
            report,
            (
                "current_ratio",
                "currentRatio",
            ),
        )

        interest_coverage = self._find_numeric_value(
            report,
            (
                "interest_coverage",
                "interestCoverage",
            ),
        )

        scores: list[float] = []

        if debt_to_equity is not None:
            scores.append(
                self._inverse_score(
                    value=debt_to_equity,
                    safe=0.5,
                    dangerous=3.0,
                )
            )

        if current_ratio is not None:
            if current_ratio >= 2:
                scores.append(100.0)
            elif current_ratio <= 0.5:
                scores.append(10.0)
            else:
                scores.append(
                    10.0
                    + (
                        current_ratio - 0.5
                    ) / 1.5 * 90.0
                )

        if interest_coverage is not None:
            if interest_coverage >= 5:
                scores.append(100.0)
            elif interest_coverage <= 1:
                scores.append(10.0)
            else:
                scores.append(
                    10.0
                    + (
                        interest_coverage - 1
                    ) / 4 * 90.0
                )

        safety_score = (
            float(np.mean(scores))
            if scores
            else 50.0
        )

        return self._clamp(safety_score), {
            "debt_to_equity": self._round_optional(
                debt_to_equity
            ),
            "current_ratio": self._round_optional(
                current_ratio
            ),
            "interest_coverage": self._round_optional(
                interest_coverage
            ),
        }

    # ==========================================================
    # Strengths and Risks
    # ==========================================================

    @staticmethod
    def _collect_risks(
        annualized_volatility: float | None,
        downside_volatility: float | None,
        max_drawdown: float | None,
        value_at_risk_95: float | None,
        leverage_metrics: dict[str, Any],
    ) -> list[str]:
        risks: list[str] = []

        if (
            annualized_volatility is not None
            and annualized_volatility > 35
        ):
            risks.append(
                "High historical price volatility"
            )

        if (
            downside_volatility is not None
            and downside_volatility > 30
        ):
            risks.append(
                "High downside volatility"
            )

        if (
            max_drawdown is not None
            and max_drawdown > 35
        ):
            risks.append(
                "Large historical maximum drawdown"
            )

        if (
            value_at_risk_95 is not None
            and value_at_risk_95 > 4
        ):
            risks.append(
                "Elevated one-day Value at Risk"
            )

        debt_to_equity = leverage_metrics.get(
            "debt_to_equity"
        )

        if (
            debt_to_equity is not None
            and debt_to_equity > 2
        ):
            risks.append(
                "High debt-to-equity ratio"
            )

        current_ratio = leverage_metrics.get(
            "current_ratio"
        )

        if (
            current_ratio is not None
            and current_ratio < 1
        ):
            risks.append(
                "Weak short-term liquidity"
            )

        if not risks:
            risks.append(
                "No major risk signal was identified"
            )

        return risks

    @staticmethod
    def _collect_strengths(
        annualized_volatility: float | None,
        max_drawdown: float | None,
        sharpe_ratio: float | None,
        leverage_metrics: dict[str, Any],
    ) -> list[str]:
        strengths: list[str] = []

        if (
            annualized_volatility is not None
            and annualized_volatility <= 20
        ):
            strengths.append(
                "Relatively low historical volatility"
            )

        if (
            max_drawdown is not None
            and max_drawdown <= 20
        ):
            strengths.append(
                "Controlled historical drawdown"
            )

        if (
            sharpe_ratio is not None
            and sharpe_ratio >= 1
        ):
            strengths.append(
                "Strong historical risk-adjusted return"
            )

        debt_to_equity = leverage_metrics.get(
            "debt_to_equity"
        )

        if (
            debt_to_equity is not None
            and debt_to_equity <= 1
        ):
            strengths.append(
                "Manageable financial leverage"
            )

        current_ratio = leverage_metrics.get(
            "current_ratio"
        )

        if (
            current_ratio is not None
            and current_ratio >= 1.5
        ):
            strengths.append(
                "Healthy short-term liquidity"
            )

        return strengths

    # ==========================================================
    # Missing Data
    # ==========================================================

    def _build_missing_prices_report(
        self,
        symbol: str,
        company_name: str,
        fundamental_report: dict[str, Any] | None,
    ) -> dict[str, Any]:
        fundamental_score, metrics = (
            self._evaluate_fundamental_risk(
                fundamental_report
            )
        )

        return {
            "symbol": symbol,
            "company_name": company_name,
            "generated_at": datetime.now().isoformat(),
            "risk_score": round(
                fundamental_score,
                2,
            ),
            "risk_level": self._get_risk_level(
                fundamental_score
            ),
            "higher_is_riskier": False,
            "market_safety_score": None,
            "fundamental_safety_score": round(
                fundamental_score,
                2,
            ),
            "metrics": {
                "observations": 0,
                "annualized_volatility": None,
                "downside_volatility": None,
                "max_drawdown": None,
                "value_at_risk_95": None,
                "conditional_var_95": None,
                "sharpe_ratio": None,
                **metrics,
            },
            "volatility": None,
            "max_drawdown": None,
            "strengths": [],
            "risks": [
                "Historical price data was unavailable"
            ],
            "summary": (
                f"{company_name} received a limited risk "
                "assessment because historical price data "
                "was unavailable."
            ),
        }

    # ==========================================================
    # Loading
    # ==========================================================

    def _load_prices(
        self,
        symbol: str,
    ) -> pd.DataFrame:
        possible_files = [
            self.prices_dir / f"{symbol}.csv",
            self.prices_dir / f"{symbol}.parquet",
            self.prices_dir / f"{symbol}.json",
            self.prices_dir / symbol / "prices.csv",
            self.prices_dir / symbol / "historical_prices.csv",
        ]

        for file_path in possible_files:
            if not file_path.exists():
                continue

            try:
                if file_path.suffix == ".csv":
                    frame = pd.read_csv(
                        file_path
                    )

                elif file_path.suffix == ".parquet":
                    frame = pd.read_parquet(
                        file_path
                    )

                elif file_path.suffix == ".json":
                    frame = pd.read_json(
                        file_path
                    )

                else:
                    continue

                if not frame.empty:
                    logger.info(
                        "Loaded price data for {} from {}.",
                        symbol,
                        file_path,
                    )

                    return frame

            except Exception as exc:
                logger.warning(
                    "Could not load {}: {}",
                    file_path,
                    exc,
                )

        return pd.DataFrame()

    @staticmethod
    def _load_json(
        file_path: Path,
    ) -> dict[str, Any] | None:
        if not file_path.exists():
            return None

        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                value = json.load(file)

            return value if isinstance(
                value,
                dict,
            ) else None

        except (
            OSError,
            json.JSONDecodeError,
        ) as exc:
            logger.warning(
                "Could not read {}: {}",
                file_path,
                exc,
            )

            return None

    # ==========================================================
    # Helpers
    # ==========================================================

    @staticmethod
    def _extract_close(
        frame: pd.DataFrame,
    ) -> pd.Series:
        possible_columns = (
            "Close",
            "close",
            "Adj Close",
            "adj_close",
            "adjusted_close",
        )

        for column in possible_columns:
            if column in frame.columns:
                close = pd.to_numeric(
                    frame[column],
                    errors="coerce",
                ).dropna()

                close = close[
                    close > 0
                ]

                return close

        raise ValueError(
            "Price data does not contain a close column."
        )

    def _find_numeric_value(
        self,
        data: Any,
        keys: tuple[str, ...],
    ) -> float | None:
        if not isinstance(data, dict):
            return None

        normalized_keys = {
            key.casefold()
            for key in keys
        }

        for key, value in data.items():
            if key.casefold() in normalized_keys:
                numeric_value = self._to_float(
                    value
                )

                if numeric_value is not None:
                    return numeric_value

        for value in data.values():
            if isinstance(value, dict):
                result = self._find_numeric_value(
                    value,
                    keys,
                )

                if result is not None:
                    return result

        return None

    @staticmethod
    def _extract_company_name(
        report: dict[str, Any] | None,
        symbol: str,
    ) -> str:
        if report:
            for key in (
                "company_name",
                "name",
                "companyName",
            ):
                value = report.get(key)

                if value:
                    return str(value).strip()

        return symbol

    @staticmethod
    def _build_summary(
        company_name: str,
        risk_score: float,
        risk_level: str,
        annualized_volatility: float | None,
        max_drawdown: float | None,
        risks: list[str],
    ) -> str:
        summary = (
            f"{company_name} received a safety score of "
            f"{risk_score:.1f}/100 and a {risk_level} "
            "investment risk classification."
        )

        if annualized_volatility is not None:
            summary += (
                f" Annualized volatility was "
                f"{annualized_volatility:.1f}%."
            )

        if max_drawdown is not None:
            summary += (
                f" Maximum drawdown was "
                f"{max_drawdown:.1f}%."
            )

        if risks:
            summary += (
                f" Main risk: {risks[0]}."
            )

        return summary

    def _save_report(
        self,
        symbol: str,
        report: dict[str, Any],
    ) -> Path:
        output_file = (
            self.output_dir / f"{symbol}.json"
        )

        temporary_file = (
            output_file.with_suffix(".json.tmp")
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_file.replace(
            output_file
        )

        logger.info(
            "Risk report saved to {}.",
            output_file,
        )

        return output_file

    @staticmethod
    def _clean_symbol(
        symbol: str,
    ) -> str:
        cleaned = str(symbol).strip()

        if cleaned.endswith(".0"):
            cleaned = cleaned[:-2]

        if not cleaned:
            raise ValueError(
                "Symbol cannot be empty."
            )

        return cleaned

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float | None:
        if value is None or isinstance(
            value,
            bool,
        ):
            return None

        try:
            result = float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

        return (
            result
            if np.isfinite(result)
            else None
        )

    @staticmethod
    def _finite_float(
        value: Any,
    ) -> float | None:
        try:
            numeric_value = float(value)

        except (
            TypeError,
            ValueError,
        ):
            return None

        return (
            numeric_value
            if np.isfinite(numeric_value)
            else None
        )

    @staticmethod
    def _round_optional(
        value: float | None,
        digits: int = 4,
    ) -> float | None:
        if value is None:
            return None

        return round(
            float(value),
            digits,
        )

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        return max(
            0.0,
            min(
                100.0,
                float(value),
            ),
        )