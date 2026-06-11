"""Simplified 2D ray tracing against campus obstacle polygons."""

from __future__ import annotations

from collections.abc import Sequence

from shapely.geometry import LineString, Polygon

from lora_antenna.gis.kml_parser import KMLPolygon, KMLPolygonRole

OBSTACLE_ROLES = {KMLPolygonRole.BUILDING, KMLPolygonRole.OBSTACLE}


def count_buildings_crossed(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    buildings: Sequence[KMLPolygon],
) -> int:
    """Count building/obstacle polygons crossed by a 2D line of sight."""
    line = LineString([(lon1, lat1), (lon2, lat2)])
    count = 0

    for building in buildings:
        if building.role not in OBSTACLE_ROLES:
            continue

        polygon = Polygon(building.exterior_ring)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        if polygon.is_empty:
            continue

        if line.crosses(polygon) or line.within(polygon) or line.intersects(polygon):
            count += 1

    return count


def building_attenuation_db(
    n_buildings: int,
    nominal_db_per_building: float = 15.0,
) -> float:
    """Return cumulative building attenuation in dB."""
    if n_buildings < 0:
        raise ValueError("n_buildings must be non-negative.")
    if nominal_db_per_building < 0:
        raise ValueError("nominal_db_per_building must be non-negative.")
    return n_buildings * nominal_db_per_building
