"""Conversão geodésica e vetor ENU para cálculo de azimute/elevação reais."""
from __future__ import annotations

import math
from dataclasses import dataclass

# WGS-84
_a = 6_378_137.0
_f = 1 / 298.257_223_563
_b = _a * (1 - _f)
_e2 = 1 - (_b / _a) ** 2


@dataclass
class ENUVector:
    east_m: float
    north_m: float
    up_m: float

    @property
    def distance_2d(self) -> float:
        return math.sqrt(self.east_m ** 2 + self.north_m ** 2)

    @property
    def distance_3d(self) -> float:
        return math.sqrt(self.east_m ** 2 + self.north_m ** 2 + self.up_m ** 2)

    @property
    def azimuth_deg(self) -> float:
        """Azimute (0=Norte, sentido horário), graus."""
        return math.degrees(math.atan2(self.east_m, self.north_m)) % 360

    @property
    def elevation_deg(self) -> float:
        """Ângulo de elevação acima do horizonte, graus."""
        return math.degrees(math.atan2(self.up_m, self.distance_2d))


def geodetic_to_ecef(lat_deg: float, lon_deg: float, alt_m: float) -> tuple[float, float, float]:
    """Converte lat/lon/alt (graus/metros) para ECEF (X, Y, Z em metros)."""
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    N = _a / math.sqrt(1 - _e2 * math.sin(lat) ** 2)
    x = (N + alt_m) * math.cos(lat) * math.cos(lon)
    y = (N + alt_m) * math.cos(lat) * math.sin(lon)
    z = (N * (1 - _e2) + alt_m) * math.sin(lat)
    return x, y, z


def geodetic_to_enu(
    lat_ref: float, lon_ref: float, alt_ref: float,
    lat_tgt: float, lon_tgt: float, alt_tgt: float,
) -> ENUVector:
    """Vetor ENU do ponto de referência até o ponto alvo. Altitudes em metros."""
    x_r, y_r, z_r = geodetic_to_ecef(lat_ref, lon_ref, alt_ref)
    x_t, y_t, z_t = geodetic_to_ecef(lat_tgt, lon_tgt, alt_tgt)

    dx, dy, dz = x_t - x_r, y_t - y_r, z_t - z_r

    lat = math.radians(lat_ref)
    lon = math.radians(lon_ref)

    east = -math.sin(lon) * dx + math.cos(lon) * dy
    north = (
        -math.sin(lat) * math.cos(lon) * dx
        - math.sin(lat) * math.sin(lon) * dy
        + math.cos(lat) * dz
    )
    up = (
        math.cos(lat) * math.cos(lon) * dx
        + math.cos(lat) * math.sin(lon) * dy
        + math.sin(lat) * dz
    )

    return ENUVector(east, north, up)
