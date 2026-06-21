# Fase 2 — Modelos e Schemas

**Objetivo:** enriquecer os modelos de dados para suportar as features físicas das fases seguintes — sem ainda implementar a lógica de cálculo. Esta fase é pré-requisito para Fases 3 e 4.

**Dependências:** Fase 1 concluída.
**Arquivos afetados:** `backend/app/schemas/node_spec.py`, `backend/app/schemas/link_scenario.py`, `backend/app/schemas/lora_module.py` (novo), `backend/app/api/library_routes.py`, `backend/app/storage/`, `backend/app/solvers/`

---

## Etapa 1 — Estender `NodeSpec` com Perdas Adicionais e Orientação

**Objetivo:** adicionar ao `NodeSpec` os campos de perda extra, polarização, fading e orientação de antena (pré-requisito para G(θ,φ) na Fase 3).

### 1.1 — Editar `backend/app/schemas/node_spec.py`

Adicionar os seguintes campos à classe `NodeSpec`:

```python
class NodeSpec(BaseModel):
    # Campos existentes (não remover):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    lat: float
    lon: float
    height_m: float = 0.0
    antenna_id: Optional[str] = None
    tx_power_dbm: float = 14.0
    rx_sensitivity_dbm: float = -137.0
    cable_loss_db: float = 0.0
    is_hub: bool = False

    # Novos campos de perda (Gap 4 e 11):
    extra_loss_db: float = Field(
        default=0.0,
        description="Perda adicional por obstrução, vegetação ou clutter (dB). Ex: 8 dB em campus arborizado."
    )
    fading_margin_db: float = Field(
        default=0.0,
        description="Margem de fading a reservar para variações temporais do canal (dB). Ex: 10 dB para link crítico."
    )
    polarization_loss_db: float = Field(
        default=0.0,
        description="Perda por descasamento de polarização TX/RX (dB). Ex: 3 dB para V vs H."
    )

    # Novos campos de orientação (Gap 3 — pré-requisito para G(θ,φ)):
    azimuth_deg: Optional[float] = Field(
        default=None,
        description="Azimute do boresight da antena (graus, 0=Norte, clockwise). None = omnidirecional."
    )
    tilt_deg: float = Field(
        default=0.0,
        description="Inclinação do boresight em elevação (graus, positivo = acima do horizonte)."
    )
    lora_module_id: Optional[str] = Field(
        default=None,
        description="ID do módulo LoRa selecionado da biblioteca de módulos. Sobrescreve rx_sensitivity_dbm e tx_power_dbm se preenchido."
    )
```

### 1.2 — Verificar compatibilidade retroativa

Os novos campos têm todos `default` definido, então cenários salvos anteriormente (JSON sem esses campos) continuarão a carregar sem erro — Pydantic preencherá com os defaults.

Testar:
```bash
uv run pytest tests/ -v   # zero falhas após essa alteração
```

---

## Etapa 2 — Schema de Módulo LoRa (`LoRaModule`)

**Objetivo:** criar um catálogo de módulos LoRa com sensibilidades por SF/BW, corrente de TX e parâmetros de consumo (Gap 6).

### 2.1 — Criar `backend/app/schemas/lora_module.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class SensitivityByMode(BaseModel):
    sf: int            # Spreading Factor (7–12)
    bw_khz: int        # Bandwidth em kHz (125, 250, 500)
    sensitivity_dbm: float

class LoRaModule(BaseModel):
    id: str
    name: str                                    # ex: "RFM95W_915MHz"
    manufacturer: str                            # ex: "HopeRF"
    frequency_mhz: float                         # ex: 915.0
    tx_power_options_dbm: list[float]            # ex: [7, 10, 14, 17, 20]
    tx_current_options_ma: list[float]           # mA correspondente a cada opção de TX
    voltage_range_v: tuple[float, float]         # ex: (1.8, 3.7)
    sleep_current_ua: float                      # µA
    sensitivity_modes: list[SensitivityByMode]   # tabela SF × BW × sensibilidade
    notes: str = ""

    def get_sensitivity(self, sf: int = 12, bw_khz: int = 125) -> Optional[float]:
        """Retorna sensibilidade (dBm) para o modo SF/BW solicitado."""
        for mode in self.sensitivity_modes:
            if mode.sf == sf and mode.bw_khz == bw_khz:
                return mode.sensitivity_dbm
        return None
