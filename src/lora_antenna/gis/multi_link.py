"""Batch orchestration for geographic multi-node LoRa links."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    distance_for_pair,
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
from lora_antenna.propagation.friis import (
    LinkRisk,
    classify_link_risk,
    friis_received_power_dbm,
    fspl_db,
    link_margin_db,
)
from lora_antenna.propagation.interference import sir_db, sir_is_decodable


class LinkPair(BaseModel):
    """Directed pair ready for scalar RF calculation."""

    model_config = ConfigDict(frozen=True)

    origin_label: str
    dest_label: str
    distance_m: float

    @model_validator(mode="after")
    def validate_pair(self) -> "LinkPair":
        if self.origin_label == self.dest_label:
            raise ValueError("origin_label and dest_label must be different.")
        if self.distance_m <= 0:
            raise ValueError("distance_m must be positive.")
        return self


class LinkBatchRequest(BaseModel):
    """Batch request crossing the GIS-to-propagation boundary."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    pairs: list[LinkPair]
    antenna: Antenna
    tx_power_dbm: float = DEFAULT_TX_POWER_DBM
    frequency_hz: float = LORA_DEFAULT_HZ
    rx_sensitivity_dbm: float = DEFAULT_RX_SENSITIVITY_DBM
    extra_losses_db: float = 0.0
    sf: int = 12

    @field_validator("frequency_hz")
    @classmethod
    def validate_frequency(cls, value: float) -> float:
        return validate_lora_br_frequency_hz(value)

    @field_validator("extra_losses_db")
    @classmethod
    def validate_extra_losses(cls, value: float) -> float:
        if value < 0:
            raise ValueError("extra_losses_db must be non-negative.")
        return value

    @field_validator("sf")
    @classmethod
    def validate_sf(cls, value: int) -> int:
        if value < 7 or value > 12:
            raise ValueError("sf must be between 7 and 12.")
        return value

    @model_validator(mode="after")
    def validate_request(self) -> "LinkBatchRequest":
        if not self.pairs:
            raise ValueError("LinkBatchRequest requires at least one pair.")
        return self


class LinkBatchResult(BaseModel):
    """Result for one directed link in a multi-node topology."""

    model_config = ConfigDict(frozen=True)

    origin_label: str
    dest_label: str
    distance_m: float
    distance_3d_m: float
    fspl_db: float
    extra_loss_db: float
    received_power_dbm: float
    link_margin_db: float
    link_risk: LinkRisk
    sir_db: Optional[float] = None
    sir_decodable: Optional[bool] = None
    interferer_labels: list[str] = Field(default_factory=list)
    n_buildings_crossed: int = 0


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
    """Run Friis, 2D obstacle loss, 3D distance, and SIR for all links.

    Block 1 functions receive only scalar values. All KML, polygons, altitude,
    and ray-tracing concerns remain inside this GIS orchestration layer.
    """
    if len(doc.points) < 2:
        raise ValueError("At least two KML points are required for batch links.")

    validate_lora_br_frequency_hz(frequency_hz)
    matrix = distance_matrix or compute_distance_matrix(doc.positions())
    obstacle_polygons = _default_obstacles(doc, buildings)
    pairs = _build_pairs(doc.points, matrix, directed=directed)
    request = LinkBatchRequest(
        pairs=pairs,
        antenna=antenna,
        tx_power_dbm=tx_power_dbm,
        frequency_hz=frequency_hz,
        rx_sensitivity_dbm=rx_sensitivity_dbm,
        extra_losses_db=extra_losses_db,
        sf=sf,
    )

    raw_results: list[LinkBatchResult] = []
    for pair in request.pairs:
        origin = _require_point(doc, pair.origin_label)
        destination = _require_point(doc, pair.dest_label)

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
        total_extra_loss_db = request.extra_losses_db + obstacle_loss_db
        d3_m = distance_3d_m(origin, destination, pair.distance_m)

        path_loss_db = fspl_db(d3_m, request.frequency_hz)
        received_power_dbm = friis_received_power_dbm(
            tx_power_dbm=request.tx_power_dbm,
            tx_gain_dbi=request.antenna.gain_dbi,
            rx_gain_dbi=request.antenna.gain_dbi,
            fspl_db=path_loss_db,
            losses_db=total_extra_loss_db + request.antenna.losses_db,
        )
        margin_db = link_margin_db(
            received_power_dbm,
            request.rx_sensitivity_dbm,
        )

        raw_results.append(
            LinkBatchResult(
                origin_label=pair.origin_label,
                dest_label=pair.dest_label,
                distance_m=round(pair.distance_m, 1),
                distance_3d_m=round(d3_m, 1),
                fspl_db=round(path_loss_db, 2),
                extra_loss_db=round(total_extra_loss_db, 2),
                received_power_dbm=round(received_power_dbm, 2),
                link_margin_db=round(margin_db, 2),
                link_risk=classify_link_risk(
                    received_power_dbm,
                    request.rx_sensitivity_dbm,
                ),
                n_buildings_crossed=n_buildings,
            )
        )

    return _with_sir(raw_results, sf=request.sf)


def results_to_sir_matrix(
    results: Sequence[LinkBatchResult],
) -> dict[tuple[str, str], float]:
    """Return {(origin, destination): sir_db} for results with SIR."""
    return {
        (result.origin_label, result.dest_label): result.sir_db
        for result in results
        if result.sir_db is not None
    }


def _build_pairs(
    points: Sequence[KMLPoint],
    matrix: Mapping[tuple[str, str], float],
    *,
    directed: bool,
) -> list[LinkPair]:
    pairs: list[LinkPair] = []
    for i, origin in enumerate(points):
        for j, destination in enumerate(points):
            if i == j:
                continue
            if not directed and j <= i:
                continue
            pairs.append(
                LinkPair(
                    origin_label=origin.label,
                    dest_label=destination.label,
                    distance_m=distance_for_pair(
                        dict(matrix),
                        origin.label,
                        destination.label,
                    ),
                )
            )
    return pairs


def _default_obstacles(
    doc: KMLDocument,
    buildings: Sequence[KMLPolygon] | None,
) -> list[KMLPolygon]:
    if buildings is not None:
        return list(buildings)
    return doc.polygons_by_role(KMLPolygonRole.BUILDING, KMLPolygonRole.OBSTACLE)


def _require_point(doc: KMLDocument, label: str) -> KMLPoint:
    point = doc.get_point(label)
    if point is None:
        raise KeyError(f"KML point not found: {label}")
    return point


def _with_sir(results: Sequence[LinkBatchResult], sf: int) -> list[LinkBatchResult]:
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
