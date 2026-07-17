"""
SignalIQ - Portfolio Agent

Builds a portfolio by comparing all Supervisor Agent reports.

The agent:
- Loads final supervisor reports
- Filters weak or high-risk companies
- Ranks eligible companies
- Assigns normalized portfolio weights
- Applies a maximum allocation per company
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger


class PortfolioAgent:
    """Construct a portfolio from Supervisor Agent reports."""

    def __init__(
        self,
        supervisor_dir: str | Path = "data/analysis/supervisor",
        risk_dir: str | Path = "data/analysis/risk",
        output_dir: str | Path = "data/analysis/portfolio",
        max_positions: int = 10,
        max_weight: float = 0.20,
        minimum_score: float = 55.0,
    ) -> None:
        self.supervisor_dir = Path(
            supervisor_dir
        )

        self.risk_dir = Path(
            risk_dir
        )

        self.output_dir = Path(
            output_dir
        )

        self.max_positions = max_positions
        self.max_weight = max_weight
        self.minimum_score = minimum_score

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # Public API
    # ==========================================================

    def run(
        self,
        symbols: list[str] | None = None,
        portfolio_value: float = 100_000.0,
        save: bool = True,
    ) -> dict[str, Any]:
        """
        Build a portfolio.

        Args:
            symbols:
                Optional list of symbols. If omitted, all Supervisor
                JSON reports are used.

            portfolio_value:
                Total portfolio value in SAR.

            save:
                Save the portfolio report.

        Returns:
            Portfolio recommendation.
        """

        if portfolio_value <= 0:
            raise ValueError(
                "portfolio_value must be greater than zero."
            )

        logger.info(
            "Starting portfolio construction."
        )

        reports = self._load_supervisor_reports(
            symbols
        )

        if not reports:
            raise ValueError(
                "No Supervisor reports were found."
            )

        candidates = [
            self._build_candidate(report)
            for report in reports
        ]

        eligible = [
            candidate
            for candidate in candidates
            if self._is_eligible(candidate)
        ]

        excluded = [
            self._build_excluded_result(
                candidate
            )
            for candidate in candidates
            if not self._is_eligible(candidate)
        ]

        eligible.sort(
            key=lambda item: item[
                "portfolio_score"
            ],
            reverse=True,
        )

        selected = eligible[
            : self.max_positions
        ]

        allocations = self._allocate_weights(
            selected
        )

        positions = []

        for candidate, weight in zip(
            selected,
            allocations,
            strict=True,
        ):
            position_value = (
                portfolio_value * weight
            )

            positions.append(
                {
                    **candidate,
                    "weight": round(
                        weight,
                        6,
                    ),
                    "weight_percent": round(
                        weight * 100,
                        2,
                    ),
                    "allocation_sar": round(
                        position_value,
                        2,
                    ),
                }
            )

        invested_weight = sum(
            item["weight"]
            for item in positions
        )

        cash_weight = max(
            0.0,
            1.0 - invested_weight,
        )

        portfolio = {
            "generated_at": datetime.now().isoformat(),
            "portfolio_value_sar": round(
                portfolio_value,
                2,
            ),
            "number_of_positions": len(
                positions
            ),
            "invested_weight": round(
                invested_weight,
                6,
            ),
            "cash_weight": round(
                cash_weight,
                6,
            ),
            "cash_allocation_sar": round(
                portfolio_value
                * cash_weight,
                2,
            ),
            "settings": {
                "maximum_positions": self.max_positions,
                "maximum_weight_per_company": self.max_weight,
                "minimum_supervisor_score": self.minimum_score,
            },
            "portfolio_score": self._calculate_portfolio_score(
                positions
            ),
            "portfolio_risk_level": (
                self._calculate_portfolio_risk(
                    positions
                )
            ),
            "positions": positions,
            "excluded_companies": excluded,
            "summary": self._build_summary(
                positions=positions,
                excluded=excluded,
                portfolio_value=portfolio_value,
                cash_weight=cash_weight,
            ),
        }

        if save:
            self._save_report(portfolio)

        logger.success(
            "Portfolio completed with {} positions.",
            len(positions),
        )

        return portfolio

    # ==========================================================
    # Candidate Scoring
    # ==========================================================

    def _build_candidate(
        self,
        supervisor_report: dict[str, Any],
    ) -> dict[str, Any]:
        symbol = str(
            supervisor_report.get(
                "symbol",
                "",
            )
        ).strip()

        final_score = self._to_float(
            supervisor_report.get(
                "final_score"
            )
        )

        final_score = (
            final_score
            if final_score is not None
            else 50.0
        )

        recommendation = str(
            supervisor_report.get(
                "recommendation",
                "Hold",
            )
        ).strip()

        confidence = self._to_float(
            supervisor_report.get(
                "confidence"
            )
        )

        confidence = (
            confidence
            if confidence is not None
            else 0.0
        )

        # Supervisor confidence is currently between 0 and 1.
        if confidence > 1:
            confidence /= 100.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence,
            ),
        )

        risk_report = self._load_json(
            self.risk_dir / f"{symbol}.json"
        )

        risk_score = self._extract_risk_score(
            risk_report
        )

        risk_level = self._extract_risk_level(
            risk_report
        )

        technical_score = self._extract_component_score(
            supervisor_report,
            "technical",
        )

        fundamental_score = self._extract_component_score(
            supervisor_report,
            "fundamental",
        )

        # Portfolio score rewards:
        # - Final investment score
        # - Safety
        # - Confidence
        # - Technical momentum
        # - Fundamental quality
        portfolio_score = (
            final_score * 0.45
            + risk_score * 0.20
            + confidence * 100 * 0.15
            + technical_score * 0.10
            + fundamental_score * 0.10
        )

        portfolio_score = self._clamp(
            portfolio_score
        )

        return {
            "symbol": symbol,
            "company_name": supervisor_report.get(
                "company_name",
                symbol,
            ),
            "recommendation": recommendation,
            "supervisor_score": round(
                final_score,
                2,
            ),
            "portfolio_score": round(
                portfolio_score,
                2,
            ),
            "confidence": round(
                confidence,
                4,
            ),
            "risk_score": round(
                risk_score,
                2,
            ),
            "risk_level": risk_level,
            "fundamental_score": round(
                fundamental_score,
                2,
            ),
            "technical_score": round(
                technical_score,
                2,
            ),
            "reason": self._build_candidate_reason(
                final_score=final_score,
                recommendation=recommendation,
                risk_level=risk_level,
                portfolio_score=portfolio_score,
            ),
        }

    def _is_eligible(
        self,
        candidate: dict[str, Any],
    ) -> bool:
        recommendation = str(
            candidate["recommendation"]
        ).casefold()

        risk_level = str(
            candidate["risk_level"]
        ).casefold()

        if candidate[
            "supervisor_score"
        ] < self.minimum_score:
            return False

        if recommendation in {
            "sell",
            "strong sell",
        }:
            return False

        if risk_level in {
            "very high",
            "critical",
        }:
            return False

        return True

    def _build_excluded_result(
        self,
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        reasons: list[str] = []

        if (
            candidate["supervisor_score"]
            < self.minimum_score
        ):
            reasons.append(
                "Supervisor score below minimum"
            )

        if str(
            candidate["recommendation"]
        ).casefold() in {
            "sell",
            "strong sell",
        }:
            reasons.append(
                "Negative investment recommendation"
            )

        if str(
            candidate["risk_level"]
        ).casefold() in {
            "very high",
            "critical",
        }:
            reasons.append(
                "Risk level exceeds portfolio limit"
            )

        return {
            "symbol": candidate["symbol"],
            "company_name": candidate[
                "company_name"
            ],
            "supervisor_score": candidate[
                "supervisor_score"
            ],
            "risk_level": candidate[
                "risk_level"
            ],
            "reasons": reasons,
        }

    # ==========================================================
    # Allocation
    # ==========================================================

    def _allocate_weights(
        self,
        selected: list[dict[str, Any]],
    ) -> list[float]:
        if not selected:
            return []

        raw_scores = np.array(
            [
                max(
                    0.01,
                    float(
                        item[
                            "portfolio_score"
                        ]
                    ),
                )
                for item in selected
            ],
            dtype=float,
        )

        weights = (
            raw_scores / raw_scores.sum()
        )

        weights = self._apply_weight_cap(
            weights=weights,
            cap=self.max_weight,
        )

        return [
            float(weight)
            for weight in weights
        ]

    @staticmethod
    def _apply_weight_cap(
        weights: np.ndarray,
        cap: float,
    ) -> np.ndarray:
        """
        Cap large positions and redistribute excess weight.

        If the position limit makes full investment impossible,
        the unused amount remains as cash.
        """

        if len(weights) == 0:
            return weights

        weights = weights.copy()

        for _ in range(100):
            over_cap = weights > cap

            if not np.any(over_cap):
                break

            excess = float(
                np.sum(
                    weights[over_cap] - cap
                )
            )

            weights[over_cap] = cap

            under_cap = weights < cap
            available_capacity = float(
                np.sum(
                    cap - weights[under_cap]
                )
            )

            if (
                excess <= 1e-12
                or available_capacity <= 1e-12
            ):
                break

            current_under_total = float(
                np.sum(
                    weights[under_cap]
                )
            )

            if current_under_total > 0:
                redistribution = (
                    weights[under_cap]
                    / current_under_total
                    * min(
                        excess,
                        available_capacity,
                    )
                )

            else:
                redistribution = np.full(
                    int(np.sum(under_cap)),
                    min(
                        excess,
                        available_capacity,
                    )
                    / int(
                        np.sum(under_cap)
                    ),
                )

            weights[under_cap] += (
                redistribution
            )

        weights = np.minimum(
            weights,
            cap,
        )

        return weights

    # ==========================================================
    # Portfolio Metrics
    # ==========================================================

    @staticmethod
    def _calculate_portfolio_score(
        positions: list[dict[str, Any]],
    ) -> float:
        if not positions:
            return 0.0

        invested_weight = sum(
            position["weight"]
            for position in positions
        )

        if invested_weight <= 0:
            return 0.0

        weighted_score = sum(
            position["portfolio_score"]
            * position["weight"]
            for position in positions
        )

        return round(
            weighted_score
            / invested_weight,
            2,
        )

    @staticmethod
    def _calculate_portfolio_risk(
        positions: list[dict[str, Any]],
    ) -> str:
        if not positions:
            return "no positions"

        invested_weight = sum(
            position["weight"]
            for position in positions
        )

        if invested_weight <= 0:
            return "no positions"

        weighted_safety = sum(
            position["risk_score"]
            * position["weight"]
            for position in positions
        ) / invested_weight

        if weighted_safety >= 80:
            return "very low"

        if weighted_safety >= 65:
            return "low"

        if weighted_safety >= 45:
            return "medium"

        if weighted_safety >= 25:
            return "high"

        return "very high"

    # ==========================================================
    # Loading
    # ==========================================================

    def _load_supervisor_reports(
        self,
        symbols: list[str] | None,
    ) -> list[dict[str, Any]]:
        reports: list[dict[str, Any]] = []

        if symbols is None:
            files = sorted(
                self.supervisor_dir.glob(
                    "*.json"
                )
            )

        else:
            files = [
                self.supervisor_dir
                / f"{self._clean_symbol(symbol)}.json"
                for symbol in symbols
            ]

        for file_path in files:
            report = self._load_json(
                file_path
            )

            if report:
                reports.append(report)

            else:
                logger.warning(
                    "Supervisor report unavailable: {}",
                    file_path,
                )

        return reports

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
    def _extract_component_score(
        report: dict[str, Any],
        component: str,
    ) -> float:
        scores = report.get(
            "component_scores",
            {},
        )

        if not isinstance(scores, dict):
            return 50.0

        value = PortfolioAgent._to_float(
            scores.get(component)
        )

        return (
            PortfolioAgent._clamp(value)
            if value is not None
            else 50.0
        )

    @staticmethod
    def _extract_risk_score(
        report: dict[str, Any] | None,
    ) -> float:
        if not report:
            return 50.0

        value = PortfolioAgent._to_float(
            report.get("risk_score")
        )

        if value is not None:
            if 0 <= value <= 1:
                value *= 100

            if report.get(
                "higher_is_riskier",
                False,
            ):
                value = 100 - value

            return PortfolioAgent._clamp(
                value
            )

        level = PortfolioAgent._extract_risk_level(
            report
        )

        return {
            "very low": 90.0,
            "low": 80.0,
            "medium": 60.0,
            "high": 35.0,
            "very high": 20.0,
            "critical": 10.0,
        }.get(
            level,
            50.0,
        )

    @staticmethod
    def _extract_risk_level(
        report: dict[str, Any] | None,
    ) -> str:
        if not report:
            return "medium"

        return str(
            report.get(
                "risk_level",
                "medium",
            )
        ).strip().casefold()

    @staticmethod
    def _build_candidate_reason(
        final_score: float,
        recommendation: str,
        risk_level: str,
        portfolio_score: float,
    ) -> str:
        return (
            f"{recommendation} recommendation with a "
            f"{final_score:.1f}/100 supervisor score, "
            f"{risk_level} risk, and a "
            f"{portfolio_score:.1f}/100 portfolio score."
        )

    @staticmethod
    def _build_summary(
        positions: list[dict[str, Any]],
        excluded: list[dict[str, Any]],
        portfolio_value: float,
        cash_weight: float,
    ) -> str:
        if not positions:
            return (
                "No companies satisfied the portfolio "
                "selection requirements."
            )

        top_position = positions[0]

        return (
            f"The portfolio allocates SAR "
            f"{portfolio_value:,.2f} across "
            f"{len(positions)} companies. "
            f"The highest-ranked company is "
            f"{top_position['company_name']} "
            f"with a {top_position['weight_percent']:.1f}% "
            f"allocation. Cash represents "
            f"{cash_weight * 100:.1f}% of the portfolio. "
            f"{len(excluded)} companies were excluded."
        )

    def _save_report(
        self,
        report: dict[str, Any],
    ) -> Path:
        output_file = (
            self.output_dir
            / "portfolio.json"
        )

        temporary_file = (
            output_file.with_suffix(
                ".json.tmp"
            )
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
            "Portfolio report saved to {}.",
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