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
    is_hub: bool = False

    # Perdas adicionais (Gap 4 e 11)
    extra_loss_db: float = Field(default=0.0)
    fading_margin_db: float = Field(default=0.0)
    polarization_loss_db: float = Field(default=0.0)

    # Orientação de antena — pré-requisito para G(θ,φ) na Fase 3
    azimuth_deg: Optional[float] = Field(default=None)
    tilt_deg: float = Field(default=0.0)

    # Módulo LoRa selecionado da biblioteca (sobrescreve rx_sensitivity_dbm/tx_power_dbm se preenchido)
    lora_module_id: Optional[str] = Field(default=None)
