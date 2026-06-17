"""
Testes de Site Selection — Fase 10.

Cenário base: dois hubs (node-a, node-b) + dois nós folha (node-c, node-d).
Candidatos fixos com posições conhecidas para margem determinística.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

# ── Fixtures ──────────────────────────────────────────────────────────────────

BASE_SCENARIO = {
    "name": "Site Selection Teste",
    "topology_type": "STAR",
    "frequency_hz": 915e6,
    "node_a": {
        "id": "node-a",
        "name": "Sensor Norte",
        "lat": -23.50,
        "lon": -46.60,
        "height_m": 5,
        "tx_power_dbm": 14,
        "rx_sensitivity_dbm": -137,
        "cable_loss_db": 0,
    },
    "node_b": {
        "id": "node-b",
        "name": "Sensor Sul",
        "lat": -23.55,
        "lon": -46.65,
        "height_m": 5,
        "tx_power_dbm": 14,
        "rx_sensitivity_dbm": -137,
        "cable_loss_db": 0,
    },
    "extra_nodes": [],
    "links": [],
    "polygons": [],
}

# Candidato próximo (≈ 3 km dos sensores) — deve cobrir todos
CANDIDATE_NEAR = {
    "id": "cand-near",
    "name": "Torre Centro",
    "lat": -23.525,
    "lon": -46.625,
    "height_m": 30.0,
    "is_existing_tower": False,
}

# Candidato distante (≈ 2500 km) — FSPL ≈ 161 dB → margem negativa com Tx 20 dBm / sens -137 dBm
CANDIDATE_FAR = {
    "id": "cand-far",
    "name": "Torre Distante",
    "lat": -1.0,
    "lon": -35.0,
    "height_m": 30.0,
    "is_existing_tower": True,
}


def _create_scenario(overrides=None):
    payload = {**BASE_SCENARIO, **(overrides or {})}
    r = client.post("/api/v1/scenarios", json=payload)
    assert r.status_code == 201
    return r.json()


def _add_candidate(scenario_id, candidate):
    r = client.post(f"/api/v1/scenarios/{scenario_id}/candidates", json=candidate)
    assert r.status_code == 200
    return r.json()


# ── add_candidate ─────────────────────────────────────────────────────────────

def test_add_candidate_returns_updated_scenario():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/candidates", json=CANDIDATE_NEAR)
    assert r.status_code == 200
    data = r.json()
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["name"] == "Torre Centro"


def test_add_candidate_with_explicit_id():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/candidates", json={**CANDIDATE_NEAR, "id": "my-id"})
    assert r.status_code == 200
    assert r.json()["candidates"][0]["id"] == "my-id"


def test_add_candidate_is_existing_tower():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/candidates", json=CANDIDATE_FAR)
    assert r.status_code == 200
    assert r.json()["candidates"][0]["is_existing_tower"] is True


def test_add_candidate_scenario_not_found():
    r = client.post("/api/v1/scenarios/nonexistent/candidates", json=CANDIDATE_NEAR)
    assert r.status_code == 404


# ── list_candidates ───────────────────────────────────────────────────────────

def test_list_candidates_empty():
    s = _create_scenario()
    r = client.get(f"/api/v1/scenarios/{s['id']}/candidates")
    assert r.status_code == 200
    assert r.json() == []


def test_list_candidates_after_adding():
    s = _create_scenario()
    _add_candidate(s["id"], CANDIDATE_NEAR)
    _add_candidate(s["id"], CANDIDATE_FAR)
    r = client.get(f"/api/v1/scenarios/{s['id']}/candidates")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_candidates_scenario_not_found():
    r = client.get("/api/v1/scenarios/nonexistent/candidates")
    assert r.status_code == 404


# ── site_selection ────────────────────────────────────────────────────────────

def test_site_selection_no_candidates_returns_empty():
    s = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{s['id']}/site-selection", json={})
    assert r.status_code == 200
    assert r.json()["candidates"] == []


def test_site_selection_near_candidate_covers_all():
    """Candidato a ~3 km com 20 dBm → margem positiva nos 2 nós."""
    s = _create_scenario()
    _add_candidate(s["id"], CANDIDATE_NEAR)
    r = client.post(f"/api/v1/scenarios/{s['id']}/site-selection", json={})
    assert r.status_code == 200
    data = r.json()
    assert len(data["candidates"]) == 1
    c = data["candidates"][0]
    assert c["coverage_pct"] == 100.0
    assert c["feasibility"] == "verde"
    assert all(nr["link_margin_db"] > 0 for nr in c["node_results"])


def test_site_selection_far_candidate_low_coverage():
    """Candidato distante → margem negativa, cobertura baixa."""
    s = _create_scenario()
    _add_candidate(s["id"], CANDIDATE_FAR)
    r = client.post(f"/api/v1/scenarios/{s['id']}/site-selection", json={})
    assert r.status_code == 200
    data = r.json()
    c = data["candidates"][0]
    assert c["coverage_pct"] == 0.0
    assert c["feasibility"] == "vermelho"


def test_site_selection_ranked_by_coverage():
    """Candidato próximo deve aparecer antes do distante."""
    s = _create_scenario()
    _add_candidate(s["id"], CANDIDATE_FAR)   # add far first
    _add_candidate(s["id"], CANDIDATE_NEAR)  # add near second
    r = client.post(f"/api/v1/scenarios/{s['id']}/site-selection", json={})
    data = r.json()
    assert len(data["candidates"]) == 2
    # First must be the one with higher coverage
    assert data["candidates"][0]["coverage_pct"] >= data["candidates"][1]["coverage_pct"]
    assert data["candidates"][0]["candidate_id"] == "cand-near"


def test_site_selection_persists_result():
    """site_selection_result deve ser salvo no cenário."""
    s = _create_scenario()
    _add_candidate(s["id"], CANDIDATE_NEAR)
    client.post(f"/api/v1/scenarios/{s['id']}/site-selection", json={})
    r = client.get(f"/api/v1/scenarios/{s['id']}")
    assert r.json()["site_selection_result"] is not None


def test_site_selection_node_results_per_candidate():
    """node_results deve ter uma entrada por nó de campo."""
    s = _create_scenario()
    _add_candidate(s["id"], CANDIDATE_NEAR)
    r = client.post(f"/api/v1/scenarios/{s['id']}/site-selection", json={})
    data = r.json()
    c = data["candidates"][0]
    # node_a and node_b = 2 field nodes
    assert len(c["node_results"]) == 2
    node_ids = {nr["node_id"] for nr in c["node_results"]}
    assert "node-a" in node_ids
    assert "node-b" in node_ids


def test_site_selection_height_override():
    """height_overrides deve atualizar height_m no resultado."""
    s = _create_scenario()
    _add_candidate(s["id"], {**CANDIDATE_NEAR, "id": "cand-h"})
    r = client.post(
        f"/api/v1/scenarios/{s['id']}/site-selection",
        json={"height_overrides": {"cand-h": 50.0}},
    )
    assert r.status_code == 200
    c = r.json()["candidates"][0]
    assert c["height_m"] == 50.0


def test_site_selection_scenario_not_found():
    r = client.post("/api/v1/scenarios/nonexistent/site-selection", json={})
    assert r.status_code == 404


# ── KML tower detection ───────────────────────────────────────────────────────

KML_WITH_TOWER = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>Torre Nordeste</name>
      <Point><coordinates>-46.5,-23.4,45.0</coordinates></Point>
    </Placemark>
    <Placemark>
      <name>Sensor Campo</name>
      <Point><coordinates>-46.6,-23.5,5.0</coordinates></Point>
    </Placemark>
  </Document>
</kml>"""


def test_kml_tower_imported_as_candidate():
    """Placemark com nome contendo 'torre' → CandidateSite com is_existing_tower=True."""
    s = _create_scenario()
    resp = client.post(
        f"/api/v1/scenarios/{s['id']}/kml",
        files={"file": ("test.kml", KML_WITH_TOWER.encode(), "application/vnd.google-earth.kml+xml")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["candidates_imported"] == 1
    assert data["nodes_imported"] == 1
    assert data["candidates"][0]["name"] == "Torre Nordeste"
    assert data["candidates"][0]["is_existing_tower"] is True
    assert data["candidates"][0]["height_m"] == 45.0


def test_kml_regular_node_not_a_candidate():
    """Placemark sem 'torre'/'tower' → NodeSpec, não CandidateSite."""
    s = _create_scenario()
    resp = client.post(
        f"/api/v1/scenarios/{s['id']}/kml",
        files={"file": ("test.kml", KML_WITH_TOWER.encode(), "application/vnd.google-earth.kml+xml")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes"][0]["name"] == "Sensor Campo"
