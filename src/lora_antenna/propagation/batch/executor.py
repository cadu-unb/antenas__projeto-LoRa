"""Pure RF batch executor — Bloco 1, no GIS dependencies."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from lora_antenna.propagation.batch.contracts import (
    LinkBatchRequest,
    LinkBatchResult,
)
from lora_antenna.propagation.friis import (
    classify_link_risk,
    friis_received_power_dbm,
    fspl_db,
    link_margin_db,
)
from lora_antenna.propagation.interference import sir_db, sir_is_decodable


def execute_link_batch(request: LinkBatchRequest) -> list[LinkBatchResult]:
    """Compute Friis + SIR for all scalar link inputs.

    Receives only scalars — no KML, no lat/lon, no Shapely, no SRTM.
    """
    raw: list[LinkBatchResult] = []
    for inp in request.pairs:
        path_loss_db = fspl_db(inp.distance_3d_m, request.frequency_hz)
        rx_power_dbm = friis_received_power_dbm(
            tx_power_dbm=request.tx_power_dbm,
            tx_gain_dbi=request.antenna.gain_dbi,
            rx_gain_dbi=request.antenna.gain_dbi,
            fspl_db=path_loss_db,
            losses_db=inp.total_extra_loss_db + request.antenna.losses_db,
        )
        margin_db = link_margin_db(rx_power_dbm, request.rx_sensitivity_dbm)

        raw.append(
            LinkBatchResult(
                origin_label=inp.origin_label,
                dest_label=inp.dest_label,
                distance_m=round(inp.distance_m, 1),
                distance_3d_m=round(inp.distance_3d_m, 1),
                fspl_db=round(path_loss_db, 2),
                extra_loss_db=round(inp.total_extra_loss_db, 2),
                received_power_dbm=round(rx_power_dbm, 2),
                link_margin_db=round(margin_db, 2),
                link_risk=classify_link_risk(rx_power_dbm, request.rx_sensitivity_dbm),
                feasible=margin_db > 0.0,
                n_buildings_crossed=inp.n_buildings_crossed,
            )
        )

    return _with_sir(raw, sf=request.sf)


def _with_sir(
    results: Sequence[LinkBatchResult],
    sf: int,
) -> list[LinkBatchResult]:
    by_destination: dict[str, list[LinkBatchResult]] = defaultdict(list)
    for result in results:
        by_destination[result.dest_label].append(result)

    updated: list[LinkBatchResult] = []
    for result in results:
        interferers = [
            other
            for other in by_destination[result.dest_label]
            if other.origin_label != result.origin_label
        ]
        interferer_powers = [item.received_power_dbm for item in interferers]
        interferer_labels = [item.origin_label for item in interferers]

        if interferer_powers:
            sir_value_db = sir_db(result.received_power_dbm, interferer_powers)
            updated.append(
                result.model_copy(
                    update={
                        "sir_db": round(sir_value_db, 2),
                        "sir_decodable": sir_is_decodable(sir_value_db, sf=sf),
                        "interferer_labels": interferer_labels,
                    }
                )
            )
        else:
            updated.append(
                result.model_copy(
                    update={
                        "sir_db": float("inf"),
                        "sir_decodable": True,
                        "interferer_labels": [],
                    }
                )
            )

    return sorted(
        updated,
        key=lambda item: (
            item.sir_decodable is True,
            item.link_margin_db,
            item.sir_db if item.sir_db is not None else float("-inf"),
        ),
        reverse=True,
    )
