"""Testes Fase 4 — estimativa de consumo energético e minimax gateway."""
import pytest
from fastapi.testclient import TestClient

from backend.app.domain.energy import estimate_energy
from backend.app.main import app
from backend.app.storage import lora_module_storage

client = TestClient(app)

import pathlib
DATA_DIR = pathlib.Path("backend/data/scenarios")


def _cleanup(id_: str):
    (DATA_DIR / f"{id_}.json").unlink(missing_ok=True)


# ── estimate_energy unit tests ────────────────────────────────────────────────

def test_energy_sf12_slower_than_sf7():
    """SF12 → ToA maior que SF7."""
    module = lora_module_storage.get_module("rfm95w_915")
    e12 = estimate_energy(module, tx_power_dbm=20, sf=12)
    e7 = estimate_energy(module, tx_power_dbm=20, sf=7)
    assert e12.tx_duration_ms > e7.tx_duration_ms


def test_energy_sf12_less_battery_life_than_sf7():
    """SF12 consome mais energia → vida de bateria menor."""
    module = lora_module_storage.get_module("rfm95w_915")
    e12 = estimate_energy(module, tx_power_dbm=20, sf=12)
    e7 = estimate_energy(module, tx_power_dbm=20, sf=7)
    assert e12.battery_life_days < e7.battery_life_days


def test_energy_battery_life_positive():
    """Vida de bateria > 0."""
    module = lora_module_storage.get_module("rfm95w_915")
    est = estimate_energy(module, tx_power_dbm=20, sf=12)
    assert est.battery_life_days > 0


def test_energy_daily_mwh_positive():
    """Consumo diário em mWh > 0."""
    module = lora_module_storage.get_module("rfm95w_915")
    est = estimate_energy(module, tx_power_dbm=20, sf=12)
    assert est.daily_energy_mwh > 0


def test_energy_tx_duration_sf7_lt_1000ms():
    """SF7 com payload 20 bytes → ToA < 1000 ms (sanidade física)."""
    module = lora_module_storage.get_module("rfm95w_915")
    est = estimate_energy(module, tx_power_dbm=20, sf=7)
    assert est.tx_duration_ms < 1000


def test_energy_more_transmissions_shorter_battery():
    """Mais transmissões/dia → vida de bateria menor."""
    module = lora_module_storage.get_module("rfm95w_915")
    e96 = estimate_energy(module, tx_power_dbm=20, sf=12, transmissions_per_day=96)
    e288 = estimate_energy(module, tx_power_dbm=20, sf=12, transmissions_per_day=288)
    assert e96.battery_life_days > e288.battery_life_days


def test_energy_all_modules_positive():
    """Todos os módulos retornam battery_life > 0."""
    for m in lora_module_storage.list_modules():
        est = estimate_energy(m, tx_power_dbm=m.tx_power_options_dbm[-1], sf=12)
        assert est.battery_life_days > 0, f"Módulo {m.id}: vida <= 0"


# ── API endpoint /energy ──────────────────────────────────────────────────────

def test_energy_endpoint_sf12_returns_ok():
    r = client.post("/api/v1/antennas/lora-modules/rfm95w_915/energy?sf=12&tx_power_dbm=20")
    assert r.status_code == 200
    data = r.json()
    assert "battery_life_days" in data
    assert "tx_duration_ms" in data
    assert "daily_energy_mwh" in data


def test_energy_endpoint_battery_life_gt_1():
    # 14 dBm = 29 mA no RFM95W → ~3.6 dias com 2000 mAh
    r = client.post("/api/v1/antennas/lora-modules/rfm95w_915/energy?sf=12&tx_power_dbm=14")
    assert r.status_code == 200
    data = r.json()
    assert data["battery_life_days"] > 1


def test_energy_endpoint_sf7_faster():
    """SF7 deve ter tx_duration_ms menor que SF12 via API."""
    r12 = client.post("/api/v1/antennas/lora-modules/rfm95w_915/energy?sf=12&tx_power_dbm=20")
    r7 = client.post("/api/v1/antennas/lora-modules/rfm95w_915/energy?sf=7&tx_power_dbm=20")
    assert r12.json()["tx_duration_ms"] > r7.json()["tx_duration_ms"]


