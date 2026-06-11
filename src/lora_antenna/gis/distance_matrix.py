"""Distance matrix calculation for KML/GIS nodes."""

from __future__ import annotations

from collections.abc import Iterable

from lora_antenna.gis.geodesic import geodesic_distance_m
from lora_antenna.models.geo import GeographicPosition

DistanceMatrix = dict[tuple[str, str], float]


def compute_distance_matrix(
    positions: Iterable[GeographicPosition],
    *,
    precision_m: int = 1,
) -> DistanceMatrix:
    """Compute the upper-triangular 2D distance matrix for positions."""
    points = list(positions)
    matrix: DistanceMatrix = {}

    for i, origin in enumerate(points):
        for destination in points[i + 1 :]:
            matrix[(origin.label, destination.label)] = round(
                geodesic_distance_m(origin, destination),
                precision_m,
            )

    return matrix


def distance_for_pair(
    matrix: DistanceMatrix,
    origin_label: str,
    dest_label: str,
) -> float:
    """Return a matrix distance regardless of tuple orientation."""
    if (origin_label, dest_label) in matrix:
        return matrix[(origin_label, dest_label)]
    if (dest_label, origin_label) in matrix:
        return matrix[(dest_label, origin_label)]
    raise KeyError(f"Distance not found for pair {origin_label}->{dest_label}.")
