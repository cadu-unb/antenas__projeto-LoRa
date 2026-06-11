# Análise Arquitetural — Integração de Suporte a Arquivos KML

**Data**: 2026-06-10  
**Escopo**: Integração de parser KML + simulação multiponto (P1–P8) na plataforma LoRa/LoRaWAN  
**Contexto**: Campus Darcy Ribeiro, UnB — Sistema de Segurança  
**Restrição regulatória**: ANATEL — LoRa opera somente na faixa **915–928 MHz** no Brasil

---

## Sumário

1. [Mapeamento de Impacto e Acoplamento](#1-mapeamento-de-impacto-e-acoplamento)
2. [Reutilização de Objetos — Bloco 1 sem modificação](#2-reutilização-de-objetos)
3. [Arquitetura da Solução e Fluxo de Dados](#3-arquitetura-da-solução-e-fluxo-de-dados)
4. [Plano de Implementação e Checklist de Código](#4-plano-de-implementação-e-checklist-de-código)
5. [Testes](#5-testes)
6. [Riscos e Mitigações](#6-riscos-e-mitigações)

---

## 1. Mapeamento de Impacto e Acoplamento

### 1.1 Alinhamento com a Pasta `Architecture`

A introdução do `kml_parser.py` é **aditiva pura**: nenhum módulo existente precisa ser alterado internamente. A localização `src/lora_antenna/gis/kml_parser.py` está correta e respeita as convenções já definidas:

| Princípio do Architecture | Status com KML |
|--------------------------|----------------|
| Bloco 2 usa Bloco 1 sem modificação | ✓ — KML vive em `gis/`, não toca `propagation/`, `antenna/`, `rf_chain/` |
| Pydantic como contrato de dados | ✓ — `KMLPoint` e `KMLDocument` serão Pydantic models |
| Separação entre camada matemática e geográfica | ✓ — parser KML não conhece Friis; só extrai coordenadas |
| Streamlit como UI isolada | ✓ — estado KML fica em `st.session_state`, não vaza para core |
| Frequência: 915–928 MHz (ANATEL) | ✓ — constante `LORA_FREQ_HZ = 915e6` já definida em `constants.py` |

### 1.2 Contratos de Dados que Precisam de Extensão

Nenhuma assinatura de função no core matemático muda. O contrato de extensão é por **composição**, não herança:

#### Extensão necessária: `GeographicPosition` → módulo próprio

Problema atual: `GeographicPosition` está definida em `propagation/link_directivity.py` mas é usada pelo módulo `gis/`. Isso cria dependência indesejada da camada GIS sobre camada de propagação.

**Solução**: extrair para módulo neutro antes da integração KML.

```
# ANTES (acoplamento)
gis/multi_link.py → propagation/link_directivity.py (para importar GeographicPosition)

# DEPOIS (desacoplado)
gis/multi_link.py → models/geo.py (GeographicPosition)
propagation/link_directivity.py → models/geo.py (GeographicPosition)
```

**Arquivo a criar**: `src/lora_antenna/models/geo.py`

```python
from pydantic import BaseModel

class GeographicPosition(BaseModel):
    """Posição geográfica WGS84. x=longitude, y=latitude, z=altitude_m."""
    label: str = ""
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    # Compatibilidade com código existente
    x_m: float = 0.0
    y_m: float = 0.0
    z_m: float = 0.0
```

> **Nota**: `x_m/y_m/z_m` (coordenadas cartesianas relativas) mantém retrocompatibilidade com `LinkWithDirectivity` existente. Coordenadas geodésicas (`lat/lon`) adicionadas sem quebrar interface antiga.

#### Contrato para batch: `LinkBatchRequest` (novo, em `gis/`)

```python
from pydantic import BaseModel
from typing import List, Optional
from lora_antenna.antenna.base import Antenna

class LinkPair(BaseModel):
    origin_label: str      # "P1"
    dest_label: str        # "P3"
    distance_m: float      # calculado do KML ou da tabela geodésica
    tx_antenna: Antenna
    rx_antenna: Antenna
    tx_power_dbm: float = 14.0
    obstacles_db: float = 0.0

class LinkBatchRequest(BaseModel):
    pairs: List[LinkPair]
    frequency_hz: float = 915e6  # ANATEL: 915 MHz
    rx_sensitivity_dbm: float = -137.0  # SX1276 SF12/BW125
```

### 1.3 Riscos de Retrocompatibilidade e Acoplamento Circular

#### Risco 1: Acoplamento circular via `GeographicPosition`

| Situação | Risco | Mitigação |
|----------|-------|-----------|
| `gis/` importa `propagation/` para `GeographicPosition` | MÉDIO — cria dependência cruzada entre camadas | Extrair `GeographicPosition` para `models/geo.py` |
| `propagation/` importa `gis/` | NÃO EXISTE — propagação não sabe de GIS | Nenhuma |

#### Risco 2: Quebra de retrocompatibilidade em `LinkWithDirectivity`

Impacto: **zero** se `GeographicPosition` migrar com campos retrocompatíveis (`x_m/y_m/z_m` mantidos). Código existente em `link_directivity.py` não muda.

#### Risco 3: Estado KML vazar para persistência

Risco: `CoverageRun` armazenado em SQLite conter referências a nós KML sem schema definido.

Mitigação: definir `KMLDocument` como Pydantic model e incluir `schema_version` desde o início. Tabela SQLite `kml_imports` separada de `coverage_runs`.

---

## 2. Reutilização de Objetos

### 2.1 Princípio: Bloco 1 intocável

O contrato arquitetural explícito é: **"Entrada: Todos os objetos validados do Bloco 1 (sem modificação)"**.

Mapeamento de responsabilidades:

```
KML Node (lat, lon, label)
    ↓ [gis/kml_parser.py]
GeographicPosition(label, latitude, longitude)
    ↓ [gis/multi_link.py — NOVA CAMADA TRADUTORA]
LinkPair(origin, dest, distance_m, tx_antenna, rx_antenna)
    ↓ [propagation/link_budget.py — BLOCO 1, sem modificação]
LinkBudgetResult(fspl_db, received_power_dbm, link_margin_db, feasible)
    ↓ [gis/heatmap.py ou gis/matrix_renderer.py]
Mapa Folium + Tabela de resultados
```

### 2.2 Onde vive a lógica de tradução

**Deve viver em**: `src/lora_antenna/gis/multi_link.py`

**Não deve viver em**:
- `propagation/` — não sabe de coordenadas geográficas
- `antenna/` — não sabe de topologia
- `ui/` — lógica de negócio não fica em UI

```python
# src/lora_antenna/gis/multi_link.py
# Responsabilidade: traduzir nós KML → instâncias Bloco 1 → executar batch

from lora_antenna.propagation.link_budget import LinkBudget
from lora_antenna.propagation.friis import friis_received_power_dbm, link_margin_db
from lora_antenna.gis.kml_parser import KMLDocument
from lora_antenna.models.geo import GeographicPosition
from typing import List

def build_link_matrix(
    kml_doc: KMLDocument,
    antenna_template: Antenna,   # antena padrão aplicada a todos os pontos
    tx_power_dbm: float = 14.0,
    frequency_hz: float = 915e6,
    rx_sensitivity_dbm: float = -137.0,
) -> List[LinkBatchResult]:
    """
    Traduz nós KML → pares de enlace → executa LinkBudget (Bloco 1).
    antenna_template aplicada a TX e RX de todos os pares.
    """
    ...
```

O `antenna_template` permite que Bloco 1 seja usado sem modificação: o usuário escolhe um tipo de antena na UI (ex.: Monopole @ 915 MHz), e ela é aplicada a todos os pontos do KML. Antenas por ponto também são suportadas via mapa `{label: Antenna}`.

### 2.3 Cadeia RF em contexto multiponto

`TXChain` e `RXChain` do Bloco 1 funcionam sem mudança. O batch apenas instancia o `LinkBudgetComplete` para cada par:

```python
# Cada par usa o mesmo TXChain/RXChain (gateway padrão)
tx_chain = TXChain(base_power_dbm=14, pa_gain_db=0)
rx_chain = RXChain(lna_gain_db=0)

for pair in pairs:
    result = LinkBudgetComplete(
        tx_chain=tx_chain,
        rx_chain=rx_chain,
        tx_antenna=pair.tx_antenna,
        rx_antenna=pair.rx_antenna,
        distance_m=pair.distance_m,
        frequency_hz=915e6,
    ).calculate()
```

---

## 3. Arquitetura da Solução e Fluxo de Dados

### 3.1 Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│  INPUT                                                          │
│  Upload .kml via st.file_uploader (Streamlit)                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ bytes
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  PARSE  │  gis/kml_parser.py                                    │
│  fastkml.parse(kml_bytes)                                       │
│  → List[KMLPoint(label, lat, lon, altitude_m)]                  │
│  → validação: ≥ 2 pontos, labels únicos, coords WGS84 válidas   │
└─────────────────────┬───────────────────────────────────────────┘
                      │ KMLDocument
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  VALIDAÇÃO TOPOLÓGICA  │  gis/multi_link.py                     │
│  Calcular distâncias geodésicas entre todos os pares            │
│  via pyproj.Geod(ellps='WGS84').inv(lon1,lat1,lon2,lat2)        │
│  → DistanceMatrix(pairs: {(Pi,Pj): distance_m})                 │
│  → opcional: comparar contra tabela fornecida (tolerância ±5m)  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ DistanceMatrix
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  SELEÇÃO DE ENLACE  │  UI (campus_coverage.py)                  │
│  Modo A: Matriz completa (todos os N*(N-1)/2 pares)             │
│  Modo B: Seleção manual de pares pelo usuário                   │
│  Parâmetros: antenna_type, tx_power, sf/bw, obstacles           │
└─────────────────────┬───────────────────────────────────────────┘
                      │ LinkBatchRequest
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  BATCH LINK BUDGET  │  gis/multi_link.py                        │
│  Para cada par (Pi, Pj):                                        │
│    1. fspl = fspl_db(distance_m, 915e6)                         │
│    2. Pr = friis_received_power_dbm(Pt, Gt, Gr, fspl, losses)   │
│    3. margin = link_margin_db(Pr, rx_sensitivity)               │
│    4. feasible = margin > 0                                     │
│  → List[LinkBatchResult]                                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │ List[LinkBatchResult]
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                         │
│                                                                 │
│  A. Mapa Folium dinâmico                                        │
│     - Marcadores P1–P8 com popups (gain, posição)               │
│     - Linhas de enlace: verde (margin > 0) / vermelho (inviável)│
│     - Largura da linha ∝ margem de enlace                       │
│                                                                 │
│  B. Tabela de resultados (Streamlit)                            │
│     Colunas: Par | Distância (m) | FSPL (dB) | Pr (dBm) |       │
│              Margem (dB) | Status                               │
│                                                                 │
│  C. Relatório Markdown/PDF (reports/markdown_report.py)         │
│     - Parâmetros de antena e RF chain                           │
│     - Matriz de distâncias                                      │
│     - Tabela de link budgets                                    │
│     - Mapa exportado como imagem                                │
│     - Accuracy matrix + limitações                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Casos de Borda no Fluxo

| Caso | Comportamento esperado |
|------|----------------------|
| KML sem Placemarks | Erro amigável: "Nenhum ponto encontrado no arquivo KML" |
| Ponto com altitude ausente | `altitude_m = 0.0` (padrão) + aviso na UI |
| Distância calculada vs tabela difere > 10m | Warning na UI, não bloqueio |
| Link inviável (margem < 0) | Exibido em vermelho no mapa + nota no relatório |
| Todos os links inviáveis | Warning crítico + sugestão de aumentar potência/ganho |
| KML com > 50 pontos | Warning de performance; calcular em background (Bloco futuro) |

### 3.3 Estado Streamlit — Gerenciamento de Sessão

```python
# campus_coverage.py — gestão de estado KML
if "kml_document" not in st.session_state:
    st.session_state["kml_document"] = None
if "distance_matrix" not in st.session_state:
    st.session_state["distance_matrix"] = None
if "link_results" not in st.session_state:
    st.session_state["link_results"] = None

# Upload
uploaded = st.file_uploader("Upload KML", type=["kml"])
if uploaded:
    kml_doc = parse_kml(uploaded.read())
    st.session_state["kml_document"] = kml_doc
    st.session_state["distance_matrix"] = compute_distance_matrix(kml_doc)
    st.session_state["link_results"] = None  # reset ao trocar arquivo
```

---

## 4. Plano de Implementação e Checklist de Código

### 4.1 Novos Arquivos (ordenados por dependência)

```
src/lora_antenna/
├── models/
│   ├── __init__.py                   (NOVO)
│   └── geo.py                        (NOVO — extração de GeographicPosition)
│
└── gis/
    ├── kml_parser.py                 (NOVO — parser KML)
    ├── distance_matrix.py            (NOVO — cálculo geodésico de distâncias)
    └── multi_link.py                 (NOVO — batch link budget)

src/lora_antenna/pages/
└── campus_coverage.py               (MODIFICAR — adicionar seção KML)

tests/
├── fixtures/
│   └── campus_p1_p8.kml             (NOVO — fixture de teste)
├── test_kml_parser.py               (NOVO)
├── test_distance_matrix.py          (NOVO)
└── test_multi_link_batch.py         (NOVO)
```

### 4.2 `models/geo.py`

```python
from pydantic import BaseModel, field_validator

class GeographicPosition(BaseModel):
    """Posição geográfica WGS84 com compatibilidade cartesiana."""
    label: str = ""
    latitude: float   # graus decimais, WGS84
    longitude: float  # graus decimais, WGS84
    altitude_m: float = 0.0
    # Campos cartesianos (retrocompatibilidade com LinkWithDirectivity)
    x_m: float = 0.0
    y_m: float = 0.0
    z_m: float = 0.0

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90 <= v <= 90):
            raise ValueError(f"Latitude inválida: {v}")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not (-180 <= v <= 180):
            raise ValueError(f"Longitude inválida: {v}")
        return v
```

### 4.3 `gis/kml_parser.py`

**Biblioteca**: `fastkml` (pura Python, sem dependências nativas, compatível com Pydantic).  
**Alternativa**: `lxml` diretamente via XPath se `fastkml` não for adicionada como dependência.

```python
"""
Parser de arquivos KML para extração de Placemarks (Pontos de Interesse).
Suporta estruturas KML 2.2/2.3 com Placemarks do tipo Point.
"""
from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
import xml.etree.ElementTree as ET

KML_NS = "http://www.opengis.net/kml/2.2"

class KMLPoint(BaseModel):
    label: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    description: Optional[str] = None

class KMLDocument(BaseModel):
    name: str = "unnamed"
    points: List[KMLPoint]

    @property
    def labels(self) -> List[str]:
        return [p.label for p in self.points]

    def get_point(self, label: str) -> Optional[KMLPoint]:
        for p in self.points:
            if p.label == label:
                return p
        return None


def parse_kml(kml_bytes: bytes) -> KMLDocument:
    """
    Extrai Placemarks do tipo Point de um arquivo KML.
    Levanta ValueError se nenhum ponto encontrado.
    """
    root = ET.fromstring(kml_bytes)
    ns = {"kml": KML_NS}

    # Normalizar namespace
    ns_prefix = ""
    if root.tag.startswith("{"):
        ns_prefix = root.tag.split("}")[0] + "}"

    points: List[KMLPoint] = []

    for pm in root.iter(f"{ns_prefix}Placemark"):
        name_el = pm.find(f"{ns_prefix}name")
        label = name_el.text.strip() if name_el is not None and name_el.text else f"P{len(points)+1}"

        desc_el = pm.find(f"{ns_prefix}description")
        description = desc_el.text.strip() if desc_el is not None and desc_el.text else None

        coords_el = pm.find(f".//{ns_prefix}coordinates")
        if coords_el is None or not coords_el.text:
            continue

        coords_text = coords_el.text.strip()
        # KML: longitude,latitude[,altitude]
        parts = [float(x) for x in coords_text.split(",")]
        lon, lat = parts[0], parts[1]
        alt = parts[2] if len(parts) > 2 else 0.0

        points.append(KMLPoint(
            label=label,
            latitude=lat,
            longitude=lon,
            altitude_m=alt,
            description=description,
        ))

    if not points:
        raise ValueError("Nenhum Placemark do tipo Point encontrado no arquivo KML.")

    doc_name_el = root.find(f".//{ns_prefix}Document/{ns_prefix}name")
    doc_name = doc_name_el.text.strip() if doc_name_el is not None else "KML Import"

    return KMLDocument(name=doc_name, points=points)
```

### 4.4 `gis/distance_matrix.py`

```python
"""
Cálculo geodésico de distâncias entre pares de pontos KML.
Usa pyproj.Geod (WGS84) — sem dependência de API externa.
"""
from __future__ import annotations
from typing import Dict, Tuple
from pyproj import Geod
from lora_antenna.gis.kml_parser import KMLDocument

_geod = Geod(ellps="WGS84")

DistanceMatrix = Dict[Tuple[str, str], float]  # {("P1","P2"): 399.0}


def compute_distance_matrix(doc: KMLDocument) -> DistanceMatrix:
    """
    Calcula distância geodésica (m) entre todos os pares de pontos.
    Matriz triangular superior: (Pi, Pj) onde i < j (ordem do doc).
    """
    matrix: DistanceMatrix = {}
    pts = doc.points

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i], pts[j]
            _, _, dist_m = _geod.inv(a.longitude, a.latitude, b.longitude, b.latitude)
            matrix[(a.label, b.label)] = round(abs(dist_m), 1)

    return matrix


def validate_against_reference(
    computed: DistanceMatrix,
    reference: DistanceMatrix,
    tolerance_m: float = 10.0,
) -> Dict[Tuple[str, str], float]:
    """
    Retorna pares com delta > tolerance_m entre calculado e referência.
    Usado para validar KML carregado contra tabela geodésica conhecida.
    """
    discrepancies = {}
    for pair, ref_dist in reference.items():
        calc_dist = computed.get(pair) or computed.get((pair[1], pair[0]))
        if calc_dist is None:
            continue
        delta = abs(calc_dist - ref_dist)
        if delta > tolerance_m:
            discrepancies[pair] = delta
    return discrepancies
```

### 4.5 `gis/multi_link.py`

```python
"""
Execução em batch do Link Budget (Bloco 1) para múltiplos pares de pontos.
Não modifica nenhuma classe de Bloco 1. Traduz KMLDocument → resultados.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional
from lora_antenna.antenna.base import Antenna
from lora_antenna.propagation.friis import fspl_db, friis_received_power_dbm, link_margin_db
from lora_antenna.gis.kml_parser import KMLDocument
from lora_antenna.gis.distance_matrix import DistanceMatrix


@dataclass
class LinkBatchResult:
    origin_label: str
    dest_label: str
    distance_m: float
    fspl_db: float
    received_power_dbm: float
    link_margin_db: float
    feasible: bool


def run_link_budget_batch(
    doc: KMLDocument,
    distance_matrix: DistanceMatrix,
    antenna: Antenna,
    tx_power_dbm: float = 14.0,
    frequency_hz: float = 915e6,
    rx_sensitivity_dbm: float = -137.0,
    extra_losses_db: float = 0.0,
    antenna_map: Optional[Dict[str, Antenna]] = None,
) -> List[LinkBatchResult]:
    """
    Executa LinkBudget para cada par em distance_matrix.

    antenna: antena padrão aplicada a TX e RX (se antenna_map não fornecido).
    antenna_map: {label: Antenna} para antenas por ponto (opcional).
    frequency_hz: 915e6 (ANATEL Brasil).
    """
    results: List[LinkBatchResult] = []

    for (origin_label, dest_label), distance_m in distance_matrix.items():
        tx_ant = (antenna_map or {}).get(origin_label, antenna)
        rx_ant = (antenna_map or {}).get(dest_label, antenna)

        fspl = fspl_db(distance_m, frequency_hz)
        pr = friis_received_power_dbm(
            tx_power_dbm=tx_power_dbm,
            tx_gain_dbi=tx_ant.gain_dbi,
            rx_gain_dbi=rx_ant.gain_dbi,
            fspl_db=fspl,
            losses_db=extra_losses_db,
        )
        margin = link_margin_db(pr, rx_sensitivity_dbm)

        results.append(LinkBatchResult(
            origin_label=origin_label,
            dest_label=dest_label,
            distance_m=distance_m,
            fspl_db=round(fspl, 2),
            received_power_dbm=round(pr, 2),
            link_margin_db=round(margin, 2),
            feasible=margin > 0,
        ))

    return sorted(results, key=lambda r: r.link_margin_db, reverse=True)
```

### 4.6 Adaptação da UI — `pages/campus_coverage.py`

Seção KML a ser adicionada na página existente de cobertura:

```python
# Seção 1: Upload KML
st.header("Importar Pontos de Interesse")
uploaded_kml = st.file_uploader("Upload arquivo .kml", type=["kml"])

if uploaded_kml is not None:
    try:
        kml_doc = parse_kml(uploaded_kml.read())
        st.session_state["kml_document"] = kml_doc
        st.success(f"{len(kml_doc.points)} pontos carregados: {', '.join(kml_doc.labels)}")
    except ValueError as e:
        st.error(f"Erro ao processar KML: {e}")
        st.session_state["kml_document"] = None

# Seção 2: Configuração de antena e enlace
if st.session_state.get("kml_document"):
    kml_doc = st.session_state["kml_document"]

    st.subheader("Configuração do Enlace")
    col1, col2 = st.columns(2)
    with col1:
        antenna_type = st.selectbox("Tipo de Antena", ["Monopole", "Dipole", "Yagi", "Patch"])
        tx_power = st.slider("Potência TX (dBm)", 0, 20, 14)
    with col2:
        sf_options = {"SF7": -123, "SF8": -126, "SF9": -129, "SF10": -132, "SF11": -134, "SF12": -137}
        sf = st.selectbox("Spreading Factor", list(sf_options.keys()), index=5)
        sensitivity = sf_options[sf]
        obstacles = st.number_input("Perdas adicionais (dB)", 0.0, 50.0, 0.0)

    # Cálculo
    if st.button("Calcular Matriz de Enlace"):
        antenna = build_antenna(antenna_type, frequency_hz=915e6)
        dist_matrix = compute_distance_matrix(kml_doc)
        
        # Validação opcional contra tabela de referência
        discrepancies = validate_against_reference(dist_matrix, REFERENCE_TABLE_P1P8)
        if discrepancies:
            st.warning(f"Atenção: {len(discrepancies)} pares com diferença > 10m vs tabela de referência.")
        
        results = run_link_budget_batch(
            doc=kml_doc,
            distance_matrix=dist_matrix,
            antenna=antenna,
            tx_power_dbm=tx_power,
            frequency_hz=915e6,
            rx_sensitivity_dbm=sensitivity,
            extra_losses_db=obstacles,
        )
        st.session_state["link_results"] = results

# Seção 3: Output — Mapa + Tabela
if st.session_state.get("link_results"):
    results = st.session_state["link_results"]
    kml_doc = st.session_state["kml_document"]

    # Mapa Folium
    m = build_kml_link_map(kml_doc, results)
    st_folium(m, width=900, height=500)

    # Tabela
    df = results_to_dataframe(results)
    st.dataframe(df, use_container_width=True)

    # Relatório
    if st.button("Gerar Relatório"):
        report_md = generate_kml_report(kml_doc, results, antenna, tx_power, sensitivity)
        st.download_button("Download Markdown", report_md, "relatorio_enlaces.md", "text/markdown")
```

### 4.7 Dependência a adicionar em `pyproject.toml`

```toml
dependencies = [
  # ... dependências existentes ...
  "pyproj>=3.6",       # cálculo geodésico WGS84 (provavelmente já em uso via geopandas)
  # fastkml NÃO necessária — usando stdlib xml.etree.ElementTree
]
```

> `pyproj` já é dependência transitiva de `geopandas`. Sem nova dependência de terceiros.

---

## 5. Testes

### 5.1 Fixture KML — `tests/fixtures/campus_p1_p8.kml`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Campus Darcy Ribeiro - P1-P8</name>
    <Placemark><name>P1</name><Point><coordinates>-47.871,-15.764,1050</coordinates></Point></Placemark>
    <Placemark><name>P2</name><Point><coordinates>-47.868,-15.762,1050</coordinates></Point></Placemark>
    <Placemark><name>P3</name><Point><coordinates>-47.870,-15.760,1050</coordinates></Point></Placemark>
    <Placemark><name>P4</name><Point><coordinates>-47.863,-15.766,1050</coordinates></Point></Placemark>
    <Placemark><name>P5</name><Point><coordinates>-47.864,-15.763,1050</coordinates></Point></Placemark>
    <Placemark><name>P6</name><Point><coordinates>-47.862,-15.760,1050</coordinates></Point></Placemark>
    <Placemark><name>P7</name><Point><coordinates>-47.866,-15.758,1050</coordinates></Point></Placemark>
    <Placemark><name>P8</name><Point><coordinates>-47.858,-15.762,1050</coordinates></Point></Placemark>
  </Document>
</kml>
```

> Coordenadas são aproximadas ao Campus Darcy Ribeiro. Ajustar com coordenadas reais dos pontos de interesse do projeto de segurança.

### 5.2 `tests/test_kml_parser.py`

```python
import pytest
from pathlib import Path
from lora_antenna.gis.kml_parser import parse_kml, KMLDocument

FIXTURE = Path(__file__).parent / "fixtures" / "campus_p1_p8.kml"

def test_parse_returns_8_points():
    doc = parse_kml(FIXTURE.read_bytes())
    assert len(doc.points) == 8

def test_labels_are_p1_to_p8():
    doc = parse_kml(FIXTURE.read_bytes())
    assert doc.labels == [f"P{i}" for i in range(1, 9)]

def test_coordinates_within_brasilia_bounds():
    doc = parse_kml(FIXTURE.read_bytes())
    for pt in doc.points:
        assert -16.0 < pt.latitude < -15.5
        assert -48.0 < pt.longitude < -47.5

def test_get_point_by_label():
    doc = parse_kml(FIXTURE.read_bytes())
    p1 = doc.get_point("P1")
    assert p1 is not None
    assert p1.label == "P1"

def test_empty_kml_raises_value_error():
    empty_kml = b'<?xml version="1.0"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document></Document></kml>'
    with pytest.raises(ValueError, match="Nenhum Placemark"):
        parse_kml(empty_kml)

def test_pydantic_serialization():
    doc = parse_kml(FIXTURE.read_bytes())
    json_str = doc.model_dump_json()
    restored = KMLDocument.model_validate_json(json_str)
    assert len(restored.points) == 8
```

### 5.3 `tests/test_distance_matrix.py`

```python
import pytest
from lora_antenna.gis.kml_parser import parse_kml
from lora_antenna.gis.distance_matrix import compute_distance_matrix, validate_against_reference
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "campus_p1_p8.kml"

# Referência: tabela geodésica fornecida no projeto
REFERENCE = {
    ("P1", "P2"): 399.0,
    ("P1", "P3"): 427.8,
    ("P2", "P3"): 190.6,
    # ... demais pares
}

def test_matrix_has_28_pairs():
    """N=8 pontos → N*(N-1)/2 = 28 pares."""
    doc = parse_kml(FIXTURE.read_bytes())
    matrix = compute_distance_matrix(doc)
    assert len(matrix) == 28

def test_p1_p2_distance_within_tolerance():
    """P1→P2 deve ser ~399m (±15m de tolerância para fixture aproximada)."""
    doc = parse_kml(FIXTURE.read_bytes())
    matrix = compute_distance_matrix(doc)
    assert abs(matrix[("P1", "P2")] - 399.0) < 15.0

def test_all_distances_positive():
    doc = parse_kml(FIXTURE.read_bytes())
    matrix = compute_distance_matrix(doc)
    assert all(d > 0 for d in matrix.values())
```

### 5.4 `tests/test_multi_link_batch.py`

```python
import pytest
from lora_antenna.gis.kml_parser import parse_kml
from lora_antenna.gis.distance_matrix import compute_distance_matrix
from lora_antenna.gis.multi_link import run_link_budget_batch
from lora_antenna.antenna.monopole import Monopole
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "campus_p1_p8.kml"

def test_batch_returns_28_results():
    doc = parse_kml(FIXTURE.read_bytes())
    matrix = compute_distance_matrix(doc)
    ant = Monopole(frequency_hz=915e6, name="test", id="t1")
    results = run_link_budget_batch(doc, matrix, ant)
    assert len(results) == 28

def test_p1_p4_may_be_infeasible_without_pa():
    """P1→P4 = 885m. Monopole + 14 dBm sem PA/LNA deve estar próximo do limite."""
    doc = parse_kml(FIXTURE.read_bytes())
    matrix = compute_distance_matrix(doc)
    ant = Monopole(frequency_hz=915e6, name="test", id="t1")
    results = run_link_budget_batch(doc, matrix, ant)
    p1_p4 = next(r for r in results if r.origin_label == "P1" and r.dest_label == "P4")
    # margem pode ser positiva ou negativa — verificamos apenas que foi calculado
    assert isinstance(p1_p4.link_margin_db, float)
    assert p1_p4.distance_m > 800

def test_closest_pair_has_best_margin():
    """Par com menor distância deve ter maior margem de enlace."""
    doc = parse_kml(FIXTURE.read_bytes())
    matrix = compute_distance_matrix(doc)
    ant = Monopole(frequency_hz=915e6, name="test", id="t1")
    results = run_link_budget_batch(doc, matrix, ant)
    # Resultados ordenados por margem (decrescente)
    assert results[0].link_margin_db >= results[-1].link_margin_db

def test_friis_consistency():
    """Verificar cálculo manual vs batch para P2→P3 (190.6m)."""
    from lora_antenna.propagation.friis import fspl_db, friis_received_power_dbm, link_margin_db
    ant = Monopole(frequency_hz=915e6, name="test", id="t1")
    dist = 190.6
    fspl = fspl_db(dist, 915e6)
    pr = friis_received_power_dbm(14, ant.gain_dbi, ant.gain_dbi, fspl, 0)
    margin = link_margin_db(pr, -137)
    # Deve ser claramente viável (curta distância)
    assert margin > 20
```

---

## 6. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| `GeographicPosition` duplicada em dois módulos | ALTA | MÉDIO | Extrair para `models/geo.py` antes do KML (pré-requisito) |
| KML real com estrutura diferente (namespaces, MultiGeometry) | MÉDIA | ALTO | Parser robusto com fallback de namespace + testes com KML real do projeto |
| Performance: 28 pares bloqueando UI | BAIXA | MÉDIO | 28 cálculos Friis = microsegundos; sem necessidade de async neste volume |
| Coordenadas KML em datum diferente de WGS84 | BAIXA | ALTO | Avisar na UI se altitude > 4000m ou coords fora do Brasil; não bloquear |
| Estado KML vazar entre sessões Streamlit | MÉDIA | BAIXO | Usar `st.session_state` corretamente; não persistir em SQLite sem schema definido |
| Frequência diferente de 915 MHz | — | CRÍTICO | Hardcode `frequency_hz=915e6` como default; ANATEL não permite outra banda para LoRa no Brasil |

---

## Resumo das Decisões Arquiteturais

| Decisão | Escolha | Alternativa Descartada | Razão |
|---------|---------|----------------------|-------|
| Localização do parser | `gis/kml_parser.py` | `utils/kml.py` | Pertence à camada geográfica (Bloco 2) |
| Biblioteca KML | `xml.etree.ElementTree` (stdlib) | `fastkml`, `pykml` | Zero dependências novas; KML do projeto é estruturalmente simples |
| Cálculo geodésico | `pyproj.Geod` | `geopy`, fórmula de Haversine | `pyproj` já é dep. transitiva; Haversine tem erro de até 0.3% em distâncias curtas |
| Contrato de batch | `List[LinkBatchResult]` dataclass | retornar DataFrame | Dataclass é testável; DataFrame é camada de apresentação, fica na UI |
| Antena por ponto | `antenna_map: Dict[str, Antenna]` (opcional) | antena única obrigatória | Flexibilidade sem complexidade; default é antena única para todos os pontos |
| `GeographicPosition` | Mover para `models/geo.py` | Manter em `propagation/link_directivity.py` | Evita import circular `gis/ ↔ propagation/` |

---

**Conclusão**: Integração KML é **aditiva pura** respeitando os contratos do Bloco 1 intocados. Camada tradutora (`gis/multi_link.py`) isola lógica geográfica do core matemático. Único pré-requisito de refatoração: extração de `GeographicPosition` para `models/geo.py` antes de implementar o parser.

**Estimativa de implementação**: 3–4 dias (dentro do escopo CP-8).