```

### 2.2 — Criar catálogo inicial `backend/app/data/lora_modules.json`

Criar o arquivo com os três módulos do MATLAB de referência:

```json
[
  {
    "id": "rfm95w_915",
    "name": "RFM95W_915MHz",
    "manufacturer": "HopeRF",
    "frequency_mhz": 915.0,
    "tx_power_options_dbm": [7, 10, 14, 17, 20],
    "tx_current_options_ma": [28, 29, 29, 87, 120],
    "voltage_range_v": [1.8, 3.7],
    "sleep_current_ua": 0.2,
    "sensitivity_modes": [
      {"sf": 12, "bw_khz": 125, "sensitivity_dbm": -139},
      {"sf": 10, "bw_khz": 125, "sensitivity_dbm": -136},
      {"sf": 7,  "bw_khz": 125, "sensitivity_dbm": -118}
    ],
    "notes": "LongRange: SF12=-139dBm, Balanced: SF10=-136dBm, HighDataRate: SF7=-118dBm"
  },
  {
    "id": "lro2_asr6601",
    "name": "LRO2_ASR6601",
    "manufacturer": "ASR",
    "frequency_mhz": 915.0,
    "tx_power_options_dbm": [10, 14, 17, 20, 22],
    "tx_current_options_ma": [38, 42, 70, 80, 100],
    "voltage_range_v": [2.0, 3.7],
    "sleep_current_ua": 1.0,
    "sensitivity_modes": [
      {"sf": 12, "bw_khz": 125, "sensitivity_dbm": -138},
      {"sf": 10, "bw_khz": 125, "sensitivity_dbm": -135},
      {"sf": 7,  "bw_khz": 125, "sensitivity_dbm": -117}
    ],
    "notes": "ASR6601 — módulo LoRa/LoRaWAN 915 MHz"
  },
  {
    "id": "e220_900t22d",
    "name": "E220_900T22D",
    "manufacturer": "EBYTE",
    "frequency_mhz": 900.0,
    "tx_power_options_dbm": [13, 17, 20, 22],
    "tx_current_options_ma": [100, 180, 380, 480],
    "voltage_range_v": [2.3, 5.5],
    "sleep_current_ua": 2.0,
    "sensitivity_modes": [
      {"sf": 12, "bw_khz": 125, "sensitivity_dbm": -147},
      {"sf": 10, "bw_khz": 125, "sensitivity_dbm": -143},
      {"sf": 7,  "bw_khz": 125, "sensitivity_dbm": -126}
    ],
    "notes": "EBYTE E220 — chip SX1268, 22 dBm, alta sensibilidade"
  }
]
```

### 2.3 — Criar `backend/app/storage/lora_module_storage.py`

```python
import json
from pathlib import Path
from backend.app.schemas.lora_module import LoRaModule

_DATA_FILE = Path(__file__).parent.parent / "data" / "lora_modules.json"

