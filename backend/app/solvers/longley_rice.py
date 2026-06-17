"""Modelo de perda de percurso Longley-Rice / ITM (versão simplificada).

Referência: A. G. Longley & P. L. Rice, "Prediction of Tropospheric Radio
Transmission Loss over Irregular Terrain: A Computer Method",
ESSA Tech. Rep. ERL 79-ITS 67, U.S. Dept. of Commerce, 1968.

Esta é uma implementação analítica simplificada baseada nos conceitos do ITM.
Para produção em análise de terreno real, usar splat! ou a biblioteca ITM original
(disponível em NTIA/ITS, domínio público, implementada em C++).

Intervalo de validade desta implementação:
  Frequência   : 20 MHz – 20 GHz
  Distância    : 1 – 2000 km
  Alturas      : > 0 m
  delta_h      : irregularidade de terreno em metros (típico: 50–500 m)
"""
import math
from typing import Optional

from pydantic import BaseModel

C = 3e8  # m/s
EARTH_RADIUS_M = 6_371_000.0
# Raio efetivo da Terra com gradiente atmosférico padrão (k=4/3)
EARTH_EFFECTIVE_M = 4 / 3 * EARTH_RADIUS_M


class LongleyRiceResult(BaseModel):
    path_loss_db: float
    model: str = "longley_rice_simplified"
    los: bool
    fspl_db: float
    warning: Optional[str] = None


def longley_rice(
    frequency_mhz: float,
    dist_km: float,
    h_tx_m: float,
    h_rx_m: float,
    delta_h_m: float = 50.0,
    climate: int = 5,
) -> LongleyRiceResult:
    """Calcula perda de percurso pelo modelo Longley-Rice / ITM simplificado.

    Args:
        frequency_mhz: Frequência em MHz.
        dist_km: Distância entre tx e rx em km.
        h_tx_m: Altura da antena transmissora em metros.
        h_rx_m: Altura da antena receptora em metros.
        delta_h_m: Parâmetro de irregularidade de terreno (m). Padrão: 50 m.
            Valores típicos: terreno plano ≈ 10, colinas ≈ 50, montanhas ≈ 500.
        climate: Tipo climático ITM (1–7). 5 = continental temperado (padrão).

    Returns:
        LongleyRiceResult com path_loss_db e metadados.
    """
    warn_parts = []
    if not (20 <= frequency_mhz <= 20_000):
        warn_parts.append(f"Frequência {frequency_mhz} MHz fora do intervalo (20–20000 MHz).")
    if dist_km > 2000:
        warn_parts.append(f"Distância {dist_km} km além do limite recomendado (2000 km).")
    warn: Optional[str] = " ".join(warn_parts) if warn_parts else None

    lam_m = C / (frequency_mhz * 1e6)  # comprimento de onda em metros
    d_m = dist_km * 1e3

    # Distâncias de horizonte (Terra esférica com raio efetivo k=4/3)
    d_hor_tx = math.sqrt(2.0 * EARTH_EFFECTIVE_M * h_tx_m)
    d_hor_rx = math.sqrt(2.0 * EARTH_EFFECTIVE_M * h_rx_m)
    d_los = d_hor_tx + d_hor_rx  # distância máxima de visada direta
    is_los = d_m <= d_los

    # FSPL como baseline
    fspl_db = 20.0 * math.log10(4.0 * math.pi * d_m / lam_m)

    # Correção de irregularidade de terreno (ATN — terrain adjustment)
    # Baseado em Longley-Rice Vol. 1, Sec. 4.5 (simplificado)
    f_factor = math.log10(max(frequency_mhz, 20) / 100.0)
    atn_terrain = 0.01 * delta_h_m * f_factor

    if is_los:
        loss = fspl_db + atn_terrain
    else:
        # Região de difração: perda adicional por difração de gume de faca
        excess = d_m - d_los
        # Parâmetro de Fresnel ν para difração em Terra esférica
        nu = excess / math.sqrt(lam_m * d_m / 2.0)

        # Fator de atenuação por difração J(ν) — Boithias/Sadiku aproximação
        if nu < -0.7:
            j_nu_db = 0.0
        elif nu < 0.0:
            j_nu_db = 20.0 * math.log10(0.5 + 0.62 * nu)
        elif nu < 1.0:
            j_nu_db = 20.0 * math.log10(0.5 * math.exp(-0.95 * nu))
        elif nu < 2.4:
            inner = max(0.1184 - (0.38 - 0.1 * nu) ** 2, 1e-10)
            j_nu_db = 20.0 * math.log10(0.4 - math.sqrt(inner))
        else:
            j_nu_db = 20.0 * math.log10(0.225 / nu)

        # Correção adicional por irregularidade de terreno além da visada
        atn_diff = 0.057 * (delta_h_m ** (1.0 / 3.0)) * ((frequency_mhz / 1000.0) ** (1.0 / 3.0))

        loss = fspl_db - j_nu_db + atn_diff + atn_terrain

    return LongleyRiceResult(
        path_loss_db=round(max(loss, 0.0), 2),
        los=is_los,
        fspl_db=round(fspl_db, 2),
        warning=warn,
    )
