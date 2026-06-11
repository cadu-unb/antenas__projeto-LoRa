"""Base antenna contract used by propagation and GIS orchestration."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from lora_antenna.core.constants import LORA_DEFAULT_HZ
from lora_antenna.core.validators import validate_lora_br_frequency_hz


class Antenna(BaseModel):
    """Minimal antenna model required by the link budget engine."""

    model_config = ConfigDict(frozen=True)

    name: str = "Generic 915MHz Antenna"
    antenna_type: str = "generic"
    frequency_hz: float = LORA_DEFAULT_HZ
    gain_dbi: float = 2.15
    losses_db: float = 0.0

    @field_validator("frequency_hz")
    @classmethod
    def validate_frequency(cls, value: float) -> float:
        return validate_lora_br_frequency_hz(value)

    @field_validator("losses_db")
    @classmethod
    def validate_losses(cls, value: float) -> float:
        if value < 0:
            raise ValueError("losses_db must be non-negative.")
        return value
