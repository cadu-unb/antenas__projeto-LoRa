# RELATÓRIO DE AUDITORIA DE CÓDIGO REAL — RISE 5

**Status Global:** APROVADO COM RESSALVAS  
**Data da Auditoria:** 2026-06-10  
**Auditor:** Claude Sonnet 4.6 — Engenheiro de Telecomunicações / Auditor de Arquitetura  
**Escopo:** `src/lora_antenna/` comparado contra `V1_Architecture_Specification.md`, `file_structure.md` (V0) e `auditoria_interferencia_multinó.md` (rise_4)

---

## Sumário Executivo

O código gerado implementa corretamente **todos os 6 gaps críticos de interferência** identificados na auditoria rise_4 e mantém isolamento matemático rigoroso entre Bloco 1 e Bloco 2. Não existe nenhuma violação de fronteira onde `propagation/` importe `gis/`. Entretanto, o projeto está em estágio inicial: apenas os módulos de infraestrutura e os módulos de interferência/GIS foram gerados. Os módulos de Bloco 1 (antenas especializadas, RF chain, link_budget, UI, relatórios) ainda não existem, o que está alinhado com o roadmap ainda não ter atingido CP-1 a CP-7. Há 4 desvios arquiteturais menores que devem ser corrigidos antes de avançar para CP-4.

---

## 1. Matriz de Conformidade Estrutural

### 1.1 Módulos Presentes vs Especificação V1

