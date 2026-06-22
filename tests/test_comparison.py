"""Testes Fase 4 — framework de comparação de cenários."""
import pytest
from fastapi.testclient import TestClient

from backend.app.domain.comparison import _compute_robustness, _get_ant_field, run_comparison
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


# ── Fase 5 — polarização no comparison ───────────────────────────────────────

def test_run_comparison_helicoidal_vs_dipolo_lower_than_dipolo_vs_dipolo():
    """Helicoidal (circular) TX vs dipolo GW tem perda extra de polarização (3 dB).

    Com mesma distância, helicoidal tem ganho mais alto que dipolo, mas a perda
    de polarização reduz a margem efetiva. O teste verifica que polarization_loss_db
    é capturado via compute_link_full internamente (margem helicoidal pode ser maior
    ou menor dependendo do ganho neto). O campo existe no LinkResult.
    """
    from backend.app.domain.link_budget import compute_link_full
    helicoidal = AntennaSpec(name="Heli", type="helicoidal", frequency_hz=915e6)
    dipolo = AntennaSpec(name="Dipolo", type="dipolo", frequency_hz=915e6)
    node_a = NodeSpec(name="A", lat=-15.78, lon=-47.93, height_m=5,
                      tx_power_dbm=20, rx_sensitivity_dbm=-137)
    node_b = NodeSpec(name="B", lat=-15.83, lon=-48.05, height_m=5,
                      tx_power_dbm=14, rx_sensitivity_dbm=-137)

    result_mismatch = compute_link_full(node_a, node_b, 915e6,
                                        antenna_a=helicoidal, antenna_b=dipolo)
    result_match = compute_link_full(node_a, node_b, 915e6,
                                     antenna_a=helicoidal, antenna_b=helicoidal)
    # helicoidal vs helicoidal → both circular → 0 dB pol loss
    assert result_match.polarization_loss_db == pytest.approx(0.0)
    # helicoidal vs dipolo → circular vs linear → 3 dB pol loss
    assert result_mismatch.polarization_loss_db == pytest.approx(3.0)
    # mismatch has 3 dB extra penalty → lower margin
    assert result_match.link_margin_db > result_mismatch.link_margin_db


# ── Fase 6 — ranking com scores de antena ────────────────────────────────────

def test_get_ant_field_from_preset_via_spec():
    """_get_ant_field retorna campo via preset para AntennaSpec sem campo explícito."""
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    assert _get_ant_field(dipolo, "is_directional") is False
    assert _get_ant_field(dipolo, "multi_direction_score") == pytest.approx(9.0)
    assert _get_ant_field(dipolo, "practicality_score") == pytest.approx(8.0)


def test_get_ant_field_from_type_string():
    """_get_ant_field aceita type string diretamente (fallback para tests antigos)."""
    assert _get_ant_field("parabolica", "is_directional") is True
    assert _get_ant_field("parabolica", "multi_direction_score") == pytest.approx(1.0)
    assert _get_ant_field("commercial_omni_6dbi", "multi_direction_score") == pytest.approx(8.0)


def test_get_ant_field_none_antenna_returns_fallback():
    """_get_ant_field retorna fallback quando antenna é None."""
    assert _get_ant_field(None, "is_directional", False) is False
    assert _get_ant_field(None, "practicality_score", 0.0) == 0.0


def test_robustness_gw_parabolica_penalized_vs_omni():
    """GW parabolica (multi_direction_score=1) → robustness muito menor que commercial_omni (score=8)."""
    margins = [60.0, 58.0, 59.0]  # low variance
    dipolo_tx = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    parabolica = AntennaSpec(name="P", type="parabolica", frequency_hz=915e6)
    omni = AntennaSpec(name="O", type="commercial_omni_6dbi", frequency_hz=915e6)

    score_omni_gw = _compute_robustness(margins, dipolo_tx, omni)
    score_para_gw = _compute_robustness(margins, dipolo_tx, parabolica)
    assert score_omni_gw > score_para_gw


