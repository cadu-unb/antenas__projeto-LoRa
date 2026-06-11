"""Standalone point-to-point link simulation — no KML, no GIS imports."""

import streamlit as st

from lora_antenna.antenna.base import Antenna
from lora_antenna.core.constants import DEFAULT_RX_SENSITIVITY_DBM, DEFAULT_TX_POWER_DBM
from lora_antenna.network.channel_plan import LORA_CHANNELS_MHZ
from lora_antenna.propagation.batch import (
    LinkBatchRequest,
    ScalarLinkInput,
    execute_link_batch,
)
from lora_antenna.propagation.friis import LinkRisk

CHANNEL_OPTIONS: dict[str, float] = {
    f"{ch:.1f} MHz": ch * 1_000_000.0 for ch in LORA_CHANNELS_MHZ
}

RISK_BADGE: dict[LinkRisk, str] = {
    LinkRisk.LOW: ":green[LOW]",
    LinkRisk.MEDIUM: ":orange[MEDIUM]",
    LinkRisk.HIGH: ":red[HIGH]",
}

st.title("Simulação Standalone — Enlace Ponto a Ponto")

with st.sidebar:
    st.header("Parâmetros RF")
    freq_label = st.selectbox("Frequência", list(CHANNEL_OPTIONS.keys()), index=0)
    freq_hz = CHANNEL_OPTIONS[freq_label]

    tx_power = st.slider(
        "Potência TX (dBm)", min_value=-20, max_value=30, value=int(DEFAULT_TX_POWER_DBM)
    )
    gain = st.number_input("Ganho antena (dBi)", min_value=0.0, value=2.15, step=0.1)
    extra_loss = st.number_input("Perdas extras (dB)", min_value=0.0, value=0.0, step=0.5)
    dist_2d = st.number_input("Distância 2D (m)", min_value=1.0, value=300.0, step=10.0)
    dist_3d = st.number_input(
        "Distância 3D (m)", min_value=1.0, value=300.0, step=10.0
    )
    rx_sens = st.number_input(
        "Sensibilidade RX (dBm)",
        max_value=-1.0,
        value=float(DEFAULT_RX_SENSITIVITY_DBM),
        step=1.0,
    )
    sf = st.selectbox("SF", options=[7, 8, 9, 10, 11, 12], index=5)

if dist_3d < dist_2d:
    st.warning("Distância 3D deve ser ≥ distância 2D.")
else:
    scalar = ScalarLinkInput(
        origin_label="TX",
        dest_label="RX",
        distance_m=float(dist_2d),
        distance_3d_m=float(dist_3d),
        total_extra_loss_db=float(extra_loss),
        n_buildings_crossed=0,
    )
    request = LinkBatchRequest(
        pairs=[scalar],
        antenna=Antenna(gain_dbi=float(gain), losses_db=0.0),
        tx_power_dbm=float(tx_power),
        frequency_hz=freq_hz,
        rx_sensitivity_dbm=float(rx_sens),
        sf=int(sf),
    )
    results = execute_link_batch(request)
    r = results[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Potência Recebida", f"{r.received_power_dbm:.2f} dBm")
    with col2:
        st.metric("Margem de Enlace", f"{r.link_margin_db:.2f} dB")
    with col3:
        st.metric("Risco", r.link_risk.value)
    with col4:
        st.metric("Enlace", "Viável" if r.feasible else "Inviável")

    st.markdown(f"**Classificação:** {RISK_BADGE[r.link_risk]}")

    filter_opt = st.radio(
        "Filtro", ["Todos", "Só viáveis", "Só inviáveis"], horizontal=True
    )

    row = {
        "Origem": r.origin_label,
        "Destino": r.dest_label,
        "Dist 2D (m)": r.distance_m,
        "Dist 3D (m)": r.distance_3d_m,
        "FSPL (dB)": r.fspl_db,
        "Perdas extra (dB)": r.extra_loss_db,
        "Pr (dBm)": r.received_power_dbm,
        "Margem (dB)": r.link_margin_db,
        "Risco": r.link_risk.value,
        "Viável": r.feasible,
        "SIR (dB)": r.sir_db,
        "SIR decodável": r.sir_decodable,
    }
    rows = [row]

    if filter_opt == "Só viáveis":
        rows = [row for row in rows if row["Viável"]]
    elif filter_opt == "Só inviáveis":
        rows = [row for row in rows if not row["Viável"]]

    st.dataframe(rows, use_container_width=True)
