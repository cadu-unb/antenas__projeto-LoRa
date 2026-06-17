"""Analytic link budget calculations — pure functions, no I/O."""
from __future__ import annotations

import math

EARTH_R = 6_371_000.0  # mean radius in meters
C = 3e8  # m/s


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in meters (Haversine formula)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial bearing from point A to point B in degrees [0, 360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def elevation_angle(distance_m: float, height_a: float, height_b: float) -> float:
    """Elevation angle in degrees from A looking toward B."""
    if distance_m <= 0:
        return 90.0
    return math.degrees(math.atan2(height_b - height_a, distance_m))


def fspl_db(distance_m: float, frequency_hz: float) -> float:
    """Free Space Path Loss in dB.

    FSPL = 20·log10(4π·d·f / c)
    """
    if distance_m <= 0:
        return 0.0
    return 20 * math.log10(4 * math.pi * distance_m * frequency_hz / C)


def compute_link(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    tx_cable_db: float,
    path_loss_db: float,
    rx_gain_dbi: float,
    rx_cable_db: float,
    rx_sensitivity_dbm: float,
) -> tuple[float, float]:
    """Return (rx_power_dbm, link_margin_db)."""
    rx_power = (
        tx_power_dbm
        + tx_gain_dbi
        - tx_cable_db
        - path_loss_db
        - rx_cable_db
        + rx_gain_dbi
    )
    return rx_power, rx_power - rx_sensitivity_dbm


def feasibility(margin_db: float) -> str:
    if margin_db > 10:
        return "verde"
    if margin_db >= 0:
        return "amarelo"
    return "vermelho"


def find_islands(all_node_ids: list[str], links: list) -> list[str]:
    """Return node IDs that appear in no link."""
    connected: set[str] = set()
    for edge in links:
        connected.add(edge.node_a_id)
        connected.add(edge.node_b_id)
    return [nid for nid in all_node_ids if nid not in connected]


def best_path_margin(target_node_id: str, hops: list) -> float | None:
    """Return best (highest) link_margin_db among all hops ending at target_node_id."""
    margins = [
        h.link_margin_db for h in hops
        if h.node_b_id == target_node_id or h.node_a_id == target_node_id
    ]
    return max(margins) if margins else None
