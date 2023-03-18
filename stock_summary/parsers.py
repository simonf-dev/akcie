""" parser functions """
import optparse  # pylint: disable=W4901


def add_entry_parser() -> optparse.OptionParser:
    """Parser for entry command."""
    parser = optparse.OptionParser(
        usage="main.py add-entry [options]\n" "Add pair to to the list"
    )
    parser.add_option(
        "-s", "--stock", dest="stock", help="Symbol of the stock to entry."
    )
    parser.add_option(
        "-d", "--date", dest="date", help="Date of the entry, please add as DD/MM/YYYY"
    )
    parser.add_option("-c", "--count", dest="count", help="Count of the stocks bought.")
    parser.add_option("-p", "--price", dest="price", help="Price of the stocks.")
    return parser


def import_parser() -> optparse.OptionParser:
    """Parser for import command"""
    parser = optparse.OptionParser(
        usage="main.py import-data [options]\n" "Import data from your custom files."
    )
    parser.add_option(
        "-e", "--entries", dest="entries", help="Path to your custom file with entries."
    )
    parser.add_option(
        "-p",
        "--portfolio",
        dest="portfolio",
        help="Path to your custom file with portfolio.",
    )
    parser.add_option(
        "-d",
        "--dividends",
        dest="dividends",
        help="Path to your custom file with dividends.",
    )
    parser.add_option(
        "-y",
        dest="confirmation",
        action="store_true",
        help="Flag to automatically confirm all actions as overwrite of your current datafiles",
        default=False,
    )

    parser.add_option(
        "--initialize",
        dest="initialize",
        action="store_true",
        help="Flag for initialization of basic data false, has to be used with -y, or it has no"
        "effect.",
        default=False,
    )

    return parser


def export_parser() -> optparse.OptionParser:
    """Parser for export command."""
    parser = optparse.OptionParser(
        usage="main.py import-data [options]\n"
        "Export data from your custom files to some"
        "directory."
    )
    parser.add_option(
        "-d", "--directory", dest="directory", help="Path to directory for the output."
    )

    return parser


def dividend_parser() -> optparse.OptionParser:
    """Parser for dividend command."""
    parser = optparse.OptionParser(
        usage="main.py add-entry [options]\n" "Add dividend entry to to the list"
    )
    parser.add_option(
        "-s", "--stock", dest="stock", help="Symbol of the stock for dividend."
    )
    parser.add_option(
        "-d",
        "--date",
        dest="date",
        help="Date of the dividend entry, please add as DD/MM/YYYY",
    )
    parser.add_option(
        "-a",
        "--amount",
        dest="amount",
        help="Amount of the earned money " "(in stock currency)",
    )
    return parser


def cloud_parser() -> optparse.OptionParser:
    """Parser for cloud commands."""
    parser = optparse.OptionParser(
        usage="main.py set-cloud [options]\n" "Set cloud settings for the files."
    )
    parser.add_option(
        "--cloud",
        dest="cloud",
        help="Type of the cloud to use (now supported 'none'(default, only local files)"
        " and 'azure')",
    )
    parser.add_option(
        "--azure",
        dest="azure",
        help="Connection string for the Azure File storage, shares, directories and files will be"
        "created by the tool itself.",
    )

    parser.add_option(
        "--tactic",
        dest="tactic",
        help="Tactic for the sync. You can specify 'cloud' (your files will be overwritten from the cloud)"
             " or 'local' (your files will rewrite the cloud ones)."
    )
    return parser
