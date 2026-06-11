"""Campus KML simulation — multi-node RF, SIR, map, channel plan."""

import html as _html
import urllib.request
import urllib.error

import streamlit as st

from lora_antenna.antenna.base import Antenna
from lora_antenna.core.constants import DEFAULT_RX_SENSITIVITY_DBM, DEFAULT_TX_POWER_DBM
from lora_antenna.gis.kml_parser import KMLPolygonRole, parse_kml
from lora_antenna.gis.multi_link import results_to_sir_matrix, run_link_budget_batch
from lora_antenna.network.channel_plan import (
    LORA_CHANNELS_MHZ,
    build_interference_graph,
    count_channel_collisions,
    greedy_channel_assignment,
)

CHANNEL_OPTIONS: dict[str, float] = {
    f"{ch:.1f} MHz": ch * 1_000_000.0 for ch in LORA_CHANNELS_MHZ
}

LINK_COLORS = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}


@st.cache_data(ttl=30)
def _leaflet_cdn_reachable() -> bool:
    try:
        urllib.request.urlopen("https://cdn.jsdelivr.net", timeout=1.5)
        return True
    except Exception:
        return False

st.title("Campus KML — Simulação Multiponto")

# Phase 1 — KML upload
st.header("1. Upload KML")
uploaded = st.file_uploader("Arquivo KML do campus", type=["kml"])

if uploaded is None:
    st.info("Faça upload de um arquivo KML para continuar.")
    st.stop()

if st.session_state.get("_kml_name") != uploaded.name:
    try:
        doc = parse_kml(uploaded.read())
    except Exception as exc:
        st.error(f"Erro ao processar KML: {exc}")
        st.stop()
    st.session_state.update(
        {
            "_kml_name": uploaded.name,
            "kml_document": doc,
            "distance_matrix": None,
            "link_results": None,
            "sir_matrix": None,
            "channel_assignments": None,
        }
    )

doc = st.session_state["kml_document"]
if doc is None:
    st.stop()

st.success(
    f"KML carregado: **{len(doc.points)}** pontos, **{len(doc.polygons)}** polígonos"
)

# Phase 2 — RF configuration
with st.sidebar:
    st.header("Parâmetros RF")
    freq_label = st.selectbox("Frequência", list(CHANNEL_OPTIONS.keys()), index=0)
    freq_hz = CHANNEL_OPTIONS[freq_label]

    tx_power = st.slider(
        "Potência TX (dBm)", min_value=-20, max_value=30, value=int(DEFAULT_TX_POWER_DBM)
    )
    gain = st.number_input("Ganho antena (dBi)", min_value=0.0, value=2.15, step=0.1)
    extra_loss = st.number_input("Perdas extras (dB)", min_value=0.0, value=0.0, step=0.5)
    rx_sens = st.number_input(
        "Sensibilidade RX (dBm)",
        max_value=-1.0,
        value=float(DEFAULT_RX_SENSITIVITY_DBM),
        step=1.0,
    )
    sf = st.selectbox("SF", options=[7, 8, 9, 10, 11, 12], index=5)

    if st.button("Limpar resultados"):
        st.session_state.update(
            {
                "link_results": None,
                "sir_matrix": None,
                "channel_assignments": None,
            }
        )

# Phase 3 — Simulation
st.header("3. Simulação")
if st.button("Executar simulação"):
    st.session_state.update(
        {"link_results": None, "sir_matrix": None, "channel_assignments": None}
    )
    try:
        with st.spinner("Calculando enlaces..."):
            antenna = Antenna(gain_dbi=float(gain), losses_db=0.0)
            link_results = run_link_budget_batch(
                doc,
                antenna,
                frequency_hz=freq_hz,
                tx_power_dbm=float(tx_power),
                rx_sensitivity_dbm=float(rx_sens),
                sf=int(sf),
                extra_losses_db=float(extra_loss),
            )
        st.session_state["link_results"] = link_results
        st.session_state["sir_matrix"] = results_to_sir_matrix(link_results)
    except Exception as exc:
        st.error(f"Erro na simulação: {exc}")