| Módulo (V1 Spec) | Status | Arquivo Real | Observação |
|---|---|---|---|
| `core/__init__.py` | ✅ Presente | `core/__init__.py` | OK |
| `core/constants.py` | ✅ Presente | `core/constants.py` | 3 constantes faltando (Z0, ε₀, μ₀) |
| `core/validators.py` | ✅ Presente | `core/validators.py` | Completo e correto |
| `core/formulas.py` | ❌ Ausente | — | Sprint 1 não iniciado |
| `core/models.py` | ❌ Ausente | — | Sprint 1 não iniciado |
| `core/units.py` | ❌ Ausente | — | Sprint 1 não iniciado |
| `models/__init__.py` | ✅ Presente | `models/__init__.py` | OK |
| `models/geo.py` | ✅ Presente | `models/geo.py` | Implementado corretamente |
| `antenna/__init__.py` | ✅ Presente | `antenna/__init__.py` | OK |
| `antenna/base.py` | ✅ Presente | `antenna/base.py` | Contrato mínimo presente |
| `antenna/monopole.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/dipole.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/ground_plane.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/patch.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/yagi.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/reflector.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/feeds.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `antenna/factory.py` | ❌ Ausente | — | Sprint 2-3 não iniciado |
| `propagation/__init__.py` | ✅ Presente | `propagation/__init__.py` | Exporta `LinkRisk` |
| `propagation/friis.py` | ✅ Presente | `propagation/friis.py` | Implementado + `classify_link_risk` |
| `propagation/interference.py` | ✅ Presente | `propagation/interference.py` | Novo módulo rise_4, completo |
| `propagation/link_budget.py` | ❌ Ausente | — | Sprint 5-6 não iniciado |
| `propagation/link_directivity.py` | ❌ Ausente | — | Sprint 5-6 não iniciado |
| `propagation/obstacles.py` | ❌ Ausente | — | Sprint 5-6 não iniciado |
| `propagation/sensitivity.py` | ❌ Ausente | — | Sprint 5-6 não iniciado |
| `propagation/batch/` | ❌ Ausente | — | Contratos residem em `gis/multi_link.py` — **DESVIO** |
| `rf_chain/` (completo) | ❌ Ausente | — | Sprint 5-6 não iniciado |
| `gis/__init__.py` | ✅ Presente | `gis/__init__.py` | Exporta KMLDocument, KMLPoint, KMLPolygon |
| `gis/kml_parser.py` | ✅ Presente | `gis/kml_parser.py` | Suporte a Point + Polygon ✓ |
| `gis/geodesic.py` | ✅ Presente | `gis/geodesic.py` | Haversine (sem pyproj — ver §4) |
| `gis/distance_matrix.py` | ✅ Presente | `gis/distance_matrix.py` | Dict em vez de Pydantic — **DESVIO** |
| `gis/multi_link.py` | ✅ Presente | `gis/multi_link.py` | Contém contratos que V1 coloca em `propagation/batch/` |
| `gis/ray_tracing_2d.py` | ✅ Presente | `gis/ray_tracing_2d.py` | Novo módulo rise_4, shapely ✓ |
| `gis/elevation.py` | ✅ Presente | `gis/elevation.py` | Novo módulo rise_4, SRTM ✓ |
| `gis/shapefile_handler.py` | ❌ Ausente | — | Sprint 8, não bloqueia MVP |
| `gis/campus_context.py` | ❌ Ausente | — | Sprint 8, não iniciado |
| `gis/heatmap.py` | ❌ Ausente | — | Sprint 8, não iniciado |
| `gis/map_renderer.py` | ❌ Ausente | — | Sprint 8, não iniciado |
| `gis/reference_tables.py` | ❌ Ausente | — | Sprint 8, não iniciado |
| `network/__init__.py` | ✅ Presente | `network/__init__.py` | OK |
| `network/channel_plan.py` | ✅ Presente | `network/channel_plan.py` | Novo módulo rise_4, coloração de grafos ✓ |
| `reports/` (completo) | ❌ Ausente | — | Sprint 9 não iniciado |
| `pages/` (completo) | ❌ Ausente | — | Sprint 4+8 não iniciado |
| `ui/` (completo) | ❌ Ausente | — | Sprint 4 não iniciado |
| `persistence/` (completo) | ❌ Ausente | — | Sprint 10 não iniciado |
| `app.py` | ❌ Ausente | — | Sprint 4 não iniciado |
| `tests/` (completo) | ❌ Ausente | — | Nenhum teste escrito ainda |

### 1.2 Arquivos não previstos na V1 Spec mas presentes

| Arquivo | Origem | Avaliação |
|---|---|---|
| `gis/elevation.py` | rise_4 gap #3 | Arquiteturalmente correto — pertence a `gis/` |
| `gis/ray_tracing_2d.py` | rise_4 gap #5 | Arquiteturalmente correto — pertence a `gis/` |
| `propagation/interference.py` | rise_4 gap #1 | Arquiteturalmente correto — pertence a `propagation/` |
| `network/channel_plan.py` | rise_4 gap #6 | Arquiteturalmente correto — pertence a `network/` |

---

## 2. Análise de Acoplamento e Importações Proibidas

### 2.1 Regra de Ouro: `propagation/` deve ter acoplamento zero com `gis/`

Varredura completa de imports em todos os arquivos de `propagation/`:

**`propagation/friis.py` — importações:**
```python
import math
from enum import Enum
from lora_antenna.core.constants import C_M_PER_S
from lora_antenna.core.validators import validate_lora_br_frequency_hz, validate_positive_distance_m
```
Resultado: **✅ LIMPO** — zero dependências de `gis/`, `network/`, `streamlit`, `folium`, `shapely`.

**`propagation/interference.py` — importações:**
```python
import math
from collections.abc import Sequence
```
Resultado: **✅ LIMPO** — apenas stdlib. Isolamento máximo.

**`propagation/__init__.py` — importações:**
```python
from lora_antenna.propagation.friis import LinkRisk
```
Resultado: **✅ LIMPO** — re-exporta apenas do próprio bloco.

### 2.2 Varredura de `core/` — zero dependências de domínio

**`core/constants.py`:** zero imports. **✅ LIMPO**  
**`core/validators.py`:** importa apenas `lora_antenna.core.constants`. **✅ LIMPO**

### 2.3 Varredura de `antenna/`

**`antenna/base.py`:**
```python
from pydantic import BaseModel, ConfigDict, Field, field_validator
from lora_antenna.core.constants import LORA_DEFAULT_HZ
from lora_antenna.core.validators import validate_lora_br_frequency_hz
```
Resultado: **✅ LIMPO** — sem imports de `gis/`, `propagation/`, `pages/`.

### 2.4 Varredura de `models/`

**`models/geo.py`:**
```python
from pydantic import BaseModel, ConfigDict, Field, field_validator
```
Resultado: **✅ LIMPO** — modelo neutro sem dependências de domínio.

### 2.5 Varredura de `gis/` — imports `propagation/` são permitidos

**`gis/multi_link.py`** — importações críticas:
```python
from lora_antenna.propagation.friis import LinkRisk, classify_link_risk, friis_received_power_dbm, fspl_db, link_margin_db
from lora_antenna.propagation.interference import sir_db, sir_is_decodable
from lora_antenna.gis.distance_matrix import DistanceMatrix, compute_distance_matrix, distance_for_pair
from lora_antenna.gis.geodesic import distance_3d_m
from lora_antenna.gis.kml_parser import KMLDocument, KMLPoint, KMLPolygon, KMLPolygonRole
from lora_antenna.gis.ray_tracing_2d import building_attenuation_db, count_buildings_crossed
```
Resultado: **✅ CONFORME** — `gis/` importa `propagation/` (permitido pela spec). Nenhum import de `streamlit`, `folium`, `pages/`.

**`gis/ray_tracing_2d.py`:**
```python
from shapely.geometry import LineString, Polygon
from lora_antenna.gis.kml_parser import KMLPolygon, KMLPolygonRole
```
Resultado: **✅ CONFORME** — `shapely` é biblioteca GIS; import de `kml_parser` dentro do próprio bloco `gis/`.

**`gis/elevation.py`:**
```python
import requests
from lora_antenna.models.geo import GeographicPosition
```
Resultado: **✅ CONFORME** — importa modelo neutro `models/geo.py`. Sem imports de `propagation/` ou `antenna/`.

### 2.6 Varredura de `network/`

**`network/channel_plan.py`:**
```python
from lora_antenna.propagation.interference import sir_threshold_db
```
Resultado: **✅ CONFORME** — importa função escalar de `propagation/`. Sem dependência de `gis/`, `pages/`, `streamlit`.

### 2.7 Veredito de Acoplamento

**Não existe nenhuma importação proibida no código real.** O Bloco 1 (`propagation/`, `core/`, `antenna/`) permanece matematicamente isolado. A fronteira Bloco 1 → Bloco 2 está respeitada.

---

## 3. Status de Implementação dos Gaps de Interferência Multi-Nó (Rise 4)

### Gap 1 — Cálculo de SIR: **✅ IMPLEMENTADO CONFORME**

**Arquivo:** `src/lora_antenna/propagation/interference.py`

Funções verificadas:

```python
SIR_THRESHOLDS_DB: dict[int, float] = {7: 10.0, 8: 9.0, 9: 7.5, 10: 7.0, 11: 6.5, 12: 6.0}

