from unittest.mock import patch
from stock_summary.library import get_entries_summary
from pathlib import Path
TESTING_DATASETS_PATH = Path(__file__).parent.resolve() / "testing_data"
# zamyslet se jak preharcodovat value na jednotlive data files, bud jen pro testy, nebo i pro uzivatele
def test_entries_summary() -> None:
    # namockovat funkce pro exchange a pairs
    # vypocitat, kolik by mely dat summary funkce, zkontrolovat
    # vypocitat, kolik by melo dat portfolio, zkontrolovat
    # zmenit cenu akcii a kurz, otestovat znovu
    # A-20 B-10 kurz - 25
    # A-20 B-10 kurz - 24
    # A-25 B-6 kurz - 25
    # A-25 B-6 kurz - 24
    with patch(
            "stock_summary.library.get_pair_prices"
    ) as pair_prices_mock:
        pair_prices_mock.return_value = {"A": {"currency": "EUR", "regularMarketPrice": 20, "symbol": "A"},
                                 "B": {"currency": "EUR", "regularMarketPrice": 10, "symbol": "B"}}
        with patch(
                "stock_summary.library.get_exchange_rates"
        ) as exchange_mock:
            exchange_mock.return_value = {"EUR": 25}
            expected_sum_dict = {"A": {"symbol": "A", "actual_price": 20.0, "actual_basis": 2500.0, "cost_basis": -100.0, "count": 5.0, "currency": "EUR"},
                                 "B": {"symbol": "B", "actual_price": 10.0, "actual_basis": 1250.0, "cost_basis": 575.0, "count": 5.0, "currency": "EUR"}}
            assert get_entries_summary(entries_path=TESTING_DATASETS_PATH /"testing_data_A" / "entries") == expected_sum_dict
            exchange_mock.return_value = {"EUR": 24}
            expected_sum_dict = {"A": {"symbol": "A", "actual_price": 20.0, "actual_basis": 2400.0, "cost_basis": -100.0, "count": 5.0, "currency": "EUR"},
                                 "B": {"symbol": "B", "actual_price": 10.0, "actual_basis": 1200.0, "cost_basis": 575.0, "count": 5.0, "currency": "EUR"}}
            assert get_entries_summary(entries_path=TESTING_DATASETS_PATH /"testing_data_A" / "entries") == expected_sum_dict
            pair_prices_mock.return_value = {
                "A": {"currency": "EUR", "regularMarketPrice": 25, "symbol": "A"},
                "B": {"currency": "EUR", "regularMarketPrice": 6, "symbol": "B"}}
            expected_sum_dict = {"A": {"symbol": "A", "actual_price": 25.0, "actual_basis": 3000.0, "cost_basis": -100.0, "count": 5.0, "currency": "EUR"},
                                 "B": {"symbol": "B", "actual_price": 6.0, "actual_basis": 720.0, "cost_basis": 575.0, "count": 5.0, "currency": "EUR"}}
            assert get_entries_summary(entries_path=TESTING_DATASETS_PATH /"testing_data_A" / "entries") == expected_sum_dict
            exchange_mock.return_value = {"EUR": 25}
            expected_sum_dict = {"A": {"symbol": "A", "actual_price": 25.0, "actual_basis": 3125.0, "cost_basis": -100.0, "count": 5.0, "currency": "EUR"},
                                 "B": {"symbol": "B", "actual_price": 6.0, "actual_basis": 750.0, "cost_basis": 575.0, "count": 5.0, "currency": "EUR"}}
            assert get_entries_summary(entries_path=TESTING_DATASETS_PATH /"testing_data_A" / "entries") \
                   == expected_sum_dict
def test_dividend_summary() -> None:
    # otestovat dividend summary stejne jako entries summary
    pass

def test_html_output() -> None:
    # otestovat html a jestli jsou v tabulkach spravne hodnoty
    pass

def test_dividend_sum() -> None:
    #otestovat sum dividend
    pass

def test_get_pairs() -> None:
    # vyzkouset get_pairs
    pass

