"""
Testes do catálogo de módulos LoRa.
GET /api/v1/antennas/lora-modules
GET /api/v1/antennas/lora-modules/{module_id}
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.lora_module import LoRaModule
from backend.app.storage import lora_module_storage

client = TestClient(app)


# ── Testes unitários de storage ───────────────────────────────────────────────

def test_list_modules_returns_three():
    modules = lora_module_storage.list_modules()
    assert len(modules) == 3


def test_all_modules_are_lora_module_instances():
    modules = lora_module_storage.list_modules()
    for m in modules:
        assert isinstance(m, LoRaModule)


def test_get_module_rfm95w():
    m = lora_module_storage.get_module("rfm95w_915")
    assert m is not None
    assert m.manufacturer == "HopeRF"


def test_get_module_unknown_returns_none():
    assert lora_module_storage.get_module("nao_existe") is None


def test_rfm95w_sensitivity_sf12():
    m = lora_module_storage.get_module("rfm95w_915")
    assert m.get_sensitivity(sf=12, bw_khz=125) == -139.0


def test_rfm95w_sensitivity_sf7():
    m = lora_module_storage.get_module("rfm95w_915")
    assert m.get_sensitivity(sf=7, bw_khz=125) == -118.0


def test_e220_sensitivity_sf12():
    m = lora_module_storage.get_module("e220_900t22d")
    assert m.get_sensitivity(sf=12, bw_khz=125) == -147.0


def test_get_sensitivity_missing_mode_returns_none():
    m = lora_module_storage.get_module("rfm95w_915")
    assert m.get_sensitivity(sf=9, bw_khz=125) is None


# ── Testes de API ─────────────────────────────────────────────────────────────

def test_api_list_lora_modules_200():
    r = client.get("/api/v1/antennas/lora-modules")
    assert r.status_code == 200


def test_api_list_lora_modules_count():
    r = client.get("/api/v1/antennas/lora-modules")
    assert len(r.json()) == 3


def test_api_get_rfm95w_200():
    r = client.get("/api/v1/antennas/lora-modules/rfm95w_915")
    assert r.status_code == 200


def test_api_rfm95w_sensitivity_sf12():
    r = client.get("/api/v1/antennas/lora-modules/rfm95w_915")
    modes = r.json()["sensitivity_modes"]
    sf12 = next(m for m in modes if m["sf"] == 12)
    assert sf12["sensitivity_dbm"] == -139


def test_api_get_lro2_200():
    r = client.get("/api/v1/antennas/lora-modules/lro2_asr6601")
    assert r.status_code == 200
    assert r.json()["manufacturer"] == "ASR"


def test_api_get_e220_200():
    r = client.get("/api/v1/antennas/lora-modules/e220_900t22d")
    assert r.status_code == 200
    assert r.json()["frequency_mhz"] == 900.0


def test_api_unknown_module_404():
    r = client.get("/api/v1/antennas/lora-modules/nao_existe")
    assert r.status_code == 404


def test_api_lora_module_has_tx_power_options():
    r = client.get("/api/v1/antennas/lora-modules/rfm95w_915")
    data = r.json()
    assert isinstance(data["tx_power_options_dbm"], list)
    assert 20 in data["tx_power_options_dbm"]


def test_api_lora_module_has_voltage_range():
    r = client.get("/api/v1/antennas/lora-modules/rfm95w_915")
    vr = r.json()["voltage_range_v"]
    assert len(vr) == 2
    assert vr[0] < vr[1]