def list_modules() -> list[LoRaModule]:
    with open(_DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return [LoRaModule(**item) for item in raw]

def get_module(module_id: str) -> LoRaModule | None:
    for m in list_modules():
        if m.id == module_id:
            return m
    return None
```

### 2.4 — Adicionar rotas em `backend/app/api/library_routes.py`

Ao final do arquivo, adicionar:

```python
from backend.app.storage import lora_module_storage
from backend.app.schemas.lora_module import LoRaModule

@router.get("/lora-modules", response_model=list[LoRaModule])
async def list_lora_modules():
    """Lista todos os módulos LoRa disponíveis no catálogo."""
    return lora_module_storage.list_modules()

@router.get("/lora-modules/{module_id}", response_model=LoRaModule)
async def get_lora_module(module_id: str):
    m = lora_module_storage.get_module(module_id)
    if m is None:
        raise HTTPException(status_code=404, detail="Módulo não encontrado")
    return m
```

### 2.5 — Escrever testes

Criar `tests/test_lora_modules.py`:

```python
def test_list_modules_returns_three(client):
    resp = client.get("/api/v1/library/lora-modules")
    assert resp.status_code == 200
    assert len(resp.json()) == 3

def test_rfm95w_sensitivity_sf12(client):
    resp = client.get("/api/v1/library/lora-modules/rfm95w_915")
    assert resp.status_code == 200
    modes = resp.json()["sensitivity_modes"]
    sf12 = next(m for m in modes if m["sf"] == 12)
    assert sf12["sensitivity_dbm"] == -139

def test_unknown_module_404(client):
    resp = client.get("/api/v1/library/lora-modules/nao_existe")
    assert resp.status_code == 404
```

---

## Etapa 3 — Novos Tipos de Antena (Gap 2)

**Objetivo:** adicionar `PCB_Compact` e `Commercial_Omni_6dBi` ao sistema de solvers.

### 3.1 — Criar `backend/app/solvers/pcb_solver.py`

`PCB_Compact` — antena integrada ao PCB, quasi-omnidirecional, G ≈ 0–2 dBi com irregularidades angulares:

```python
import math
from backend.app.solvers.base_solver import BaseSolver

class PcbSolver(BaseSolver):
    antenna_type = "pcb_compact"

    def gain_dbi(self, freq_hz: float, **kwargs) -> float:
        """Ganho típico de antena PCB integrada: 0 a 2 dBi conforme frequência."""
        freq_mhz = freq_hz / 1e6
        if freq_mhz < 800:
            return 0.0
        elif freq_mhz < 1000:
            return 1.5
        else:
            return 2.0

    def impedance_ohm(self, freq_hz: float, **kwargs) -> float:
        """Impedância nominal de antena PCB: 50 Ω."""
        return 50.0

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """
        Padrão quasi-omni com irregularidades.
        theta: 0 = boresight (horizontal), 90 = zenith.
        Penalidade de até 3 dB dependendo da elevação.
        """
        g_max = self.gain_dbi(freq_hz)
        # Penalidade de elevação: PCB perde ganho acima de 30° de elevação
        elev_penalty = max(0.0, abs(theta_deg) - 30) * 0.05  # 0.05 dB/grau acima de 30°
        return g_max - elev_penalty
```

### 3.2 — Criar `backend/app/solvers/colinear_solver.py`

`Commercial_Omni_6dBi` — antena colinear comercial, 6 dBi, padrão mais estreito em elevação que dipolo:

```python
import math
from backend.app.solvers.base_solver import BaseSolver

class ColinearSolver(BaseSolver):
    antenna_type = "commercial_omni_6dbi"

    def gain_dbi(self, freq_hz: float, **kwargs) -> float:
        """Ganho nominal: 6 dBi."""
        return 6.0

    def impedance_ohm(self, freq_hz: float, **kwargs) -> float:
        return 50.0

    def pattern_g(self, theta_deg: float, phi_deg: float, freq_hz: float, **kwargs) -> float:
        """
        Padrão colinear: alta diretividade em elevação, omni em azimute.
        theta: ângulo de elevação (0 = horizonte, 90 = zenith).
        HPBW de elevação típico: ~20° para antena 6 dBi.
        """
        g_max = self.gain_dbi(freq_hz)
        hpbw_elev = 20.0  # graus
        # Modelo gaussiano em elevação
        sigma = hpbw_elev / (2 * math.sqrt(2 * math.log(2)))
        penalty = (theta_deg ** 2) / (2 * sigma ** 2)
        g_linear = (10 ** (g_max / 10)) * math.exp(-penalty)
        return 10 * math.log10(max(g_linear, 1e-10))
```

### 3.3 — Registrar os novos solvers

Localizar onde os solvers são registrados (provavelmente em `backend/app/solvers/__init__.py` ou em `sandbox_routes.py`). Adicionar os novos imports e mapeamentos:

```python
from backend.app.solvers.pcb_solver import PcbSolver
from backend.app.solvers.colinear_solver import ColinearSolver

SOLVER_MAP = {
    # existentes...
    "dipolo":     DipoloSolver,
    "monopolo":   MonopoloSolver,
    "helicoidal": HelicalSolver,
    "parabolica": ParabolicSolver,
    # novos:
    "pcb_compact":           PcbSolver,
    "commercial_omni_6dbi":  ColinearSolver,
}
```

### 3.4 — Atualizar `AntennaSpec` (se necessário)

Em `backend/app/schemas/antenna_spec.py`, verificar se `antenna_type` é um `Literal` ou `str`. Se for `Literal`, adicionar os dois novos valores:

```python
antenna_type: Literal[
    "dipolo", "monopolo", "helicoidal", "parabolica",
    "pcb_compact", "commercial_omni_6dbi"    # novos
]
```

### 3.5 — Testes dos novos solvers

Criar `tests/test_new_antenna_solvers.py`:

```python
def test_pcb_gain_at_915mhz():
    solver = PcbSolver()
    assert 0.0 <= solver.gain_dbi(915e6) <= 2.0

def test_colinear_gain_nominal():
    solver = ColinearSolver()
    assert solver.gain_dbi(915e6) == 6.0

def test_colinear_pattern_peaks_at_horizon():
    solver = ColinearSolver()
    g_horizon = solver.pattern_g(0.0, 0.0, 915e6)
    g_zenith  = solver.pattern_g(90.0, 0.0, 915e6)
    assert g_horizon > g_zenith  # colinear perde ganho no zenith

def test_pcb_pattern_penalizes_high_elevation():
    solver = PcbSolver()
    g_low  = solver.pattern_g(10.0, 0.0, 915e6)
    g_high = solver.pattern_g(60.0, 0.0, 915e6)
    assert g_low > g_high
```

---

## Critério de Conclusão da Fase 2

- [ ] `uv run pytest tests/ -v` — zero falhas
- [ ] `GET /api/v1/library/lora-modules` retorna lista com 3 módulos
- [ ] `GET /api/v1/library/lora-modules/rfm95w_915` retorna sensibilidade SF12=-139 dBm
- [ ] Sandbox aceita `antenna_type: "pcb_compact"` e `"commercial_omni_6dbi"` sem erro 422
- [ ] `NodeSpec` aceita campos `extra_loss_db`, `fading_margin_db`, `polarization_loss_db`, `azimuth_deg`, `tilt_deg`, `lora_module_id` sem erro
- [ ] Cenários salvos antes desta fase ainda carregam corretamente (retrocompatibilidade)
