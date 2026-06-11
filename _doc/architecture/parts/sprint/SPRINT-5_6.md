### Objetivos Curto Prazo
- LinkBudget simples e completo
- LinkWithDirectivity (azimute/elevação)
- UI para enlace com 2 antenas
- Comparação PA/LNA on/off

### Tarefas Principais

#### 6.1 `src/lora_antenna/propagation/link_budget.py`
```python
from dataclasses import dataclass
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import friis_received_power_dbm, link_margin_db

@dataclass
class LinkBudget:
    """Link budget simples (Friis sem diretividade)"""
    
    tx_antenna: Antenna
    rx_antenna: Antenna
    distance_m: float
    tx_power_dbm: float = 14
    losses_db: float = 0
    
    @property
    def received_power_dbm(self) -> float:
        """Potência recebida via Friis"""
        return friis_received_power_dbm(
            tx_power_dbm=self.tx_power_dbm,
            tx_gain_dbi=self.tx_antenna.gain_dbi,
            rx_gain_dbi=self.rx_antenna.gain_dbi,
            distance_m=self.distance_m,
            frequency_hz=self.tx_antenna.frequency_hz,
            losses_db=self.losses_db
        )
    
    def link_margin_db(self, rx_sensitivity_dbm: float = -137) -> float:
        """Margem de enlace"""
        return link_margin_db(self.received_power_dbm, rx_sensitivity_dbm)
```

#### 6.2 `src/lora_antenna/propagation/link_directivity.py` (NOVO)
```python
import math
from typing import Tuple
from lora_antenna.antenna.base import Antenna
from lora_antenna.models.geo import GeographicPosition

class LinkWithDirectivity:
    """Link budget com diretividade (azimute/elevação)"""
    
    def __init__(
        self,
        tx_antenna: Antenna,
        rx_antenna: Antenna,
        tx_position: GeographicPosition,
        rx_position: GeographicPosition,
        tx_azimuth_deg: float = 0,
        tx_elevation_deg: float = 0,
        rx_azimuth_deg: float = 0,
        rx_elevation_deg: float = 0,
        distance_m: float = None,
        tx_power_dbm: float = 14,
        losses_db: float = 0,
    ):
        self.tx_antenna = tx_antenna
        self.rx_antenna = rx_antenna
        self.tx_position = tx_position
        self.rx_position = rx_position
        self.tx_azimuth_deg = tx_azimuth_deg
        self.tx_elevation_deg = tx_elevation_deg
        self.rx_azimuth_deg = rx_azimuth_deg
        self.rx_elevation_deg = rx_elevation_deg
        self.tx_power_dbm = tx_power_dbm
        self.losses_db = losses_db
        
        # Calcular distância se não fornecida
        if distance_m is None:
            dx = rx_position.x_m - tx_position.x_m
            dy = rx_position.y_m - tx_position.y_m
            dz = rx_position.z_m - tx_position.z_m
            self.distance_m = math.sqrt(dx**2 + dy**2 + dz**2)
        else:
            self.distance_m = distance_m
    
    def _directivity_gain_reduction_db(
        self,
        antenna_type: str,
        off_axis_angle_deg: float
    ) -> float:
        """Redução de ganho por off-axis angle"""
        
        if antenna_type == "Monopole" or antenna_type == "Dipole":
            # Omnidirecionais: sem perda
            return 0
        
        elif antenna_type == "Yagi":
            # Modelo cos^n simplificado
            n = 2
            off_axis_rad = math.radians(off_axis_angle_deg)
            reduction = -10 * n * math.log10(abs(math.cos(off_axis_rad)) + 0.01)
            return min(reduction, -30)  # Máximo -30 dB atrás
        
        elif antenna_type == "ReflectorAntenna":
            # Parabola: modelo estreito (gaussiano)
            beamwidth = getattr(self.antenna, 'beamwidth_3db_deg', 1.0)
            reduction = -12 * (off_axis_angle_deg / beamwidth) ** 2
            return min(reduction, -40)  # Máximo -40 dB
        
        else:
            return 0
    
    def received_power_dbm_with_directivity(self) -> float:
        """Potência recebida considerando diretividade"""
        
        # TX: perda por desalinhamento
        tx_off_axis = math.degrees(
            math.acos(max(-1, min(1, math.cos(math.radians(self.tx_azimuth_deg)))))
        )
        tx_reduction = self._directivity_gain_reduction_db(
            self.tx_antenna.antenna_type, tx_off_axis
        )
        
        # RX: perda por desalinhamento
        rx_off_axis = math.degrees(
            math.acos(max(-1, min(1, math.cos(math.radians(self.rx_azimuth_deg)))))
        )
        rx_reduction = self._directivity_gain_reduction_db(
            self.rx_antenna.antenna_type, rx_off_axis
        )
        
        # Friis com ganhos reduzidos
        from lora_antenna.formulas import friis_received_power_dbm
        
        tx_gain_effective = self.tx_antenna.gain_dbi + tx_reduction
        rx_gain_effective = self.rx_antenna.gain_dbi + rx_reduction
        
        return friis_received_power_dbm(
            tx_power_dbm=self.tx_power_dbm,
            tx_gain_dbi=tx_gain_effective,
            rx_gain_dbi=rx_gain_effective,
            distance_m=self.distance_m,
            frequency_hz=self.tx_antenna.frequency_hz,
            losses_db=self.losses_db
        )
```

