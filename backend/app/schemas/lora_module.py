from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SensitivityByMode(BaseModel):
    sf: int
    bw_khz: int
    sensitivity_dbm: float


class LoRaModule(BaseModel):
    id: str
    name: str
    manufacturer: str
    frequency_mhz: float
    tx_power_options_dbm: list[float]
    tx_current_options_ma: list[float]
    voltage_range_v: tuple[float, float]
    sleep_current_ua: float
    sensitivity_modes: list[SensitivityByMode]
    notes: str = ""

    def get_sensitivity(self, sf: int = 12, bw_khz: int = 125) -> Optional[float]:
        for mode in self.sensitivity_modes:
            if mode.sf == sf and mode.bw_khz == bw_khz:
                return mode.sensitivity_dbm
        return None
