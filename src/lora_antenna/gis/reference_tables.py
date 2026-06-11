"""MATLAB flat-earth reference distances for the P1–P8 test topology.

Derived from _path/mathlab/EnlacesLora.m using the flat-earth approximation:
    dlat_m = (lat2 - lat1) * 111_320
    dlon_m = (lon2 - lon1) * 111_320 * cos(avg_lat_rad)
    d      = sqrt(dlat_m² + dlon_m²)

Python Haversine (WGS84 geodesic) may differ by < 1 m at this urban scale.
"""

from __future__ import annotations

_MATLAB_REFERENCE_M: dict[tuple[str, str], float] = {
    ("P1", "P2"): 399.4,
    ("P1", "P3"): 428.3,
    ("P1", "P4"): 886.5,
    ("P1", "P5"): 660.5,
    ("P1", "P6"): 720.4,
    ("P1", "P7"): 511.9,
    ("P1", "P8"): 604.8,
    ("P2", "P3"): 190.9,
    ("P2", "P4"): 504.4,
    ("P2", "P5"): 336.8,
    ("P2", "P6"): 538.6,
    ("P2", "P7"): 571.5,
    ("P2", "P8"): 927.3,
    ("P3", "P4"): 615.9,
    ("P3", "P5"): 508.2,
    ("P3", "P6"): 729.2,
    ("P3", "P7"): 737.4,
    ("P3", "P8"): 1018.2,
    ("P4", "P5"): 271.4,
    ("P4", "P6"): 507.3,
    ("P4", "P7"): 805.3,
    ("P4", "P8"): 1306.4,
    ("P5", "P6"): 288.8,
    ("P5", "P7"): 536.5,
    ("P5", "P8"): 1036.3,
    ("P6", "P7"): 368.7,
    ("P6", "P8"): 909.9,
    ("P7", "P8"): 541.5,
}


def normalize_pair(origin: str, dest: str) -> tuple[str, str]:
    """Return canonical (lexicographically lower, higher) pair."""
    return (origin, dest) if origin <= dest else (dest, origin)


def reference_distance_m(origin: str, dest: str) -> float:
    """Return MATLAB flat-earth reference distance for pair."""
    key = normalize_pair(origin, dest)
    if key not in _MATLAB_REFERENCE_M:
        raise KeyError(f"No reference distance for pair {origin}->{dest}.")
    return _MATLAB_REFERENCE_M[key]


def delta_reference_m(origin: str, dest: str, computed_distance_m: float) -> float:
    """Return computed − reference in metres (positive = computed longer)."""
    return round(computed_distance_m - reference_distance_m(origin, dest), 1)


def reference_table() -> dict[tuple[str, str], float]:
    """Return a copy of the full MATLAB reference table."""
    return dict(_MATLAB_REFERENCE_M)