#### 6.3 `src/lora_antenna/rf_chain/chain.py` (NOVO)
```python
from dataclasses import dataclass, field
from typing import Optional
from lora_antenna.antenna.base import Antenna

@dataclass
class TxChain:
    """Cadeia transmissora completa"""
    
    base_power_dbm: float = 14  # SX1276 ou similar
    pa_gain_db: float = 0  # 0 (sem PA) até +13 dB
    tx_filter_loss_db: float = 1.0
    tx_circulator_loss_db: float = 0.5
    tx_cable_loss_db: float = 0  # Calculado automaticamente
    tx_connectors_loss_db: float = 0.4  # ~2 conectores @ 0.2 dB each
    
    @property
    def eirp_dbm(self, antenna_gain_dbi: float) -> float:
        """EIRP = Pt + PA + Gt - todas as perdas"""
        losses = (
            self.tx_filter_loss_db +
            self.tx_circulator_loss_db +
            self.tx_cable_loss_db +
            self.tx_connectors_loss_db
        )
        return self.base_power_dbm + self.pa_gain_db + antenna_gain_dbi - losses

@dataclass
class RxChain:
    """Cadeia receptora completa"""
    
    rx_filter_loss_db: float = 1.0
    rx_circulator_loss_db: float = 0.5
    rx_cable_loss_db: float = 0
    rx_connectors_loss_db: float = 0.4
    lna_gain_db: float = 0  # 0 (sem LNA) até +35 dB
    lna_nf_db: float = 1.0  # Figura de ruído
    
    @property
    def effective_sensitivity_dbm(self, base_sensitivity_dbm: float) -> float:
        """Sensibilidade efetiva com LNA"""
        losses = (
            self.rx_filter_loss_db +
            self.rx_circulator_loss_db +
            self.rx_cable_loss_db +
            self.rx_connectors_loss_db
        )
        return base_sensitivity_dbm - self.lna_gain_db + losses + self.lna_nf_db

@dataclass
class LinkBudgetComplete:
    """Link budget COMPLETO (cadeia TX/RX + todas as perdas)"""
    
    tx_antenna: Antenna
    rx_antenna: Antenna
    distance_m: float
    
    tx_chain: TxChain = field(default_factory=TxChain)
    rx_chain: RxChain = field(default_factory=RxChain)
    
    obstacles_loss_db: float = 0
    
    def link_margin_db(self, rx_base_sensitivity_dbm: float = -137) -> float:
        """Margem com cadeia completa"""
        
        eirp = self.tx_chain.eirp_dbm(self.tx_antenna.gain_dbi)
        
        # FSPL
        from lora_antenna.formulas import fspl_db
        fspl = fspl_db(self.distance_m, self.tx_antenna.frequency_hz)
        
        # Potência recebida
        received = eirp - fspl - self.obstacles_loss_db + self.rx_antenna.gain_dbi
        
        # Sensibilidade efetiva
        eff_sensitivity = self.rx_chain.effective_sensitivity_dbm(rx_base_sensitivity_dbm)
        
        return received - eff_sensitivity
```

