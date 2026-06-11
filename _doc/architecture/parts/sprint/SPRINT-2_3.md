### Objetivos Curto Prazo
- Modelos Pydantic para antenas
- 6 tipos de antena funcionais (Monopole até ReflectorAntenna)
- Serialização JSON/SQLite
- Testes de instanciação

### Dependências
- Sprint 1: formulas.py ✓
- docs/antenna_details.md ✓

### Tarefas Principais

#### 4.1 `src/lora_antenna/antenna/base.py`
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, List

class Antenna(BaseModel):
    """Base class para todas as antenas"""
    
    id: str = Field(..., description="UUID único")
    name: str = Field(..., description="Nome descritivo")
    antenna_type: str = Field(..., description="Tipo (Monopole, Dipole, etc)")
    frequency_hz: float = Field(..., gt=0, description="Frequência em Hz")
    gain_dbi: float = Field(..., description="Ganho em dBi")
    impedance_ohm: complex = Field(default=complex(50, 0))
    vswr: float = Field(default=1.0)
    efficiency: float = Field(default=0.9)
    polarization: str = Field(default="Linear")
    effective_area_m2: float = Field(default=0.0)
    orientation_azimuth_deg: float = Field(default=0.0)
    orientation_elevation_deg: float = Field(default=0.0)
    location: Optional[Dict] = Field(default=None)
    schema_version: str = Field(default="1.0")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None)
    radiation_pattern: Optional[Dict[str, List[float]]] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ant-001",
                "name": "Monopole 915MHz",
                "antenna_type": "Monopole",
                "frequency_hz": 915e6,
                "gain_dbi": 2.15,
            }
        }
```

#### 4.2 `src/lora_antenna/antenna/monopole.py`
```python
import math
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class Monopole(Antenna):
    """Antena monopolo λ/4"""
    
    def __init__(self, frequency_hz: float, **kwargs):
        self.antenna_type = "Monopole"
        self.frequency_hz = frequency_hz
        
        # Cálculos automáticos
        wl = wavelength_m(frequency_hz)
        self.height_m = wl / 4
        self.gain_dbi = 2.15  # Nominal
        self.impedance_ohm = complex(36.5, 21.25)  # Ressonante
        self.vswr = 2.0
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        self.efficiency = 0.9
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.3 `src/lora_antenna/antenna/dipole.py`
```python
from enum import Enum
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class DipoleEnvironment(str, Enum):
    FREE_SPACE = "free_space"
    ABOVE_GROUND = "above_ground"
    NEAR_STRUCTURE = "near_structure"
    CAVITY = "cavity"

class Dipole(Antenna):
    """Antena dipolo λ/2"""
    
    def __init__(
        self,
        frequency_hz: float,
        environment: DipoleEnvironment = DipoleEnvironment.FREE_SPACE,
        **kwargs
    ):
        self.antenna_type = "Dipole"
        self.frequency_hz = frequency_hz
        self.environment = environment
        
        wl = wavelength_m(frequency_hz)
        self.length_m = wl / 2
        self.gain_dbi = 2.15  # Base
        
        # Ajustar por ambiente
        if environment == DipoleEnvironment.FREE_SPACE:
            self.impedance_ohm = complex(73.1, 0)
            self.vswr = 1.45
        elif environment == DipoleEnvironment.ABOVE_GROUND:
            self.impedance_ohm = complex(60, -25)
            self.vswr = 2.0
        elif environment == DipoleEnvironment.NEAR_STRUCTURE:
            self.impedance_ohm = complex(50, -50)
            self.vswr = 2.5
        else:  # CAVITY
            self.impedance_ohm = complex(80, 40)
            self.vswr = 2.8
        
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        self.efficiency = 0.85
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.4 `src/lora_antenna/antenna/ground_plane.py`
```python
from enum import Enum
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class GroundPlaneShape(str, Enum):
    SQUARE = "square"
    CIRCULAR = "circular"
    INFINITE = "infinite"

