""" file with settings """
import logging
from enum import Enum
from typing import TypedDict

import appdirs

DATA_PATH = appdirs.user_data_dir("stock_summary")
SETTINGS_PATH = appdirs.user_config_dir("stock_summary")


class LoggingSettings(Enum):
    """Enum which saves settings for logging"""

    OUTPUT_FILE = "tmp.log"
    LOGGING_LEVEL = logging.DEBUG


class PairResponse(TypedDict):
    """Pair response that we get from API for each pair."""

    symbol: str
    regularMarketPrice: float
    currency: str


class SummaryDict(TypedDict):
    """This dict is used to summarize entries for view Jinja HTML"""

    symbol: str
    actual_price: float
    actual_basis: float
    cost_basis: float
    count: float
    currency: str

class Dividend(TypedDict):
    """ THis dict is used to summarize dividends for view Jinja HTML"""
    currency: str
    symbol: str
    converted_value: float
    value: float

ENTRIES_PATH = f"{DATA_PATH}/entries"
PORTFOLIO_PATH = f"{DATA_PATH}/portfolio"
DIVIDEND_PATH = f"{DATA_PATH}/dividends"
INDEX_HTML_FILE = f"{DATA_PATH}/index.html"
MAIN_CSS_FILE = f"{DATA_PATH}/main.css"
TOKEN_PATH = f"{SETTINGS_PATH}/token"
try:
    with open(TOKEN_PATH, "r", encoding="utf-8") as token_file:
        API_TOKEN = token_file.read().strip()
except FileNotFoundError:
    API_TOKEN = ""

EXCHANGE_RATE_URL = "https://fixer-fixer-currency-v1.p.rapidapi.com"
EXCHANGE_RATE_HEADERS = {
    "X-RapidAPI-Key": API_TOKEN,
    "X-RapidAPI-Host": "fixer-fixer-currency-v1.p.rapidapi.com",
}

STOCK_PRICE_URL = "https://yahoo-finance15.p.rapidapi.com/api/yahoo/qu/quote"
STOCK_PRICE_HEADERS = {
    "X-RapidAPI-Key": API_TOKEN,
    "X-RapidAPI-Host": "yahoo-finance15.p.rapidapi.com",
}