#### 6.4 UI para Link Budget
```python
# src/lora_antenna/ui/pages/link.py
import streamlit as st
from lora_antenna.models.geo import GeographicPosition
from lora_antenna.propagation.link_budget import LinkBudget, LinkWithDirectivity
from lora_antenna.rf_chain.chain import LinkBudgetComplete, TxChain, RxChain

st.title("🔗 Link Budget Calculator")

# Carregar antenas (from database ou session)
# ...

col1, col2 = st.columns(2)

with col1:
    st.subheader("TX Antenna")
    tx_antenna = st.selectbox("Select TX Antenna", ["Monopole 915MHz", "Yagi 915MHz"])

with col2:
    st.subheader("RX Antenna")
    rx_antenna = st.selectbox("Select RX Antenna", ["Monopole 915MHz", "Parabola 915MHz"])

# Distância
distance = st.slider("Distance (m)", 100, 10000, 1000)

# Modo simples vs completo
mode = st.radio("Mode", ["Simple (Friis)", "With Directivity", "Complete (TX/RX Chains)"])

if mode == "Simple (Friis)":
    # LinkBudget simples
    pass

elif mode == "With Directivity":
    # LinkWithDirectivity
    st.subheader("Orientation")
    col1, col2 = st.columns(2)
    with col1:
        tx_az = st.number_input("TX Azimuth (°)", 0, 360, 0)
        tx_el = st.number_input("TX Elevation (°)", -90, 90, 0)
    with col2:
        rx_az = st.number_input("RX Azimuth (°)", 0, 360, 180)
        rx_el = st.number_input("RX Elevation (°)", -90, 90, 0)

elif mode == "Complete (TX/RX Chains)":
    st.subheader("TX Chain")
    pa_gain = st.slider("PA Gain (dB)", 0, 13, 0)
    
    st.subheader("RX Chain")
    lna_gain = st.slider("LNA Gain (dB)", 0, 35, 0)
    
    # Comparação antes/depois
    # ...
```

### Critérios de Aceite (DoD)

- [ ] LinkBudget, LinkWithDirectivity, LinkBudgetComplete implementados
- [ ] UI para link budget funciona
- [ ] Comparação PA/LNA on/off mostra diferenças reais
- [ ] Testes passam: `pytest tests/test_friis_budget.py`
- [ ] Margem de enlace calculada corretamente

### Validação Automática

```bash
# Checklist Sprint 5-6

# 1. Testes
uv run pytest tests/test_friis_budget.py tests/test_link_directivity.py -v

# 2. Validação de casos conhecidos
python -c "
from lora_antenna.propagation.link_budget import LinkBudget
from lora_antenna.antenna.monopole import Monopole

tx = Monopole(frequency_hz=915e6, id='tx', name='TX')
rx = Monopole(frequency_hz=915e6, id='rx', name='RX')
link = LinkBudget(tx, rx, distance_m=1000, tx_power_dbm=14)

pr = link.received_power_dbm
assert abs(pr - (-73.37)) < 0.5, f'Expected -73.37 dBm, got {pr}'
print(f'✓ Link budget: {pr:.2f} dBm')
"

# 3. UI testa
timeout 10 uv run streamlit run src/lora_antenna/app.py &
```