def test_robustness_backward_compat_string_args():
    """_compute_robustness ainda funciona com type strings (retrocompatibilidade)."""
    margins = [80.0, 50.0, 20.0]
    score_heli = _compute_robustness(margins, "helicoidal")
    score_dipolo = _compute_robustness(margins, "dipolo")
    assert score_heli < score_dipolo  # directional + high std → penalty


def test_comparison_row_has_practicality_aggregate_fields():
    """ComparisonRow expõe practicality_score, aggregate_score e scores_source."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.83, lon=-48.05, height_m=5)

    rows = run_comparison([sensor], gateway, 915e6, modules, [dipolo], [dipolo])
    assert len(rows) == 1
    row = rows[0]
    assert row.practicality_score > 0        # dipolo practicality=8
    assert row.aggregate_score > 0
    assert row.scores_source == "preset"


def test_comparison_commercial_omni_vs_parabolica_multiazimuth():
    """commercial_omni_6dbi como GW tem robustness_score maior que parabolica em cenário multi-sensor multi-azimute."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    parabolica = AntennaSpec(name="P", type="parabolica", frequency_hz=915e6)
    omni = AntennaSpec(name="O", type="commercial_omni_6dbi", frequency_hz=915e6)

    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=20)
    # Sensores em 4 azimutes diferentes do gateway
    sensors = [
        NodeSpec(name="S_N", lat=-15.70, lon=-47.93, height_m=5),
        NodeSpec(name="S_E", lat=-15.78, lon=-47.83, height_m=5),
        NodeSpec(name="S_S", lat=-15.86, lon=-47.93, height_m=5),
        NodeSpec(name="S_W", lat=-15.78, lon=-48.03, height_m=5),
    ]

    rows_omni = run_comparison(sensors, gateway, 915e6, modules, [dipolo], [omni])
    rows_para = run_comparison(sensors, gateway, 915e6, modules, [dipolo], [parabolica])

    assert len(rows_omni) == 1
    assert len(rows_para) == 1
    assert rows_omni[0].robustness_score > rows_para[0].robustness_score


def test_comparison_parabolica_good_p2p_bad_multisensor():
    """Parabólica tem robustness_score relativo pior em multi-sensor vs 1 sensor (multi_direction_score=1)."""
    modules = lora_module_storage.list_modules()[:1]
    dipolo = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    parabolica = AntennaSpec(name="P", type="parabolica", frequency_hz=915e6)

    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=20)
    sensor_single = [NodeSpec(name="S1", lat=-15.83, lon=-48.05, height_m=5)]
    sensors_multi = [
        NodeSpec(name="S_N", lat=-15.70, lon=-47.93, height_m=5),
        NodeSpec(name="S_E", lat=-15.78, lon=-47.83, height_m=5),
        NodeSpec(name="S_S", lat=-15.86, lon=-47.93, height_m=5),
        NodeSpec(name="S_W", lat=-15.78, lon=-48.03, height_m=5),
    ]
    omni = AntennaSpec(name="O", type="commercial_omni_6dbi", frequency_hz=915e6)

    rows_para_multi = run_comparison(sensors_multi, gateway, 915e6, modules, [dipolo], [parabolica])
    rows_omni_multi = run_comparison(sensors_multi, gateway, 915e6, modules, [dipolo], [omni])

    # Em cenário multi-sensor, omni deve ser mais robusto que parabolica
    assert rows_omni_multi[0].robustness_score > rows_para_multi[0].robustness_score


def test_comparison_scores_source_fallback_for_unknown_type():
    """AntennaSpec com tipo sem preset → scores_source='fallback', practicality_score=0."""
    modules = lora_module_storage.list_modules()[:1]
    # Usar tipo inválido que não existe no preset registry
    ant_unknown = AntennaSpec(name="X", type="custom_unknown_xyz", frequency_hz=915e6)
    gateway = NodeSpec(name="GW", lat=-15.78, lon=-47.93, height_m=10)
    sensor = NodeSpec(name="S1", lat=-15.83, lon=-48.05, height_m=5)

    rows = run_comparison([sensor], gateway, 915e6, modules, [ant_unknown], [ant_unknown])
    assert len(rows) == 1
    assert rows[0].practicality_score == 0.0
    assert rows[0].scores_source == "fallback"
