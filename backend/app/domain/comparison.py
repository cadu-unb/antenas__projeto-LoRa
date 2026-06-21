"""Framework de comparação de cenários: módulo × antena_TX × antena_GW."""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from ..schemas.antenna_spec import AntennaSpec
from ..schemas.lora_module import LoRaModule
from ..schemas.node_spec import NodeSpec

_DIRECTIONAL = {"helicoidal", "parabolica", "commercial_omni_6dbi"}


@dataclass
class ComparisonRow:
    scenario_label: str
    module_id: str
    tx_antenna_type: str
    gw_antenna_type: str
    min_margin_db: float
    mean_margin_db: float
    max_margin_db: float
    failure_count: int       # margem < 0
    critical_count: int      # 0 ≤ margem < 5 dB
    comfortable_count: int   # margem ≥ 10 dB
    robustness_score: float
    link_margins: list[float] = field(default_factory=list)


def _compute_robustness(margins: list[float], tx_antenna_type: str) -> float:
    """Penaliza antenas diretivas com alta variância de margem entre sensores."""
    mean_m = statistics.mean(margins)
    std_m = statistics.stdev(margins) if len(margins) > 1 else 0.0
    base = mean_m / (std_m + 1.0)
    penalty = 0.5 if tx_antenna_type in _DIRECTIONAL and std_m > 10.0 else 1.0
    return base * penalty


def run_comparison(
    sensor_nodes: list[NodeSpec],
    gateway_node: NodeSpec,
    freq_hz: float,
    modules: list[LoRaModule],
    tx_antenna_specs: list[AntennaSpec],
    gw_antenna_specs: list[AntennaSpec],
) -> list[ComparisonRow]:
    """Varre todas combinações módulo × antena_tx × antena_gw. Retorna ordenado por min_margin_db desc."""
    from .link_budget import compute_link_full

    rows: list[ComparisonRow] = []
    label_counter = 0

    for module in modules:
        tx_power = module.tx_power_options_dbm[-1]
        sensitivity = module.get_sensitivity(sf=12) or -137.0

        for tx_ant in tx_antenna_specs:
            for gw_ant in gw_antenna_specs:
                label_counter += 1
                label = chr(64 + label_counter) if label_counter <= 26 else str(label_counter)

                margins: list[float] = []
                for sensor in sensor_nodes:
                    node_tx = sensor.model_copy(update={
                        "tx_power_dbm": tx_power,
                        "rx_sensitivity_dbm": sensitivity,
                    })
                    node_gw = gateway_node.model_copy(update={
                        "rx_sensitivity_dbm": sensitivity,
                    })
                    result = compute_link_full(node_tx, node_gw, freq_hz, antenna_a=tx_ant, antenna_b=gw_ant)
                    margins.append(result.link_margin_db)

                rows.append(ComparisonRow(
                    scenario_label=label,
                    module_id=module.id,
                    tx_antenna_type=tx_ant.type,
                    gw_antenna_type=gw_ant.type,
                    min_margin_db=min(margins),
                    mean_margin_db=sum(margins) / len(margins),
                    max_margin_db=max(margins),
                    failure_count=sum(1 for m in margins if m < 0),
                    critical_count=sum(1 for m in margins if 0 <= m < 5),
                    comfortable_count=sum(1 for m in margins if m >= 10),
                    robustness_score=_compute_robustness(margins, tx_ant.type),
                    link_margins=margins,
                ))

    rows.sort(key=lambda r: r.min_margin_db, reverse=True)
    return rows
