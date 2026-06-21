"""
Testes do endpoint de exportação seletiva de cenários.
GET /api/v1/scenarios/{id}/export
GET /api/v1/scenarios/{id}/export?include_results=true
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

SCENARIO_PAYLOAD = {
    "name": "Exportação Teste",
    "node_a": {
        "name": "Plano Piloto",
        "lat": -15.7801,
        "lon": -47.9292,
        "height_m": 5.0,
        "tx_power_dbm": 20.0,
        "rx_sensitivity_dbm": -137.0,
        "cable_loss_db": 0.0,
    },
    "node_b": {
        "name": "Taguatinga",
        "lat": -15.8300,
        "lon": -48.0500,
        "height_m": 5.0,
        "tx_power_dbm": 14.0,
        "rx_sensitivity_dbm": -137.0,
        "cable_loss_db": 0.0,
    },
    "frequency_hz": 915_000_000.0,
}


def _create_and_calculate():
    r = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    assert r.status_code == 201
    sid = r.json()["id"]
    client.post(f"/api/v1/scenarios/{sid}/calculate")
    return sid


def test_export_setup_returns_200():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export")
    assert r.status_code == 200


def test_export_full_returns_200():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export?include_results=true")
    assert r.status_code == 200


def test_export_setup_excludes_results():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export")
    data = r.json()
    assert "results" not in data
    assert "topology_result" not in data
    assert "site_selection_result" not in data


def test_export_full_includes_results():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export?include_results=true")
    data = r.json()
    # results key must be present (may be non-null after calculate)
    assert "results" in data
    assert data["results"] is not None


def test_export_setup_preserves_nodes():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export")
    data = r.json()
    assert data["node_a"]["name"] == "Plano Piloto"
    assert data["node_b"]["name"] == "Taguatinga"


def test_export_content_disposition_setup():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export")
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "setup" in cd


def test_export_content_disposition_full():
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}/export?include_results=true")
    cd = r.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "completo" in cd


def test_export_unknown_scenario_404():
    r = client.get("/api/v1/scenarios/nao-existe/export")
    assert r.status_code == 404


def test_get_scenario_original_unaffected():
    """GET /{id} original deve retornar tudo incluindo results."""
    sid = _create_and_calculate()
    r = client.get(f"/api/v1/scenarios/{sid}")
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert "topology_result" in data
    assert "site_selection_result" in data


def test_distance_warning_present_for_long_link():
    """Enlace >200 km deve retornar warnings no LinkResult."""
    payload = {
        "name": "Longa distância",
        "node_a": {
            "name": "DF",
            "lat": -15.78, "lon": -47.93,
            "height_m": 5, "tx_power_dbm": 20,
            "rx_sensitivity_dbm": -137, "cable_loss_db": 0,
        },
        "node_b": {
            "name": "Nordeste",
            "lat": -3.72, "lon": -38.54,  # ~1700 km de DF
            "height_m": 5, "tx_power_dbm": 20,
            "rx_sensitivity_dbm": -137, "cable_loss_db": 0,
        },
        "frequency_hz": 915_000_000.0,
    }
    r = client.post("/api/v1/scenarios", json=payload)
    sid = r.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{sid}/calculate")
    assert r2.status_code == 200
    data = r2.json()
    assert "warnings" in data
    assert len(data["warnings"]) > 0
    assert "200" in data["warnings"][0]


def test_distance_warning_absent_for_short_link():
    """Enlace <200 km não deve gerar warnings."""
    sid = _create_and_calculate()
    r = client.post(f"/api/v1/scenarios/{sid}/calculate")
    data = r.json()
    assert data["warnings"] == []
