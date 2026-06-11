"""Neutral geographic models shared across GIS and RF calculations."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GeographicPosition(BaseModel):
    """WGS84 position with optional SRTM altitude.

    altitude_m is the KML/user-provided altitude. altitude_srtm_m is the
    terrain altitude fetched from SRTM and has priority when present.
    x_m/y_m/z_m are retained for compatibility with Cartesian directivity
    calculations.
    """

    model_config = ConfigDict(frozen=True)

    label: str = ""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: float = 0.0
    altitude_srtm_m: Optional[float] = None
    x_m: float = 0.0
    y_m: float = 0.0
    z_m: float = 0.0

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        return value.strip()

    @property
    def effective_altitude_m(self) -> float:
        """Use SRTM altitude when available, otherwise KML altitude."""
        if self.altitude_srtm_m is not None:
            return self.altitude_srtm_m
        return self.altitude_m
