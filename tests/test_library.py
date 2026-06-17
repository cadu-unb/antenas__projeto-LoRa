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
