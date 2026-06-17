from __future__ import annotations

import math
from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..schemas.antenna_spec import AntennaSpec
from ..solvers.mom_solver import MoMSolver
from ..solvers.aperture_solver import ApertureSolver

C = 3e8  # m/s

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

_mom = MoMSolver()
_aperture = ApertureSolver()


# ── Response model ────────────────────────────────────────────────────────────

class PatternPoint(BaseModel):
    angle_deg: float
    gain_linear: float


class PreviewResult(BaseModel):
    gain_dbi: float
    impedance_ohm: float
    swr: float
    efficiency_pct: float
    radiation_pattern: str
    pattern_data: list[PatternPoint]
    solver_used: str = "rapido"
    is_fixture: bool = False
    warning: Optional[str] = None


# ── Request model (partial — name is optional for preview) ────────────────────

class SandboxPreviewRequest(BaseModel):
    name: str = "Antena"
    type: str
    frequency_hz: float
    geometry: dict[str, Any] = Field(default_factory=dict)
    material: dict[str, Any] = Field(default_factory=dict)
    solver: str = "rapido"


# ── Pattern generators ────────────────────────────────────────────────────────

def _dipole_pattern(kl: float = math.pi, n: int = 360) -> list[PatternPoint]:
    pts = []
    for i in range(n):
        theta = math.radians(i)
        sin_t = math.sin(theta)
        if abs(sin_t) < 1e-9:
            g = 0.0
        else:
            g = ((math.cos(kl / 2 * math.cos(theta)) - math.cos(kl / 2)) / sin_t) ** 2
        pts.append(PatternPoint(angle_deg=float(i), gain_linear=round(g, 6)))
    return pts


def _omni_pattern(n: int = 360) -> list[PatternPoint]:
    return [PatternPoint(angle_deg=float(i), gain_linear=1.0) for i in range(n)]


def _directional_pattern(beamwidth_deg: float, n: int = 360) -> list[PatternPoint]:
    sigma = max(beamwidth_deg / (2 * math.sqrt(2 * math.log(2))), 1.0)
    pts = []
    for i in range(n):
        delta = min(abs(i - 90), 360 - abs(i - 90))
        g = math.exp(-0.5 * (delta / sigma) ** 2)
        pts.append(PatternPoint(angle_deg=float(i), gain_linear=round(g, 6)))
    return pts


def _helix_axial_pattern(n_turns: int, n: int = 360) -> list[PatternPoint]:
    pts = []
    for i in range(n):
        theta = math.radians(i)
        g = max(math.cos(theta), 0.0) ** (2 * max(n_turns, 1))
        pts.append(PatternPoint(angle_deg=float(i), gain_linear=round(g, 6)))
    return pts


# ── Analytic solvers ──────────────────────────────────────────────────────────

def _swr(z_in: float, z0: float = 50.0) -> float:
    if z_in <= 0:
        return 99.0
    gamma = abs(z_in - z0) / (z_in + z0)
    if gamma >= 1.0:
        return 99.0
    return round((1 + gamma) / (1 - gamma), 2)


def _solve_dipolo(req: SandboxPreviewRequest) -> PreviewResult:
    lam = C / req.frequency_hz
    length = req.geometry.get("length_m", lam / 2)
    kl = 2 * math.pi / lam * length  # electrical length

    ratio = kl / math.pi  # 1.0 = half-wave resonance

    # Gain: 2.15 dBi at resonance, drops away from it
    gain_dbi = round(2.15 - 6 * (1 - ratio) ** 2 if ratio <= 1.0 else 2.15 - 2 * (ratio - 1) ** 2, 2)

    # Input resistance: Balanis approximation — peaks ~73 Ω at half-wave
    z_in = max(1.0, 73.0 * min(ratio, 1.0) ** 2 + 20.0 * max(0.0, ratio - 1.0))

    return PreviewResult(
        gain_dbi=gain_dbi,
        impedance_ohm=round(z_in, 1),
        swr=_swr(z_in),
        efficiency_pct=98.0,
        radiation_pattern="omnidirecional",
        pattern_data=_dipole_pattern(kl),
    )


def _solve_monopolo(req: SandboxPreviewRequest) -> PreviewResult:
    lam = C / req.frequency_hz
    height = req.geometry.get("height_m", lam / 4)
    kh = 2 * math.pi / lam * height
    ratio = kh / (math.pi / 2)  # 1.0 = quarter-wave resonance

    gain_dbi = round(5.15 - 6 * (1 - ratio) ** 2 if ratio <= 1.0 else 5.15 - 2 * (ratio - 1) ** 2, 2)
    z_in = max(1.0, 36.5 * min(ratio, 1.0) ** 2)

    return PreviewResult(
        gain_dbi=gain_dbi,
        impedance_ohm=round(z_in, 1),
        swr=_swr(z_in),
        efficiency_pct=97.0,
        radiation_pattern="omnidirecional (hemisférico)",
        pattern_data=_dipole_pattern(kh * 2),
    )


