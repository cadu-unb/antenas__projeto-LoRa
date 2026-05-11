### Objetivos Curto Prazo
- Interface Streamlit para criar antena
- Exibição de parâmetros calculados
- Gráficos 2D/3D de padrão de radiação
- Salvar/carregar antenas (JSON)

### Tarefas Principais

#### 5.1 `src/lora_antenna/ui/pages/antenna.py`
```python
import streamlit as st
from lora_antenna.antenna.monopole import Monopole
from lora_antenna.antenna.dipole import Dipole, DipoleEnvironment
# ... outras imports

st.set_page_config(page_title="Antenna Designer", layout="wide")

st.title("📡 Antenna Designer")

# Sidebar: Configurações
with st.sidebar:
    st.header("Antenna Configuration")
    
    antenna_type = st.selectbox(
        "Antenna Type",
        ["Monopole", "Dipole", "Ground Plane", "Patch", "Yagi", "ReflectorAntenna"]
    )
    
    frequency = st.selectbox(
        "Frequency",
        {"433 MHz": 433e6, "868 MHz": 868e6, "915 MHz": 915e6, "Custom": None}
    )
    
    if frequency is None:
        frequency = st.number_input("Custom Frequency (Hz)", min_value=100e6, value=915e6)
    
    name = st.text_input("Antenna Name", value=f"{antenna_type} {frequency/1e6:.0f}MHz")

# Criar antena based on type
if antenna_type == "Monopole":
    ant = Monopole(frequency_hz=frequency, name=name, id=f"ant-{int(time.time())}")

elif antenna_type == "Dipole":
    env = st.sidebar.selectbox("Environment", list(DipoleEnvironment))
    ant = Dipole(frequency_hz=frequency, environment=DipoleEnvironment(env), name=name, id=f"ant-{int(time.time())}")

# ... outros tipos

# Exibir resultados em tabs
tab1, tab2, tab3, tab4 = st.tabs(["Parameters", "Radiation Pattern", "Impedance", "Export"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Frequency", f"{frequency/1e6:.0f} MHz")
    col2.metric("Gain", f"{ant.gain_dbi:.2f} dBi")
    col3.metric("VSWR", f"{ant.vswr:.2f}")
    
    col4, col5, col6 = st.columns(3)
    col4.metric("Effective Area", f"{ant.effective_area_m2:.4f} m²")
    col5.metric("Impedance", f"{ant.impedance_ohm}")
    col6.metric("Efficiency", f"{ant.efficiency:.1%}")

with tab2:
    st.info("🔴 DISCLAIMER: Padrões simplificados (sem lóbulos secundários)")
    # Gráficos Plotly aqui

with tab3:
    # Análise de impedância e VSWR

with tab4:
    # Exportar JSON
    json_data = ant.model_dump_json()
    st.download_button(
        "Download JSON",
        data=json_data,
        file_name=f"{name}.json",
        mime="application/json"
    )
```

### Critérios de Aceite (DoD)

- [ ] Streamlit app roda sem erro
- [ ] Todos os tipos de antena podem ser criados via UI
- [ ] Parâmetros calculados aparecem corretamente
- [ ] Gráficos renderizam (Plotly)
- [ ] JSON exporta/importa corretamente

### Validação Automática

```bash
# Checklist Sprint 4

# 1. App roda
timeout 10 uv run streamlit run src/lora_antenna/app.py --server.port 3953 &

# 2. Verificar páginas carregam
curl -s http://localhost:3953 | grep -q "Antenna"

# 3. Export JSON válido
python -c "
import json
from lora_antenna.antenna.monopole import Monopole
m = Monopole(frequency_hz=915e6, id='test', name='Test')
data = json.loads(m.model_dump_json())
assert data['antenna_type'] == 'Monopole'
"
```