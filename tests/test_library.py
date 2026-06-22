from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

DATA_DIR = Path("backend/data/antenna_specs")

VALID_SPEC = {
    "name": "Dipolo Meia Onda",
    "type": "dipolo",
    "frequency_hz": 915_000_000.0,
    "units": {"frequency": "Hz", "gain": "dBi", "impedance": "Ohm"},
    "geometry": {"length_m": 0.164, "diameter_mm": 1.5},
    "material": {"conductor": "cobre", "conductivity": 5.8e7},
    "solver": "rapido",
    "results": None,
    "metadata": {},
}

INVALID_SPEC = {
    "name": "Sem frequência",
    # missing: type, frequency_hz
}


def _cleanup(id_: str):
    (DATA_DIR / f"{id_}.json").unlink(missing_ok=True)


def test_post_valid_returns_201():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert data["name"] == VALID_SPEC["name"]
    _cleanup(data["id"])


def test_post_invalid_returns_422():
    r = client.post("/api/v1/antennas", json=INVALID_SPEC)
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body


def test_get_list_returns_array():
    r = client.get("/api/v1/antennas")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_by_id_returns_spec():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    id_ = r.json()["id"]
    r2 = client.get(f"/api/v1/antennas/{id_}")
    assert r2.status_code == 200
    assert r2.json()["id"] == id_
    _cleanup(id_)


def test_get_unknown_id_returns_404():
    r = client.get("/api/v1/antennas/nao-existe-id")
    assert r.status_code == 404


def test_delete_removes_file():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    id_ = r.json()["id"]
    path = DATA_DIR / f"{id_}.json"
    assert path.exists()
    r2 = client.delete(f"/api/v1/antennas/{id_}")
    assert r2.status_code == 204
    assert not path.exists()


def test_spec_saved_to_disk():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    id_ = r.json()["id"]
    path = DATA_DIR / f"{id_}.json"
    assert path.exists()
    _cleanup(id_)


# ── Schema v2 — new physical fields ──────────────────────────────────────────

SPEC_WITH_PHYSICAL_FIELDS = {
    "name": "Commercial Omni 6dBi",
    "type": "commercial_omni_6dbi",
    "frequency_hz": 915_000_000.0,
    "gmax_dbi": 6.0,
    "hpbw_deg": 35.0,
    "polarization": "linear vertical",
    "is_directional": False,
    "pattern_model": "omni_colinear",
    "practicality_score": 9.0,
    "multi_direction_score": 8.0,
    "notes": "Kit E220-900T22D reference antenna",
}


def test_post_with_physical_fields_returns_201():
    r = client.post("/api/v1/antennas", json=SPEC_WITH_PHYSICAL_FIELDS)
    assert r.status_code == 201
    _cleanup(r.json()["id"])


def test_physical_fields_preserved_on_save_and_load():
    r = client.post("/api/v1/antennas", json=SPEC_WITH_PHYSICAL_FIELDS)
    id_ = r.json()["id"]
    r2 = client.get(f"/api/v1/antennas/{id_}")
    data = r2.json()
    assert data["gmax_dbi"] == 6.0
    assert data["hpbw_deg"] == 35.0
    assert data["polarization"] == "linear vertical"
    assert data["is_directional"] is False
    assert data["pattern_model"] == "omni_colinear"
    assert data["practicality_score"] == 9.0
    assert data["multi_direction_score"] == 8.0
    assert data["notes"] == "Kit E220-900T22D reference antenna"
    _cleanup(id_)


def test_schema_version_bumped_to_2_when_physical_fields_present():
    r = client.post("/api/v1/antennas", json=SPEC_WITH_PHYSICAL_FIELDS)
    assert r.json()["schema_version"] == "2.0"
    _cleanup(r.json()["id"])


def test_schema_version_stays_1_for_old_spec():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    assert r.json()["schema_version"] == "1.0"
    _cleanup(r.json()["id"])


def test_old_spec_without_physical_fields_loads():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    id_ = r.json()["id"]
    r2 = client.get(f"/api/v1/antennas/{id_}")
    assert r2.status_code == 200
    data = r2.json()
    assert data["gmax_dbi"] is None
    assert data["hpbw_deg"] is None
    assert data["notes"] == ""
    _cleanup(id_)


def test_hpbw_zero_rejected():
    spec = {**SPEC_WITH_PHYSICAL_FIELDS, "hpbw_deg": 0.0}
    r = client.post("/api/v1/antennas", json=spec)
    assert r.status_code == 422


def test_hpbw_negative_rejected():
    spec = {**SPEC_WITH_PHYSICAL_FIELDS, "hpbw_deg": -10.0}
    r = client.post("/api/v1/antennas", json=spec)
    assert r.status_code == 422


def test_practicality_score_out_of_range_rejected():
    spec = {**SPEC_WITH_PHYSICAL_FIELDS, "practicality_score": 11.0}
    r = client.post("/api/v1/antennas", json=spec)
    assert r.status_code == 422


def test_multi_direction_score_negative_rejected():
    spec = {**SPEC_WITH_PHYSICAL_FIELDS, "multi_direction_score": -1.0}
    r = client.post("/api/v1/antennas", json=spec)
    assert r.status_code == 422


def test_physical_fields_are_optional():
    r = client.post("/api/v1/antennas", json=VALID_SPEC)
    assert r.status_code == 201
    _cleanup(r.json()["id"])
