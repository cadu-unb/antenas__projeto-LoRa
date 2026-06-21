"""Estimativa de consumo energético para módulos LoRa."""
from __future__ import annotations

import math
from dataclasses import dataclass

from ..schemas.lora_module import LoRaModule


@dataclass
class EnergyEstimate:
    tx_duration_ms: float
    energy_per_tx_mj: float
    daily_tx_count: int
    daily_energy_mj: float
    daily_energy_mwh: float
    battery_life_days: float


def estimate_energy(
    module: LoRaModule,
    tx_power_dbm: float,
    sf: int = 12,
    bw_khz: int = 125,
    payload_bytes: int = 20,
    transmissions_per_day: int = 96,
    battery_capacity_mah: float = 2000,
    battery_voltage_v: float = 3.3,
) -> EnergyEstimate:
    """Estima consumo energético via ToA simplificado.

    ToA = preamble + ceil(payload_bytes*8/SF) símbolos
    E_tx = I_tx(A) × V × t(s) × 1000  [mJ]
    """
    tx_current_ma = module.tx_current_options_ma[-1]
    for pwr, cur in zip(module.tx_power_options_dbm, module.tx_current_options_ma):
        if abs(pwr - tx_power_dbm) < 0.5:
            tx_current_ma = cur
            break

    bw_hz = bw_khz * 1000
    symbol_duration_ms = (2 ** sf / bw_hz) * 1000
    preamble_ms = 8 * symbol_duration_ms
    payload_symbols = math.ceil(payload_bytes * 8 / sf)
    tx_duration_ms = preamble_ms + payload_symbols * symbol_duration_ms

    energy_per_tx_mj = (tx_current_ma / 1000) * battery_voltage_v * (tx_duration_ms / 1000) * 1000
    daily_energy_mj = energy_per_tx_mj * transmissions_per_day
    daily_energy_mwh = daily_energy_mj / 3600

    battery_mj = battery_capacity_mah * battery_voltage_v * 3.6
    battery_life_days = battery_mj / daily_energy_mj if daily_energy_mj > 0 else float("inf")

    return EnergyEstimate(
        tx_duration_ms=tx_duration_ms,
        energy_per_tx_mj=energy_per_tx_mj,
        daily_tx_count=transmissions_per_day,
        daily_energy_mj=daily_energy_mj,
        daily_energy_mwh=daily_energy_mwh,
        battery_life_days=battery_life_days,
    )
