"""Analytic link budget calculations — pure functions, no I/O."""
from __future__ import annotations

import math

from .geometry import ENUVector, geodetic_to_enu

EARTH_R = 6_371_000.0  # mean radius in meters
C = 3e8  # m/s

# Polarization mismatch constants
_CIRCULAR_KEYWORDS = ("circular", "elliptical", "elliptic")
_FEED_DEPENDENT = "feed-dependent"
LINEAR_MISMATCH_LOSS_DB: float = 1.5  # penalty for explicitly incompatible linear pols (e.g., H vs V)


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in meters (Haversine formula)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * EARTH_R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Initial bearing from point A to point B in degrees [0, 360)."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def elevation_angle(distance_m: float, height_a: float, height_b: float) -> float:
    """Elevation angle in degrees from A looking toward B."""
    if distance_m <= 0:
        return 90.0
    return math.degrees(math.atan2(height_b - height_a, distance_m))


def fspl_db(distance_m: float, frequency_hz: float) -> float:
    """Free Space Path Loss in dB.

    FSPL = 20·log10(4π·d·f / c)
    """
    if distance_m <= 0:
        return 0.0
    return 20 * math.log10(4 * math.pi * distance_m * frequency_hz / C)


def compute_link(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    tx_cable_db: float,
    path_loss_db: float,
    rx_gain_dbi: float,
    rx_cable_db: float,
    rx_sensitivity_dbm: float,
) -> tuple[float, float]:
    """Return (rx_power_dbm, link_margin_db)."""
    rx_power = (
        tx_power_dbm
        + tx_gain_dbi
        - tx_cable_db
        - path_loss_db
        - rx_cable_db
        + rx_gain_dbi
    )
    return rx_power, rx_power - rx_sensitivity_dbm


def path_loss_db(
    dist_m: float,
    freq_hz: float,
    model: str = "fspl",
    tx_height_m: float = 5.0,
    rx_height_m: float = 5.0,
    environment: str = "suburban",
) -> float:
    """Dispatch de modelo de propagação. Retorna perda de percurso em dB."""
    if model == "okumura_hata":
        from ..solvers.okumura_hata import okumura_hata
        r = okumura_hata(freq_hz / 1e6, dist_m / 1000, tx_height_m, rx_height_m, environment)  # type: ignore[arg-type]
        return r.path_loss_db
    if model == "longley_rice":
        from ..solvers.longley_rice import longley_rice
        r = longley_rice(freq_hz / 1e6, dist_m / 1000, tx_height_m, rx_height_m)
        return r.path_loss_db
    return fspl_db(dist_m, freq_hz)


def _get_polarization(antenna: object) -> str | None:
    """Return effective polarization string, filling from preset if available."""
    if antenna is None:
        return None
    if hasattr(antenna, "model_dump"):
        from ..domain.antenna_presets import apply_antenna_defaults
        filled = apply_antenna_defaults(antenna).spec
        return getattr(filled, "polarization", None)
    return getattr(antenna, "polarization", None)


def estimate_polarization_loss(tx_ant: object, rx_ant: object) -> float:
    """Polarization mismatch loss in dB.

    Rules:
    - circular/elliptical vs linear: 3 dB
    - two linears with explicitly different orientations (H vs V): LINEAR_MISMATCH_LOSS_DB
    - same, unknown, or feed-dependent: 0 dB
    """
    tx_pol = _get_polarization(tx_ant)
    rx_pol = _get_polarization(rx_ant)

    if not tx_pol or not rx_pol:
        return 0.0
    if tx_pol == _FEED_DEPENDENT or rx_pol == _FEED_DEPENDENT:
        return 0.0

    def _is_circular(p: str) -> bool:
        pl = p.lower()
        return any(kw in pl for kw in _CIRCULAR_KEYWORDS)

    def _is_linear(p: str) -> bool:
        return p.lower().startswith("linear")

    tx_circ = _is_circular(tx_pol)
    rx_circ = _is_circular(rx_pol)
    tx_lin = _is_linear(tx_pol)
    rx_lin = _is_linear(rx_pol)

    if (tx_circ and rx_lin) or (tx_lin and rx_circ):
        return 3.0

    if tx_lin and rx_lin and tx_pol != rx_pol:
        # Only penalize when both have explicit orientation and they differ
        # "linear" (bare) vs "linear vertical" → compatible (empty vs something)
        tx_orient = tx_pol.lower().replace("linear", "").strip()
        rx_orient = rx_pol.lower().replace("linear", "").strip()
        if tx_orient and rx_orient and tx_orient != rx_orient:
            return LINEAR_MISMATCH_LOSS_DB

    return 0.0


