""" Module with main functionality of the tool"""
import csv
import datetime
import logging
import os
import platform
import shutil
import sys
import webbrowser
from collections import defaultdict
from pathlib import Path
from typing import Dict, Literal, Optional, Annotated
import appeal

import jinja2

from stock_summary.clouds.logic import sync_files_down, sync_files_up
from stock_summary.help_structures import CloudType

logging_level = os.environ.get("DEBUG_LEVEL")
logging.basicConfig(level=logging_level if logging_level else "DEBUG")
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

app = appeal.Appeal()


@app.command("generate-portfolio")
def generate_portfolio_main() -> None:
    """
    generates actual value of your portfolio in CZK and
    percentage move from the start of your investments
    """
    sync_files_down()
    conversion_rates = get_exchange_rates()
    pairs = get_pairs()
    prices = get_pair_prices(pairs)
    with open(settings.ENTRIES_PATH, newline="", encoding="utf-8") as csvfile:
        entries_reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
        init_value: float = 0
        curr_value: float = 0
        next(entries_reader)
        stock_dict = defaultdict(int)
        for row in entries_reader:
            if not row:
                continue
            count = float(row[2])
            init_value += float(row[4])
            stock_dict[row[1]] += count
            logging.info(stock_dict)
        for stock_tag, count in stock_dict.items():
            if count != 0:
                conversion_rate = conversion_rates[prices[stock_tag].currency]
                curr_value += count * prices[stock_tag].regularMarketPrice * conversion_rate
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


