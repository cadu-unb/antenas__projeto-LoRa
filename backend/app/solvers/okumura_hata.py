"""Modelo empírico de perda de percurso Okumura-Hata.

Referência: M. Hata, "Empirical Formula for Propagation Loss in Land Mobile
Radio Services", IEEE Trans. Veh. Technol., vol. 29, pp. 317–325, 1980.

Intervalo de validade:
  Frequência : 150–1500 MHz
  Distância  : 1–20 km
  h_base     : 30–200 m
  h_mobile   : 1–10 m
"""
import math
from typing import Literal, Optional

from pydantic import BaseModel


class OkumuraHataResult(BaseModel):
    path_loss_db: float
    environment: str
    frequency_mhz: float
    dist_km: float
    h_base_m: float
    h_mobile_m: float
    model: str = "okumura_hata"
    warning: Optional[str] = None


def okumura_hata(
    frequency_mhz: float,
    dist_km: float,
    h_base_m: float,
    h_mobile_m: float,
    environment: Literal["urban_large", "urban_small", "suburban", "open"] = "urban_large",
) -> OkumuraHataResult:
    """Calcula perda de percurso pelo modelo Okumura-Hata.

    Args:
        frequency_mhz: Frequência em MHz (150–1500).
        dist_km: Distância em km (1–20).
        h_base_m: Altura da estação base em metros (30–200).
        h_mobile_m: Altura do terminal móvel em metros (1–10).
        environment: "urban_large" | "urban_small" | "suburban" | "open".

    Returns:
        OkumuraHataResult com path_loss_db e metadados.
    """
    warn_parts = []
    if not (150 <= frequency_mhz <= 1500):
        warn_parts.append(f"Frequência {frequency_mhz} MHz fora do intervalo válido (150–1500 MHz).")
    if not (1 <= dist_km <= 20):
        warn_parts.append(f"Distância {dist_km} km fora do intervalo válido (1–20 km).")
    if not (30 <= h_base_m <= 200):
        warn_parts.append(f"h_base {h_base_m} m fora do intervalo válido (30–200 m).")
    if not (1 <= h_mobile_m <= 10):
        warn_parts.append(f"h_mobile {h_mobile_m} m fora do intervalo válido (1–10 m).")
    warn: Optional[str] = " ".join(warn_parts) if warn_parts else None

    f = frequency_mhz
    d = dist_km
    h_b = h_base_m
    h_m = h_mobile_m

    # Fator de correção de altura do terminal a(h_m)
    if environment == "urban_large":
        if f >= 300:
            # Grande cidade, f ≥ 300 MHz
            a_hm = 3.2 * (math.log10(11.75 * h_m)) ** 2 - 4.97
        else:
            # Grande cidade, f < 300 MHz
            a_hm = 8.29 * (math.log10(1.54 * h_m)) ** 2 - 1.1
    else:
        # Cidade pequena/média, suburbano, rural
        a_hm = (1.1 * math.log10(f) - 0.7) * h_m - (1.56 * math.log10(f) - 0.8)

    # Perda urbana base (Hata eq. 1)
    L_u = (
        69.55
        + 26.16 * math.log10(f)
        - 13.82 * math.log10(h_b)
        - a_hm
        + (44.9 - 6.55 * math.log10(h_b)) * math.log10(d)
    )

    if environment in ("urban_large", "urban_small"):
        loss = L_u
    elif environment == "suburban":
        # Hata eq. 2
        loss = L_u - 2.0 * (math.log10(f / 28.0)) ** 2 - 5.4
    else:  # open
        # Hata eq. 3
        loss = L_u - 4.78 * (math.log10(f)) ** 2 + 18.33 * math.log10(f) - 40.94

    return OkumuraHataResult(
        path_loss_db=round(loss, 2),
        environment=environment,
        frequency_mhz=f,
        dist_km=d,
        h_base_m=h_b,
        h_mobile_m=h_m,
        warning=warn,
    )
