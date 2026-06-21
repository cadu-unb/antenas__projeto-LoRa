"""
Testes dos novos solvers: PcbSolver e ColinearSolver.
Valida: ganho, impedância, padrão de radiação e integração via sandbox API.
"""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.solvers.pcb_solver import PcbSolver
from backend.app.solvers.colinear_solver import ColinearSolver

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