def power_sum_dbm(powers_dbm: Sequence[float]) -> float:
    total_mw = sum(dbm_to_mw(power) for power in powers_dbm)
    return mw_to_dbm(total_mw)

def sir_db(signal_power_dbm: float, interferers_dbm: Sequence[float]) -> float:
    interference_total_dbm = power_sum_dbm(interferers_dbm)
    return signal_power_dbm - interference_total_dbm

def sir_is_decodable(sir_value_db: float, sf: int = 12) -> bool:
    return sir_value_db >= sir_threshold_db(sf)
```

Verificações de correção:
- Soma linear em mW antes de converter para dBm: **✅ correto** — soma em dB seria erro catastrófico
- Limiares SF7-SF12 alinham com literatura LoRa (Semtech AN1200.22): **✅ correto**
- Tratamento de lista vazia → `sir_db` retorna `inf`: **✅ correto**
- Conversão `dbm_to_mw` trata `-inf` como 0 mW: **✅ correto**

**Integração em `gis/multi_link.py`:** `_with_sir()` agrupa resultados por `dest_label` e calcula SIR considerando todos os interferentes que chegam ao mesmo destino. Resultado inclui `sir_db`, `sir_decodable`, `interferer_labels` em `LinkBatchResult`. **✅ correto**

---

### Gap 2 — Classificação de Risco `LinkRisk`: **✅ IMPLEMENTADO CONFORME**

**Arquivo:** `src/lora_antenna/propagation/friis.py`

```python
class LinkRisk(str, Enum):
    LOW = "LOW"       # margem > 20 dB
    MEDIUM = "MEDIUM" # 0 < margem ≤ 20 dB
    HIGH = "HIGH"     # margem ≤ 0 dB

