""" Module with main functionality of the tool"""
import csv
import datetime
import logging
import os
import platform
import shutil
import sys
import webbrowser
from pathlib import Path
from typing import Dict

import jinja2

from stock_summary.clouds.logic import sync_files_down, sync_files_up
from stock_summary.help_structures import CloudType

logging_level = os.environ.get("DEBUG_LEVEL")
logging.basicConfig(level=logging_level if logging_level else "INFO")
from stock_summary import settings
from stock_summary.library import (
    convert_currency,
    export_data,
    get_dividend_sum,
    get_dividend_summary,
    get_entries_summary,
    get_exchange_rates,
    get_pair_prices,
    get_pairs,
    get_plot_html,
    import_data,
    prepare_portfolio_data,
    rewrite_data_files,
    save_dividend,
    save_entry,
    save_variables_to_file,
    validate_date,
)
from stock_summary.parsers import (
    add_entry_parser,
    cloud_parser,
    dividend_parser,
    export_parser,
    import_parser,
)


def generate_portfolio_main() -> None:
    """Generates portfolio for actual time and entered entries."""
    sync_files_down()
    conversion_rates = get_exchange_rates()
    pairs = get_pairs()
    prices = get_pair_prices(pairs)
    with open(settings.ENTRIES_PATH, newline="", encoding="utf-8") as csvfile:
        entries_reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
        init_value: float = 0
        curr_value: float = 0
        next(entries_reader)
        for row in entries_reader:
            if not row:
                continue
            count = float(row[2])
            conversion_rate = conversion_rates[prices[row[1]].currency]
            init_value += float(row[4])
            curr_value += count * prices[row[1]].regularMarketPrice * conversion_rate
    with open(settings.PORTFOLIO_PATH, "a", encoding="utf-8") as result_file:
        now = datetime.datetime.now()
        result_file.write(
            f"{now.strftime('%d/%m/%y')} {curr_value} "
            f"{curr_value - init_value + get_dividend_sum()}\n"
        )
    sync_files_up(paths=[settings.PORTFOLIO_PATH])
    logging.info(
        "Portfolio with cost basis %s and profit %s generated and added.",
        curr_value,
        curr_value - init_value,
    )


def generate_html_main() -> None:
    """
    Generates HTML and executes it in your browser.
    """
    sync_files_down()
    summary_records = list(get_entries_summary().values())
    dividend_summary = list(get_dividend_summary().values())

    portfolio_data = prepare_portfolio_data()
    plot_html = get_plot_html(portfolio_data)
    environment = jinja2.Environment()
    with open(
        Path(__file__).parent.resolve() / "html_files" / "jinja.html",
        "r",
        encoding="utf-8",
    ) as html_template:
        template = environment.from_string(html_template.read())
    with open(settings.INDEX_HTML_FILE, "w", encoding="utf-8") as index_file:
        index_file.write(
            template.render(
                plot_html=plot_html, records=summary_records, dividends=dividend_summary
            )
        )
    shutil.copy2(
        Path(__file__).parent.resolve() / "html_files" / "main.css",
        settings.MAIN_CSS_FILE,
    )
    logging.info(f"Index html file successfully saved to {settings.INDEX_HTML_FILE}")
    prepend_str = ""
    if platform.system().lower() == "darwin":
        prepend_str = "file:///"
    webbrowser.open(f"{prepend_str}{settings.INDEX_HTML_FILE}")


def add_entry_main() -> None:
    """
    Root function for the add entry argument from the command line.
    """
    parser = add_entry_parser()
    (options, _) = parser.parse_args()
    sync_files_down()
    if not options.stock or not options.date or not options.count or not options.price:
        logging.error("You have to enter all needed params")
        raise ValueError("You have to enter all needed params")
    pair = options.stock.strip()
    try:
        date = validate_date(options.date)
        count = float(options.count)
        price = float(options.price)
    except TypeError as err:
        raise RuntimeError("parameters have bad types, please try again") from err
    currency = get_pair_prices(get_pairs())[options.stock].currency
    converted_amount = convert_currency(date, currency, "CZK", count * price)
    save_entry(options.date, pair, options.count, options.price, converted_amount)
    logging.info(
        "Entry with date %s , stock %s, count %s , price %s successfully added.",
        options.date,
        options.stock,
        options.count,
        options.price,
    )
    sync_files_up(paths=[settings.ENTRIES_PATH])


def export_data_main() -> None:
    """Main function for export data command."""
    parser = export_parser()
    (options, _) = parser.parse_args()
    sync_files_down()
    if not options.directory:
        logging.error("You need to pass the directory for the output.")
        sys.exit(1)
    export_data(Path(options.directory))


