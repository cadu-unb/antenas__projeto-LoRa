"""
Testes Fase 3: compute_link_full, ganho direcional, perdas extras, modelos de propagação.
Testes Fase 4: _effective_gain com campos explícitos, presets, exceção PCB.
"""
import math
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.app.domain.link_budget import _effective_gain, compute_link_full, path_loss_db
from backend.app.domain.geometry import ENUVector
from backend.app.main import app
from backend.app.schemas.antenna_spec import AntennaSpec
from backend.app.schemas.node_spec import NodeSpec

client = TestClient(app)

DATA_DIR = __import__("pathlib").Path("backend/data/scenarios")


def _make_node(name, lat, lon, height_m=5, tx_power_dbm=20, rx_sensitivity_dbm=-137, **kwargs):
    return NodeSpec(
        name=name, lat=lat, lon=lon, height_m=height_m,
        tx_power_dbm=tx_power_dbm, rx_sensitivity_dbm=rx_sensitivity_dbm,
        **kwargs,
    )


# ── Geometria 3D ──────────────────────────────────────────────────────────────

def test_3d_distance_gt_2d_when_altitude_differs():
    """Distância 3D > 2D quando nós têm altitudes diferentes."""
    from backend.app.domain.link_budget import haversine
    node_a = _make_node("A", -15.78, -47.93, height_m=5)
    node_b = _make_node("B", -15.83, -48.05, height_m=1000)
    result = compute_link_full(node_a, node_b, 915e6)
    dist_2d = haversine(node_a.lat, node_a.lon, node_b.lat, node_b.lon)
    assert result.distance_m > dist_2d


def test_3d_distance_approx_2d_when_same_height():
    """Com mesma altura, 3D ≈ 2D (diferença < 100 m para 14 km — modelos geodésicos diferentes)."""
    from backend.app.domain.link_budget import haversine
    node_a = _make_node("A", -15.78, -47.93, height_m=10)
    node_b = _make_node("B", -15.83, -48.05, height_m=10)
    result = compute_link_full(node_a, node_b, 915e6)
    dist_2d = haversine(node_a.lat, node_a.lon, node_b.lat, node_b.lon)
    assert abs(result.distance_m - dist_2d) < 100.0


# ── Perdas adicionais ─────────────────────────────────────────────────────────

def test_extra_loss_reduces_margin_exactly():
    """extra_loss_db=10 reduz margem em exatamente 10 dB."""
    node_a = _make_node("A", -15.78, -47.93, extra_loss_db=0)
    node_b = _make_node("B", -15.83, -48.05)
    r1 = compute_link_full(node_a, node_b, 915e6)

    node_a2 = node_a.model_copy(update={"extra_loss_db": 10.0})
    r2 = compute_link_full(node_a2, node_b, 915e6)

    assert abs(r1.link_margin_db - r2.link_margin_db - 10.0) < 0.01


def test_fading_margin_reduces_margin():
    """fading_margin_db=5 reduz margem em 5 dB."""
    node_a = _make_node("A", -15.78, -47.93, fading_margin_db=0)
    node_b = _make_node("B", -15.83, -48.05)
    r1 = compute_link_full(node_a, node_b, 915e6)

    node_a2 = node_a.model_copy(update={"fading_margin_db": 5.0})
    r2 = compute_link_full(node_a2, node_b, 915e6)

    assert abs(r1.link_margin_db - r2.link_margin_db - 5.0) < 0.01


def test_extra_loss_in_result():
    """extra_loss_db retornado no LinkResult."""
    node_a = _make_node("A", -15.78, -47.93, extra_loss_db=3.0)
    node_b = _make_node("B", -15.83, -48.05)
    result = compute_link_full(node_a, node_b, 915e6)
    assert result.extra_loss_db == pytest.approx(3.0, abs=0.01)


# ── Ganho direcional ──────────────────────────────────────────────────────────

def test_directional_gain_penalizes_misalignment():
    """Helicoidal apontada para Oeste perde margem em enlace para Norte."""
    antenna_helicoidal = AntennaSpec(name="Heli", type="helicoidal", frequency_hz=915e6)

    # Norte de A
    node_a = _make_node("A", -15.78, -47.93, azimuth_deg=270, tilt_deg=0)  # boresight Oeste
    node_b = _make_node("B", -15.68, -47.93)  # diretamente ao Norte

    result_misaligned = compute_link_full(node_a, node_b, 915e6, antenna_a=antenna_helicoidal)

    node_a_aligned = node_a.model_copy(update={"azimuth_deg": 0})  # boresight Norte
    result_aligned = compute_link_full(node_a_aligned, node_b, 915e6, antenna_a=antenna_helicoidal)

    assert result_aligned.link_margin_db > result_misaligned.link_margin_db


