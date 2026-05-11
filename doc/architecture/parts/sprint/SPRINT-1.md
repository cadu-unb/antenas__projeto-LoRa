### Objetivos Curto Prazo
- Funções matemáticas puras implementadas
- Testes unitários para casos conhecidos
- Validação contra literatura (cases conhecidos)

### Dependências
- Sprint 0.5: docs com fórmulas ✓
- Sprint 0: ambiente rodando ✓

### Tarefas Principais

#### 3.1 `src/lora_antenna/constants.py`
```python
# Constantes físicas
C_M_PER_S = 299_792_458  # Velocidade da luz

# Bandas LoRa
FREQ_433_MHZ = 433e6
FREQ_868_MHZ = 868e6
FREQ_915_MHZ = 915e6

# Impedância de referência
Z0_OHM = 50

# SX1276 sensibilidades (SF7-SF12 @ BW=125kHz)
SX1276_SENSITIVITY_DBM = {
    7: -123,
    8: -126,
    9: -129,
    10: -132,
    11: -134,
    12: -137,
}
```

#### 3.2 `src/lora_antenna/formulas.py`
```python
import math
from lora_antenna.constants import C_M_PER_S

def wavelength_m(frequency_hz: float) -> float:
    """λ = c / f"""
    return C_M_PER_S / frequency_hz

def effective_area_m2(gain_dbi: float, wavelength_m: float) -> float:
    """A_e = G * λ² / (4π)"""
    gain_linear = 10 ** (gain_dbi / 10)
    return gain_linear * wavelength_m ** 2 / (4 * math.pi)

def reflection_coefficient(z_load: complex, z0: float = 50) -> complex:
    """Γ = (Z_L - Z0) / (Z_L + Z0)"""
    return (z_load - z0) / (z_load + z0)

def vswr(z_load: complex, z0: float = 50) -> float:
    """VSWR = (1 + |Γ|) / (1 - |Γ|)"""
    gamma = reflection_coefficient(z_load, z0)
    gamma_mag = abs(gamma)
    return (1 + gamma_mag) / (1 - gamma_mag)

def return_loss_db(gamma: complex) -> float:
    """RL = -20 * log10(|Γ|)"""
    return -20 * math.log10(abs(gamma))

def fspl_db(distance_m: float, frequency_hz: float) -> float:
    """FSPL = 20*log10(distance) + 20*log10(f) + 20*log10(4π/c)"""
    const = 20 * math.log10(4 * math.pi / C_M_PER_S)
    return 20 * math.log10(distance_m) + 20 * math.log10(frequency_hz) + const

def friis_received_power_dbm(
    tx_power_dbm: float,
    tx_gain_dbi: float,
    rx_gain_dbi: float,
    distance_m: float,
    frequency_hz: float,
    losses_db: float = 0
) -> float:
    """Pr(dBm) = Pt + Gt + Gr - FSPL - losses"""
    fspl = fspl_db(distance_m, frequency_hz)
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - fspl - losses_db

def link_margin_db(received_power_dbm: float, sensitivity_dbm: float) -> float:
    """Margem = Pr - Sensibilidade"""
    return received_power_dbm - sensitivity_dbm
```

#### 3.3 `tests/test_formulas.py`
```python
import math
import pytest
from lora_antenna.formulas import (
    wavelength_m, effective_area_m2, vswr, fspl_db, friis_received_power_dbm
)

class TestFormulas:
    
    def test_wavelength_915mhz(self):
        """Test case: λ @ 915 MHz ≈ 0.3276 m"""
        expected = 0.3276
        actual = wavelength_m(915e6)
        assert abs(actual - expected) < 0.0005  # ±0.1%
    
    def test_wavelength_868mhz(self):
        """Test case: λ @ 868 MHz ≈ 0.3456 m"""
        expected = 0.3456
        actual = wavelength_m(868e6)
        assert abs(actual - expected) < 0.0005
    
    def test_fspl_1km_915mhz(self):
        """Test case: FSPL @ 1 km, 915 MHz ≈ 91.67 dB"""
        expected = 91.67
        actual = fspl_db(1000, 915e6)
        assert abs(actual - expected) < 0.1
    
    def test_friis_monopole_monopole(self):
        """
        Test case: Monopole-Monopole link
        Pt=14 dBm, Gt=2.15 dBi, Gr=2.15 dBi, dist=1km, f=915MHz
        Expected Pr ≈ -73.37 dBm
        """
        actual = friis_received_power_dbm(
            tx_power_dbm=14,
            tx_gain_dbi=2.15,
            rx_gain_dbi=2.15,
            distance_m=1000,
            frequency_hz=915e6,
            losses_db=0
        )
        expected = -73.37
        assert abs(actual - expected) < 0.5
```

### Critérios de Aceite (DoD)

- [ ] `pytest tests/test_formulas.py` passa 100%
- [ ] Todos os casos conhecidos dentro de tolerância
- [ ] Code coverage > 95%
- [ ] Sem warnings (ruff, mypy)
- [ ] Documentação em docstrings

### Validação Automática

```bash
# Checklist Sprint 1

# 1. Testes passam
uv run pytest tests/test_formulas.py -v

# 2. Coverage
uv run pytest tests/test_formulas.py --cov=src/lora_antenna --cov-report=term

# 3. Linting
uv run ruff check src/lora_antenna/formulas.py

# 4. Type check
uv run mypy src/lora_antenna/formulas.py

# 5. Docstring coverage
python -m doctest src/lora_antenna/formulas.py -v
```

### Rollback Plan

```bash
# Se teste falhar
git diff tests/test_formulas.py  # Revisar mudança
git checkout tests/test_formulas.py

# Se fórmula estiver errada
# Consultar docs/formulas.md e literatura
```