class GroundPlane(Antenna):
    """Monopolo λ/4 sobre plano de terra"""
    
    def __init__(
        self,
        frequency_hz: float,
        plane_size_wavelengths: float = 2.0,
        shape: GroundPlaneShape = GroundPlaneShape.SQUARE,
        **kwargs
    ):
        self.antenna_type = "Ground Plane"
        self.frequency_hz = frequency_hz
        self.plane_size_wavelengths = plane_size_wavelengths
        self.shape = shape
        
        wl = wavelength_m(frequency_hz)
        self.monopole_height_m = wl / 4
        self.plane_size_m = plane_size_wavelengths * wl
        self.gain_dbi = 5.15  # +3 dB vs monopole standalone
        
        # Impedância depende do tamanho do plano
        if plane_size_wavelengths >= 2.0:
            self.impedance_ohm = complex(45, 0)
            self.design_note = "✓ Tamanho adequado (≥ 2λ)"
        else:
            factor = plane_size_wavelengths / 2.0
            z_real = 45 / factor
            self.impedance_ohm = complex(z_real, 0)
            self.design_note = "⚠️ Aviso: Plano pequeno, impedância pode variar ±20%"
        
        self.vswr = 1.5
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        self.efficiency = 0.9
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.5 `src/lora_antenna/antenna/patch.py`
```python
from enum import Enum
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class SubstrateType(str, Enum):
    FR4 = "FR4"
    ROGERS_4003 = "Rogers 4003"
    ROGERS_5880 = "Rogers 5880"
    DUROID = "Duroid"

# Tabela de substratos
SUBSTRATE_DATA = {
    "FR4": {"epsilon_r": 4.4, "tan_delta": 0.02, "thickness_mm": 1.6},
    "Rogers 4003": {"epsilon_r": 3.55, "tan_delta": 0.0027, "thickness_mm": 0.508},
    "Rogers 5880": {"epsilon_r": 2.2, "tan_delta": 0.0009, "thickness_mm": 0.787},
    "Duroid": {"epsilon_r": 2.17, "tan_delta": 0.0009, "thickness_mm": 0.787},
}

class Patch(Antenna):
    """Antena Patch (Microstrip)"""
    
    def __init__(
        self,
        frequency_hz: float,
        substrate: SubstrateType = SubstrateType.FR4,
        **kwargs
    ):
        self.antenna_type = "Patch"
        self.frequency_hz = frequency_hz
        self.substrate_type = substrate
        
        wl = wavelength_m(frequency_hz)
        sub = SUBSTRATE_DATA[substrate.value]
        
        # Dimensões (Pozar aproximado)
        self.length_m = wl / (2 * (sub["epsilon_r"] ** 0.5))
        self.width_m = self.length_m * 1.2
        
        # Ganho depende do substrato
        if substrate == SubstrateType.FR4:
            self.gain_dbi = 5.5
            self.efficiency = 0.8
        elif substrate == SubstrateType.ROGERS_4003:
            self.gain_dbi = 6.0
            self.efficiency = 0.85
        elif substrate == SubstrateType.ROGERS_5880:
            self.gain_dbi = 6.5
            self.efficiency = 0.9
        else:  # DUROID
            self.gain_dbi = 6.8
            self.efficiency = 0.92
        
        self.impedance_ohm = complex(50, 0)
        self.vswr = 1.2
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.6 `src/lora_antenna/antenna/yagi.py`
```python
import math
from lora_antenna.antenna.base import Antenna
from lora_antenna.formulas import wavelength_m, effective_area_m2

