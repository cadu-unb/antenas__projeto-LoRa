"""Geodesic utilities for the GIS layer."""

from __future__ import annotations

import math

from lora_antenna.models.geo import GeographicPosition

EARTH_RADIUS_M = 6_371_000.0


def geodesic_distance_m(
    origin: GeographicPosition,
    destination: GeographicPosition,
) -> float:
    """Return WGS84-like surface distance using the Haversine formula."""
    lat1 = math.radians(origin.latitude)
    lat2 = math.radians(destination.latitude)
    dlat = math.radians(destination.latitude - origin.latitude)
    dlon = math.radians(destination.longitude - origin.longitude)

    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_M * c


def distance_3d_m(
    origin: GeographicPosition,
    destination: GeographicPosition,
    distance_2d_m: float | None = None,
) -> float:
    """Return 3D distance using geodesic distance and altitude delta."""
    horizontal_m = (
        geodesic_distance_m(origin, destination)
        if distance_2d_m is None
        else distance_2d_m
    )
    dz_m = destination.effective_altitude_m - origin.effective_altitude_m
    return math.sqrt(horizontal_m**2 + dz_m**2)