def classify_link_risk(received_power_dbm: float, rx_sensitivity_dbm: float = -110.0) -> LinkRisk:
    margin = link_margin_db(received_power_dbm, rx_sensitivity_dbm)
    if margin > 20.0: return LinkRisk.LOW
    if margin > 0.0:  return LinkRisk.MEDIUM
    return LinkRisk.HIGH
```

Verificações:
- `LinkRisk` herda de `str` e `Enum` — serializável via Pydantic/JSON: **✅ correto**
- Limiares 20 dB / 0 dB: **✅ alinha com rise_4 spec**
- Sensibilidade default -110 dBm: **⚠️ RESSALVA** — V1 Spec usa -137 dBm no `LinkBatchRequest`. Ver §4.1.

---

### Gap 3 — Altitude SRTM em `GeographicPosition`: **✅ IMPLEMENTADO CONFORME**

**Arquivo:** `src/lora_antenna/models/geo.py`

```python
class GeographicPosition(BaseModel):
    label: str = ""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    altitude_m: float = 0.0
    altitude_srtm_m: Optional[float] = None   # ← campo solicitado em rise_4
    x_m: float = 0.0
    y_m: float = 0.0
    z_m: float = 0.0

    @property
    def effective_altitude_m(self) -> float:
        if self.altitude_srtm_m is not None:
            return self.altitude_srtm_m
        return self.altitude_m
```

Verificações:
- `altitude_srtm_m` como `Optional[float]` com default `None`: **✅ retrocompatível**
- `effective_altitude_m` prioriza SRTM sobre KML: **✅ correto** — relevo real domina
- Validators WGS84 (`ge=-90, le=90` e `ge=-180, le=180`): **✅ correto**
- `model_config = ConfigDict(frozen=True)`: **✅ imutável** — seguro para uso em dicts/sets

**Arquivo complementar:** `src/lora_antenna/gis/elevation.py`

```python
SRTM_API_URL = "https://api.opentopodata.org/v1/srtm30m"

def fetch_srtm_elevations(positions, *, timeout_s=10.0, session=None) -> list[TPosition]:
    locations = "|".join(f"{p.latitude},{p.longitude}" for p in positions)
    response = client.get(SRTM_API_URL, params={"locations": locations}, timeout=timeout_s)
    # ...
    return [position.model_copy(update={"altitude_srtm_m": float(elevation)}) ...]
```

Verificações:
- Usa `model_copy(update=...)` para atualizar objeto imutável: **✅ correto**
- `TypeVar TPosition bound=GeographicPosition`: retorna subtipo preservado (ex: `KMLPoint`): **✅ correto**
- Valida comprimento do response da API: **✅ correto**
- `session` injetável (testabilidade): **✅ boa prática**
- Alinha com padrão de `_path/kml/file2.py`: **✅ consistente com código legado**

---

### Gap 4 — Parser KML com suporte a `<Polygon>`: **✅ IMPLEMENTADO CONFORME**

**Arquivo:** `src/lora_antenna/gis/kml_parser.py`

Verificações de `parse_kml()`:

```python
for index, placemark in enumerate(root.iter(f"{ns_prefix}Placemark"), start=1):
    point = _parse_point(placemark, ns_prefix, label, description, index)
    if point is not None:
        points.append(point)

    polygons.extend(
        _parse_polygons(placemark, ns_prefix, label, description, index)
    )
