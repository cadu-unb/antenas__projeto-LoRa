from __future__ import annotations

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field


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
