import socket
from typing import Any, Callable, Dict, List, Tuple

sock = socket.socket


class NetworkBlocker(socket.socket):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise Exception("Network call blocked")


def block_network(function: Callable[[], None]) -> Callable[[], None]:
    def wrapper_blocking_network() -> None:
        try:
            socket.socket = NetworkBlocker  # type: ignore
            function()
        except Exception as err:
            raise err
        finally:
            socket.socket = sock  # type: ignore

    return wrapper_blocking_network


socket.socket = NetworkBlocker  # type: ignore


from pathlib import Path
from unittest.mock import patch

from stock_summary.library import get_dividend_sum, get_entries_summary, get_pairs
from stock_summary.settings import INIT_DATASETS_PATH

TESTING_DATASETS_PATH = Path(__file__).parent.resolve() / "testing_data"
# unblock connection again
socket.socket = sock  # type: ignore


@block_network
def test_entries_summary() -> None:
    # namockovat funkce pro exchange a pairs
    # vypocitat, kolik by mely dat summary funkce, zkontrolovat
    # vypocitat, kolik by melo dat portfolio, zkontrolovat
    # zmenit cenu akcii a kurz, otestovat znovu
    # A-20 B-10 kurz - 25
    # A-20 B-10 kurz - 24
    # A-25 B-6 kurz - 25
    # A-25 B-6 kurz - 24
    with patch("stock_summary.library.get_pair_prices") as pair_prices_mock:
        pair_prices_mock.return_value = {
            "A": {"currency": "EUR", "regularMarketPrice": 20, "symbol": "A"},
            "B": {"currency": "EUR", "regularMarketPrice": 10, "symbol": "B"},
        }
        with patch("stock_summary.library.get_exchange_rates") as exchange_mock:
            exchange_mock.return_value = {"EUR": 25}
            expected_sum_dict = {
                "A": {
                    "symbol": "A",
                    "actual_price": 20.0,
                    "actual_basis": 2500.0,
                    "cost_basis": -100.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
                "B": {
                    "symbol": "B",
                    "actual_price": 10.0,
                    "actual_basis": 1250.0,
                    "cost_basis": 575.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
            }
            assert (
                get_entries_summary(
                    entries_path=TESTING_DATASETS_PATH / "testing_data_A" / "entries"
                )
                == expected_sum_dict
            )
            exchange_mock.return_value = {"EUR": 24}
            expected_sum_dict = {
                "A": {
                    "symbol": "A",
                    "actual_price": 20.0,
                    "actual_basis": 2400.0,
                    "cost_basis": -100.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
                "B": {
                    "symbol": "B",
                    "actual_price": 10.0,
                    "actual_basis": 1200.0,
                    "cost_basis": 575.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
            }
            assert (
                get_entries_summary(
                    entries_path=TESTING_DATASETS_PATH / "testing_data_A" / "entries"
                )
                == expected_sum_dict
            )
            pair_prices_mock.return_value = {
                "A": {"currency": "EUR", "regularMarketPrice": 25, "symbol": "A"},
                "B": {"currency": "EUR", "regularMarketPrice": 6, "symbol": "B"},
            }
            expected_sum_dict = {
                "A": {
                    "symbol": "A",
                    "actual_price": 25.0,
                    "actual_basis": 3000.0,
                    "cost_basis": -100.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
                "B": {
                    "symbol": "B",
                    "actual_price": 6.0,
                    "actual_basis": 720.0,
                    "cost_basis": 575.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
            }
            assert (
                get_entries_summary(
                    entries_path=TESTING_DATASETS_PATH / "testing_data_A" / "entries"
                )
                == expected_sum_dict
            )
            exchange_mock.return_value = {"EUR": 25}
            expected_sum_dict = {
                "A": {
                    "symbol": "A",
                    "actual_price": 25.0,
                    "actual_basis": 3125.0,
                    "cost_basis": -100.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
                "B": {
                    "symbol": "B",
                    "actual_price": 6.0,
                    "actual_basis": 750.0,
                    "cost_basis": 575.0,
                    "count": 5.0,
                    "currency": "EUR",
                },
            }
            assert (
                get_entries_summary(
                    entries_path=TESTING_DATASETS_PATH / "testing_data_A" / "entries"
                )
                == expected_sum_dict
            )


@block_network
def test_dividend_summary() -> None:
    """testing get_dividend_summary function"""


@block_network
def test_html_output() -> None:
    """testing html output from main function"""


@block_network
def test_dividend_sum() -> None:
    """Testing get_dividend_sum function"""
    dividend_sum = get_dividend_sum(
        dividend_path=TESTING_DATASETS_PATH / "testing_data_A" / "dividends"
    )
    assert dividend_sum == 192
    dividend_sum = get_dividend_sum(dividend_path=INIT_DATASETS_PATH / "dividends")
    assert dividend_sum == 0


@block_network
def test_get_pairs() -> None:
    """Testing get_pairs function"""
    pairs = get_pairs(entries_path=TESTING_DATASETS_PATH / "testing_data_A" / "entries")
    assert len(pairs) == len(set(pairs))
    assert len(pairs) == 2
    pairs = get_pairs(entries_path=INIT_DATASETS_PATH / "entries")
    assert len(pairs) == 0
