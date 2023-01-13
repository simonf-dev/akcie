""" parser functions """
import optparse


def add_entry_parser() -> optparse.OptionParser:
    """ Parser for entry command. """
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
    """ Parser for import command """
    parser = optparse.OptionParser(
        usage="main.py import-data [options]\n" "Import data from your custom files."
    )
    parser.add_option(
        "-e", "--entries", dest="entries", help="Path to your custom file with entries."
    )
    parser.add_option(
        "-p", "--portfolio", dest="portfolio", help="Path to your custom file with portfolio."
    )

    return parser

def export_parser() -> optparse.OptionParser:
    """ Parser for export command."""
    parser = optparse.OptionParser(
        usage="main.py import-data [options]\n" "Export data from your custom files to some"
              "directory."
    )
    parser.add_option(
        "-d", "--directory", dest="directory", help="Path to directory for the output."
    )

    return parser
