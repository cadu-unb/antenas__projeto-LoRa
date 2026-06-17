"""
Testes dos solvers avançados — Fase 6.

Cenário de referência (dipolo λ/2, 915 MHz):
  Comprimento = λ/2 = 300/915 MHz / 2 ≈ 0.164 m
  Ganho esperado analítico: 2.15 dBi (referência: Balanis, "Antenna Theory", 3ª ed., p. 455)
  Intervalo aceito pelo checkpoint: 1.8–2.5 dBi

Cenário de referência (Okumura-Hata urbano grande):
  f=900 MHz, h_b=30 m, h_m=1.5 m, d=1 km, urban_large
  Perda esperada: 126.43 dB (Hata 1980, Eq. 1, com a(h_m)≈0 para grande cidade)
  Tolerância: ±1 dB
"""
import asyncio
import os
from types import SimpleNamespace

import pytest

from backend.app.solvers.base_solver import BaseSolver, SolverResult
from backend.app.solvers.mom_solver import MoMSolver
from backend.app.solvers.aperture_solver import ApertureSolver
from backend.app.solvers.okumura_hata import okumura_hata
from backend.app.solvers.longley_rice import longley_rice
from backend.app.workers.resource_guard import ResourceGuard, ResourceLimitError
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


# ── BaseSolver ────────────────────────────────────────────────────────────────

def test_base_solver_is_abstract():
    with pytest.raises(TypeError):
        BaseSolver()  # type: ignore


def test_base_solver_importable():
    assert issubclass(MoMSolver, BaseSolver)
    assert issubclass(ApertureSolver, BaseSolver)


# ── MoMSolver — dipolo λ/2 ──────────────────────────────────────────────────

def _dipolo_spec(freq_hz=915e6, length_m=None):
    """Cenário de referência: dipolo a 915 MHz (LoRa AU/BR)."""
    lam = 3e8 / freq_hz
    return SimpleNamespace(
        type="dipolo",
        frequency_hz=freq_hz,
        geometry={"length_m": length_m if length_m else lam / 2},
    )


def test_dipolo_meia_onda_ganho_intervalo():
    """Dipolo λ/2 deve retornar ganho entre 1.8 dBi e 2.5 dBi."""
    solver = MoMSolver()
    result = solver.solve(_dipolo_spec())
    assert 1.8 <= result.gain_dbi <= 2.5, (
        f"Ganho {result.gain_dbi} dBi fora do intervalo 1.8–2.5 dBi. "
        f"Solver: {result.solver_used}"
    )


def test_dipolo_resultado_e_solver_result():
    solver = MoMSolver()
    r = solver.solve(_dipolo_spec())
    assert isinstance(r, SolverResult)


def test_dipolo_swr_positivo():
    solver = MoMSolver()
    r = solver.solve(_dipolo_spec())
    assert r.swr >= 1.0


def test_dipolo_impedancia_positiva():
    solver = MoMSolver()
    r = solver.solve(_dipolo_spec())
    assert r.impedance_ohm > 0


@pytest.mark.skipif(
    __import__("backend.app.solvers.mom_solver", fromlist=["_PYNEC_AVAILABLE"])._PYNEC_AVAILABLE,
    reason="PyNEC disponível — fallback não ativo neste ambiente",
)
def test_mom_solver_fallback_sem_pynec():
    """Quando PyNEC ausente, MoMSolver usa fallback analítico."""
    from backend.app.solvers import mom_solver
    solver = MoMSolver()
    r = solver.solve(_dipolo_spec())
    assert r.solver_used == "mom_analitico"
    assert r.warning is not None
    assert "PyNEC" in r.warning


@pytest.mark.skipif(
    not __import__("backend.app.solvers.mom_solver", fromlist=["_PYNEC_AVAILABLE"])._PYNEC_AVAILABLE,
    reason="PyNEC não instalado neste ambiente",
)
def test_mom_solver_pynec_quando_disponivel():
    """Quando PyNEC instalado, MoMSolver usa NEC-2 real."""
    solver = MoMSolver()
    r = solver.solve(_dipolo_spec())
    assert r.solver_used == "mom_pynec"
    assert r.warning is None
    assert 1.8 <= r.gain_dbi <= 2.5


def test_mom_solver_monopolo():
    solver = MoMSolver()
    spec = SimpleNamespace(type="monopolo", frequency_hz=915e6, geometry={})
    r = solver.solve(spec)
    assert r.gain_dbi > 0