class Yagi(Antenna):
    """Antena Yagi-Uda com 3-10 elementos"""
    
    def __init__(
        self,
        frequency_hz: float,
        num_elements: int = 5,
        **kwargs
    ):
        self.antenna_type = "Yagi"
        self.frequency_hz = frequency_hz
        self.num_elements = num_elements
        
        if num_elements < 3 or num_elements > 10:
            raise ValueError("num_elements deve estar entre 3 e 10")
        
        wl = wavelength_m(frequency_hz)
        
        # Ganho empírico (Cebik formula)
        num_directors = num_elements - 2
        self.gain_dbi = 8 + 4.5 * math.log10(max(num_directors, 1))
        
        # HPBW aproximado
        self.hpbw_deg = 50 / max(self.gain_dbi, 1)
        
        self.impedance_ohm = complex(50, 0)
        self.vswr = 1.3
        self.efficiency = 0.95
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        
        # Orientation obrigatória para diretivas
        self.design_note = "⚠️ Orientação (azimute/elevação) OBRIGATÓRIA"
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.7 `src/lora_antenna/antenna/reflector.py` (NOVO)
```python
from enum import Enum
from typing import Optional
from pydantic import Field
from lora_antenna.antenna.base import Antenna
from lora_antenna.antenna.feeds import FeedSpecification
from lora_antenna.formulas import wavelength_m, effective_area_m2
import math

class ReflectorType(str, Enum):
    PARABOLIC_CIRCULAR = "parabolic_circular"
    PARABOLIC_OFFSET = "parabolic_offset"
    CASSEGRAIN = "cassegrain"
    GREGORIAN = "gregorian"

class ReflectorAntenna(Antenna):
    """Antena refletora (base para paraboloides)"""
    
    reflector_type: ReflectorType = Field(..., description="Tipo de refletora")
    primary_diameter_m: float = Field(..., gt=0, description="Diâmetro primário")
    focal_ratio: float = Field(default=0.4, gt=0, lt=1)
    efficiency_aperture: float = Field(default=0.65, gt=0, lt=1)
    feed_specification: FeedSpecification = Field(..., description="Alimentador (OBRIGATÓRIO)")
    
    def __init__(
        self,
        frequency_hz: float,
        reflector_type: ReflectorType = ReflectorType.PARABOLIC_OFFSET,
        primary_diameter_m: float = 0.5,
        feed_specification: FeedSpecification = None,
        **kwargs
    ):
        self.antenna_type = "ReflectorAntenna"
        self.frequency_hz = frequency_hz
        self.reflector_type = reflector_type
        self.primary_diameter_m = primary_diameter_m
        
        if feed_specification is None:
            raise ValueError("feed_specification é OBRIGATÓRIO")
        self.feed_specification = feed_specification
        
        wl = wavelength_m(frequency_hz)
        
        # Ganho: G = η_total * (π * D / λ)²
        self.focal_length_m = self.focal_ratio * primary_diameter_m
        eta_total = self.efficiency_aperture * feed_specification.efficiency
        gain_linear = eta_total * (math.pi * primary_diameter_m / wl) ** 2
        self.gain_dbi = 10 * math.log10(gain_linear)
        
        # HPBW: ~1.22 * λ / D
        self.beamwidth_3db_deg = 1.22 * wl / primary_diameter_m
        
        self.impedance_ohm = complex(50, 0)
        self.vswr = 1.5
        self.efficiency = eta_total
        self.effective_area_m2 = effective_area_m2(self.gain_dbi, wl)
        
        # CRÍTICO: Feed determina o resultado
        self.design_note = (
            f"⚠️ Ganho depende do feed: "
            f"G = {self.gain_dbi:.1f} dBi "
            f"(aperture {self.efficiency_aperture:.0%} × feed {feed_specification.efficiency:.0%})"
        )
        
        super().__init__(frequency_hz=frequency_hz, **kwargs)
```

