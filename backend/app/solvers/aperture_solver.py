import math
from typing import Any

from .base_solver import BaseSolver, SolverResult

C = 3e8  # m/s


class ApertureSolver(BaseSolver):
    """Solver de aproximação de abertura para antenas parabólicas.

    Método: G = η × (π D / λ)²  onde η é a eficiência de abertura.
    Válido para D >> λ (regime de óptica geométrica).
    Não usar MoM para parabólicas — corrente superficial é ineficiente
    e numericamente instável para grandes refletores.

    Referência: Balanis, "Antenna Theory: Analysis and Design", Cap. 15.
    """

    def gain_dbi(self, freq_hz: float, **kwargs) -> float:
        lam = C / freq_hz
        D = kwargs.get("diameter_m", 0.3)
        eta = kwargs.get("efficiency", 0.55)
        gain_lin = max(1.0, eta * (math.pi * D / lam) ** 2)
        return round(10 * math.log10(gain_lin), 2)

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """Padrão gaussiano: G(θ) ≈ G_max - 12·(θ/HPBW)². HPBW = 70λ/D."""
        g_max = self.gain_dbi(freq_hz, **kwargs)
        lam = C / freq_hz
        D = kwargs.get("diameter_m", 0.3)
        hpbw_deg = 70 * lam / D
        attenuation_db = 12 * (theta_deg / hpbw_deg) ** 2
        return g_max - attenuation_db

    def solve(self, spec: Any) -> SolverResult:
        freq_hz = getattr(spec, "frequency_hz", 2.4e9)
        geometry = getattr(spec, "geometry", {})
        lam = C / freq_hz
        D = geometry.get("diameter_m", 0.6)
        eta = geometry.get("efficiency", 0.55)

        gain_lin = max(1.0, eta * (math.pi * D / lam) ** 2)
        gain_dbi = round(10 * math.log10(gain_lin), 2)
        beamwidth = 70 * lam / D  # HPBW empírico em graus

        return SolverResult(
            gain_dbi=gain_dbi,
            impedance_ohm=50.0,
            swr=1.0,
            efficiency_pct=round(eta * 100, 1),
            radiation_pattern=f"direcional (feixe {beamwidth:.1f}°)",
            solver_used="abertura",
            extra={
                "beamwidth_deg": round(beamwidth, 1),
                "diameter_m": D,
                "wavelength_m": round(lam, 4),
                "efficiency": eta,
            },
        )