def test_no_orientation_uses_gmax():
    """Sem azimuth_deg definido, ganho = G_max (sem penalidade)."""
    antenna = AntennaSpec(name="Dipolo", type="dipolo", frequency_hz=915e6)
    node_a = _make_node("A", -15.78, -47.93)  # azimuth_deg=None (default)
    node_b = _make_node("B", -15.83, -48.05)
    result = compute_link_full(node_a, node_b, 915e6, antenna_a=antenna)
    # Com G_max dipolo ~2.15 dBi, margem deve ser maior que sem antena
    result_no_ant = compute_link_full(node_a, node_b, 915e6)
    assert result.link_margin_db > result_no_ant.link_margin_db


# ── Modelos de propagação ─────────────────────────────────────────────────────

def test_path_loss_db_fspl_matches_fspl_db():
    """path_loss_db com model='fspl' == fspl_db()."""
    from backend.app.domain.link_budget import fspl_db
    dist_m, freq_hz = 5000, 915e6
    assert abs(path_loss_db(dist_m, freq_hz, model="fspl") - fspl_db(dist_m, freq_hz)) < 0.001


def test_okumura_hata_gives_higher_loss_than_fspl():
    """Okumura-Hata (urbano) > FSPL para mesma distância e frequência."""
    dist_m, freq_hz = 5000, 915e6
    fspl = path_loss_db(dist_m, freq_hz, model="fspl")
    oh = path_loss_db(dist_m, freq_hz, model="okumura_hata", tx_height_m=30, rx_height_m=1.5)
    assert oh > fspl


def test_longley_rice_returns_positive_loss():
    """Longley-Rice retorna perda positiva."""
    loss = path_loss_db(5000, 915e6, model="longley_rice", tx_height_m=30, rx_height_m=5)
    assert loss > 0


def test_propagation_model_field_in_result():
    """LinkResult contém propagation_model."""
    node_a = _make_node("A", -15.78, -47.93)
    node_b = _make_node("B", -15.83, -48.05)
    result = compute_link_full(node_a, node_b, 915e6, propagation_model="fspl")
    assert result.propagation_model == "fspl"


# ── Integração via API ────────────────────────────────────────────────────────

SCENARIO_PAYLOAD = {
    "name": "Fase3 Test",
    "node_a": {
        "name": "A", "lat": -15.78, "lon": -47.93, "height_m": 10,
        "tx_power_dbm": 20, "rx_sensitivity_dbm": -137,
    },
    "node_b": {
        "name": "B", "lat": -15.83, "lon": -48.05, "height_m": 10,
        "tx_power_dbm": 14, "rx_sensitivity_dbm": -137,
    },
    "frequency_hz": 915_000_000.0,
}

SCENARIO_OKUMURA = {**SCENARIO_PAYLOAD, "propagation_model": "okumura_hata", "name": "Fase3 OH"}


def _cleanup(id_: str):
    (DATA_DIR / f"{id_}.json").unlink(missing_ok=True)


def test_api_calculate_returns_warnings_field():
    """Resultado de /calculate contém campo warnings."""
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/calculate")
    assert "warnings" in r2.json()
    _cleanup(id_)


def test_api_calculate_returns_extra_loss_db():
    """Resultado contém extra_loss_db."""
    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_ = r1.json()["id"]
    r2 = client.post(f"/api/v1/scenarios/{id_}/calculate")
    assert "extra_loss_db" in r2.json()
    _cleanup(id_)


def test_api_calculate_okumura_hata_different_loss():
    """Okumura-Hata retorna fspl_db diferente de FSPL puro."""
    from backend.app.domain.link_budget import fspl_db

    r1 = client.post("/api/v1/scenarios", json=SCENARIO_PAYLOAD)
    id_fspl = r1.json()["id"]
    r_fspl = client.post(f"/api/v1/scenarios/{id_fspl}/calculate")
    fspl_val = r_fspl.json()["fspl_db"]

    r2 = client.post("/api/v1/scenarios", json=SCENARIO_OKUMURA)
    id_oh = r2.json()["id"]
    r_oh = client.post(f"/api/v1/scenarios/{id_oh}/calculate")
    oh_val = r_oh.json()["fspl_db"]

    assert oh_val != pytest.approx(fspl_val, abs=1.0), (
        f"Okumura-Hata ({oh_val}) deve diferir de FSPL ({fspl_val})"
    )
    _cleanup(id_fspl)
    _cleanup(id_oh)


# ── Fase 4 — _effective_gain com campos explícitos ────────────────────────────

def _enu_east(dist_m: float = 1000.0) -> ENUVector:
    return ENUVector(dist_m, 0.0, 0.0)


def _node_no_az() -> SimpleNamespace:
    return SimpleNamespace(azimuth_deg=None, tilt_deg=0.0)


