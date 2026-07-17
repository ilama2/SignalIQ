"""
SignalIQ Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# ==========================================================
# API Keys
# ==========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SAHMK_API_KEY = os.getenv("SAHMK_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


# ==========================================================
# Cache
# ==========================================================

PROFILE_CACHE_DAYS = int(os.getenv("PROFILE_CACHE_DAYS", 30))
PRICE_CACHE_DAYS = int(os.getenv("PRICE_CACHE_DAYS", 1))
FINANCIAL_CACHE_DAYS = int(os.getenv("FINANCIAL_CACHE_DAYS", 90))


# ==========================================================
# Yahoo Finance
# ==========================================================

DEFAULT_PRICE_PERIOD = os.getenv("DEFAULT_PRICE_PERIOD", "5y")
DEFAULT_PRICE_INTERVAL = os.getenv("DEFAULT_PRICE_INTERVAL", "1d")


# ==========================================================
# Requests
# ==========================================================

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))


# ==========================================================
# Paths
# ==========================================================

DATA_DIR = os.getenv("DATA_DIR", "Data")
PROFILE_DIR = os.getenv("PROFILE_DIR", "Data/profiles")
PRICE_DIR = os.getenv("PRICE_DIR", "Data/prices")
FINANCIAL_DIR = os.getenv("FINANCIAL_DIR", "Data/financials")
CACHE_DIR = os.getenv("CACHE_DIR", "Data/cache")
LOG_DIR = os.getenv("LOG_DIR", "logs")