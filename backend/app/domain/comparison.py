"""Framework de comparação de cenários: módulo × antena_TX × antena_GW."""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from ..schemas.antenna_spec import AntennaSpec
from ..schemas.lora_module import LoRaModule
from ..schemas.node_spec import NodeSpec

# Fallback type set for specs without is_directional (backward compat only)
_DIRECTIONAL_FALLBACK = {"helicoidal", "parabolica"}


def _get_ant_field(antenna: object, field_name: str, fallback=None):
    """Get field from antenna object, filling from preset if AntennaSpec.

    Accepts: AntennaSpec, type string, SimpleNamespace, or None.
    """
    if antenna is None:
        return fallback
    if isinstance(antenna, str):
        from ..domain.antenna_presets import ANTENNA_PRESETS
        return ANTENNA_PRESETS.get(antenna.lower(), {}).get(field_name, fallback)
    if hasattr(antenna, "model_dump"):
        from ..domain.antenna_presets import apply_antenna_defaults
        filled = apply_antenna_defaults(antenna).spec
        return getattr(filled, field_name, fallback)
    return getattr(antenna, field_name, fallback)


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
    practicality_score: float = 0.0   # avg(tx_prac, gw_prac) from preset/spec
    aggregate_score: float = 0.0      # robustness + practicality contribution
    scores_source: str = "fallback"   # "preset" | "spec" | "fallback"
    link_margins: list[float] = field(default_factory=list)


def _compute_robustness(margins: list[float], tx_antenna: object, gw_antenna: object = None) -> float:
    """Compute robustness score.

    Penalties:
    - TX directional + high margin variance (std > 10): multiply by 0.5
    - GW multi_direction_score: scale by score/10 (penalizes directional GW in multi-sensor)

    Falls back to _DIRECTIONAL_FALLBACK type set when is_directional field absent.
    """
    mean_m = statistics.mean(margins)
    std_m = statistics.stdev(margins) if len(margins) > 1 else 0.0
    base = mean_m / (std_m + 1.0)

    # TX directional penalty
    tx_is_dir = _get_ant_field(tx_antenna, "is_directional", None)
    if tx_is_dir is None:
        tx_type = tx_antenna if isinstance(tx_antenna, str) else getattr(tx_antenna, "type", "")
        tx_is_dir = tx_type in _DIRECTIONAL_FALLBACK
    dir_penalty = 0.5 if tx_is_dir and std_m > 10.0 else 1.0

    # GW multi-direction factor: low score = bad for multi-azimuth coverage
    gw_mds = _get_ant_field(gw_antenna, "multi_direction_score", None)
    mds_factor = (gw_mds / 10.0) if gw_mds is not None else 1.0

    return base * dir_penalty * mds_factor


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

                rob = _compute_robustness(margins, tx_ant, gw_ant)

                tx_prac = _get_ant_field(tx_ant, "practicality_score", None)
                gw_prac = _get_ant_field(gw_ant, "practicality_score", None)
                if tx_prac is not None and gw_prac is not None:
                    prac = (tx_prac + gw_prac) / 2.0
                    scores_src = "preset"
                elif tx_prac is not None or gw_prac is not None:
                    prac = (tx_prac or 0.0) + (gw_prac or 0.0)
                    scores_src = "spec"
                else:
                    prac = 0.0
                    scores_src = "fallback"

                agg = rob + prac * 0.5

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
                    robustness_score=rob,
                    practicality_score=prac,
                    aggregate_score=agg,
                    scores_source=scores_src,
                    link_margins=margins,
                ))

    rows.sort(key=lambda r: r.min_margin_db, reverse=True)
    return rows
