""" library functions """
import csv
import datetime
import json
import logging
import os
import pathlib
import shutil
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

from stock_summary.settings import (
    DATA_PATH,
    DIVIDEND_PATH,
    ENTRIES_PATH,
    EXCHANGE_RATE_HEADERS,
    EXCHANGE_RATE_URL,
    INIT_DATASETS_PATH,
    PORTFOLIO_PATH,
    STOCK_PRICE_HEADERS,
    STOCK_PRICE_URL,
    Dividend,
    PairResponse,
    SummaryDict,
)


def check_pair_responses(pairs: List[PairResponse]) -> None:
    """Do same basic checks on incoming responses from API for stock prices."""
    for pair in pairs:
        if pair["regularMarketPrice"] <= 0:
            raise ValueError(f"Entered symbol {pair['symbol']} has invalid price <=0.")
    logging.debug(f"Successfully checked responses for {pairs}")


@lru_cache()
def get_exchange_rates(
    date: Optional[datetime.datetime] = None, base_pair: str = "CZK"
) -> Dict[str, float]:
    """Returns dict with actual values for conversions between other currencies and CZK"""
    url = (
        f"{EXCHANGE_RATE_URL}/latest"
        if date is None
        else f"{EXCHANGE_RATE_URL}/{date.strftime('%Y-%m-%d')}"
    )
    response = requests.request(
        "GET",
        url,
        timeout=10,
        headers=EXCHANGE_RATE_HEADERS,
        params={"base": base_pair},
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


def validate_date(date_text: str) -> datetime.datetime:
    """Validates date to our custom format."""
    try:
        date = datetime.datetime.strptime(date_text, "%d/%m/%Y")
        logging.debug(f"Validated data for {date_text}")
        return date
    except ValueError as err:
        raise ValueError("Incorrect data format, should be DD/MM/YYYY") from err


def get_entries_summary(
    entries_path: pathlib.Path = ENTRIES_PATH,
) -> Dict[str, SummaryDict]:
    """
    Returns entries summary with keys as stock symbols and values as dicts with all important
    values (see TypedDict) in settings.
    """
    entries_dict: Dict[str, SummaryDict] = {}
    with open(entries_path, newline="", encoding="utf-8") as csvfile:
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
            entries_dict[entry[1]]["cost_basis"] += float(entry[4])
    exchange_rates = get_exchange_rates()
    pair_prices = get_pair_prices(list(entries_dict.keys()))
    for key, value in entries_dict.items():
        value["currency"] = pair_prices[key]["currency"]
        value["actual_price"] = pair_prices[key]["regularMarketPrice"]
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
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=dataset["DATE"], y=dataset["TOTAL_PRICE"], name="AKTUÁLNÍ HODNOTA"
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=dataset["DATE"], y=dataset["PROFIT"], name="PROFIT"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(title_text="Přehled portfolia v čase")

    # Set x-axis title
    fig.update_xaxes(title_text="Čas")

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>AKTUÁLNÍ HODNOTA</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>PROFIT</b>", secondary_y=True)

    fig.show()
    return fig.to_html()


def rewrite_data_files(rewrite: bool = False) -> None:
    """Check if files exist in memory, if not then creates them with initialized headers."""
    os.makedirs(DATA_PATH, exist_ok=True)
    if rewrite or not os.path.exists(ENTRIES_PATH):
        shutil.copy2(
            f"{INIT_DATASETS_PATH.joinpath('entries')}",
            ENTRIES_PATH,
        )
        logging.debug(f"Created init entries file {ENTRIES_PATH}")
    if rewrite or not os.path.exists(PORTFOLIO_PATH):
        shutil.copy2(
            f"{INIT_DATASETS_PATH.joinpath('portfolio')}",
            PORTFOLIO_PATH,
        )
        logging.debug(f"Created init portfolio file {ENTRIES_PATH}")
    if rewrite or not os.path.exists(DIVIDEND_PATH):
        shutil.copy2(
            f"{INIT_DATASETS_PATH.joinpath('dividends')}",
            DIVIDEND_PATH,
        )
        logging.debug(f"Created init portfolio file {DIVIDEND_PATH}")


def import_data(from_file: pathlib.Path, to_file: pathlib.Path) -> None:
    """
    Imports data from entry file to target file. If target file already exists, then
    asks user for confirmation
    """
    shutil.copy2(from_file.resolve(), to_file.resolve())
    logging.debug(
        f"Successfully moved data from {from_file.resolve()} to {to_file.resolve()}"
    )


def export_data(directory: pathlib.Path) -> None:
    """
    Exports all data files to target directory, creates recursively, if doesn't exist.
    """
    path = directory.resolve()
    os.makedirs(path, exist_ok=True)
    shutil.copy2(ENTRIES_PATH, f"{path.joinpath(ENTRIES_PATH.parts[-1]).resolve()}")
    shutil.copy2(PORTFOLIO_PATH, f"{path.joinpath(PORTFOLIO_PATH.parts[-1]).resolve()}")
    shutil.copy2(DIVIDEND_PATH, f"{path.joinpath(DIVIDEND_PATH.parts[-1]).resolve()}")


def save_dividend(date: datetime.datetime, stock: str, amount: float) -> None:
    """ Saves dividend into the file"""
    currency = get_pair_prices([stock])[stock]["currency"]
    converted_amount = convert_currency(date, currency, "CZK", amount)
    with open(DIVIDEND_PATH, "a", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=" ", quotechar="|")
        csv_writer.writerow(
            [date.strftime("%d/%m/%Y"), stock, amount, converted_amount]
        )
    logging.debug(
        f"Dividend date: {date} stock: {stock} amount: {amount} "
        f"converted_amount: {converted_amount} saved to {DIVIDEND_PATH}"
    )


def convert_currency(
    date: datetime.datetime, from_curr: str, to_curr: str, amount: float
) -> float:
    """ Convert currency by rate from the given date"""
    exchange_rates = get_exchange_rates(date, to_curr)
    return amount * exchange_rates[from_curr]


def get_dividend_summary() -> Dict[str, Dividend]:
    """Returns dividend summary"""
    dividend_summary: Dict[str, Dividend] = {}
    with open(DIVIDEND_PATH, newline="", encoding="utf-8") as csvfile:
        dividends = csv.reader(csvfile, delimiter=" ", quotechar="|")
        next(dividends)
        for dividend in dividends:
            if dividend[1] not in dividend_summary:
                dividend_summary[dividend[1]] = {
                    "symbol": dividend[1],
                    "value": 0,
                    "converted_value": 0,
                    "currency": "",
                }
            dividend_summary[dividend[1]]["value"] += float(dividend[2])
            dividend_summary[dividend[1]]["converted_value"] += float(dividend[3])
    pair_prices = get_pair_prices(list(dividend_summary.keys()))
    for key, value in dividend_summary.items():
        value["currency"] = pair_prices[key]["currency"]
    return dividend_summary


def get_dividend_sum(dividend_path: pathlib.Path = DIVIDEND_PATH) -> float:
    """Returns sum of the all dividends."""
    with open(dividend_path, newline="", encoding="utf-8") as csvfile:
        dividend_lines = csv.reader(csvfile, delimiter=" ", quotechar="|")
        next(dividend_lines)
        sum_value = 0.0
        for dividend in dividend_lines:
            sum_value += float(dividend[3])
    return sum_value


def get_pairs(entries_path: pathlib.Path = ENTRIES_PATH) -> List[str]:
    """Returns list of pairs."""
    with open(entries_path, newline="", encoding="utf-8") as csvfile:
        pair_lines = csv.reader(csvfile, delimiter=" ", quotechar="|")
        next(pair_lines)
        pairs = [pair[1].strip() for pair in pair_lines if pair]
        logging.debug("Getting pairs %s", pairs)
        return list(set(pairs))


def save_entry(
    date: str, stock: str, count: str, price: str, converted_amount: float
) -> None:
    """Save entries to CSV file."""
    with open(ENTRIES_PATH, "a", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=" ", quotechar="|")
        csv_writer.writerow([date, stock, count, price, converted_amount])
    logging.debug(
        f"Entry date: {date} stock: {stock} count: {count} "
        f"price: {price} saved to {ENTRIES_PATH}"
    )
