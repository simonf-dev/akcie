""" file with settings """
import logging
import os
import pathlib

import appdirs
from dotenv import load_dotenv

from stock_summary.help_structures import CloudType

DATA_PATH = pathlib.Path(appdirs.user_data_dir("stock_summary")).resolve()
SETTINGS_PATH = pathlib.Path(appdirs.user_config_dir("stock_summary")).resolve()
INIT_DATASETS_PATH = (
    pathlib.Path(__file__).parent.resolve().joinpath("init_datasets").resolve()
)


ENTRIES_PATH = DATA_PATH.joinpath("entries").resolve()
PORTFOLIO_PATH = DATA_PATH.joinpath("portfolio").resolve()
DIVIDEND_PATH = DATA_PATH.joinpath("dividends").resolve()
INDEX_HTML_FILE = DATA_PATH.joinpath("index.html").resolve()
MAIN_CSS_FILE = DATA_PATH.joinpath("main.css").resolve()
TOKEN_PATH = SETTINGS_PATH.joinpath("token").resolve()
ENV_VARIABLES = SETTINGS_PATH.joinpath(".env").resolve()
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


# Cloud variables
load_dotenv(ENV_VARIABLES)

try:
    CLOUD_TYPE = (
        CloudType(os.environ["CLOUD_TYPE"])
        if os.environ.get("CLOUD_TYPE") is not None
        else CloudType.NONE
    )
except ValueError:
    logging.warning("Invalid value '%s' of the cloud type.", os.environ["CLOUD_TYPE"])
    CLOUD_TYPE = CloudType.NONE
AZURE_CONNECTION_STR = (
    os.environ["AZURE_CONNECTION_STR"]
    if os.environ.get("AZURE_CONNECTION_STR") is not None and os.environ.get("AZURE_CONNECTION_STR") != ""
    else None
)