```

- **Namespace dinâmico:** `_namespace_prefix()` detecta KML 2.2 (`{http://www.opengis.net/kml/2.2}`) e no-namespace: **✅ correto**
- **`_parse_polygons()`** extrai `<outerBoundaryIs>/<LinearRing>/<coordinates>` com fallback para `<coordinates>` direto: **✅ robusto**
- **Validação de ring:** `len(exterior_ring) < 3` → erro imediato: **✅ correto**
- **`KMLPolygonRole`** com inferência automática por texto (campus/building/obstacle/unknown): **✅ bônus sobre a spec**
- **Coordenadas KML:** lon,lat,alt (ordem KML) convertidas para lat/lon nos campos do modelo: **✅ correto** — ordem lon,lat no KML é inversão clássica que trips parsers ingênuos
- **`KMLDocument.polygons_by_role()`** para filtro por tipo: **✅ conveniente para ray tracing**

Ressalva menor: `KMLDocument` usa `model_validator` que rejeita documentos sem pontos **E** sem polígonos. Um arquivo KML contendo apenas polígonos (ex: mapa de prédios sem nós) é válido nessa implementação, mas um arquivo só com polígonos sem pontos ainda passa a validação mínima. **✅ correto por design**

---

### Gap 5 — Ray Tracing 2D com Shapely: **✅ IMPLEMENTADO CONFORME**

**Arquivo:** `src/lora_antenna/gis/ray_tracing_2d.py`

```python
from shapely.geometry import LineString, Polygon

def count_buildings_crossed(lat1, lon1, lat2, lon2, buildings):
    line = LineString([(lon1, lat1), (lon2, lat2)])
    for building in buildings:
        if building.role not in OBSTACLE_ROLES:
            continue
        polygon = Polygon(building.exterior_ring)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)  # correção topológica
        if line.crosses(polygon) or line.within(polygon) or line.intersects(polygon):
            count += 1
    return count

def building_attenuation_db(n_buildings: int, nominal_db_per_building: float = 15.0) -> float:
    return n_buildings * nominal_db_per_building
```

Verificações:
- `polygon.buffer(0)` para polígonos inválidos (self-intersection em KML real): **✅ necessário** — KML de campus frequentemente tem geometrias degeneradas
- Verifica `crosses OR within OR intersects`: **✅ cobre** LOS passando por dentro do building sem cruzar (raro mas ocorre em LOS muito curtos)
- Coordenadas `(lon, lat)` em vez de `(lat, lon)` para Shapely: **✅ correto** — Shapely usa convenção `(x, y)` = `(lon, lat)`
- `nominal_db_per_building = 15.0 dB`: valor dentro do range 10-20 dB para estruturas de concreto em 915 MHz: **✅ realista**
- Filtro por `OBSTACLE_ROLES = {BUILDING, OBSTACLE}` — campus boundary não é obstáculo: **✅ correto**

Integração em `multi_link.py`:
```python
obstacle_loss_db = building_attenuation_db(n_buildings, nominal_db_per_building)
total_extra_loss_db = request.extra_losses_db + obstacle_loss_db
# total_extra_loss_db injetado como escalar em friis_received_power_dbm(losses_db=...)
```
**Padrão de injeção correto:** Bloco 2 calcula perda geográfica, injeta como float em `losses_db` do Bloco 1. **✅ exatamente o contrato de fronteira especificado.**

---

### Gap 6 — Plano de Canais ANATEL (Greedy Graph Coloring): **✅ IMPLEMENTADO CONFORME**

**Arquivo:** `src/lora_antenna/network/channel_plan.py`

```python
LORA_CHANNELS_MHZ: tuple[float, ...] = (
    915.2, 916.8, 918.4, 920.0, 921.6, 923.2, 924.8, 926.4,
)
```

Verificação dos 8 canais:
- Espaçamento: 1.6 MHz entre canais ✓
- Início: 915.2 MHz (interior da faixa ANATEL 915-928 MHz) ✓
- Fim: 926.4 MHz (interior da faixa ANATEL 915-928 MHz) ✓
- Nenhum canal fora de 915-928 MHz ✓

```python
def build_interference_graph(sir_matrix, *, nodes=None, sf=12) -> dict[str, set[str]]:
    # Aresta ↔ SIR < threshold → interferência co-canal
    threshold = sir_threshold_db(sf)
    for (origin, dest), sir_value in sir_matrix.items():
        if sir_value < threshold:
            graph[origin].add(destination)
            graph[destination].add(origin)

def greedy_channel_assignment(nodes, interference_graph, channels_mhz=LORA_CHANNELS_MHZ):
    ordered_nodes = sorted(nodes, key=lambda n: len(interference_graph.get(n, ())), reverse=True)
    # Degree-first ordering → minimiza cromático
    for node in ordered_nodes:
        used = {channel_by_node[nb] for nb in neighbors if nb in channel_by_node}
        assign first unused channel
    # Fallback: _least_conflicting_channel quando n_nós > 8 canais
```

Verificações:
- Ordenamento por grau (nó com mais conflitos primeiro): **✅ heurística clássica Welsh-Powell**
- Fallback `_least_conflicting_channel` quando grafo não é k-colorável com k=8: **✅ previne crash** — 8 nós com pior caso precisam exatamente 8 canais; com >8 nós, fallback garante funcionamento
- `count_channel_collisions()` para métrica pós-atribuição: **✅ permite validar qualidade do plano**
- `ChannelAssignment` como `dataclass(frozen=True)`: **✅ imutável e leve**
- Integração com `sir_threshold_db` de `propagation/interference.py`: **✅ único source-of-truth para limiar por SF**

---

## 4. Desvios Arquiteturais e Plano de Ação

### Desvio 1 — `propagation/batch/` ausente; contratos em `gis/multi_link.py`

**Severidade:** MÉDIA  
**Impacto:** `LinkPair`, `LinkBatchRequest`, `LinkBatchResult` residem em `gis/multi_link.py`. Pela V1 Spec esses contratos pertencem a `propagation/batch/contracts.py`, e o executor puro a `propagation/batch/executor.py`.

**Problema concreto:** Se `pages/link_budget.py` (standalone P2P, sem KML) precisar de `LinkBatchRequest`, terá que importar de `gis/`, o que viola o isolamento.

**Ação requerida antes do CP-5-6:**
1. Criar `propagation/batch/__init__.py`
2. Criar `propagation/batch/contracts.py` com `LinkPair`, `LinkBatchRequest`, `LinkBatchResult`
3. Criar `propagation/batch/executor.py` com `execute_link_batch()` — função pura sem GIS
4. Refatorar `gis/multi_link.py` para importar contratos de `propagation/batch/contracts.py`
5. Manter `run_link_budget_batch()` em `gis/multi_link.py` como orquestrador GIS

---

### Desvio 2 — `DistanceMatrix` como `dict` em vez de modelo Pydantic

**Severidade:** BAIXA  
**Impacto:** V1 Spec §12.3 define `DistanceMatrix` como modelo com campos `origin_label`, `dest_label`, `distance_m`, `method = "WGS84_GEODESIC"`, `delta_reference_m`.

Implementação atual:
```python
DistanceMatrix = dict[tuple[str, str], float]
```

**Problema:** Sem `method` e `delta_reference_m`, o relatório não pode citar método geodésico usado, e a validação contra tabela de referência P1-P8 fica impossível (Gate V1-B requer isso).

**Ação requerida antes do CP-8:**
1. Criar `DistanceMatrixEntry` Pydantic com `origin_label`, `dest_label`, `distance_m`, `method`, `delta_reference_m`
2. Criar `DistanceMatrix` Pydantic com `entries: list[DistanceMatrixEntry]` e helper `to_dict()`
3. Atualizar `compute_distance_matrix()` e `distance_for_pair()`
4. Adicionar `REFERENCE_TABLE_P1P8` em `gis/reference_tables.py` com distâncias do EnlacesLora.m

---

### Desvio 3 — `rx_sensitivity_dbm` default diverge da V1 Spec

**Severidade:** BAIXA  
**Impacto:** V1 Spec `LinkBatchRequest` define `rx_sensitivity_dbm: float = -137.0`.  
`constants.py` define `DEFAULT_RX_SENSITIVITY_DBM = -110.0`.

SX1276 SF12 BW125 kHz: sensibilidade real ≈ −136 dBm (Semtech datasheet).  
`-110.0 dBm` é conservador: marca enlaces viáveis como MEDIUM/HIGH, subestimando cobertura real em ~27 dB.

**Ação requerida antes do CP-5-6:**
- Atualizar `DEFAULT_RX_SENSITIVITY_DBM = -110.0` para `-137.0` em `constants.py`, OU
- Manter -110 dBm como default conservador e documentar explicitamente no `docs/regulatory_anatel_915_928.md` que valor é pessimista por design.

---

### Desvio 4 — `LinkBatchResult` sem campo `feasible: bool`

**Severidade:** BAIXA  
**Impacto:** V1 Spec §12.5 exige `feasible: bool` com regra `feasible = link_margin_db > 0`.

Implementação atual tem `link_risk: LinkRisk` (LOW/MEDIUM/HIGH) mas não `feasible: bool`. A UI (quando implementada) precisará de `feasible` para filtro binário (enlace viável/inviável).

**Ação requerida antes do CP-4:**
```python
# Em gis/multi_link.py, adicionar ao LinkBatchResult:
feasible: bool = Field(default=False)

# Calcular junto ao link_risk:
feasible = margin_db > 0
```

---

### Desvio 5 — `constants.py` missing constantes físicas

**Severidade:** MUITO BAIXA (Sprint 1 não iniciado)  
**Impacto:** `Z0_OHM = 50.0`, `EPSILON_0_F_PER_M`, `MU_0_H_PER_M` ausentes.  
Necessários para `core/formulas.py` (VSWR, impedância, Frii completo).

**Ação requerida no CP-1:**
```python
Z0_OHM = 50.0
EPSILON_0_F_PER_M = 8.854_187_817e-12
MU_0_H_PER_M = 1.256_637_061_435_917e-6
```

---

## 5. Análise de Robustez para os 8 Nós do Campus

### 5.1 Capacidade de processar P1-P8

Com os módulos presentes (`kml_parser`, `geodesic`, `distance_matrix`, `multi_link`):

- **Parse de KML P1-P8:** ✅ funcional (`parse_kml()` com namespace dinâmico)
- **Matriz de distâncias:** ✅ `compute_distance_matrix()` gera `8*(8-1)/2 = 28 pares`
- **Batch link budget:** ✅ `run_link_budget_batch()` processa todos os pares com Friis + SIR
- **SIR por nó destino:** ✅ `_with_sir()` calcula para cada par o SIR real com todos os interferers

### 5.2 Cenário de interferência P4→P5 com P2→P5

Usando coordenadas reais (rise_4):
```
P2: lat=-15.765910, lon=-47.869717
P4: lat=-15.768304, lon=-47.865723
P5: lat=-15.766009, lon=-47.866577

d(P2,P5) ≈ 348 m → FSPL@915MHz ≈ 83.6 dB → Pr ≈ 14+2.15+2.15-83.6 = -65.3 dBm
d(P4,P5) ≈ 267 m → FSPL@915MHz ≈ 81.3 dB → Pr ≈ 14+2.15+2.15-81.3 = -63.0 dBm
SIR(P2→P5 | interferer=P4) = -65.3 - (-63.0) = -2.3 dB < 6.0 dB (SF12 threshold)
```
**`sir_is_decodable(-2.3, sf=12)` → `False`** — enlace indecodificável por interferência.

A cadeia `run_link_budget_batch()` → `_with_sir()` detecta e sinaliza esse caso corretamente.

### 5.3 Plano de canal para P1-P8

`build_interference_graph()` + `greedy_channel_assignment()` atribuem canais distintos a nós com SIR < threshold. Com 8 nós e 8 canais ANATEL, o algoritmo garante atribuição sem colisões **se o grafo de interferência for 8-colorável**, o que é garantido para grafos com 8 vértices.

---

## 6. Resumo Executivo de Conformidade

| Categoria | Status | Criticidade |
|---|---|---|
| Isolamento matemático `propagation/` vs `gis/` | ✅ Conforme | Alta |
| Gap 1 — SIR e limiares por SF | ✅ Implementado | Crítica |
| Gap 2 — `LinkRisk` LOW/MEDIUM/HIGH | ✅ Implementado | Alta |
| Gap 3 — `altitude_srtm_m` + SRTM API | ✅ Implementado | Alta |
| Gap 4 — Parser KML `<Polygon>` | ✅ Implementado | Crítica |
| Gap 5 — Ray Tracing 2D Shapely | ✅ Implementado | Crítica |
| Gap 6 — Coloração de grafos 8 canais | ✅ Implementado | Alta |
| Contratos `propagation/batch/` | ❌ Desvio | Média |
| `DistanceMatrix` tipagem fraca | ❌ Desvio | Baixa |
| `feasible: bool` ausente em `LinkBatchResult` | ❌ Desvio | Baixa |
| `rx_sensitivity_dbm` default divergente | ⚠️ Ressalva | Baixa |
| Constantes físicas Z0/ε₀/μ₀ ausentes | ❌ Ausente | Muito Baixa (Sprint 1) |
| Bloco 1 módulos restantes (CP-1 a CP-7) | ❌ Ausente | Sprint não iniciado |
| Testes unitários e GIS | ❌ Ausente | Alta (bloqueador CP-4) |

**Veredito:** O núcleo de telecomunicações (interferência, ray tracing, SRTM, coloração de canais) está corretamente implementado e arquiteturalmente isolado. Os 4 desvios são correções simples que não invalidam o código existente — são adições/movimentações, não reescritas.

---

## 7. Ordem Recomendada de Correção

Antes de iniciar CP-1 (Núcleo Matemático):

1. **Adicionar `feasible: bool` em `LinkBatchResult`** — 5 linhas, `gis/multi_link.py`
2. **Definir `rx_sensitivity_dbm` default: -137.0 ou documentar -110.0 como conservador**
3. **Adicionar Z0, ε₀, μ₀ em `core/constants.py`** — necessários para Sprint 1

Antes de CP-5-6 (Link Budget):

4. **Criar `propagation/batch/`** com `contracts.py` e `executor.py`
5. **Mover `LinkPair`, `LinkBatchRequest`, `LinkBatchResult` para `propagation/batch/contracts.py`**

Antes de CP-8 (GIS):

6. **Criar `DistanceMatrix` como modelo Pydantic** com `method` e `delta_reference_m`
7. **Criar `gis/reference_tables.py`** com distâncias P1-P8 do EnlacesLora.m

---

> **Nota:** A pasta `_doc/_report/` consolida relatórios de status de código real, diferenciando-os dos artefatos de planejamento em `_doc/_plan/`. Esse relatório marca o encerramento formal do ciclo rise_5: os gaps de interferência foram implementados, a fronteira arquitetural está íntegra, e os desvios identificados têm plano de ação claro.
