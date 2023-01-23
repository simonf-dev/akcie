""" Module with main functionality of the tool"""
import csv
import datetime
import logging
import os
import pathlib
import platform
import shutil
import sys
import webbrowser
from typing import List

import jinja2

logging_level = os.environ.get("DEBUG_LEVEL")
logging.basicConfig(level=logging_level if logging_level else "INFO")
from stock_summary.library import (
    export_data,
    get_entries_summary,
    get_exchange_rates,
    get_pair_prices,
    get_plot_html,
    import_data,
    prepare_portfolio_data,
    validate_date,
    check_if_files_exist
)
from stock_summary.parsers import add_entry_parser, export_parser, import_parser
from stock_summary.settings import (
    ENTRIES_PATH,
    INDEX_HTML_FILE,
    MAIN_CSS_FILE,
    PORTFOLIO_PATH,
    SETTINGS_PATH,
    TOKEN_PATH,
)


def get_pairs() -> List[str]:
    """Returns list of pairs."""
    with open(ENTRIES_PATH, newline="", encoding="utf-8") as csvfile:
        pair_lines = csv.reader(csvfile, delimiter=" ", quotechar="|")
        next(pair_lines)
        pairs = [pair[1].strip() for pair in pair_lines if pair]
        logging.debug("Getting pairs %s", pairs)
        return list(set(pairs))


def generate_portfolio_main() -> None:
    """Generates portfolio for actual time and entered entries."""
    conversion_rates = get_exchange_rates()
    pairs = get_pairs()
    prices = get_pair_prices(pairs)
    with open(ENTRIES_PATH, newline="", encoding="utf-8") as csvfile:
        entries_reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
        init_value: float = 0
        curr_value: float = 0
        next(entries_reader)
        for row in entries_reader:
            if not row:
                continue
            count = float(row[2])
            init_price = float(row[3])
            conversion_rate = conversion_rates[prices[row[1]]["currency"]]
            init_value += count * init_price * conversion_rate
            curr_value += count * prices[row[1]]["regularMarketPrice"] * conversion_rate
    with open(PORTFOLIO_PATH, "a", encoding="utf-8") as result_file:
        now = datetime.datetime.now()
        result_file.write(
            f"{now.strftime('%d/%m/%y')} {curr_value} {(curr_value / init_value - 1) * 100}\n"
        )
    logging.info(
        "Portfolio with price %s and percentage move %s generated and added.",
        curr_value,
        (curr_value / init_value - 1) * 100,
    )


def save_entry(date: str, stock: str, count: str, price: str) -> None:
    """Save entries to CSV file."""
    with open(ENTRIES_PATH, "a", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=" ", quotechar="|")
        csv_writer.writerow([date, stock, count, price])
    logging.debug(
        f"Entry date: {date} stock: {stock} count: {count} "
        f"price: {price} saved to {ENTRIES_PATH}"
    )


def generate_html_main() -> None:
    """
    Generates HTML and executes it in your browser.
    """
    summary_records = list(get_entries_summary().values())
    portfolio_data = prepare_portfolio_data()
    plot_html = get_plot_html(portfolio_data)
    environment = jinja2.Environment()
    with open(
        f"{pathlib.Path(__file__).parent.resolve()}/html_files/jinja.html",
        "r",
        encoding="utf-8",
    ) as html_template:
        template = environment.from_string(html_template.read())
    with open(INDEX_HTML_FILE, "w", encoding="utf-8") as index_file:
        index_file.write(template.render(plot_html=plot_html, records=summary_records))
    shutil.copy2(
        f"{pathlib.Path(__file__).parent.resolve()}/html_files/main.css", MAIN_CSS_FILE
    )
    logging.info(f"Index html file successfully saved to {INDEX_HTML_FILE}")
    prepend_str = ""
    if platform.system().lower() == "darwin":
        prepend_str = "file:///"
    webbrowser.open(f"{prepend_str}{INDEX_HTML_FILE}")


def add_entry_main() -> None:
    """
    Root function for the add entry argument from the command line.
    """
    parser = add_entry_parser()
    (options, _) = parser.parse_args()
    if not options.stock or not options.date or not options.count or not options.price:
        logging.error("You have to enter all needed params")
        raise ValueError("You have to enter all needed params")
    pair = options.stock.strip()
    if pair not in get_pairs():
        raise ValueError("Adding non existing stock symbol.")
    try:
        validate_date(options.date)
        int(options.count)
        int(options.price)
    except TypeError as err:
        raise RuntimeError("parameters have bad types, please try again") from err
    save_entry(options.date, options.stock, options.count, options.price)
    logging.info(
        "Entry with date %s , stock %s, count %s , price %s successfully added.",
        options.date,
        options.stock,
        options.count,
        options.price,
    )


def export_data_main() -> None:
    """Main function for export data command."""
    parser = export_parser()
    (options, _) = parser.parse_args()
    if not options.directory:
        logging.error("You need to pass the directory for the output.")
        sys.exit(1)
    export_data(options.directory)


def import_data_main() -> None:
    """Main function for import data command."""
    parser = import_parser()
    (options, _) = parser.parse_args()
    if options.portfolio:
        import_data(options.portfolio, PORTFOLIO_PATH, options.confirmation)
        logging.info(
            f"Portfolio {options.portfolio} successfully updated to {PORTFOLIO_PATH}"
        )
    if options.entries:
        import_data(options.entries, ENTRIES_PATH, options.confirmation)
        logging.info(
            f"Entries {options.entries} successfully updated to {ENTRIES_PATH}"
        )


def save_token_main() -> None:
    """Main function for save token command."""
    token = sys.argv[2]
    os.makedirs(SETTINGS_PATH, exist_ok=True)
    with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
        token_file.write(token)
    logging.info(f"Token successfully saved to {TOKEN_PATH}")


def print_main_help() -> None:
    """Prints main help"""
    print(
        "Available commands:\n\n"
        "add-entry [opts] - add entry for current date, stock, count and price\n\n"
        "generate-portfolio [opts] - generates actual value of your portfolio in CZK and "
        "percentage move from the start of your investments\n"
        "generate-html [opts] - generates summary page from all current data\n\n"
        "import-data [opts] - imports data from your custom files\n\n"
        "export-data [opts] - exports data to your directory\n\n"
        "save-token (token) - save your token to rapidAPI\n\n"
    )


def main() -> None:
    """Main function."""
    try:
        check_if_files_exist()
        if sys.argv[1] == "generate-html":
            generate_html_main()
        elif sys.argv[1] == "add-entry":
            add_entry_main()
        elif sys.argv[1] == "generate-portfolio":
            generate_portfolio_main()
        elif sys.argv[1] == "export-data":
            export_data_main()
        elif sys.argv[1] == "import-data":
            import_data_main()
        elif sys.argv[1] == "save-token":
            save_token_main()
        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print_main_help()
        else:
            logging.error(
                "Invalid first command, use option from: 'retrain-model','make-analysis"
                ",'retrain-model','get-result'"
            )
            sys.exit(1)
    except (RuntimeError, ValueError) as err:
        logging.error(err)
        raise err
    sys.exit(0)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()