def test_mom_solver_helicoidal_axial():
    solver = MoMSolver()
    lam = 3e8 / 915e6
    spec = SimpleNamespace(
        type="helicoidal",
        frequency_hz=915e6,
        geometry={"turns": 10, "circumference_m": lam, "pitch_angle_deg": 14.0},
    )
    r = solver.solve(spec)
    assert r.gain_dbi > 0


# ── ApertureSolver ────────────────────────────────────────────────────────────

def test_aperture_solver_used():
    """Parabólica deve usar aperture solver, não MoM."""
    solver = ApertureSolver()
    spec = SimpleNamespace(frequency_hz=2.4e9, geometry={"diameter_m": 0.6})
    r = solver.solve(spec)
    assert r.solver_used == "abertura"


def test_aperture_ganho_antena_grande():
    """Parabólica 1.2 m a 2.4 GHz deve ter ganho > 20 dBi."""
    solver = ApertureSolver()
    spec = SimpleNamespace(frequency_hz=2.4e9, geometry={"diameter_m": 1.2, "efficiency": 0.55})
    r = solver.solve(spec)
    assert r.gain_dbi > 20.0


def test_aperture_extra_fields():
    solver = ApertureSolver()
    spec = SimpleNamespace(frequency_hz=915e6, geometry={"diameter_m": 0.6})
    r = solver.solve(spec)
    assert "beamwidth_deg" in r.extra
    assert "diameter_m" in r.extra


# ── Okumura-Hata ──────────────────────────────────────────────────────────────

def test_okumura_hata_referencia_urban_large():
    """Referência: f=900 MHz, h_b=30 m, h_m=1.5 m, d=1 km, urban_large → 126.43 dB ±1 dB."""
    r = okumura_hata(
        frequency_mhz=900,
        dist_km=1,
        h_base_m=30,
        h_mobile_m=1.5,
        environment="urban_large",
    )
    assert abs(r.path_loss_db - 126.43) <= 1.0, (
        f"Perda {r.path_loss_db} dB fora de 126.43 ±1 dB"
    )


def test_okumura_hata_tipo_resultado():
    from backend.app.solvers.okumura_hata import OkumuraHataResult
    r = okumura_hata(900, 5, 50, 2, "suburban")
    assert isinstance(r, OkumuraHataResult)


def test_okumura_hata_perda_positiva():
    r = okumura_hata(900, 5, 50, 2, "urban_large")
    assert r.path_loss_db > 0


def test_okumura_hata_suburbano_menor_que_urbano():
    """Suburbano deve ter menor perda que urbano grande na mesma rota."""
    urban = okumura_hata(900, 5, 50, 2, "urban_large")
    suburban = okumura_hata(900, 5, 50, 2, "suburban")
    assert suburban.path_loss_db < urban.path_loss_db


def test_okumura_hata_aviso_fora_do_intervalo():
    r = okumura_hata(frequency_mhz=100, dist_km=1, h_base_m=30, h_mobile_m=1.5)
    assert r.warning is not None


def test_okumura_hata_sem_aviso_dentro_do_intervalo():
    r = okumura_hata(frequency_mhz=900, dist_km=5, h_base_m=50, h_mobile_m=2.0)
    assert r.warning is None


# ── Longley-Rice ─────────────────────────────────────────────────────────────

def test_longley_rice_retorna_valor_positivo():
    r = longley_rice(frequency_mhz=915, dist_km=10, h_tx_m=30, h_rx_m=2, delta_h_m=50)
    assert r.path_loss_db > 0


def test_longley_rice_los_vs_nlos():
    """LOS (distância curta) deve ter menor perda que NLOS (distância longa)."""
    r_los = longley_rice(915, 5, 30, 10, delta_h_m=50)
    r_nlos = longley_rice(915, 50, 5, 2, delta_h_m=50)
    assert r_nlos.path_loss_db > r_los.path_loss_db


def test_longley_rice_campo_los():
    from backend.app.solvers.longley_rice import LongleyRiceResult
    r = longley_rice(915, 1, 50, 10)
    assert isinstance(r, LongleyRiceResult)
    assert r.los is True


def test_longley_rice_aviso_frequencia_invalida():
    r = longley_rice(frequency_mhz=5, dist_km=10, h_tx_m=30, h_rx_m=2)
    assert r.warning is not None


