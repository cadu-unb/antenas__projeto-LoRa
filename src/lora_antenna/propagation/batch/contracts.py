"""Pure data contracts for propagation batch execution.

No GIS, network, shapely, requests, or streamlit imports.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from lora_antenna.antenna.base import Antenna
from lora_antenna.core.constants import (
    DEFAULT_RX_SENSITIVITY_DBM,
    DEFAULT_TX_POWER_DBM,
    LORA_DEFAULT_HZ,
)
from lora_antenna.core.validators import validate_lora_br_frequency_hz
from lora_antenna.propagation.friis import LinkRisk


class LinkPair(BaseModel):
    """Directed pair ready for scalar RF calculation."""

    model_config = ConfigDict(frozen=True)

    origin_label: str
    dest_label: str
    distance_m: float

    @model_validator(mode="after")
    def _validate(self) -> "LinkPair":
        if self.origin_label == self.dest_label:
            raise ValueError("origin_label and dest_label must be different.")
        if self.distance_m <= 0:
            raise ValueError("distance_m must be positive.")
        return self


class ScalarLinkInput(BaseModel):
    """GIS-computed scalars for one directed link.

    GIS layer fills these before passing to the pure executor.
    """

    model_config = ConfigDict(frozen=True)

    origin_label: str
    dest_label: str
    distance_m: float
    distance_3d_m: float
    total_extra_loss_db: float
    n_buildings_crossed: int = 0

    @model_validator(mode="after")
    def _validate(self) -> "ScalarLinkInput":
        if self.origin_label == self.dest_label:
            raise ValueError("origin_label and dest_label must be different.")
        if self.distance_m <= 0:
            raise ValueError("distance_m must be positive.")
        if self.distance_3d_m <= 0:
            raise ValueError("distance_3d_m must be positive.")
        if self.total_extra_loss_db < 0:
            raise ValueError("total_extra_loss_db must be non-negative.")
        if self.n_buildings_crossed < 0:
            raise ValueError("n_buildings_crossed must be non-negative.")
        return self


class LinkBatchRequest(BaseModel):
    """Batch request on the GIS-to-propagation boundary.

    GIS layer fills ScalarLinkInput items; executor consumes only scalars.
    """

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    pairs: list[ScalarLinkInput]
    antenna: Antenna
    tx_power_dbm: float = DEFAULT_TX_POWER_DBM
    frequency_hz: float = LORA_DEFAULT_HZ
    rx_sensitivity_dbm: float = DEFAULT_RX_SENSITIVITY_DBM
    sf: int = 12

    @field_validator("frequency_hz")
    @classmethod
    def _validate_frequency(cls, value: float) -> float:
        return validate_lora_br_frequency_hz(value)

    @field_validator("sf")
    @classmethod
    def _validate_sf(cls, value: int) -> int:
        if value < 7 or value > 12:
            raise ValueError("sf must be between 7 and 12.")
        return value

    @model_validator(mode="after")
    def _validate_pairs(self) -> "LinkBatchRequest":
        if not self.pairs:
            raise ValueError("LinkBatchRequest requires at least one pair.")
        return self


class LinkBatchResult(BaseModel):
    """Result for one directed link in a multi-node topology."""

    model_config = ConfigDict(frozen=True)

    origin_label: str
    dest_label: str
    distance_m: float
    distance_3d_m: float
    fspl_db: float
    extra_loss_db: float
    received_power_dbm: float
    link_margin_db: float
    link_risk: LinkRisk
    feasible: bool
    sir_db: Optional[float] = None
    sir_decodable: Optional[bool] = None
    interferer_labels: list[str] = Field(default_factory=list)
    n_buildings_crossed: int = 0
