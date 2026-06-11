"""Validation helpers shared by the simulation engine."""

from __future__ import annotations

from lora_antenna.core.constants import LORA_BR_MAX_HZ, LORA_BR_MIN_HZ


def validate_lora_br_frequency_hz(frequency_hz: float) -> float:
    """Return a valid Brazilian LoRa frequency or raise ValueError."""
    if not LORA_BR_MIN_HZ <= frequency_hz <= LORA_BR_MAX_HZ:
        raise ValueError(
            "LoRa no Brasil deve operar somente na faixa 915-928 MHz."
        )
    return frequency_hz


def validate_positive_distance_m(distance_m: float) -> float:
    """Return a positive distance or raise ValueError."""
    if distance_m <= 0:
        raise ValueError("distance_m must be greater than zero.")
    return distance_m
