"""
SignalIQ - Technical Scoring

Converts technical indicators into an investment score.
"""

from __future__ import annotations


class TechnicalScorer:

    def __init__(self):

        self.score = 0
        self.strengths = []
        self.weaknesses = []

    # =====================================================
    # Public API
    # =====================================================

    def score_stock(
        self,
        indicators: dict,
    ) -> dict:

        self.score = 0
        self.strengths = []
        self.weaknesses = []

        self._trend(indicators)
        self._momentum(indicators)
        self._volatility(indicators)
        self._volume(indicators)

        return {
            "score": self.score,
            "rating": self._rating(),
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }

    # =====================================================
    # Trend
    # =====================================================

    def _trend(self, i):

        if i["trend"] == "Bullish":
            self.score += 20
            self.strengths.append("Bullish Trend")

        elif i["trend"] == "Sideways":
            self.score += 10

        else:
            self.weaknesses.append("Bearish Trend")

        if i["current_price"] > i["sma200"]:
            self.score += 15
            self.strengths.append("Price Above SMA200")
        else:
            self.weaknesses.append("Price Below SMA200")

        if i["ema20"] > i["ema50"]:
            self.score += 10
            self.strengths.append("Short-Term Uptrend")
        else:
            self.weaknesses.append("Short-Term Downtrend")

    # =====================================================
    # Momentum
    # =====================================================

    def _momentum(self, i):

        rsi = i["rsi"]

        if 40 <= rsi <= 70:
            self.score += 10
            self.strengths.append("Healthy RSI")

        elif rsi < 30:
            self.score += 5
            self.strengths.append("Oversold")

        elif rsi > 70:
            self.weaknesses.append("Overbought")

        if i["macd"] > i["macd_signal"]:
            self.score += 10
            self.strengths.append("Bullish MACD")
        else:
            self.weaknesses.append("Bearish MACD")

        if i["stochastic_k"] > i["stochastic_d"]:
            self.score += 5
            self.strengths.append("Positive Stochastic")

    # =====================================================
    # Volatility
    # =====================================================

    def _volatility(self, i):

        if i["adx"] >= 25:
            self.score += 10
            self.strengths.append("Strong Trend")
        else:
            self.score += 5

        if (
            i["current_price"] >= i["lower_band"]
            and i["current_price"] <= i["upper_band"]
        ):
            self.score += 5

    # =====================================================
    # Volume
    # =====================================================

    def _volume(self, i):

        if i["obv"] > 0:
            self.score += 10
            self.strengths.append("Positive Volume Trend")
        else:
            self.weaknesses.append("Weak Volume Trend")

    # =====================================================
    # Rating
    # =====================================================

    def _rating(self):

        if self.score >= 90:
            return "Strong Buy"

        if self.score >= 75:
            return "Buy"

        if self.score >= 55:
            return "Hold"

        if self.score >= 35:
            return "Sell"

        return "Strong Sell"