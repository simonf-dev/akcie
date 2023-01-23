""" library functions """
import csv
import datetime
import json
import logging
import os
import pathlib
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import requests

from stock_summary.settings import (
    DATA_PATH,
    ENTRIES_PATH,
    EXCHANGE_RATE_HEADERS,
    EXCHANGE_RATE_URL,
    PORTFOLIO_PATH,
    STOCK_PRICE_HEADERS,
    STOCK_PRICE_URL,
    PairResponse,
    SummaryDict,
)


def check_pair_responses(pairs: List[PairResponse]) -> None:
    """Do same basic checks on incoming responses from API for stock prices."""
    for pair in pairs:
        if pair["regularMarketPrice"] <= 0:
            raise ValueError(f"Entered symbol {pair['symbol']} has invalid price <=0.")
    logging.debug(f"Successfully checked responses for {pairs}")


def get_exchange_rates() -> Dict[str, float]:
    """Returns dict with actual values for conversions between other currencies and CZK"""

    response = requests.request(
        "GET", EXCHANGE_RATE_URL, headers=EXCHANGE_RATE_HEADERS, timeout=10
    )
    exchange_dict = {}
    for key, value in json.loads(response.text)["rates"].items():
        exchange_dict[key] = 1 / value
    logging.debug("Returning exchange dict %s", exchange_dict)
    return exchange_dict


def get_pair_prices(pairs: List[str]) -> Dict[str, PairResponse]:
    """
    Search for price on url and xpath, if error occurs, raises error.
    """
    url = f"{STOCK_PRICE_URL}/{','.join(pairs)}"

    response = requests.request("GET", url, headers=STOCK_PRICE_HEADERS, timeout=10)
    logging.debug("Requesting URL %s with response %s", url, response)
    result_list: List[PairResponse] = json.loads(response.text)
    check_pair_responses(result_list)
    result_dict = {}
    for result in result_list:
        result_dict[result["symbol"]] = result
    logging.debug(f"Returning pair_prices {result_dict}")
    return result_dict


def validate_date(date_text: str) -> None:
    """Validates date to our custom format."""
    try:
        datetime.datetime.strptime(date_text, "%d/%m/%Y")
    except ValueError as err:
        raise ValueError("Incorrect data format, should be DD/MM/YYYY") from err
    logging.debug(f"Validated data for {date_text}")


def get_entries_summary() -> Dict[str, SummaryDict]:
    """
    Returns entries summary with keys as stock symbols and values as dicts with all important
    values (see TypedDict) in settings.
    """
    entries_dict: Dict[str, SummaryDict] = {}
    with open(ENTRIES_PATH, newline="", encoding="utf-8") as csvfile:
        entries = csv.reader(csvfile, delimiter=" ", quotechar="|")
        next(entries)
        for entry in entries:
            if entry[1] not in entries_dict:
                entries_dict[entry[1]] = {
                    "symbol": entry[1],
                    "count": 0,
                    "cost_basis": 0,
                    "actual_basis": 0,
                    "currency": "",
                    "actual_price": 0,
                }
            entries_dict[entry[1]]["count"] += float(entry[2])
            entries_dict[entry[1]]["cost_basis"] += float(entry[2]) * float(entry[3])
    exchange_rates = get_exchange_rates()
    pair_prices = get_pair_prices(list(entries_dict.keys()))
    for key, value in entries_dict.items():
        value["currency"] = pair_prices[key]["currency"]
        value["actual_price"] = pair_prices[key]["regularMarketPrice"]
        value["cost_basis"] = (
            value["cost_basis"] * exchange_rates[pair_prices[key]["currency"]]
        )
        value["actual_basis"] = (
            value["count"] * pair_prices[key]["regularMarketPrice"]
        ) * exchange_rates[pair_prices[key]["currency"]]
    logging.debug(f"Returning entries summary {entries_dict}")
    return entries_dict


def prepare_portfolio_data() -> Any:
    """Prepares portfolio data and returns them as pandas dataset"""
    dataset = pd.read_csv(PORTFOLIO_PATH, sep=" ")
    dataset["DATE"] = pd.to_datetime(dataset["DATE"], format="%d/%m/%y")
    return dataset


def get_plot_html(dataset: Any) -> Any:
    """Exports plot as HTML and returns it."""
    fig = px.line(
        dataset,
        x="DATE",
        y="TOTAL_PRICE",
        title="Přehled portfolia v čase",
        labels={"DATE": "Čas", "TOTAL_PRICE": "Hodnota portfolia"},
        hover_data={"DATE": "|%d/%m/%y"},
    )
    return fig.to_html()


def check_if_files_exist() -> None:
    """Check if files exist in memory, if not then creates them with initialized headers."""
    os.makedirs(DATA_PATH, exist_ok=True)
    if not os.path.exists(ENTRIES_PATH):
        shutil.copy2(
            f"{pathlib.Path(__file__).parent.resolve()}/init_datasets/entries",
            ENTRIES_PATH,
        )
        logging.debug(f"Created init entries file {ENTRIES_PATH}")
    if not os.path.exists(PORTFOLIO_PATH):
        shutil.copy2(
            f"{pathlib.Path(__file__).parent.resolve()}/init_datasets/portfolio",
            PORTFOLIO_PATH,
        )
        logging.debug(f"Created init portfolio file {ENTRIES_PATH}")


def import_data(from_file: str, to_file: str, confirmation: bool = False) -> None:
    """
    Imports data from entry file to target file. If target file already exists, then
    asks user for confirmation
    """
    if os.path.exists(to_file) and not confirmation:
        confirmation = input(
            "You will rewrite your actual saved data, are you sure to proceed? "
            "Type Y: "
        )
        if not confirmation.lower() == "y":
            logging.error("Action canceled, ending without any action.")
            sys.exit(1)
    shutil.copy2(from_file, to_file)
    logging.debug(f"Successfully moved data from {from_file} to {to_file}")


def export_data(directory: str) -> None:
    """
    Exports all data files to target directory, creates recursively, if doesn't exist.
    """
    path = Path(directory)
    os.makedirs(path, exist_ok=True)
    shutil.copy2(ENTRIES_PATH, f"{path}/{ENTRIES_PATH.split('/')[-1]}")
    shutil.copy2(PORTFOLIO_PATH, f"{path}/{PORTFOLIO_PATH.split('/')[-1]}")
