"""Pure scalar co-channel interference calculations.

This module belongs to Block 1. It deliberately has no dependency on GIS,
KML, coordinates, Streamlit, or network planning.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


SIR_THRESHOLDS_DB: dict[int, float] = {
    7: 10.0,
    8: 9.0,
    9: 7.5,
    10: 7.0,
    11: 6.5,
    12: 6.0,
}


def dbm_to_mw(power_dbm: float) -> float:
    """Convert dBm to mW."""
    if math.isinf(power_dbm) and power_dbm < 0:
        return 0.0
    return 10.0 ** (power_dbm / 10.0)


def mw_to_dbm(power_mw: float) -> float:
    """Convert mW to dBm."""
    if power_mw <= 0:
        return float("-inf")
    return 10.0 * math.log10(power_mw)


def power_sum_dbm(powers_dbm: Sequence[float]) -> float:
    """Sum dBm powers in linear mW and return the total in dBm."""
    if not powers_dbm:
        return float("-inf")
    total_mw = sum(dbm_to_mw(power) for power in powers_dbm)
    return mw_to_dbm(total_mw)


def sir_db(signal_power_dbm: float, interferers_dbm: Sequence[float]) -> float:
    """Return signal-to-interference ratio in dB."""
    if not interferers_dbm:
        return float("inf")
    interference_total_dbm = power_sum_dbm(interferers_dbm)
    return signal_power_dbm - interference_total_dbm


def sir_threshold_db(sf: int = 12) -> float:
    """Return the SIR decoding threshold for a LoRa spreading factor."""
    try:
        return SIR_THRESHOLDS_DB[sf]
    except KeyError as exc:
        raise ValueError("sf must be an integer between 7 and 12.") from exc


def sir_is_decodable(sir_value_db: float, sf: int = 12) -> bool:
    """Return True when the SIR is above the LoRa decoding threshold."""
    return sir_value_db >= sir_threshold_db(sf)
