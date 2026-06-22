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
        eta = _realized_efficiency(kwargs, lam)
        passive_loss_db = _passive_loss_db(kwargs)
        gain_lin = max(1.0, eta * (math.pi * D / lam) ** 2)
        gain_lin *= 10 ** (-passive_loss_db / 10)
        return round(10 * math.log10(gain_lin), 2)

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """Padrão gaussiano: G(θ) ≈ G_max - 12·(θ/HPBW)².

        kwargs:
            gmax_dbi  — override de ganho máximo (default: calculado por abertura).
            hpbw_deg  — override de HPBW (default: 70λ/D empírico).
        """
        gmax_override = kwargs.get("gmax_dbi", None)
        g_max = gmax_override if gmax_override is not None else self.gain_dbi(freq_hz, **kwargs)
        hpbw_override = kwargs.get("hpbw_deg", None)
        if hpbw_override is not None:
            hpbw_deg = hpbw_override
        else:
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
        f = geometry.get("focal_length_m", D * 0.367)
        base_eta = geometry.get("efficiency", 0.55)
        blockage_pct = geometry.get("blockage_pct", 0.0)
        surface_rms_mm = geometry.get("surface_rms_mm", 0.0)
        passive_loss_db = _passive_loss_db(geometry)
        eta = _realized_efficiency(geometry, lam)

        gain_lin = max(1.0, eta * (math.pi * D / lam) ** 2)
        gain_lin *= 10 ** (-passive_loss_db / 10)
        gain_dbi = round(10 * math.log10(gain_lin), 2)
        beamwidth = 70 * lam / D  # HPBW empírico em graus
        first_null = 140 * lam / D
        aperture_area = math.pi * (D / 2) ** 2
        effective_area = eta * aperture_area
        far_field = 2 * D ** 2 / lam
        dish_depth = D ** 2 / (16 * f) if f > 0 else 0.0
        f_d_ratio = f / D if D > 0 else 0.0
        surface_efficiency = _surface_efficiency(surface_rms_mm, lam)
        blockage_efficiency = _blockage_efficiency(blockage_pct)
        warning = _parabolic_warning(D, lam, f_d_ratio, eta)

        return SolverResult(
            gain_dbi=gain_dbi,
            impedance_ohm=50.0,
            swr=1.0,
            efficiency_pct=round(eta * 100, 1),
            radiation_pattern=f"direcional (feixe {beamwidth:.1f}°)",
            solver_used="abertura",
            warning=warning,
            extra={
                "aperture_area_m2": round(aperture_area, 4),
                "base_efficiency_pct": round(base_eta * 100, 1),
                "blockage_efficiency_pct": round(blockage_efficiency * 100, 1),
                "blockage_loss_db": round(_loss_from_efficiency(blockage_efficiency), 2),
                "beamwidth_deg": round(beamwidth, 2),
                "diameter_m": round(D, 4),
                "dish_depth_m": round(dish_depth, 4),
                "effective_area_m2": round(effective_area, 4),
                "far_field_m": round(far_field, 2),
                "first_null_deg": round(first_null, 2),
                "focal_length_m": round(f, 4),
                "f_d_ratio": round(f_d_ratio, 3),
                "passive_loss_db": round(passive_loss_db, 2),
                "realized_efficiency_pct": round(eta * 100, 1),
                "surface_efficiency_pct": round(surface_efficiency * 100, 1),
                "surface_loss_db": round(_loss_from_efficiency(surface_efficiency), 2),
                "surface_rms_mm": round(surface_rms_mm, 3),
                "wavelength_m": round(lam, 4),
            },
        )


def _surface_efficiency(surface_rms_mm: float, wavelength_m: float) -> float:
    sigma_m = max(surface_rms_mm, 0.0) / 1000
    if sigma_m == 0:
        return 1.0
    return math.exp(-(4 * math.pi * sigma_m / wavelength_m) ** 2)


def _blockage_efficiency(blockage_pct: float) -> float:
    return max(0.0, min(1.0, 1 - blockage_pct / 100))


def _loss_from_efficiency(efficiency: float) -> float:
    if efficiency <= 0:
        return 99.0
    return -10 * math.log10(efficiency)


def _passive_loss_db(geometry: dict) -> float:
    return max(0.0, geometry.get("feed_loss_db", 0.0)) + max(0.0, geometry.get("radome_loss_db", 0.0))


def _realized_efficiency(geometry: dict, wavelength_m: float) -> float:
    base_eta = max(0.01, min(0.95, geometry.get("efficiency", 0.55)))
    surface_eta = _surface_efficiency(geometry.get("surface_rms_mm", 0.0), wavelength_m)
    blockage_eta = _blockage_efficiency(geometry.get("blockage_pct", 0.0))
    return max(0.01, base_eta * surface_eta * blockage_eta)


def _parabolic_warning(diameter_m: float, wavelength_m: float, f_d_ratio: float, efficiency: float) -> str | None:
    warnings = []
    if diameter_m / wavelength_m < 2:
        warnings.append("D/λ baixo: a aproximação de abertura fica fraca para refletores pequenos.")
    if not (0.25 <= f_d_ratio <= 0.6):
        warnings.append("f/D fora da faixa prática típica (0,25–0,60).")
    if efficiency < 0.25:
        warnings.append("Eficiência realizada baixa: verifique bloqueio, superfície e perdas passivas.")
    return " ".join(warnings) if warnings else None