# ── ResourceGuard — limite de RAM ─────────────────────────────────────────────

def test_resource_guard_memoria_acima_do_limite():
    """Simulação com RAM simulada > 25 GB deve gerar FAILED_MEMORY_LIMIT."""
    guard = ResourceGuard("test-mem-limit", _ram_override_gb=30.0)
    with pytest.raises(ResourceLimitError) as exc_info:
        guard.check_ram()
    assert exc_info.value.code == "FAILED_MEMORY_LIMIT"
    assert "FAILED_MEMORY_LIMIT" in exc_info.value.code


def test_resource_guard_memoria_abaixo_do_limite():
    """RAM normal não deve levantar erro."""
    guard = ResourceGuard("test-mem-ok", _ram_override_gb=1.0)
    guard.check_ram()  # não deve levantar


def test_resource_guard_mensagem_memoria_acionavel():
    guard = ResourceGuard("test-mem-msg", _ram_override_gb=26.0)
    with pytest.raises(ResourceLimitError) as exc_info:
        guard.check_ram()
    assert "GB" in exc_info.value.message


# ── ResourceGuard — limite de tempo ──────────────────────────────────────────

def test_resource_guard_tempo_acima_do_limite():
    """Simulação que demora mais que o timeout deve gerar FAILED_TIME_LIMIT."""
    guard = ResourceGuard("test-time-limit", _timeout_override_s=0.1)

    async def _slow():
        await asyncio.sleep(10)

    with pytest.raises(ResourceLimitError) as exc_info:
        asyncio.run(guard.run_guarded(_slow()))
    assert exc_info.value.code == "FAILED_TIME_LIMIT"


def test_resource_guard_tempo_ok():
    """Simulação rápida deve completar normalmente."""
    guard = ResourceGuard("test-time-ok", _timeout_override_s=5.0)

    async def _fast():
        return 42

    result = asyncio.run(guard.run_guarded(_fast()))
    assert result == 42


# ── ResourceGuard — log JSONL ─────────────────────────────────────────────────

def test_resource_guard_log_persiste():
    """Log deve ser gravado mesmo quando simulação é abortada por timeout."""
    import json

    guard = ResourceGuard("test-log-persist", _timeout_override_s=0.1)

    async def _slow():
        await asyncio.sleep(10)

    with pytest.raises(ResourceLimitError):
        asyncio.run(guard.run_guarded(_slow()))

    assert os.path.isfile(guard.log_path), "log.jsonl não foi criado"
    with open(guard.log_path, encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    events = [l["event"] for l in lines]
    assert "START" in events
    assert "FAILED_TIME_LIMIT" in events


def test_resource_guard_log_criado_em_path_correto():
    guard = ResourceGuard("test-log-path", _timeout_override_s=5.0)

    async def _fast():
        return True

    asyncio.run(guard.run_guarded(_fast()))
    assert os.path.isfile(guard.log_path)
    assert "test-log-path" in guard.log_path
    assert guard.log_path.endswith("log.jsonl")


# ── Sandbox endpoint — modos Padrão/Preciso ───────────────────────────────────

def test_sandbox_padrao_dipolo():
    r = client.post(
        "/api/v1/sandbox/preview",
        json={"type": "dipolo", "frequency_hz": 915e6, "solver": "padrao"},
    )
    assert r.status_code == 200
    data = r.json()
    assert 1.8 <= data["gain_dbi"] <= 2.5


def test_sandbox_preciso_dipolo():
    r = client.post(
        "/api/v1/sandbox/preview",
        json={"type": "dipolo", "frequency_hz": 915e6, "solver": "preciso"},
    )
    assert r.status_code == 200
    assert "mom" in r.json()["solver_used"]


def test_sandbox_padrao_parabolica_usa_abertura():
    r = client.post(
        "/api/v1/sandbox/preview",
        json={
            "type": "parabolica",
            "frequency_hz": 2.4e9,
            "geometry": {"diameter_m": 0.6},
            "solver": "padrao",
        },
    )
    assert r.status_code == 200
    assert r.json()["solver_used"] == "abertura"


def test_sandbox_rapido_nao_afetado():
    """Modo Rápido existente não deve ser alterado."""
    r = client.post(
        "/api/v1/sandbox/preview",
        json={"type": "dipolo", "frequency_hz": 915e6, "solver": "rapido"},
    )
    assert r.status_code == 200
