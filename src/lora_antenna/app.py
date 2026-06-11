"""Streamlit entry point — routing only, zero RF math."""

import streamlit as st

CAMPUS_DEFAULTS: dict[str, object] = {
    "_kml_name": None,
    "kml_document": None,
    "distance_matrix": None,
    "link_results": None,
    "sir_matrix": None,
    "channel_assignments": None,
}

st.set_page_config(
    page_title="Simulador LoRa",
    layout="wide",
)

for key, value in CAMPUS_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

pg = st.navigation(
    [
        st.Page("pages/standalone.py", title="Simulação Standalone"),
        st.Page("pages/campus.py", title="Campus KML"),
    ]
)
pg.run()
