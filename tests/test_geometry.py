"""Testes do módulo de geometria geodésica (ENU)."""
from backend.app.domain.geometry import geodetic_to_enu


def test_enu_distance_matches_haversine_approximately():
    """ENU 2D deve concordar com Haversine em distâncias curtas."""
    enu = geodetic_to_enu(-15.78, -47.93, 0, -15.83, -48.05, 0)
    dist_2d_km = enu.distance_2d / 1000
    assert 12 < dist_2d_km < 15, f"Esperado ~13 km, obtido {dist_2d_km:.2f} km"


def test_enu_azimuth_roughly_west():
    """Ponto a oeste deve ter azimute ~270°."""
    enu = geodetic_to_enu(-15.78, -47.93, 0, -15.78, -48.20, 0)
    assert 250 < enu.azimuth_deg < 290, f"Azimute esperado ~270°, obtido {enu.azimuth_deg:.1f}°"


def test_enu_elevation_positive_for_higher_target():
    """Alvo mais alto deve ter elevação positiva."""
    enu = geodetic_to_enu(-15.78, -47.93, 10, -15.79, -47.94, 100)
    assert enu.elevation_deg > 0, f"Elevação esperada > 0°, obtida {enu.elevation_deg:.4f}°"


def test_enu_azimuth_north():
    """Ponto ao norte deve ter azimute ~0°."""
    enu = geodetic_to_enu(-15.90, -47.93, 0, -15.78, -47.93, 0)
    az = enu.azimuth_deg
    assert az < 10 or az > 350, f"Azimute esperado ~0°, obtido {az:.1f}°"


def test_enu_distance_3d_greater_than_2d_with_altitude_diff():
    """Distância 3D > 2D quando altitudes diferem."""
    enu = geodetic_to_enu(-15.78, -47.93, 5, -15.83, -48.05, 1000)
    assert enu.distance_3d > enu.distance_2d


def test_enu_zero_distance_same_point():
    """Mesmo ponto → distâncias zero."""
    enu = geodetic_to_enu(-15.78, -47.93, 0, -15.78, -47.93, 0)
    assert enu.distance_2d < 1.0
    assert enu.distance_3d < 1.0
