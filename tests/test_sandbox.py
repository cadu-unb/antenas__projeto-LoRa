import time

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

BASE_DIPOLO = {
    "type": "dipolo",
    "frequency_hz": 915_000_000.0,
    "geometry": {"length_m": 0.164},
}

BASE_MONOPOLO = {
    "type": "monopolo",
    "frequency_hz": 915_000_000.0,
    "geometry": {"height_m": 0.082},
}

BASE_HELIX_AXIAL = {
    "type": "helicoidal",
    "frequency_hz": 2_400_000_000.0,
    "geometry": {"turns": 10, "circumference_m": 0.125, "pitch_angle_deg": 14},
}

BASE_PARABOLICA = {
    "type": "parabolica",
    "frequency_hz": 2_400_000_000.0,
    "geometry": {"diameter_m": 0.6, "focal_length_m": 0.22},
}


def test_preview_dipolo_returns_200():
    r = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    assert r.status_code == 200


def test_preview_dipolo_fields():
    r = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    d = r.json()
    assert "gain_dbi" in d
    assert "impedance_ohm" in d
    assert "swr" in d
    assert "efficiency_pct" in d
    assert "pattern_data" in d
    assert len(d["pattern_data"]) == 360


def test_preview_dipolo_half_wave_gain():
    r = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    gain = r.json()["gain_dbi"]
    # Half-wave dipole: ≈ 2.15 dBi. Accept ±1 dBi for analytic approximation.
    assert 1.0 <= gain <= 3.0


def test_preview_dipolo_half_wave_impedance():
    r = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    z = r.json()["impedance_ohm"]
    assert 50.0 <= z <= 100.0


def test_preview_monopolo_gain_higher_than_dipolo():
    r_dipolo = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    r_mono   = client.post("/api/v1/sandbox/preview", json=BASE_MONOPOLO)
    assert r_mono.json()["gain_dbi"] > r_dipolo.json()["gain_dbi"]


def test_preview_helicoidal_axial_directional():
    r = client.post("/api/v1/sandbox/preview", json=BASE_HELIX_AXIAL)
    d = r.json()
    assert d["gain_dbi"] > 5.0
    assert "axial" in d["radiation_pattern"]


def test_preview_parabolica_high_gain():
    r = client.post("/api/v1/sandbox/preview", json=BASE_PARABOLICA)
    d = r.json()
    assert d["gain_dbi"] > 10.0


def test_preview_unknown_type_returns_fixture():
    r = client.post("/api/v1/sandbox/preview", json={
        "type": "yagi",
        "frequency_hz": 915_000_000.0,
    })
    assert r.status_code == 200
    assert r.json()["is_fixture"] is True


def test_preview_missing_required_returns_422():
    r = client.post("/api/v1/sandbox/preview", json={"name": "Teste"})
    assert r.status_code == 422


def test_preview_responds_under_2s():
    start = time.monotonic()
    r = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    elapsed = time.monotonic() - start
    assert r.status_code == 200
    assert elapsed < 2.0


def test_preview_pattern_data_normalized():
    r = client.post("/api/v1/sandbox/preview", json=BASE_DIPOLO)
    pts = r.json()["pattern_data"]
    max_g = max(p["gain_linear"] for p in pts)
    assert max_g > 0


def test_preview_swr_positive():
    for body in [BASE_DIPOLO, BASE_MONOPOLO, BASE_PARABOLICA]:
        r = client.post("/api/v1/sandbox/preview", json=body)
        assert r.json()["swr"] >= 1.0
