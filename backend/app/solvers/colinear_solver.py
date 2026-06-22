import math
from typing import Any

from .base_solver import BaseSolver, SolverResult


class ColinearSolver(BaseSolver):
    """Antena colinear comercial — 6 dBi, padrão estreito em elevação, omni em azimute."""

    antenna_type = "commercial_omni_6dbi"

    def gain_dbi(self, freq_hz: float, **kwargs) -> float:
        return 6.0

    def impedance_ohm(self, freq_hz: float) -> float:
        return 50.0

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """Padrão colinear: gaussiano em elevação.

        theta: ângulo de elevação (0 = horizonte, 90 = zenith).
        kwargs:
            gmax_dbi  — override de ganho máximo (default: 6.0 dBi do solver).
            hpbw_deg  — override de HPBW (default: 35° alinhado ao MATLAB; 20° era legado).
        """
        g_max = kwargs.get("gmax_dbi", self.gain_dbi(freq_hz))
        hpbw_elev = kwargs.get("hpbw_deg", 35.0)
        sigma = hpbw_elev / (2 * math.sqrt(2 * math.log(2)))
        g_linear = (10 ** (g_max / 10)) * math.exp(-(theta_deg ** 2) / (2 * sigma ** 2))
        return 10 * math.log10(max(g_linear, 1e-10))

    def solve(self, spec: Any) -> SolverResult:
        freq_hz = getattr(spec, "frequency_hz", 915e6)
        return SolverResult(
            gain_dbi=6.0,
            impedance_ohm=50.0,
            swr=1.0,
            efficiency_pct=95.0,
            radiation_pattern="omnidirecional (colinear 6 dBi)",
            solver_used="colinear_analitico",
        )
