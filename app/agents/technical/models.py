"""
SignalIQ - Technical Analysis Models

Defines the output models used by the Technical Analysis Agent.
"""

from pydantic import BaseModel, Field


# ==========================================================
# Technical Indicators
# ==========================================================

class TechnicalIndicatorsModel(BaseModel):

    # Trend
    sma20: float = Field(..., description="20-day Simple Moving Average")
    sma50: float = Field(..., description="50-day Simple Moving Average")
    sma200: float = Field(..., description="200-day Simple Moving Average")

    ema20: float = Field(..., description="20-day Exponential Moving Average")
    ema50: float = Field(..., description="50-day Exponential Moving Average")

    # Momentum
    rsi: float = Field(..., description="Relative Strength Index")

    macd: float = Field(..., description="MACD")
    macd_signal: float = Field(..., description="MACD Signal")
    macd_histogram: float = Field(..., description="MACD Histogram")

    stochastic_k: float = Field(..., description="Stochastic %K")
    stochastic_d: float = Field(..., description="Stochastic %D")

    # Volatility
    upper_band: float = Field(..., description="Upper Bollinger Band")
    middle_band: float = Field(..., description="Middle Bollinger Band")
    lower_band: float = Field(..., description="Lower Bollinger Band")

    atr: float = Field(..., description="Average True Range")

    # Trend Strength
    adx: float = Field(..., description="Average Directional Index")

    # Volume
    obv: float = Field(..., description="On-Balance Volume")

    # Current Price
    current_price: float = Field(..., description="Latest Closing Price")

    # Overall Trend
    trend: str = Field(..., description="Bullish, Bearish or Sideways")


# ==========================================================
# Technical Score
# ==========================================================

class TechnicalScoreModel(BaseModel):

    score: int = Field(..., description="Technical score (0-100)")

    rating: str = Field(
        ...,
        description="Strong Buy, Buy, Hold, Sell, Strong Sell",
    )

    strengths: list[str] = Field(
        default_factory=list,
        description="Bullish technical signals",
    )

    weaknesses: list[str] = Field(
        default_factory=list,
        description="Bearish technical signals",
    )


# ==========================================================
# Complete Technical Report
# ==========================================================

class TechnicalReport(BaseModel):

    symbol: str

    company_name: str

    indicators: TechnicalIndicatorsModel

    score: TechnicalScoreModel