def import_data_main() -> None:
    """Main function for import data command."""
    parser = import_parser()
    (options, _) = parser.parse_args()
    if (
        options.portfolio or options.entries or options.dividends
    ) and options.initialize:
        logging.error(
            "Using rewrite option with entries and portfolio options, no effect."
        )
        sys.exit(1)
    if options.initialize and options.confirmation:
        rewrite_data_files(rewrite=True)
        logging.info("Data files initialized with empty files with correct headers.")
        return
    if not options.confirmation:
        user_confirmation = input(
            "You will rewrite your actual saved data, are you sure to proceed? "
            "Type Y: "
        )
        if not user_confirmation.lower() == "y":
            logging.error("Action canceled, ending without any action.")
            sys.exit(1)
    if options.portfolio:
        import_data(Path(options.portfolio), settings.PORTFOLIO_PATH)
        logging.info(
            f"Portfolio {options.portfolio} successfully updated to {settings.PORTFOLIO_PATH}"
        )
    if options.entries:
        import_data(Path(options.entries), settings.ENTRIES_PATH)
        logging.info(
            f"Entries {options.entries} successfully updated to {settings.ENTRIES_PATH}"
        )
    if options.dividends:
        import_data(Path(options.dividends), settings.DIVIDEND_PATH)
        logging.info(
            f"Dividends {options.dividends} successfully updated to {settings.DIVIDEND_PATH}"
        )
    sync_files_up()


def save_token_main() -> None:
    """Main function for save token command."""
    token = sys.argv[2]
    os.makedirs(settings.SETTINGS_PATH, exist_ok=True)
    with open(settings.TOKEN_PATH, "w", encoding="utf-8") as token_file:
        token_file.write(token)
    logging.info(f"Token successfully saved to {settings.TOKEN_PATH}")


def add_dividend_main() -> None:
    """
    Root function for the dividend argument from the command line.
    """
    parser = dividend_parser()
    (options, _) = parser.parse_args()
    if not options.stock or not options.date or not options.amount:
        logging.error("You have to enter all needed params")
        raise ValueError("You have to enter all needed params")
    sync_files_down()
    pair = options.stock.strip()
    try:
        date = validate_date(options.date)
        amount = float(options.amount)
    except TypeError as err:
        raise RuntimeError("parameters have bad types, please try again") from err
    save_dividend(date, pair, amount)
    sync_files_up(paths=[settings.DIVIDEND_PATH])
    logging.info(
        "Entry with date %s , stock %s, amount %s .",
        options.date,
        options.stock,
        options.amount,
    )


def set_cloud_main() -> None:
    """
    Set cloud settings to the env file, so application
    can work with them in the run.
    """
    parser = cloud_parser()
    (options, _) = parser.parse_args()
    env_vars: Dict[str, str] = {}
    if options.azure is not None:
        env_vars["AZURE_CONNECTION_STR"] = options.azure
        settings.AZURE_CONNECTION_STR = options.azure
        logging.info("Azure connection string parsed correctly.")
    cloud = None
    try:
        if options.cloud is not None:
            cloud = CloudType(options.cloud.lower())
            env_vars["CLOUD_TYPE"] = options.cloud.lower()
            settings.CLOUD_TYPE = cloud
            logging.info("Cloud %s is valid option.", options.cloud)
    except ValueError as err:
        logging.error("Provided invalid cloud type %s , raising error.", options.cloud)
        raise err
    if options.tactic is None and cloud is not None:
        err_msg = "Specified cloud but not tactic for the files. Raising error."
        logging.error(err_msg)
        raise ValueError(err_msg)
    if options.tactic == "local" and cloud is not None:
        sync_files_up(cloud_type=cloud)
        logging.info("Successfully synced with the cloud with 'local' tactic.")
    if options.tactic == "cloud" and cloud is not None:
        sync_files_down(cloud_type=cloud)
        logging.info("Successfully synced with the cloud with 'cloud' tactic.")
    save_variables_to_file(env_vars)
    logging.info(
        "Everything saved successfully to the system and all changes"
        " happened correctly."
    )


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
        "add-dividend [opts] - add dividend for current pair and date\n\n"
        "set-cloud [opts] - set up your cloud environment and sync data with it\n\n"
    )


def main() -> None:
    """Main function."""
    try:
        rewrite_data_files()
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
        elif sys.argv[1] == "add-dividend":
            add_dividend_main()
        elif sys.argv[1] == "set-cloud":
            set_cloud_main()
        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            print_main_help()
        else:
            logging.error(
                "Invalid first command, use option from: 'retrain-model','make-analysis"
                ",'retrain-model','get-result', 'set-cloud"
            )
            sys.exit(1)
    except (RuntimeError, ValueError) as err:
        logging.error(err)
        raise err
    sys.exit(0)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    main()
