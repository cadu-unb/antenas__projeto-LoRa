"""SRTM elevation lookup through OpenTopodata."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

import requests

from lora_antenna.models.geo import GeographicPosition

SRTM_API_URL = "https://api.opentopodata.org/v1/srtm30m"
TPosition = TypeVar("TPosition", bound=GeographicPosition)


def fetch_srtm_elevations(
    positions: Sequence[TPosition],
    *,
    timeout_s: float = 10.0,
    session: requests.Session | None = None,
) -> list[TPosition]:
    """Fetch SRTM 30m elevations and return copied positions with updates."""
    if not positions:
        return []

    client = session or requests.Session()
    locations = "|".join(f"{p.latitude},{p.longitude}" for p in positions)
    response = client.get(
        SRTM_API_URL,
        params={"locations": locations},
        timeout=timeout_s,
    )
    response.raise_for_status()

    payload = response.json()
    results = payload.get("results")
    if not isinstance(results, list) or len(results) != len(positions):
        raise ValueError("Invalid SRTM response: unexpected results length.")

    updated: list[TPosition] = []
    for position, result in zip(positions, results):
        elevation = result.get("elevation")
        if elevation is None:
            updated.append(position)
            continue
        updated.append(
            position.model_copy(update={"altitude_srtm_m": float(elevation)})
        )

    return updated