#### 4.8 `src/lora_antenna/antenna/feeds.py` (NOVO)
```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Literal

class FeedType(str, Enum):
    HORN_PYRAMIDAL = "horn_pyramidal"
    HORN_CONICAL_CORRUGATED = "horn_conical_corrugated"
    HORN_EXPONENTIAL = "horn_exponential"
    DIPOLE = "dipole"
    PATCH = "patch"
    HELICAL = "helical"
    PROBE = "probe"

# Tabela de Feeds (eficiências reais)
FEED_TABLE = {
    "dipole": {"efficiency": 0.40, "beamwidth_deg": 170, "gain_dbi": 2.0},
    "probe": {"efficiency": 0.45, "beamwidth_deg": 160, "gain_dbi": 2.5},
    "patch": {"efficiency": 0.60, "beamwidth_deg": 120, "gain_dbi": 5.0},
    "horn_pyramidal": {"efficiency": 0.75, "beamwidth_deg": 100, "gain_dbi": 12.0},
    "horn_exponential": {"efficiency": 0.78, "beamwidth_deg": 95, "gain_dbi": 12.5},
    "horn_conical_corrugated": {"efficiency": 0.82, "beamwidth_deg": 95, "gain_dbi": 13.0},
    "helical": {"efficiency": 0.70, "beamwidth_deg": 110, "gain_dbi": 11.0},
}

class FeedSpecification(BaseModel):
    """Especificação de alimentador para refletoras"""
    
    feed_type: FeedType = Field(..., description="Tipo de feed")
    efficiency: float = Field(..., gt=0, lt=1, description="Eficiência (0-1)")
    beamwidth_deg: float = Field(..., gt=0, description="Beamwidth em graus")
    impedance_ohm: complex = Field(default=complex(50, 0))
    return_loss_db: float = Field(default=-20.0)
    polarization: str = Field(default="Linear")
    operating_bandwidth_mhz: float = Field(default=10.0)
    feeding_method: Literal["waveguide", "coaxial", "probe"] = Field(default="coaxial")
    feeding_loss_db: float = Field(default=0.5)
    gain_dbi: float = Field(default=0.0)
    
    @classmethod
    def from_type(cls, feed_type: FeedType) -> "FeedSpecification":
        """Factory method para criar feeds a partir de tipo"""
        data = FEED_TABLE.get(feed_type.value)
        if not data:
            raise ValueError(f"Feed type {feed_type} não encontrado na tabela")
        
        return cls(
            feed_type=feed_type,
            efficiency=data["efficiency"],
            beamwidth_deg=data["beamwidth_deg"],
            gain_dbi=data["gain_dbi"],
        )
```

#### 4.9 Testes de Antenas
```python
# tests/test_antenna_monopole.py
import pytest
from lora_antenna.antenna.monopole import Monopole

def test_monopole_915mhz():
    ant = Monopole(frequency_hz=915e6, name="Test Monopole", id="mon-001")
    assert ant.antenna_type == "Monopole"
    assert abs(ant.gain_dbi - 2.15) < 0.1
    assert ant.height_m > 0
    assert abs(ant.height_m - 0.0819) < 0.0005  # λ/4

def test_monopole_pydantic_export():
    ant = Monopole(frequency_hz=~~868e6~~ (Fora da faixa definida pela ANATEL), name="Test", id="mon-002")
    json_str = ant.model_dump_json()
    assert "Monopole" in json_str
    assert "868" in json_str  # ~~868 MHz~~ (Fora da faixa definida pela ANATEL).
```

### Critérios de Aceite (DoD)

- [ ] 6 classes de antena implementadas (Monopole até ReflectorAntenna)
- [ ] FeedSpecification com 7 tipos tabelados
- [ ] Serialização Pydantic funciona (to_json, from_json)
- [ ] Todos os testes passam: `pytest tests/test_antenna_*.py`
- [ ] Impedância, VSWR, ganho dentro de faixas esperadas
- [ ] Warnings e disclaimers aparecem corretamente

### Validação Automática

```bash
# Checklist Sprint 2-3

# 1. Testes de antenas
uv run pytest tests/test_antenna_*.py -v

# 2. Cobertura
uv run pytest tests/test_antenna_*.py --cov=src/lora_antenna/antenna

# 3. Linting
uv run ruff check src/lora_antenna/antenna/

# 4. Type checking
uv run mypy src/lora_antenna/antenna/

# 5. Serialização JSON
python -c "
from lora_antenna.antenna.monopole import Monopole
m = Monopole(frequency_hz=915e6, id='test', name='Test')
print(m.model_dump_json())
"
```

### Rollback Plan

```bash
# Se antena quebrar
git diff src/lora_antenna/antenna/

# Se teste falhar, revisar valores esperados
# Consultar docs/antenna_details.md

# Rollback completo do sprint
git reset --hard <commit-anterior>
```