def _solve_helicoidal(req: SandboxPreviewRequest) -> PreviewResult:
    lam = C / req.frequency_hz
    n = int(req.geometry.get("turns", 10))
    C_h = req.geometry.get("circumference_m", lam)
    pitch_deg = req.geometry.get("pitch_angle_deg", 14.0)

    is_axial = 0.75 * lam <= C_h <= 1.33 * lam

    if is_axial:
        gain_lin = max(1.0, 15 * n * (C_h / lam) ** 2 * math.sin(math.radians(pitch_deg)))
        gain_dbi = round(10 * math.log10(gain_lin), 2)
        z_in = 140.0 * C_h / lam
        pattern = _helix_axial_pattern(n)
        pat_label = "direcional (modo axial)"
        warning = None
    else:
        gain_dbi = 2.15
        z_in = 73.0
        pattern = _dipole_pattern()
        pat_label = "omnidirecional (modo normal)"
        warning = "Circunferência fora da faixa de modo axial (0.75λ–1.33λ). Usando aproximação de modo normal."

    return PreviewResult(
        gain_dbi=gain_dbi,
        impedance_ohm=round(z_in, 1),
        swr=_swr(z_in),
        efficiency_pct=92.0,
        radiation_pattern=pat_label,
        pattern_data=pattern,
        warning=warning,
    )


def _solve_parabolica(req: SandboxPreviewRequest) -> PreviewResult:
    lam = C / req.frequency_hz
    D = req.geometry.get("diameter_m", 0.6)
    eta = 0.55

    gain_lin = max(1.0, eta * (math.pi * D / lam) ** 2)
    gain_dbi = round(10 * math.log10(gain_lin), 2)
    beamwidth = 70 * lam / D

    return PreviewResult(
        gain_dbi=gain_dbi,
        impedance_ohm=50.0,
        swr=1.0,
        efficiency_pct=round(eta * 100, 1),
        radiation_pattern=f"direcional (feixe {beamwidth:.1f}°)",
        pattern_data=_directional_pattern(beamwidth),
    )


_FIXTURE = PreviewResult(
    gain_dbi=2.0,
    impedance_ohm=50.0,
    swr=1.0,
    efficiency_pct=90.0,
    radiation_pattern="omnidirecional",
    pattern_data=_omni_pattern(),
    is_fixture=True,
    warning="Tipo sem solver analítico. Fixture fixa retornada.",
)

_SOLVERS = {
    "dipolo": _solve_dipolo,
    "monopolo": _solve_monopolo,
    "helicoidal": _solve_helicoidal,
    "parabolica": _solve_parabolica,
}


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/preview", response_model=PreviewResult)
def preview(req: SandboxPreviewRequest) -> PreviewResult:
    if req.solver in ("padrao", "preciso"):
        return _preview_advanced(req)
    solver = _SOLVERS.get(req.type.lower())
    if solver is None:
        return _FIXTURE
    return solver(req)


def _preview_advanced(req: SandboxPreviewRequest) -> PreviewResult:
    """Modo Padrão/Preciso: MoM para dipolo/monopolo/helicoidal, Abertura para parabólica."""
    antenna_type = req.type.lower()
    if antenna_type == "parabolica":
        sr = _aperture.solve(req)
        pattern_data = _directional_pattern(sr.extra.get("beamwidth_deg", 10.0))
    else:
        sr = _mom.solve(req)
        lam = C / req.frequency_hz
        geometry = req.geometry or {}
        if antenna_type == "helicoidal":
            n = int(geometry.get("turns", 10))
            pattern_data = _helix_axial_pattern(n)
        elif antenna_type == "monopolo":
            height = geometry.get("height_m", lam / 4)
            kh = 2 * math.pi / lam * height
            pattern_data = _dipole_pattern(kh * 2)
        else:
            length = geometry.get("length_m", lam / 2)
            kl = 2 * math.pi / lam * length
            pattern_data = _dipole_pattern(kl)

    return PreviewResult(
        gain_dbi=sr.gain_dbi,
        impedance_ohm=sr.impedance_ohm,
        swr=sr.swr,
        efficiency_pct=sr.efficiency_pct,
        radiation_pattern=sr.radiation_pattern,
        pattern_data=pattern_data,
        solver_used=sr.solver_used,
        warning=sr.warning,
    )
