"""Distance matrix calculation for KML/GIS nodes."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Optional

from pydantic import BaseModel, ConfigDict

from lora_antenna.gis.geodesic import geodesic_distance_m
from lora_antenna.models.geo import GeographicPosition


class DistanceMatrixEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    origin_label: str
    dest_label: str
    distance_m: float
    method: str = "WGS84_GEODESIC"
    delta_reference_m: Optional[float] = None


class DistanceMatrix(BaseModel):
    model_config = ConfigDict(frozen=True)

    entries: list[DistanceMatrixEntry]

    def to_dict(self) -> dict[tuple[str, str], float]:
        """Legacy dict for code that still expects dict[tuple[str, str], float]."""
        return {(e.origin_label, e.dest_label): e.distance_m for e in self.entries}

    def get_distance(self, origin_label: str, dest_label: str) -> float:
        """Return distance regardless of pair orientation."""
        for entry in self.entries:
            if (
                entry.origin_label == origin_label
                and entry.dest_label == dest_label
            ) or (
                entry.origin_label == dest_label
                and entry.dest_label == origin_label
            ):
                return entry.distance_m
        raise KeyError(f"Distance not found for pair {origin_label}->{dest_label}.")

    def with_reference_delta(
        self,
        reference_table: dict[tuple[str, str], float],
    ) -> "DistanceMatrix":
        """Return new DistanceMatrix with delta_reference_m filled from reference_table."""
        updated: list[DistanceMatrixEntry] = []
        for entry in self.entries:
            pair_key: tuple[str, str] = (
                (entry.origin_label, entry.dest_label)
                if entry.origin_label <= entry.dest_label
                else (entry.dest_label, entry.origin_label)
            )
            ref_dist = reference_table.get(pair_key)
            delta = round(entry.distance_m - ref_dist, 1) if ref_dist is not None else None
            updated.append(entry.model_copy(update={"delta_reference_m": delta}))
        return DistanceMatrix(entries=updated)


def compute_distance_matrix(
    positions: Iterable[GeographicPosition],
    *,
    precision_m: int = 1,
) -> DistanceMatrix:
    """Compute upper-triangular WGS84 geodesic distance matrix for positions."""
    points = list(positions)
    entries: list[DistanceMatrixEntry] = []

    for i, origin in enumerate(points):
        for destination in points[i + 1 :]:
            entries.append(
                DistanceMatrixEntry(
                    origin_label=origin.label,
                    dest_label=destination.label,
                    distance_m=round(
                        geodesic_distance_m(origin, destination),
                        precision_m,
                    ),
                )
            )

    return DistanceMatrix(entries=entries)


def distance_for_pair(
    matrix: DistanceMatrix,
    origin_label: str,
    dest_label: str,
) -> float:
    """Return a matrix distance regardless of pair orientation."""
    return matrix.get_distance(origin_label, dest_label)
