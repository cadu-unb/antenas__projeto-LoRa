from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class NodeSpec(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    lat: float
    lon: float
    height_m: float = 0.0
    antenna_id: Optional[str] = None
    tx_power_dbm: float = 14.0
    rx_sensitivity_dbm: float = -137.0
    cable_loss_db: float = 0.0