def _effective_gain(node: object, antenna: object, enu_to_peer: ENUVector) -> float:
    """Ganho efetivo em dBi.

    Priority: user-explicit spec fields > solver internal constants.
    Exception — pcb_compact: gmax_dbi from preset is nominal only; solver uses
    frequency-dependent calc unless user explicitly set gmax_dbi.
    hpbw_deg from spec/preset is always forwarded to pattern_g (key MATLAB fix:
    commercial_omni_6dbi uses 35° not 20°).
    """
    if antenna is None:
        return 0.0

    from ..solvers import get_solver
    ant_type: str = getattr(antenna, "type", "dipolo")
    freq_hz: float = getattr(antenna, "frequency_hz", 915e6)
    geometry: dict = getattr(antenna, "geometry", {})

    solver = get_solver(ant_type)
    if solver is None:
        results = getattr(antenna, "results", None) or {}
        return float(results.get("gain_dbi", 0.0))

    # Apply canonical defaults; track user-set vs preset-filled fields.
    # Guard against non-AntennaSpec objects (SimpleNamespace etc.) passed in tests.
    use_gmax: float | None = None
    use_hpbw: float | None = None
    if hasattr(antenna, "model_dump"):
        from ..domain.antenna_presets import apply_antenna_defaults
        swd = apply_antenna_defaults(antenna)
        filled = swd.spec
        from_preset = swd.from_preset

        filled_gmax = getattr(filled, "gmax_dbi", None)
        if filled_gmax is not None:
            # PCB: preset nominal (1 dBi) ≠ solver precision; use solver unless user set it.
            if ant_type == "pcb_compact" and "gmax_dbi" in from_preset:
                use_gmax = None
            else:
                # For all other types, use gmax only when user set it (not from preset),
                # so geometry-dependent solvers (helicoidal, parabolica) keep their calc.
                if "gmax_dbi" not in from_preset:
                    use_gmax = filled_gmax

        # hpbw_deg: always forward from spec/preset — critical for colinear 35° fix.
        use_hpbw = getattr(filled, "hpbw_deg", None)

    node_az = getattr(node, "azimuth_deg", None)
    if node_az is None:
        if use_gmax is not None:
            return use_gmax
        return solver.gain_dbi(freq_hz, antenna_type=ant_type, **geometry)

    boresight_az: float = node_az
    boresight_el: float = getattr(node, "tilt_deg", 0.0)

    link_az = enu_to_peer.azimuth_deg
    link_el = enu_to_peer.elevation_deg

    delta_az = abs(link_az - boresight_az) % 360
    if delta_az > 180:
        delta_az = 360 - delta_az
    delta_el = abs(link_el - boresight_el)

    theta_off = math.sqrt(delta_az ** 2 + delta_el ** 2)

    pattern_kwargs: dict = {"antenna_type": ant_type, **geometry}
    if use_gmax is not None:
        pattern_kwargs["gmax_dbi"] = use_gmax
    if use_hpbw is not None:
        pattern_kwargs["hpbw_deg"] = use_hpbw

    return solver.pattern_g(theta_off, 0.0, freq_hz, **pattern_kwargs)


