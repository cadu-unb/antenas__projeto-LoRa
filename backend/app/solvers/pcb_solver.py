import math
from typing import Any

from .base_solver import BaseSolver, SolverResult


class PcbSolver(BaseSolver):
    """Antena integrada ao PCB — quasi-omnidirecional, G ~ 0–2 dBi."""

    antenna_type = "pcb_compact"

    def gain_dbi(self, freq_hz: float, **kwargs) -> float:
        freq_mhz = freq_hz / 1e6
        if freq_mhz < 800:
            return 0.0
        elif freq_mhz < 1000:
            return 1.5
        return 2.0

    def impedance_ohm(self, freq_hz: float) -> float:
        return 50.0

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """Quasi-omni com penalidade de elevação acima de 30°.

        kwargs:
            gmax_dbi — override de ganho máximo; usado somente quando usuário definiu
                       explicitamente (não quando veio do preset; checado em _effective_gain).
        """
        gmax_override = kwargs.get("gmax_dbi", None)
        g_max = gmax_override if gmax_override is not None else self.gain_dbi(freq_hz)
        elev_penalty = max(0.0, abs(theta_deg) - 30) * 0.05
        return g_max - elev_penalty

    def solve(self, spec: Any) -> SolverResult:
        freq_hz = getattr(spec, "frequency_hz", 915e6)
        g = self.gain_dbi(freq_hz)
        return SolverResult(
            gain_dbi=round(g, 2),
            impedance_ohm=50.0,
            swr=1.0,
            efficiency_pct=85.0,
            radiation_pattern="quasi-omnidirecional (PCB)",
            solver_used="pcb_analitico",
        )