if not st.session_state.get("link_results"):
    st.info("Clique em **Executar simulação** para calcular os enlaces.")
    st.stop()

link_results = st.session_state["link_results"]

rows = [
    {
        "Origem": r.origin_label,
        "Destino": r.dest_label,
        "Dist (m)": r.distance_m,
        "FSPL (dB)": r.fspl_db,
        "Pr (dBm)": r.received_power_dbm,
        "Margem (dB)": r.link_margin_db,
        "Risco": r.link_risk.value,
        "Viável": r.feasible,
        "Prédios": r.n_buildings_crossed,
        "SIR (dB)": r.sir_db,
        "SIR decodável": r.sir_decodable,
    }
    for r in link_results
]

filter_opt = st.radio(
    "Filtro enlace", ["Todos", "Só viáveis", "Só inviáveis"], horizontal=True
)
if filter_opt == "Só viáveis":
    rows = [row for row in rows if row["Viável"]]
elif filter_opt == "Só inviáveis":
    rows = [row for row in rows if not row["Viável"]]

st.dataframe(rows, use_container_width=True)

# Phase 4 — Map
st.header("4. Mapa")

if not _leaflet_cdn_reachable():
    st.warning(
        "Sem acesso a cdn.jsdelivr.net — o mapa não renderizará. "
        "Verifique conectividade de internet ou execute fora do modo offline."
    )

try:
    import folium
    from streamlit_folium import st_folium

    center_lat = sum(p.latitude for p in doc.points) / len(doc.points)
    center_lon = sum(p.longitude for p in doc.points) / len(doc.points)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=17)

    for point in doc.points:
        folium.Marker(
            location=[point.latitude, point.longitude],
            tooltip=_html.escape(point.label),
            icon=folium.Icon(color="blue"),
        ).add_to(m)

    for polygon in doc.polygons:
        if polygon.role == KMLPolygonRole.BUILDING:
            color = "gray"
        elif polygon.role == KMLPolygonRole.OBSTACLE:
            color = "orange"
        else:
            color = "cadetblue"
        coords = [[lat, lon] for lon, lat in polygon.exterior_ring]
        folium.Polygon(
            locations=coords,
            color=color,
            fill=True,
            fill_opacity=0.3,
            tooltip=_html.escape(polygon.label),
        ).add_to(m)

    point_map = {p.label: p for p in doc.points}
    for r in link_results:
        origin = point_map.get(r.origin_label)
        dest = point_map.get(r.dest_label)
        if origin is None or dest is None:
            continue
        color = LINK_COLORS.get(r.link_risk.value, "gray")
        dash = "5 5" if r.sir_decodable is False else None
        folium.PolyLine(
            locations=[
                [origin.latitude, origin.longitude],
                [dest.latitude, dest.longitude],
            ],
            color=color,
            weight=2,
            dash_array=dash,
            tooltip=_html.escape(
                f"{r.origin_label}→{r.dest_label} | {r.link_margin_db:.1f} dB"
            ),
        ).add_to(m)

    st_folium(m, use_container_width=True, height=500)

except ImportError:
    st.warning("folium ou streamlit-folium não instalados — mapa indisponível.")
except Exception as exc:
    st.warning(f"Mapa indisponível: {exc}")

# Phase 5 — Channel optimization
st.header("5. Otimização de Canais")
if st.button("Otimizar canais"):
    sir_matrix = st.session_state["sir_matrix"] or {}
    graph = build_interference_graph(
        sir_matrix,
        nodes=[p.label for p in doc.points],
        sf=int(sf),
    )
    node_labels = [p.label for p in doc.points]
    assignments = greedy_channel_assignment(node_labels, graph)
    collisions = count_channel_collisions(assignments, graph)
    st.session_state["channel_assignments"] = assignments
    st.metric("Colisões de canal", collisions)

if st.session_state.get("channel_assignments"):
    assignments = st.session_state["channel_assignments"]
    ch_rows = [
        {
            "Nó": label,
            "Canal (MHz)": f"{a.channel_mhz:.1f}",
            "Índice": a.channel_index,
        }
        for label, a in sorted(assignments.items())
    ]
    st.dataframe(ch_rows, use_container_width=True)
