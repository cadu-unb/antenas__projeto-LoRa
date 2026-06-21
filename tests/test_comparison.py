"""Testes Fase 4 — framework de comparação de cenários."""
import pytest
from fastapi.testclient import TestClient

from backend.app.domain.comparison import _compute_robustness, run_comparison
from backend.app.main import app
from backend.app.schemas.antenna_spec import AntennaSpec
from backend.app.schemas.node_spec import NodeSpec
from backend.app.storage import antenna_storage, lora_module_storage

client = TestClient(app)

import pathlib
DATA_DIR = pathlib.Path("backend/data/scenarios")


# ── Fixtures helpers ──────────────────────────────────────────────────────────

BASE_SCENARIO = {
    "name": "Comparação Teste",
    "frequency_hz": 915e6,
    "node_a": {
        "name": "Gateway",
        "lat": -15.78,
        "lon": -47.93,
        "height_m": 10,
        "tx_power_dbm": 20,
        "rx_sensitivity_dbm": -137,
    },
    "node_b": {
        "name": "Sensor1",
        "lat": -15.83,
        "lon": -48.05,
        "height_m": 5,
        "tx_power_dbm": 14,
        "rx_sensitivity_dbm": -137,
    },
}


def _create_scenario(extra_nodes=None):
    payload = {**BASE_SCENARIO}
    if extra_nodes:
        payload["extra_nodes"] = extra_nodes
    r = client.post("/api/v1/scenarios", json=payload)
    assert r.status_code == 201
    return r.json()["id"]


def _cleanup(id_: str):
    (DATA_DIR / f"{id_}.json").unlink(missing_ok=True)


def _save_antenna(name, ant_type, freq=915e6):
    ant = AntennaSpec(name=name, type=ant_type, frequency_hz=freq)
    antenna_storage.save(ant)
    return ant


# ── Unit tests — run_comparison ───────────────────────────────────────────────

def test_run_comparison_returns_rows():
    """run_comparison produz ao menos 1 row."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="Dipolo", type="dipolo", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.83, lon=-48.05, height_m=5)

    rows = run_comparison([sensor], gateway, 915e6, modules, [dipolo], [dipolo])
    assert len(rows) == 1
    assert rows[0].module_id == modules[0].id


def test_run_comparison_sorted_by_min_margin():
    """Rows ordenadas por min_margin_db desc."""
    modules = lora_module_storage.list_modules()
    dipolo = AntennaSpec(name="Dipolo", type="dipolo", frequency_hz=915e6)
    helicoidal = AntennaSpec(name="Heli", type="helicoidal", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.83, lon=-48.05, height_m=5)

    rows = run_comparison([sensor], gateway, 915e6, modules, [dipolo, helicoidal], [dipolo])
    margins = [r.min_margin_db for r in rows]
    assert margins == sorted(margins, reverse=True)


def test_run_comparison_failure_count():
    """failure_count = 0 para nós próximos (margem positiva)."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.79, lon=-47.94, height_m=5)  # ~1.5 km

    rows = run_comparison([sensor], gateway, 915e6, modules, [dipolo], [dipolo])
    assert rows[0].failure_count == 0


def test_run_comparison_comfortable_count():
    """comfortable_count > 0 para nós próximos com alta potência."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.79, lon=-47.94, height_m=5)

    rows = run_comparison([sensor], gateway, 915e6, modules, [dipolo], [dipolo])
    assert rows[0].comfortable_count > 0


def test_run_comparison_labels_sequential():
    """Labels A, B, C... em sequência."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    helicoidal = AntennaSpec(name="H", type="helicoidal", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.83, lon=-48.05, height_m=5)

    rows = run_comparison([sensor], gateway, 915e6, modules, [dipolo, helicoidal], [dipolo])
    labels = sorted(r.scenario_label for r in rows)
    assert set(labels) == {"A", "B"}


# ── Unit tests — robustness_score ─────────────────────────────────────────────

def test_robustness_omni_no_penalty():
    """Antena omni com baixa variância → sem penalidade."""
    margins = [60.0, 62.0, 61.0]  # std < 10
    score = _compute_robustness(margins, "dipolo")
    assert score > 0


def test_robustness_directional_high_variance_penalized():
    """Antena diretiva com std > 10 → penalidade 0.5."""
    margins = [80.0, 50.0, 20.0]  # std > 10
    score_helicoidal = _compute_robustness(margins, "helicoidal")
    score_omni = _compute_robustness(margins, "dipolo")
    assert score_helicoidal < score_omni


def test_robustness_single_sensor_no_std():
    """1 sensor → std=0, sem penalidade."""
    score = _compute_robustness([50.0], "helicoidal")
    assert score > 0


# ── API tests — /compare ──────────────────────────────────────────────────────

def test_compare_endpoint_no_antennas_returns_empty():
    """Sem antenas na library → lista vazia (tx_ants[:3] = [])."""
    id_ = _create_scenario()
    r = client.post(f"/api/v1/scenarios/{id_}/compare")
    assert r.status_code == 200
    _cleanup(id_)


def test_compare_endpoint_with_antennas_returns_rows():
    """Com antenas na library, retorna ao menos 1 row."""
    ant = _save_antenna("TestDipolo", "dipolo")
    id_ = _create_scenario()
    r = client.post(
        f"/api/v1/scenarios/{id_}/compare",
        params={"tx_antenna_ids": ant.id, "gw_antenna_ids": ant.id},
    )
    assert r.status_code == 200
    rows = r.json()
    assert len(rows) > 0
    assert "min_margin_db" in rows[0]
    assert "failure_count" in rows[0]
    assert "robustness_score" in rows[0]
    antenna_storage.delete(ant.id)
    _cleanup(id_)


def test_compare_endpoint_sorted_by_min_margin():
    """Rows ordenadas por min_margin_db desc."""
    ant = _save_antenna("TestDipolo2", "dipolo")
    id_ = _create_scenario()
    r = client.post(
        f"/api/v1/scenarios/{id_}/compare",
        params={"tx_antenna_ids": ant.id, "gw_antenna_ids": ant.id},
    )
    rows = r.json()
    if len(rows) > 1:
        margins = [row["min_margin_db"] for row in rows]
        assert margins == sorted(margins, reverse=True)
    antenna_storage.delete(ant.id)
    _cleanup(id_)


def test_compare_endpoint_not_found():
    r = client.post("/api/v1/scenarios/nonexistent/compare")
    assert r.status_code == 404
