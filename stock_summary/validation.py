"""Validation for stock_summary app."""
from typing import Any, Dict, Set

from pydantic import BaseModel, validator


class ExchangeRates(BaseModel):
    """Exchange rates that we get from API."""

    base_requested: str
    base: str
    rates: Dict[str, float]

    @validator("base")
    def base_as_requested(cls, value: str, values: Dict[str, Any]) -> str:
        """Check that base is same as requested."""
        if values["base_requested"] != value:
            raise ValueError(
                f'Got base {value} isnt same as requested {values["base_requested"]}'
            )
        return value

    @validator("rates")
    def rates_are_positive(cls, value: Dict[str, float]) -> Dict[str, float]:
        """Check that all rates are positive."""
        for rate in value.values():
            if rate <= 0:
                raise ValueError(f"Got negative rate {rate}")
        return value

    @validator("rates")
    def base_not_in_rates(
        cls, value: Dict[str, float], values: Dict[str, Any]
    ) -> Dict[str, float]:
        """Checks that base is not in rates or it has value '1'"""
        if values["base"] in value and value[values["base"]] != 1:
            raise ValueError(
                f'Got base {values["base"]} in rates and '
                f'it has different value than 1: {value[values["base"]]}'
            )
        return value


class PairResponse(BaseModel):
    """Pair response that we get from API for each pair."""
    pairs: Set[str] = set()
    symbol: str
    regularMarketPrice: float
    currency: str

    @validator("regularMarketPrice")
    def price_is_positive(cls, value: float) -> float:
        """Check that price is positive."""
        if value <= 0:
            raise ValueError(f"Got negative price {value}")
        return value

    @validator("symbol")
    def symbol_is_in_pairs(cls, value: str, values: Dict[str, Any]) -> str:
        """Check that symbol is in pairs."""
        if value not in cls.pairs:
            raise ValueError(
                f'Got symbol {value} which is not in pairs {values["pairs"]}'
            )
        return value
