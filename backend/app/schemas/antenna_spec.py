from __future__ import annotations

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

_NEW_PHYSICAL_FIELDS = frozenset({
    "gmax_dbi", "hpbw_deg", "polarization", "is_directional",
    "pattern_model", "practicality_score", "multi_direction_score", "notes",
})


class AntennaSpec(BaseModel):
    schema_version: str = "1.0"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    frequency_hz: float
    units: dict[str, str] = Field(default_factory=dict)
    geometry: dict[str, Any] = Field(default_factory=dict)
    material: dict[str, Any] = Field(default_factory=dict)
    solver: str = "rapido"
    results: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Physical fields (optional, aligned with MATLAB external reference)
    gmax_dbi: Optional[float] = None
    hpbw_deg: Optional[float] = None
    polarization: Optional[str] = None
    is_directional: Optional[bool] = None
    pattern_model: Optional[str] = None
    practicality_score: Optional[float] = None
    multi_direction_score: Optional[float] = None
    notes: str = ""

    @field_validator("hpbw_deg")
    @classmethod
    def _hpbw_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("hpbw_deg must be > 0")
        return v

    @field_validator("practicality_score", "multi_direction_score")
    @classmethod
    def _score_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not (0 <= v <= 10):
            raise ValueError("score must be between 0 and 10")
        return v

    @model_validator(mode="after")
    def _bump_schema_version(self) -> "AntennaSpec":
        if self.schema_version == "1.0":
            has_new = (
                self.gmax_dbi is not None
                or self.hpbw_deg is not None
                or self.polarization is not None
                or self.is_directional is not None
                or self.pattern_model is not None
                or self.practicality_score is not None
                or self.multi_direction_score is not None
                or self.notes != ""
            )
            if has_new:
                self.schema_version = "2.0"
        return self
