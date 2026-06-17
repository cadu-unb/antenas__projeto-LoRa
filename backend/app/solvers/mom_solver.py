import logging
import math
from typing import Any, Optional

from .base_solver import BaseSolver, SolverResult

logger = logging.getLogger(__name__)

try:
    import PyNEC  # type: ignore
    _PYNEC_AVAILABLE = True
except ImportError:
    _PYNEC_AVAILABLE = False
    logger.warning(
        "PyNEC não disponível — MoMSolver usando fallback analítico. "
        "Instale com: pip install PyNEC  (requer compilador C)"
    )

C = 3e8  # m/s


def _swr(z_in: float, z0: float = 50.0) -> float:
    if z_in <= 0:
        return 99.0
    gamma = abs(z_in - z0) / (z_in + z0)
    return 99.0 if gamma >= 1.0 else round((1 + gamma) / (1 - gamma), 2)


class MoMSolver(BaseSolver):
    """Method of Moments via PyNEC para dipolo, monopolo e helicoidal.

    Se PyNEC não estiver disponível, retorna resultado analítico equivalente
    ao modo Rápido + warning no campo SolverResult.warning.
    Antenas suportadas: dipolo, monopolo, helicoidal.
    Parabólica deve usar ApertureSolver — não MoM.
    """

    def solve(self, spec: Any) -> SolverResult:
        if _PYNEC_AVAILABLE:
            return self._pynec_solve(spec)
        return self._analytic_fallback(spec)

    def _pynec_solve(self, spec: Any) -> SolverResult:
        antenna_type = getattr(spec, "type", "dipolo").lower()
        freq_hz = getattr(spec, "frequency_hz", 915e6)
        geometry = getattr(spec, "geometry", {})
        lam = C / freq_hz

        try:
            ctx = PyNEC.nec_context()
            geo = ctx.get_geometry()

            if antenna_type == "dipolo":
                length = geometry.get("length_m", lam / 2)
                half = length / 2
                geo.wire(1, 21, 0.0, 0.0, -half, 0.0, 0.0, half, lam / 200, 1.0, 1.0)
                ctx.geometry_complete(0)
                ctx.ex_card(0, 1, 11, 0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            elif antenna_type == "monopolo":
                height = geometry.get("height_m", lam / 4)
                geo.wire(1, 11, 0.0, 0.0, 0.0, 0.0, 0.0, height, lam / 200, 1.0, 1.0)
                ctx.geometry_complete(1)
                ctx.ex_card(0, 1, 1, 0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            else:
                # helicoidal — aproximação NEC via múltiplos wires é instável;
                # usar fallback analítico diretamente
                return self._analytic_fallback(spec)

            ctx.fr_card(0, 1, freq_hz / 1e6, 0.0)
            ctx.rp_card(0, 37, 73, 0, 5, 0.0, 0.0, 5.0, 5.0, 0.0, 0.0, 0.0, 0.0)

            ipt = ctx.get_input_parameters(0)
            z = complex(ipt.get_impedance())
            z_in = z.real if z.real > 0 else 50.0

            rp = ctx.get_radiation_pattern(0)
            gains = rp.get_gain()
            gain_dbi = float(max(gains)) if len(gains) > 0 else 2.15

            return SolverResult(
                gain_dbi=round(gain_dbi, 2),
                impedance_ohm=round(z_in, 1),
                swr=_swr(z_in),
                efficiency_pct=98.0,
                radiation_pattern="omnidirecional",
                solver_used="mom_pynec",
            )
        except Exception as exc:
            logger.warning("PyNEC falhou (%s) — fallback analítico", exc)
            result = self._analytic_fallback(spec)
            result.warning = f"PyNEC erro interno: {exc}. Resultado analítico."
            return result

    def _analytic_fallback(self, spec: Any) -> SolverResult:
        antenna_type = getattr(spec, "type", "dipolo").lower()
        freq_hz = getattr(spec, "frequency_hz", 915e6)
        geometry = getattr(spec, "geometry", {})
        lam = C / freq_hz

        warn: Optional[str] = None if _PYNEC_AVAILABLE else "PyNEC não disponível — resultado analítico."

        if antenna_type == "monopolo":
            height = geometry.get("height_m", lam / 4)
            kh = 2 * math.pi / lam * height
            ratio = kh / (math.pi / 2)
            gain_dbi = round(
                5.15 - 6 * (1 - ratio) ** 2 if ratio <= 1.0 else 5.15 - 2 * (ratio - 1) ** 2, 2
            )
            z_in = max(1.0, 36.5 * min(ratio, 1.0) ** 2)
            pattern = "omnidirecional (hemisférico)"

        elif antenna_type == "helicoidal":
            n = int(geometry.get("turns", 10))
            C_h = geometry.get("circumference_m", lam)
            pitch_deg = geometry.get("pitch_angle_deg", 14.0)
            is_axial = 0.75 * lam <= C_h <= 1.33 * lam
            if is_axial:
                gain_lin = max(1.0, 15 * n * (C_h / lam) ** 2 * math.sin(math.radians(pitch_deg)))
                gain_dbi = round(10 * math.log10(gain_lin), 2)
                z_in = 140.0 * C_h / lam
                pattern = "direcional (modo axial)"
            else:
                gain_dbi = 2.15
                z_in = 73.0
                pattern = "omnidirecional (modo normal)"
                extra_w = "Modo normal (circunferência fora de 0.75λ–1.33λ)."
                warn = f"{warn} {extra_w}" if warn else extra_w

        else:  # dipolo (default)
            length = geometry.get("length_m", lam / 2)
            kl = 2 * math.pi / lam * length
            ratio = kl / math.pi
            gain_dbi = round(
                2.15 - 6 * (1 - ratio) ** 2 if ratio <= 1.0 else 2.15 - 2 * (ratio - 1) ** 2, 2
            )
            z_in = max(1.0, 73.0 * min(ratio, 1.0) ** 2 + 20.0 * max(0.0, ratio - 1.0))
            pattern = "omnidirecional"

        return SolverResult(
            gain_dbi=gain_dbi,
            impedance_ohm=round(z_in, 1),
            swr=_swr(z_in),
            efficiency_pct=98.0,
            radiation_pattern=pattern,
            solver_used="mom_analitico",
            warning=warn,
        )
