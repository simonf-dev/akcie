""" Help structures as enums and typed dicts"""
import logging
from enum import Enum
from typing import TypedDict


class CloudType(Enum):
    """Enum which describes type of the cloud"""

    AZURE = "azure"
    NONE = "none"


class LoggingSettings(Enum):
    """Enum which saves settings for logging"""

    OUTPUT_FILE = "tmp.log"
    LOGGING_LEVEL = logging.DEBUG


class SummaryDict(TypedDict):
    """This dict is used to summarize entries for view Jinja HTML"""

    symbol: str
    actual_price: float
    actual_basis: float
    cost_basis: float
    count: float
    currency: str


class Dividend(TypedDict):
    """THis dict is used to summarize dividends for view Jinja HTML"""

    currency: str
    symbol: str
    converted_value: float
    value: float
