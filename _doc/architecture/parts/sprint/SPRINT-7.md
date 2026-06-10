### Objetivos Curto Prazo
- Gráficos polares para padrões de radiação
- Padrão 3D simplificado
- Gráficos de potência vs distância
- TX/RX chain breakdown visual

### Tarefas Principais

#### 7.1 `src/lora_antenna/ui/charts.py` (NOVO)
```python
import plotly.graph_objects as go
import numpy as np
from lora_antenna.antenna.base import Antenna

def radiation_pattern_polar(antenna: Antenna, num_points: int = 360):
    """Gráfico polar do padrão de radiação"""
    
    angles = np.linspace(0, 360, num_points)
    
    # Padrão simplificado (cos^n para diretivas, omni para monopole/dipole)
    if antenna.antenna_type in ["Monopole", "Dipole"]:
        # Omnidireccional em azimute
        pattern = np.ones(num_points)
    elif antenna.antenna_type == "Yagi":
        # Modelo cos^n
        n = 2
        off_axis = np.radians(angles)
        pattern = np.maximum(np.cos(off_axis) ** n, 0)
    elif antenna.antenna_type == "ReflectorAntenna":
        # Parabola: gaussiano
        beamwidth = getattr(antenna, 'beamwidth_3db_deg', 1.0)
        pattern = np.exp(-2.77 * (angles / beamwidth) ** 2)
    else:
        pattern = np.ones(num_points)
    
    # Converter para dB
    pattern_db = 10 * np.log10(pattern + 0.001)
    
    fig = go.Figure(data=
        go.Scatterpolar(
            r=pattern_db,
            theta=angles,
            fill='toself',
            name=antenna.antenna_type
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-20, 0])),
        title=f"Radiation Pattern: {antenna.name}",
        showlegend=True
    )
    
    return fig

def power_vs_distance(link_budget, max_distance: float = 5000):
    """Gráfico: Potência recebida vs distância"""
    
    distances = np.linspace(100, max_distance, 100)
    powers = [link_budget.friis_received_power_dbm(d) for d in distances]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distances,
        y=powers,
        mode='lines',
        name='Received Power',
        line=dict(color='blue')
    ))
    
    # Adicionar linha de sensibilidade
    if hasattr(link_budget, 'rx_sensitivity_dbm'):
        fig.add_hline(
            y=link_budget.rx_sensitivity_dbm,
            line_dash="dash",
            annotation_text="RX Sensitivity",
            annotation_position="right"
        )
    
    fig.update_layout(
        title="Received Power vs Distance",
        xaxis_title="Distance (m)",
        yaxis_title="Power (dBm)",
        hovermode='x unified'
    )
    
    return fig

def tx_rx_chain_breakdown(tx_chain, rx_chain, antenna_gain_tx, antenna_gain_rx):
    """Breakdown visual da cadeia TX/RX"""
    
    # TX chain
    tx_stages = [
        f"Base Power: {tx_chain.base_power_dbm:.1f} dBm",
        f"+ PA Gain: +{tx_chain.pa_gain_db:.1f} dB",
        f"+ Antenna: +{antenna_gain_tx:.1f} dBi",
        f"- Losses: -{tx_chain.tx_filter_loss_db + tx_chain.tx_cable_loss_db + tx_chain.tx_connectors_loss_db:.1f} dB",
    ]
    
    eirp = tx_chain.base_power_dbm + tx_chain.pa_gain_db + antenna_gain_tx - (...)
    
    # Gráfico em barras horizontal
    fig = go.Figure()
    
    # ... plotar TX chain
    # ... plotar RX chain
    
    return fig
```

### Critérios de Aceite (DoD)

- [ ] Gráficos polares renderizam para todos os tipos de antena
- [ ] Padrão 3D simplificado implementado (ou skeleton)
- [ ] Gráficos de potência vs distância corretos
- [ ] TX/RX chain breakdown visual funciona
- [ ] Disclaimers aparecem nos gráficos ("SIMPLIFIED", etc)