@app.command("generate-html")
def generate_html_main() -> None:
    """
    generates summary page from all current data
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


@app.command("add-entry")
def add_entry_main(stock: str, date: str, count: float, price: float) -> None:
    """
    add entry for concrete date, stock, count and price
    percentage move from the start of your investments

    stock - stock symbol
    date - date of the entry, please add as DD/MM/YYYY
    count - count of stocks
    price - price of one stock
    """

    sync_files_down()
    if not stock or not date or not count or not price:
        logging.error("You have to enter all needed params")
        raise ValueError("You have to enter all needed params")
    pair = stock.strip()
    try:
        date_datetime: datetime.datetime = validate_date(date)
    except TypeError as err:
        raise RuntimeError("parameters have bad types, please try again") from err
    currency = get_pair_prices(get_pairs())[stock].currency
    converted_amount = convert_currency(date_datetime, currency, "CZK", count * price)
    save_entry(date, pair, count, price, converted_amount)
    logging.info(
        "Entry with date %s , stock %s, count %s , price %s successfully added.",
        date,
        stock,
        count,
        price,
    )
    sync_files_up(paths=[settings.ENTRIES_PATH])


@app.command("export-data")
def export_data_main(directory: str) -> None:
    """
    exports data to your directory

    directory - path to directory for export
    """
    sync_files_down()
    if not directory:
        logging.error("You need to pass the directory for the output.")
        sys.exit(1)
    export_data(Path(directory))


@app.command("import-data")
def import_data_main(*, entries: Annotated[Optional[str], None] = None,
                     portfolio: Annotated[Optional[str], None] = None,
                     dividends: Annotated[Optional[str], None] = None,
                     initialize= False, confirmation = False) -> None:
    """
    imports data from your custom files

    --entries - Path to your entries file
    --portfolio - Path to your portfolio file
    --dividends - Path to your dividends file
    --initialize - Flag for initialization of basic data false, has to be used with -y, or it has no effect.
    --confirmation -  Flag to automatically confirm all actions as overwrite of your current datafiles
    """
    if (
            portfolio or entries or dividends
    ) and initialize:
        logging.error(
            "Using rewrite option with entries and portfolio options, no effect."
        )
        sys.exit(1)
    if initialize and confirmation:
        rewrite_data_files(rewrite=True)
        logging.info("Data files initialized with empty files with correct headers.")
        return
    if not confirmation:
        user_confirmation = input(
            "You will rewrite your actual saved data, are you sure to proceed? "
            "Type Y: "
        )
        if not user_confirmation.lower() == "y":
            logging.error("Action canceled, ending without any action.")
            sys.exit(1)
    if portfolio:
        import_data(Path(portfolio), settings.PORTFOLIO_PATH)
        logging.info(
            f"Portfolio {portfolio} successfully updated to {settings.PORTFOLIO_PATH}"
        )
    if entries:
        import_data(Path(entries), settings.ENTRIES_PATH)
        logging.info(
            f"Entries {entries} successfully updated to {settings.ENTRIES_PATH}"
        )
    if dividends:
        import_data(Path(dividends), settings.DIVIDEND_PATH)
        logging.info(
            f"Dividends {dividends} successfully updated to {settings.DIVIDEND_PATH}"
        )
    sync_files_up()


@app.command("save-token")
def save_token_main(token: str) -> None:
    """
    save your token to rapidAPI
    token - token for the cloud

    """
    os.makedirs(settings.SETTINGS_PATH, exist_ok=True)
    with open(settings.TOKEN_PATH, "w", encoding="utf-8") as token_file:
        token_file.write(token)
    logging.info(f"Token successfully saved to {settings.TOKEN_PATH}")


@app.command("add-dividend")
def add_dividend_main(date: str, stock: str, amount: float) -> None:
    """
    add dividend for current pair and date

    date - Date of the dividend entry, please add as DD/MM/YYYY
    stock - Symbol of the stock for dividend.
    amount - Amount of the earned money (in stock currency)
    """
    if not stock or not date or not amount:
        logging.error("You have to enter all needed params")
        raise ValueError("You have to enter all needed params")
    sync_files_down()
    pair = stock.strip()
    try:
        date_datetime = validate_date(date)
    except TypeError as err:
        raise RuntimeError("parameters have bad types, please try again") from err
    save_dividend(date_datetime, pair, amount)
    sync_files_up(paths=[settings.DIVIDEND_PATH])
    logging.info(
        "Entry with date %s , stock %s, amount %s .",
        date,
        stock,
        amount,
    )


@app.command("set-cloud")
@app.option("tactic", "--local-tactic", annotation=lambda: "local")
@app.option("tactic", "--cloud-tactic", annotation=lambda: "cloud")
def set_cloud_main(cloud: Annotated[Literal["none", "azure"], appeal.validate('none', 'azure')],
                   azure: Annotated[Optional[str], None] = None, *,
                   tactic: str = "local") -> None:
    """
    Set up your cloud environment and sync data with it

    cloud - type of the cloud to use (now supported 'none'(default, only local files) and 'azure')"
    --cloud-tactic - use cloud files for sync and rewrite local ones (default one)
    --local-tactic - use local files for sync and rewrite cloud ones
    azure - connection string to the azure
    """
    env_vars: Dict[str, str] = {}
    if azure is not None:
        env_vars["AZURE_CONNECTION_STR"] = azure
        settings.AZURE_CONNECTION_STR = azure
        logging.info("Azure connection string parsed correctly.")
    try:
        if cloud is not None:
            cloud_enum = CloudType(cloud.lower())
            env_vars["CLOUD_TYPE"] = cloud.lower()
            settings.CLOUD_TYPE = cloud.lower()
            logging.info("Cloud %s is valid option.", cloud)
    except ValueError as err:
        logging.error("Provided invalid cloud type %s , raising error.", cloud)
        raise err
    if tactic is None and cloud is not None:
        err_msg = "Specified cloud but not tactic for the files. Raising error."
        logging.error(err_msg)
        raise ValueError(err_msg)
    if tactic == "local" and cloud is not None:
        sync_files_up(cloud_type=cloud_enum)
        logging.info("Successfully synced with the cloud with 'local' tactic.")
    if tactic == "cloud" and cloud is not None:
        sync_files_down(cloud_type=cloud_enum)
        logging.info("Successfully synced with the cloud with 'cloud' tactic.")
    save_variables_to_file(env_vars)
    logging.info(
        "Everything saved successfully to the system and all changes"
        " happened correctly."
    )


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    app.main()
