"""
SignalIQ - Technical Indicators

Calculates all technical indicators from historical prices.
"""

from __future__ import annotations

import pandas as pd

from ta.trend import (
    SMAIndicator,
    EMAIndicator,
    MACD,
    ADXIndicator,
)

from ta.momentum import (
    RSIIndicator,
    StochasticOscillator,
)

from ta.volatility import (
    BollingerBands,
    AverageTrueRange,
)

from ta.volume import (
    OnBalanceVolumeIndicator,
)


class TechnicalIndicators:
    """
    Calculates all technical indicators.
    """

    # =====================================================
    # Helpers
    # =====================================================

    @staticmethod
    def latest(series: pd.Series) -> float:

        value = series.iloc[-1]

        if pd.isna(value):
            return 0.0

        return float(value)

    # =====================================================
    # Moving Averages
    # =====================================================

    @classmethod
    def sma20(cls, close):

        return cls.latest(
            SMAIndicator(close, window=20).sma_indicator()
        )

    @classmethod
    def sma50(cls, close):

        return cls.latest(
            SMAIndicator(close, window=50).sma_indicator()
        )

    @classmethod
    def sma200(cls, close):

        return cls.latest(
            SMAIndicator(close, window=200).sma_indicator()
        )

    @classmethod
    def ema20(cls, close):

        return cls.latest(
            EMAIndicator(close, window=20).ema_indicator()
        )

    @classmethod
    def ema50(cls, close):

        return cls.latest(
            EMAIndicator(close, window=50).ema_indicator()
        )

    # =====================================================
    # RSI
    # =====================================================

    @classmethod
    def rsi(cls, close):

        return cls.latest(
            RSIIndicator(close).rsi()
        )

    # =====================================================
    # MACD
    # =====================================================

    @classmethod
    def macd(cls, close):

        indicator = MACD(close)

        return (
            cls.latest(indicator.macd()),
            cls.latest(indicator.macd_signal()),
            cls.latest(indicator.macd_diff()),
        )

    # =====================================================
    # Bollinger Bands
    # =====================================================

    @classmethod
    def bollinger(cls, close):

        bb = BollingerBands(close)

        return (
            cls.latest(bb.bollinger_hband()),
            cls.latest(bb.bollinger_mavg()),
            cls.latest(bb.bollinger_lband()),
        )

    # =====================================================
    # ATR
    # =====================================================

    @classmethod
    def atr(
        cls,
        high,
        low,
        close,
    ):

        return cls.latest(
            AverageTrueRange(
                high,
                low,
                close,
            ).average_true_range()
        )

    # =====================================================
    # ADX
    # =====================================================

    @classmethod
    def adx(
        cls,
        high,
        low,
        close,
    ):

        return cls.latest(
            ADXIndicator(
                high,
                low,
                close,
            ).adx()
        )

    # =====================================================
    # Stochastic
    # =====================================================

    @classmethod
    def stochastic(
        cls,
        high,
        low,
        close,
    ):

        stoch = StochasticOscillator(
            high,
            low,
            close,
        )

        return (
            cls.latest(stoch.stoch()),
            cls.latest(stoch.stoch_signal()),
        )

    # =====================================================
    # OBV
    # =====================================================

    @classmethod
    def obv(
        cls,
        close,
        volume,
    ):

        return cls.latest(
            OnBalanceVolumeIndicator(
                close,
                volume,
            ).on_balance_volume()
        )

    # =====================================================
    # Trend
    # =====================================================

    @staticmethod
    def trend(
        current_price: float,
        sma50: float,
        sma200: float,
    ) -> str:

        if current_price > sma50 > sma200:
            return "Bullish"

        if current_price < sma50 < sma200:
            return "Bearish"

        return "Sideways"

    # =====================================================
    # Calculate All
    # =====================================================

    @classmethod
    def calculate_all(
        cls,
        prices: pd.DataFrame,
    ) -> dict:

        close = prices["Close"]
        high = prices["High"]
        low = prices["Low"]
        volume = prices["Volume"]

        sma20 = cls.sma20(close)
        sma50 = cls.sma50(close)
        sma200 = cls.sma200(close)

        ema20 = cls.ema20(close)
        ema50 = cls.ema50(close)

        macd, signal, hist = cls.macd(close)

        upper, middle, lower = cls.bollinger(close)

        stoch_k, stoch_d = cls.stochastic(
            high,
            low,
            close,
        )

        current_price = float(close.iloc[-1])

        return {
            "sma20": sma20,
            "sma50": sma50,
            "sma200": sma200,
            "ema20": ema20,
            "ema50": ema50,
            "rsi": cls.rsi(close),
            "macd": macd,
            "macd_signal": signal,
            "macd_histogram": hist,
            "upper_band": upper,
            "middle_band": middle,
            "lower_band": lower,
            "atr": cls.atr(
                high,
                low,
                close,
            ),
            "adx": cls.adx(
                high,
                low,
                close,
            ),
            "stochastic_k": stoch_k,
            "stochastic_d": stoch_d,
            "obv": cls.obv(
                close,
                volume,
            ),
            "current_price": current_price,
            "trend": cls.trend(
                current_price,
                sma50,
                sma200,
            ),
        }