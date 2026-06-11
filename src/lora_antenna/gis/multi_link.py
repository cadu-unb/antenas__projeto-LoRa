"""Batch orchestration for geographic multi-node LoRa links."""

from __future__ import annotations

from collections.abc import Sequence

from lora_antenna.antenna.base import Antenna
from lora_antenna.core.constants import (
    DEFAULT_RX_SENSITIVITY_DBM,
    DEFAULT_TX_POWER_DBM,
    LORA_DEFAULT_HZ,
)
from lora_antenna.core.validators import validate_lora_br_frequency_hz
from lora_antenna.gis.distance_matrix import (
    DistanceMatrix,
    compute_distance_matrix,
)
from lora_antenna.gis.geodesic import distance_3d_m
from lora_antenna.gis.kml_parser import (
    KMLDocument,
    KMLPoint,
    KMLPolygon,
    KMLPolygonRole,
)
from lora_antenna.gis.ray_tracing_2d import (
    building_attenuation_db,
    count_buildings_crossed,
)
from lora_antenna.propagation.batch import (
    LinkBatchRequest,
    LinkBatchResult,
    ScalarLinkInput,
    execute_link_batch,
)


def run_link_budget_batch(
    doc: KMLDocument,
    antenna: Antenna,
    *,
    distance_matrix: DistanceMatrix | None = None,
    tx_power_dbm: float = DEFAULT_TX_POWER_DBM,
    frequency_hz: float = LORA_DEFAULT_HZ,
    rx_sensitivity_dbm: float = DEFAULT_RX_SENSITIVITY_DBM,
    buildings: Sequence[KMLPolygon] | None = None,
    extra_losses_db: float = 0.0,
    nominal_db_per_building: float = 15.0,
    sf: int = 12,
    directed: bool = True,
) -> list[LinkBatchResult]:
    """Orchestrate geographic LoRa batch: KML → scalars → execute_link_batch.

    Block 1 (propagation.batch) receives only scalar values.
    All KML, altitude, and ray-tracing concerns stay here.
    """
    if len(doc.points) < 2:
        raise ValueError("At least two KML points are required for batch links.")

    validate_lora_br_frequency_hz(frequency_hz)

    matrix = distance_matrix or compute_distance_matrix(doc.positions())
    obstacle_polygons = _default_obstacles(doc, buildings)

    scalar_inputs = _build_scalar_inputs(
        doc.points,
        matrix,
        obstacle_polygons,
        extra_losses_db=extra_losses_db,
        nominal_db_per_building=nominal_db_per_building,
        directed=directed,
    )

    request = LinkBatchRequest(
        pairs=scalar_inputs,
        antenna=antenna,
        tx_power_dbm=tx_power_dbm,
        frequency_hz=frequency_hz,
        rx_sensitivity_dbm=rx_sensitivity_dbm,
        sf=sf,
    )

    return execute_link_batch(request)


def results_to_sir_matrix(
    results: Sequence[LinkBatchResult],
) -> dict[tuple[str, str], float]:
    """Return {(origin, destination): sir_db} for results with SIR."""
    return {
        (result.origin_label, result.dest_label): result.sir_db
        for result in results
        if result.sir_db is not None
    }


def _build_scalar_inputs(
    points: Sequence[KMLPoint],
    matrix: DistanceMatrix,
    obstacle_polygons: list[KMLPolygon],
    *,
    extra_losses_db: float,
    nominal_db_per_building: float,
    directed: bool,
) -> list[ScalarLinkInput]:
    inputs: list[ScalarLinkInput] = []
    for i, origin in enumerate(points):
        for j, destination in enumerate(points):
            if i == j:
                continue
            if not directed and j <= i:
                continue

            dist_2d_m = matrix.get_distance(origin.label, destination.label)
            d3_m = distance_3d_m(origin, destination, dist_2d_m)

            n_buildings = count_buildings_crossed(
                origin.latitude,
                origin.longitude,
                destination.latitude,
                destination.longitude,
                obstacle_polygons,
            )
            obstacle_loss_db = building_attenuation_db(
                n_buildings,
                nominal_db_per_building,
            )

            inputs.append(
                ScalarLinkInput(
                    origin_label=origin.label,
                    dest_label=destination.label,
                    distance_m=round(dist_2d_m, 1),
                    distance_3d_m=round(d3_m, 1),
                    total_extra_loss_db=round(extra_losses_db + obstacle_loss_db, 2),
                    n_buildings_crossed=n_buildings,
                )
            )
    return inputs


def _default_obstacles(
    doc: KMLDocument,
    buildings: Sequence[KMLPolygon] | None,
) -> list[KMLPolygon]:
    if buildings is not None:
        return list(buildings)
    return doc.polygons_by_role(KMLPolygonRole.BUILDING, KMLPolygonRole.OBSTACLE)