def _node_az(az: float, tilt: float = 0.0) -> SimpleNamespace:
    return SimpleNamespace(azimuth_deg=az, tilt_deg=tilt)


def test_effective_gain_pcb_915mhz_preset_gmax_ignored():
    """pcb_compact a 915 MHz sem gmax_dbi explícito → solver retorna 1.5 dBi, não preset 1.0."""
    ant = AntennaSpec(name="PCB", type="pcb_compact", frequency_hz=915e6)
    gain = _effective_gain(_node_no_az(), ant, _enu_east())
    assert gain == pytest.approx(1.5, abs=0.01)


def test_effective_gain_pcb_explicit_gmax_used():
    """pcb_compact com gmax_dbi=1.0 explícito → link budget usa 1.0 dBi."""
    ant = AntennaSpec(name="PCB", type="pcb_compact", frequency_hz=915e6, gmax_dbi=1.0)
    gain = _effective_gain(_node_no_az(), ant, _enu_east())
    assert gain == pytest.approx(1.0, abs=0.01)


def test_effective_gain_pcb_explicit_gmax_custom_value():
    """pcb_compact com gmax_dbi=2.5 explícito → usa 2.5 (override de usuário)."""
    ant = AntennaSpec(name="PCB", type="pcb_compact", frequency_hz=915e6, gmax_dbi=2.5)
    gain = _effective_gain(_node_no_az(), ant, _enu_east())
    assert gain == pytest.approx(2.5, abs=0.01)


def test_effective_gain_explicit_gmax_overrides_solver():
    """Antena dipolo com gmax_dbi=5.0 explícito → usa 5.0, não cálculo do solver."""
    ant = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6, gmax_dbi=5.0)
    gain = _effective_gain(_node_no_az(), ant, _enu_east())
    assert gain == pytest.approx(5.0, abs=0.01)


def test_effective_gain_no_explicit_gmax_uses_solver():
    """Dipolo sem gmax_dbi explícito → solver calcula ~2.15 dBi."""
    ant = AntennaSpec(name="D", type="dipolo", frequency_hz=915e6)
    gain = _effective_gain(_node_no_az(), ant, _enu_east())
    assert 1.8 <= gain <= 2.5


def test_effective_gain_colinear_hpbw_from_spec_changes_pattern():
    """hpbw_deg explícito na spec muda o ganho angular do colinear."""
    # Node aponta para Leste (az=90), enlace vai para Norte (az=0) → offset 90°
    node = _node_az(90.0)
    enu_north = ENUVector(0.0, 1000.0, 0.0)  # azimuth=0° (Norte)

    ant_narrow = AntennaSpec(name="C", type="commercial_omni_6dbi", frequency_hz=915e6, hpbw_deg=10.0)
    ant_wide = AntennaSpec(name="C", type="commercial_omni_6dbi", frequency_hz=915e6, hpbw_deg=70.0)

    gain_narrow = _effective_gain(node, ant_narrow, enu_north)
    gain_wide = _effective_gain(node, ant_wide, enu_north)
    assert gain_wide > gain_narrow


def test_effective_gain_colinear_uses_preset_hpbw_35():
    """commercial_omni_6dbi sem hpbw_deg explícito → preset aplica 35° (não 20° legado)."""
    # Verifica via comparação: ganho a 17.5° (metade de 35°) deve estar ~3 dB abaixo do pico.
    from backend.app.solvers.colinear_solver import ColinearSolver
    solver = ColinearSolver()
    g_peak = solver.pattern_g(0.0, 0.0, 915e6)
    g_half = solver.pattern_g(17.5, 0.0, 915e6)
    # 17.5° é o half-power point de 35° HPBW → diferença ≈ 3 dB
    assert abs(g_peak - g_half - 3.0) < 0.5


def test_effective_gain_aperture_hpbw_override():
    """Parabólica com hpbw_deg explícito usa esse HPBW no pattern_g."""
    node = _node_az(0.0)
    enu_off = ENUVector(1000.0, 0.0, 0.0)  # azimuth=90° → offset 90° do boresight Norte

    ant_narrow = AntennaSpec(name="P", type="parabolica", frequency_hz=2.4e9, hpbw_deg=5.0)
    ant_wide = AntennaSpec(name="P", type="parabolica", frequency_hz=2.4e9, hpbw_deg=30.0)

    gain_narrow = _effective_gain(node, ant_narrow, enu_off)
    gain_wide = _effective_gain(node, ant_wide, enu_off)
    assert gain_wide > gain_narrow


def test_effective_gain_none_antenna_returns_zero():
    """antenna=None retorna 0 dBi."""
    assert _effective_gain(_node_no_az(), None, _enu_east()) == 0.0
