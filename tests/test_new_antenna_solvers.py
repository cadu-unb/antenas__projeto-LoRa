"""
Testes dos novos solvers: PcbSolver e ColinearSolver.
Valida: ganho, impedância, padrão de radiação e integração via sandbox API.
Inclui testes dos presets canônicos (Fase 3).
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.solvers.pcb_solver import PcbSolver
from backend.app.solvers.colinear_solver import ColinearSolver
from backend.app.domain.antenna_presets import ANTENNA_PRESETS, apply_antenna_defaults
from backend.app.schemas.antenna_spec import AntennaSpec

client = TestClient(app)


# ── PcbSolver — testes unitários ──────────────────────────────────────────────

def test_pcb_gain_at_915mhz():
    solver = PcbSolver()
    g = solver.gain_dbi(915e6)
    assert 0.0 <= g <= 2.0


def test_pcb_gain_increases_with_frequency():
    solver = PcbSolver()
    assert solver.gain_dbi(915e6) > solver.gain_dbi(700e6)


def test_pcb_gain_below_800mhz_is_zero():
    solver = PcbSolver()
    assert solver.gain_dbi(500e6) == 0.0


def test_pcb_impedance_is_50_ohm():
    solver = PcbSolver()
    assert solver.impedance_ohm(915e6) == 50.0


def test_pcb_pattern_penalizes_high_elevation():
    solver = PcbSolver()
    g_low = solver.pattern_g(10.0, 0.0, 915e6)
    g_high = solver.pattern_g(60.0, 0.0, 915e6)
    assert g_low > g_high


def test_pcb_pattern_no_penalty_below_30_deg():
    solver = PcbSolver()
    g_0 = solver.pattern_g(0.0, 0.0, 915e6)
    g_30 = solver.pattern_g(30.0, 0.0, 915e6)
    assert g_0 == g_30


def test_pcb_solve_returns_solver_result():
    from backend.app.solvers.base_solver import SolverResult

    class FakeSpec:
        frequency_hz = 915e6

    solver = PcbSolver()
    result = solver.solve(FakeSpec())
    assert isinstance(result, SolverResult)
    assert result.gain_dbi >= 0.0
    assert result.impedance_ohm == 50.0


# ── ColinearSolver — testes unitários ────────────────────────────────────────

def test_colinear_gain_nominal():
    solver = ColinearSolver()
    assert solver.gain_dbi(915e6) == 6.0


def test_colinear_impedance_is_50_ohm():
    solver = ColinearSolver()
    assert solver.impedance_ohm(915e6) == 50.0


def test_colinear_pattern_peaks_at_horizon():
    solver = ColinearSolver()
    g_horizon = solver.pattern_g(0.0, 0.0, 915e6)
    g_zenith = solver.pattern_g(90.0, 0.0, 915e6)
    assert g_horizon > g_zenith


def test_colinear_pattern_symmetric():
    solver = ColinearSolver()
    g_pos = solver.pattern_g(30.0, 0.0, 915e6)
    g_neg = solver.pattern_g(-30.0, 0.0, 915e6)
    assert abs(g_pos - g_neg) < 0.01


def test_colinear_solve_returns_6dbi():
    from backend.app.solvers.base_solver import SolverResult

    class FakeSpec:
        frequency_hz = 915e6

    solver = ColinearSolver()
    result = solver.solve(FakeSpec())
    assert isinstance(result, SolverResult)
    assert result.gain_dbi == 6.0


# ── Integração via sandbox API ────────────────────────────────────────────────

def test_sandbox_pcb_compact_preview_200():
    r = client.post("/api/v1/sandbox/preview", json={
        "type": "pcb_compact",
        "frequency_hz": 915e6,
        "geometry": {},
        "solver": "rapido",
    })
    assert r.status_code == 200


def test_sandbox_pcb_compact_gain_range():
    r = client.post("/api/v1/sandbox/preview", json={
        "type": "pcb_compact",
        "frequency_hz": 915e6,
        "geometry": {},
        "solver": "rapido",
    })
    gain = r.json()["gain_dbi"]
    assert 0.0 <= gain <= 2.0


def test_sandbox_colinear_preview_200():
    r = client.post("/api/v1/sandbox/preview", json={
        "type": "commercial_omni_6dbi",
        "frequency_hz": 915e6,
        "geometry": {},
        "solver": "rapido",
    })
    assert r.status_code == 200


def test_sandbox_colinear_gain_is_6():
    r = client.post("/api/v1/sandbox/preview", json={
        "type": "commercial_omni_6dbi",
        "frequency_hz": 915e6,
        "geometry": {},
        "solver": "rapido",
    })
    assert r.json()["gain_dbi"] == 6.0


def test_sandbox_colinear_not_fixture():
    r = client.post("/api/v1/sandbox/preview", json={
        "type": "commercial_omni_6dbi",
        "frequency_hz": 915e6,
        "geometry": {},
        "solver": "rapido",
    })
    assert r.json()["is_fixture"] is False


# ── Presets canônicos (Fase 3) ────────────────────────────────────────────────

_EXPECTED_PRESETS = {
    "dipolo":               {"gmax_dbi": 2.15,  "hpbw_deg": 78.0,  "is_directional": False, "pattern_model": "dipole",           "practicality_score": 8.0,  "multi_direction_score": 9.0},
    "monopolo":             {"gmax_dbi": 5.15,  "hpbw_deg": 55.0,  "is_directional": False, "pattern_model": "monopole",         "practicality_score": 7.0,  "multi_direction_score": 8.0},
    "helicoidal":           {"gmax_dbi": 11.0,  "hpbw_deg": 55.0,  "is_directional": True,  "pattern_model": "helical",          "practicality_score": 5.0,  "multi_direction_score": 3.0},
    "parabolica":           {"gmax_dbi": 20.0,  "hpbw_deg": 18.0,  "is_directional": True,  "pattern_model": "parabolic",        "practicality_score": 2.0,  "multi_direction_score": 1.0},
    "pcb_compact":          {"gmax_dbi": 1.0,   "hpbw_deg": 120.0, "is_directional": False, "pattern_model": "pcb",              "practicality_score": 10.0, "multi_direction_score": 7.0},
    "commercial_omni_6dbi": {"gmax_dbi": 6.0,   "hpbw_deg": 35.0,  "is_directional": False, "pattern_model": "omni_colinear",    "practicality_score": 9.0,  "multi_direction_score": 8.0},
}


def test_all_six_types_have_presets():
    assert set(ANTENNA_PRESETS.keys()) == set(_EXPECTED_PRESETS.keys())


@pytest.mark.parametrize("antenna_type,expected", _EXPECTED_PRESETS.items())
def test_preset_values(antenna_type, expected):
    preset = ANTENNA_PRESETS[antenna_type]
    for key, value in expected.items():
        assert preset[key] == value, f"{antenna_type}.{key}: expected {value}, got {preset[key]}"


@pytest.mark.parametrize("antenna_type", list(_EXPECTED_PRESETS.keys()))
def test_preset_has_all_required_keys(antenna_type):
    required = {"gmax_dbi", "hpbw_deg", "polarization", "is_directional",
                "pattern_model", "practicality_score", "multi_direction_score"}
    assert required <= set(ANTENNA_PRESETS[antenna_type].keys())


# ── apply_antenna_defaults ────────────────────────────────────────────────────

def test_minimal_spec_gets_all_preset_fields():
    spec = AntennaSpec(name="X", type="dipolo", frequency_hz=915e6)
    result = apply_antenna_defaults(spec)
    assert result.spec.gmax_dbi == 2.15
    assert result.spec.hpbw_deg == 78.0
    assert result.spec.is_directional is False
    assert result.spec.pattern_model == "dipole"


def test_apply_defaults_does_not_mutate_input():
    spec = AntennaSpec(name="X", type="dipolo", frequency_hz=915e6)
    apply_antenna_defaults(spec)
    assert spec.gmax_dbi is None  # original unchanged


def test_explicit_user_value_not_overridden():
    spec = AntennaSpec(name="X", type="dipolo", frequency_hz=915e6, gmax_dbi=3.0)
    result = apply_antenna_defaults(spec)
    assert result.spec.gmax_dbi == 3.0
    assert "gmax_dbi" not in result.from_preset


def test_from_preset_tracks_filled_fields():
    spec = AntennaSpec(name="X", type="dipolo", frequency_hz=915e6)
    result = apply_antenna_defaults(spec)
    assert "gmax_dbi" in result.from_preset
    assert "hpbw_deg" in result.from_preset
    assert "is_directional" in result.from_preset


def test_from_preset_excludes_user_set_fields():
    spec = AntennaSpec(name="X", type="monopolo", frequency_hz=915e6, hpbw_deg=45.0)
    result = apply_antenna_defaults(spec)
    assert "hpbw_deg" not in result.from_preset
    assert result.spec.hpbw_deg == 45.0


def test_unknown_type_returns_spec_unchanged():
    spec = AntennaSpec(name="X", type="yagi", frequency_hz=915e6)
    result = apply_antenna_defaults(spec)
    assert result.spec is spec
    assert result.from_preset == frozenset()


def test_schema_version_bumped_after_apply_defaults():
    spec = AntennaSpec(name="X", type="dipolo", frequency_hz=915e6)
    assert spec.schema_version == "1.0"
    result = apply_antenna_defaults(spec)
    assert result.spec.schema_version == "2.0"


def test_pcb_gmax_from_preset_is_flagged():
    """pcb_compact gmax_dbi=1 from preset must be distinguishable from user-set.
    Phase 4 _effective_gain() will skip this override for pcb_compact."""
    spec = AntennaSpec(name="X", type="pcb_compact", frequency_hz=915e6)
    result = apply_antenna_defaults(spec)
    assert result.spec.gmax_dbi == 1.0
    assert "gmax_dbi" in result.from_preset  # Phase 4 must check this


def test_pcb_explicit_gmax_not_from_preset():
    spec = AntennaSpec(name="X", type="pcb_compact", frequency_hz=915e6, gmax_dbi=1.5)
    result = apply_antenna_defaults(spec)
    assert result.spec.gmax_dbi == 1.5
    assert "gmax_dbi" not in result.from_preset


@pytest.mark.parametrize("antenna_type", list(_EXPECTED_PRESETS.keys()))
def test_minimal_spec_for_each_type(antenna_type):
    spec = AntennaSpec(name="X", type=antenna_type, frequency_hz=915e6)
    result = apply_antenna_defaults(spec)
    assert result.spec.gmax_dbi is not None
    assert result.spec.hpbw_deg is not None
    assert result.spec.is_directional is not None