def test_energy_endpoint_module_not_found():
    r = client.post("/api/v1/antennas/lora-modules/nonexistent/energy")
    assert r.status_code == 404


def test_energy_endpoint_all_modules():
    """Endpoint funciona para todos os módulos do catálogo."""
    for m in lora_module_storage.list_modules():
        r = client.post(f"/api/v1/antennas/lora-modules/{m.id}/energy?sf=12")
        assert r.status_code == 200, f"Módulo {m.id} falhou"


# ── API tests — minimax site-selection ───────────────────────────────────────

BASE_SCENARIO = {
    "name": "Minimax Teste",
    "frequency_hz": 915e6,
    "node_a": {"name": "S1", "lat": -15.78, "lon": -47.93, "height_m": 5,
               "tx_power_dbm": 14, "rx_sensitivity_dbm": -137},
    "node_b": {"name": "S2", "lat": -15.83, "lon": -48.05, "height_m": 5,
               "tx_power_dbm": 14, "rx_sensitivity_dbm": -137},
}

CANDIDATE_CENTRAL = {
    "id": "cand-central",
    "name": "Torre Central",
    "lat": -15.805,   # entre S1 e S2
    "lon": -47.99,
    "height_m": 20.0,
}

CANDIDATE_FAR = {
    "id": "cand-far",
    "name": "Torre Distante",
    "lat": -15.90,
    "lon": -48.20,
    "height_m": 20.0,
}


def _create_scenario_with_candidates():
    r = client.post("/api/v1/scenarios", json=BASE_SCENARIO)
    assert r.status_code == 201
    id_ = r.json()["id"]
    client.post(f"/api/v1/scenarios/{id_}/candidates", json=CANDIDATE_CENTRAL)
    client.post(f"/api/v1/scenarios/{id_}/candidates", json=CANDIDATE_FAR)
    return id_


def test_minimax_returns_200():
    id_ = _create_scenario_with_candidates()
    r = client.post(f"/api/v1/scenarios/{id_}/site-selection?selection_mode=minimax")
    assert r.status_code == 200
    _cleanup(id_)


def test_minimax_returns_list_with_rank():
    id_ = _create_scenario_with_candidates()
    r = client.post(f"/api/v1/scenarios/{id_}/site-selection?selection_mode=minimax")
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "rank" in data[0]
    _cleanup(id_)


def test_minimax_ranks_central_first():
    """Candidato mais central (menor distância máxima) deve ter rank=1."""
    id_ = _create_scenario_with_candidates()
    r = client.post(f"/api/v1/scenarios/{id_}/site-selection?selection_mode=minimax")
    data = r.json()
    rank1 = next(d for d in data if d["rank"] == 1)
    assert rank1["candidate_id"] == "cand-central"
    _cleanup(id_)


def test_minimax_sorted_by_max_dist():
    """Resultado ordenado por max_dist_m crescente."""
    id_ = _create_scenario_with_candidates()
    r = client.post(f"/api/v1/scenarios/{id_}/site-selection?selection_mode=minimax")
    data = r.json()
    max_dists = [d["max_dist_m"] for d in data]
    assert max_dists == sorted(max_dists)
    _cleanup(id_)


def test_minimax_no_candidates_returns_empty():
    r = client.post("/api/v1/scenarios", json=BASE_SCENARIO)
    id_ = r.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/site-selection?selection_mode=minimax")
    assert r2.status_code == 200
    assert r2.json() == []
    _cleanup(id_)


def test_coverage_mode_still_works():
    """Modo coverage (default) ainda retorna SiteSelectionResult com 'candidates'."""
    id_ = _create_scenario_with_candidates()
    r = client.post(f"/api/v1/scenarios/{id_}/site-selection", json={})
    assert r.status_code == 200
    assert "candidates" in r.json()
    _cleanup(id_)
