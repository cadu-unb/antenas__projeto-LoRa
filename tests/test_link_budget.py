"""
Link budget tests with documented reference fixtures.

FSPL reference:
  d = 1000 m, f = 915 MHz → FSPL = 20·log10(4π·1000·915e6/3e8) ≈ 91.68 dB

Geodesic reference:
  A = (0°, 0°), B = (1°, 0°) → d ≈ 111_195 m  (1 degree latitude at equator)

Azimuth references:
  A=(0,0) → B=(1,0): North → 0°
  A=(0,0) → B=(0,1): East  → 90°
"""

import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.domain.link_budget import (
    bearing,
    compute_link,
    elevation_angle,
    feasibility,
    fspl_db,
    haversine,
)
from backend.app.main import app

client = TestClient(app)

DATA_DIR = Path("backend/data/scenarios")


# ── Pure function tests ────────────────────────────────────────────────────────

def test_fspl_1km_915mhz():
    result = fspl_db(1000, 915e6)
    assert abs(result - 91.68) < 0.5, f"FSPL expected ~91.68 dB, got {result:.2f}"


def test_fspl_grows_with_distance():
    assert fspl_db(2000, 915e6) > fspl_db(1000, 915e6)


def test_fspl_grows_with_frequency():
    assert fspl_db(1000, 2400e6) > fspl_db(1000, 915e6)


def test_haversine_one_degree_latitude():
    d = haversine(0, 0, 1, 0)
    assert abs(d - 111_195) / 111_195 < 0.01, f"Expected ~111195 m, got {d:.1f}"


def test_haversine_symmetry():
    d1 = haversine(0, 0, 1, 1)
    d2 = haversine(1, 1, 0, 0)
    assert abs(d1 - d2) < 0.1


def test_haversine_zero_distance():
    assert haversine(10, 20, 10, 20) == 0.0


def test_bearing_north():
    az = bearing(0, 0, 1, 0)
    assert abs(az - 0.0) < 0.01 or abs(az - 360.0) < 0.01, f"Expected 0°, got {az:.2f}"


def test_bearing_east():
    az = bearing(0, 0, 0, 1)
    assert abs(az - 90.0) < 0.1, f"Expected 90°, got {az:.2f}"


def test_bearing_range():
    az = bearing(-15.78, -47.93, -15.84, -48.05)
    assert 0 <= az < 360


def test_elevation_flat():
    assert elevation_angle(10000, 10, 10) == 0.0


def test_elevation_upward():
    assert elevation_angle(1000, 0, 100) > 0


def test_elevation_downward():
    assert elevation_angle(1000, 100, 0) < 0


def test_compute_link_isotropic():
    rx_p, margin = compute_link(14, 0, 0, 91.68, 0, 0, -137)
    assert abs(rx_p - (14 - 91.68)) < 0.01
    assert abs(margin - (rx_p - (-137))) < 0.01


def test_feasibility_verde():
    assert feasibility(15) == "verde"
    assert feasibility(10.1) == "verde"


def test_feasibility_amarelo():
    assert feasibility(10) == "amarelo"
    assert feasibility(0) == "amarelo"


def test_feasibility_vermelho():
    assert feasibility(-0.1) == "vermelho"
    assert feasibility(-20) == "vermelho"


# ── API tests ──────────────────────────────────────────────────────────────────

SCENARIO_PAYLOAD = {
    "name": "Teste Plano Piloto a Taguatinga",
    "node_a": {
        "name": "Plano Piloto",
        "lat": -15.7801,
        "lon": -47.9292,
        "height_m": 10.0,
        "tx_power_dbm": 20.0,
        "rx_sensitivity_dbm": -137.0,
        "cable_loss_db": 0.0,
    },
    "node_b": {
        "name": "Taguatinga",
        "lat": -15.8300,
        "lon": -48.0500,
        "height_m": 10.0,
        "tx_power_dbm": 14.0,
        "rx_sensitivity_dbm": -137.0,
        "cable_loss_db": 0.0,
    },
    "frequency_hz": 915_000_000.0,
}


def _cleanup(id_: str):
    (DATA_DIR / f"{id_}.json").unlink(missing_ok=True)


def test_create_scenario_returns_201():
    r = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    assert r.status_code == 201
    _cleanup(r.json()["id"])


def test_create_scenario_has_id():
    r = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    assert "id" in r.json()
    _cleanup(r.json()["id"])


def test_get_scenario_returns_200():
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.get(f"/api/v1/scenarios/{id_}")
    assert r2.status_code == 200
    _cleanup(id_)


def test_get_unknown_scenario_404():
    r = client.get("/api/v1/scenarios/does-not-exist")
    assert r.status_code == 404


def test_calculate_returns_link_result():
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/calculate")
    assert r2.status_code == 200
    d = r2.json()
    assert "distance_m" in d
    assert "fspl_db" in d
    assert "link_margin_db" in d
    assert "feasibility" in d
    _cleanup(id_)


def test_calculate_fspl_tolerance():
    """Plano Piloto → Taguatinga ~14 km, 915 MHz. FSPL ~114 dB."""
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/calculate")
    result = r2.json()
    expected_fspl = fspl_db(result["distance_m"], 915e6)
    assert abs(result["fspl_db"] - expected_fspl) < 0.5
    _cleanup(id_)


def test_calculate_distance_plano_taguatinga():
    """Plano Piloto → Taguatinga great-circle ≈ 14 km."""
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/calculate")
    d_m = r2.json()["distance_m"]
    assert 12_000 < d_m < 16_000, f"Expected ~14 km, got {d_m/1000:.1f} km"
    _cleanup(id_)


def test_calculate_saves_results_to_scenario():
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    client.post(f"/api/v1/scenarios/{id_}/calculate")
    r3 = client.get(f"/api/v1/scenarios/{id_}")
    assert r3.json()["results"] is not None
    _cleanup(id_)


def test_feasibility_in_result():
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/calculate")
    feas = r2.json()["feasibility"]
    assert feas in ("verde", "amarelo", "vermelho")
    _cleanup(id_)


def test_create_invalid_scenario_422():
    r = client.post("/api/v1/scenarios", json={"name": "sem nós"})
    assert r.status_code == 422