def compute_link_full(
    node_a: object,
    node_b: object,
    freq_hz: float,
    propagation_model: str = "fspl",
    antenna_a: object = None,
    antenna_b: object = None,
) -> object:
    """Cálculo completo de link budget com ENU 3D, ganho direcional e perdas extras.
    Retorna LinkResult.
    """
    from ..schemas.link_scenario import LinkResult

    enu = geodetic_to_enu(
        getattr(node_a, "lat", 0.0), getattr(node_a, "lon", 0.0), getattr(node_a, "height_m", 0.0),
        getattr(node_b, "lat", 0.0), getattr(node_b, "lon", 0.0), getattr(node_b, "height_m", 0.0),
    )
    dist_m = enu.distance_3d
    enu_b_to_a = ENUVector(-enu.east_m, -enu.north_m, -enu.up_m)

    g_tx = _effective_gain(node_a, antenna_a, enu)
    g_rx = _effective_gain(node_b, antenna_b, enu_b_to_a)

    l_tx: float = getattr(node_a, "cable_loss_db", 0.0)
    l_rx: float = getattr(node_b, "cable_loss_db", 0.0)

    extra: float = (
        getattr(node_a, "extra_loss_db", 0.0)
        + getattr(node_b, "extra_loss_db", 0.0)
        + getattr(node_a, "fading_margin_db", 0.0)
    )
    pol_manual: float = getattr(node_a, "polarization_loss_db", 0.0)
    pol_auto: float = estimate_polarization_loss(antenna_a, antenna_b)
    pol_total: float = pol_manual + pol_auto

    loss = path_loss_db(
        dist_m, freq_hz, model=propagation_model,
        tx_height_m=max(getattr(node_a, "height_m", 5.0), 1.0),
        rx_height_m=max(getattr(node_b, "height_m", 5.0), 1.0),
    )

    tx_power: float = getattr(node_a, "tx_power_dbm", 14.0)
    rx_sens: float = getattr(node_b, "rx_sensitivity_dbm", -137.0)

    rx_power = tx_power + g_tx - l_tx - loss - l_rx + g_rx - extra - pol_total
    margin = rx_power - rx_sens

    warnings: list[str] = []
    if dist_m > 200_000:
        warnings.append(f"Distância {dist_m / 1000:.0f} km excede escopo prático de LoRa (200 km).")

    return LinkResult(
        distance_m=round(dist_m, 1),
        azimuth_deg=round(enu.azimuth_deg, 2),
        elevation_deg=round(enu.elevation_deg, 4),
        fspl_db=round(loss, 2),
        rx_power_dbm=round(rx_power, 2),
        link_margin_db=round(margin, 2),
        feasibility=feasibility(margin),
        extra_loss_db=round(extra, 2),
        polarization_loss_db=round(pol_total, 2),
        propagation_model=propagation_model,
        warnings=warnings,
    )


def feasibility(margin_db: float) -> str:
    if margin_db > 10:
        return "verde"
    if margin_db >= 0:
        return "amarelo"
    return "vermelho"


def minimax_gateway_rank(candidates: list, sensor_nodes: list) -> list[dict]:
    """Ranqueia candidatos a gateway pelo critério minimax (minimiza distância máxima a qualquer sensor)."""
    results: list[dict] = []
    for cand in candidates:
        if not sensor_nodes:
            dists = [0.0]
        else:
            dists = [
                geodetic_to_enu(
                    cand.lat, cand.lon, cand.height_m,
                    sensor.lat, sensor.lon, sensor.height_m,
                ).distance_3d
                for sensor in sensor_nodes
            ]
        results.append({
            "candidate_id": cand.id,
            "candidate_name": cand.name,
            "max_dist_m": round(max(dists), 1),
            "mean_dist_m": round(sum(dists) / len(dists), 1),
        })

    results.sort(key=lambda r: r["max_dist_m"])
    for i, r in enumerate(results):
        r["rank"] = i + 1
    return results


def find_islands(all_node_ids: list[str], links: list) -> list[str]:
    """Return node IDs that appear in no link."""
    connected: set[str] = set()
    for edge in links:
        connected.add(edge.node_a_id)
        connected.add(edge.node_b_id)
    return [nid for nid in all_node_ids if nid not in connected]


def best_path_margin(target_node_id: str, hops: list) -> float | None:
    """Return best (highest) link_margin_db among all hops ending at target_node_id."""
    margins = [
        h.link_margin_db for h in hops
        if h.node_b_id == target_node_id or h.node_a_id == target_node_id
    ]
    return max(margins) if margins else None
