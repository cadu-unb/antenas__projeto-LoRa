"""Pure scalar Friis/link-budget functions."""

from __future__ import annotations

import math
from enum import Enum

from lora_antenna.core.constants import C_M_PER_S
from lora_antenna.core.validators import (
    validate_lora_br_frequency_hz,
    validate_positive_distance_m,
)


class LinkRisk(str, Enum):
    """Risk classification based on received-power margin."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


def fspl_db(distance_m: float, frequency_hz: float) -> float:
    """Return free-space path loss in dB."""
    validate_positive_distance_m(distance_m)
    validate_lora_br_frequency_hz(frequency_hz)
    return (
        20.0 * math.log10(distance_m)
        + 20.0 * math.log10(frequency_hz)
        + 20.0 * math.log10(4.0 * math.pi / C_M_PER_S)
    )


def friis_received_power_dbm(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    rx_gain_dbi: float,
    fspl_db: float | None = None,
    losses_db: float = 0.0,
    *,
    distance_m: float | None = None,
    frequency_hz: float | None = None,
) -> float:
    """Return received power in dBm.

    The function accepts either a precomputed FSPL value or distance/frequency
    scalars. This keeps compatibility with both standalone and batch callers.
    """
    if fspl_db is None:
        if distance_m is None or frequency_hz is None:
            raise ValueError(
                "Provide fspl_db or both distance_m and frequency_hz."
            )
        fspl_db = globals()["fspl_db"](distance_m, frequency_hz)

    if losses_db < 0:
        raise ValueError("losses_db must be non-negative.")

    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - fspl_db - losses_db


def link_margin_db(received_power_dbm: float, rx_sensitivity_dbm: float) -> float:
    """Return link margin in dB."""
    return received_power_dbm - rx_sensitivity_dbm


def classify_link_risk(
    received_power_dbm: float,
    rx_sensitivity_dbm: float = -110.0,
) -> LinkRisk:
    """Classify link risk from received power and receiver sensitivity."""
    margin = link_margin_db(received_power_dbm, rx_sensitivity_dbm)
    if margin > 20.0:
        return LinkRisk.LOW
    if margin > 0.0:
        return LinkRisk.MEDIUM
    return LinkRisk.HIGH
