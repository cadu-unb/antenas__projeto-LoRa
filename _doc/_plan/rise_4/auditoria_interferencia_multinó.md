# Auditoria Arquitetural — Simulador LoRa Multi-Nó com Interferência Mútua

**Data**: 2026-06-10  
**Auditor**: Engenheiro de Telecomunicações Sênior / Arquiteto RF  
**Escopo**: Confronto do planejamento Bloco 1 + Bloco 2 com os requisitos de interferência mútua para rede P1–P8, Campus Darcy Ribeiro (UnB)  
**Fonte de requisitos**: `_path/mathlab/EnlacesLora.m`, `_path/kml/file1.py`, `_path/kml/file2.py`  
**Restrição regulatória**: ANATEL — LoRa opera somente em **915–928 MHz** (8 canais de 200 kHz disponíveis) no Brasil

---

## Coordenadas Reais dos Nós (WGS84)

| Nó | Latitude | Longitude |
|----|----------|-----------|
| P1 | -15.762987 | -47.871879 |
| P2 | -15.765910 | -47.869717 |
| P3 | -15.766786 | -47.871248 |
| P4 | -15.768304 | -47.865723 |
| P5 | -15.766009 | -47.866577 |
| P6 | -15.763774 | -47.865209 |
| P7 | -15.761263 | -47.867451 |
| P8 | -15.757649 | -47.870830 |

**Observação crítica**: `file2.py` consulta a API SRTM 30m (`opentopodata.org`) para altitude real de cada ponto. O Campus Darcy Ribeiro tem variação de relevo significativa (~1040–1080m). Altitudes diferentes entre nós afetam distância 3D e path loss.

---

## 1. Avaliação do Núcleo Matemático (Bloco 1 vs Requisitos de Interferência)

### 1.1 Cobertura do CP-1 e CP-5-6 para SIR

**Veredicto**: ❌ **NÃO COBRE**

O motor matemático atual (`friis.py`, `link_budget.py`, `LinkBudgetComplete`) é estritamente **P2P (ponto a ponto)**. Assume que o único ruído limitante é o ruído térmico de fundo (`rx_sensitivity_dbm` como constante), o que equivale a assumir que **nenhum outro transmissor existe na mesma banda**.

Na rede real de 8 nós transmitindo simultaneamente na faixa 915–928 MHz:

```
SIR(dB) = Pr_sinal(dBm) − 10·log10( Σ Pr_interferente_i (mW) )
```

O `link_margin_db` atual calcula:
```
margem = Pr − sensibilidade_rx   ← assume apenas ruído térmico
```

O correto para rede multi-nó seria:
```
margem_efetiva = Pr − max(sensibilidade_rx, piso_de_interferência)
```

onde `piso_de_interferência = 10·log10(Σ P_interferentes)`.

**Limiar LoRa**: SIR > 6 dB (SF7) a 10 dB (SF12) para decodificação bem-sucedida. Qualquer enlace viável por Friis pode tornar-se inviável se SIR < limiar.

**Exemplo concreto com tabela fornecida**:  
P2→P5 (336 m) transmitindo; P4→P5 (271 m) também transmitindo simultaneamente no mesmo canal.  
Pr(P2→P5) ≈ -79 dBm  
Pr(P4→P5) ≈ -77 dBm (interferente mais forte)  
SIR ≈ -79 − (-77) = -2 dB → **ABAIXO do limiar → enlace falha apesar de Friis positivo**

O plano atual reportaria ambos como "viáveis". **Erro silencioso de projeto.**

### 1.2 Modelagem de Obstáculos vs Ray Tracing

**Veredicto**: ❌ **NÃO COBRE — gap crítico**

O planejamento atual (`obstacles.py`) implementa uma **tabela de atenuação nominal por tipo de obstáculo** com valores min/nominal/max em dB. Essa abordagem:

1. Requer que o **usuário insira manualmente** o número e tipo de obstáculos
2. Não conhece a geometria do campus
3. Não detecta automaticamente quantos prédios um enlace Pi→Pj cruza

O `file1.py` já extrai o polígono de fronteira do campus do KML (`mascara_campus_darcy_ribeiro.kml`). O requisito é estender isso para **polígonos de edificações** individuais e verificar interseção com o segmento de linha Pi→Pj.

**Ray Tracing 2D simplificado** (adequado para LoRa urbano a estas distâncias):
```
Para cada enlace (Pi, Pj):
  segmento = LineString(lat_i, lon_i, lat_j, lon_j)
  n_obstáculos = count(edificações onde segmento.crosses(polígono_edificação))
  atenuação_extra_db = n_obstáculos × atenuação_nominal_por_edificação
```

**As assinaturas das funções matemáticas do Bloco 1** — `friis_received_power_dbm(tx_power, tx_gain, rx_gain, fspl, losses_db)` — já têm o parâmetro `losses_db` que **absorve a atenuação extra sem modificação**. O Ray Tracing 2D calcula o valor e injeta via `losses_db`. Contrato Bloco 1 **não precisa mudar**.

---

## 2. Avaliação da Camada Geográfica e Dados (Bloco 2 vs Requisitos de Rede)

### 2.1 Parser KML — Dupla Responsabilidade

**Veredicto**: ❌ **SUPORTE PARCIAL — extensão necessária**

O `kml_parser.py` proposto em rise_3 trata apenas `<Placemark>` do tipo `<Point>`. O KML do campus (`mascara_campus_darcy_ribeiro.kml`) e KMLs de edificações contêm `<Polygon>` e `<MultiGeometry>`.

Dupla responsabilidade do KML no novo requisito:

| Responsabilidade | Elemento KML | Status no rise_3 |
|-----------------|--------------|-----------------|
| Nós P1–P8 com altitude | `<Placemark><Point>` | ✓ Coberto |
| Fronteira do campus | `<Polygon>` (MultiGeometry) | ❌ Não coberto |
| Polígonos de edificações (obstáculos) | `<Polygon>` | ❌ Não coberto |

**Impacto no design do `kml_parser.py`**:

O parser deve ser bifurcado em dois extratores:

```python
class KMLDocument(BaseModel):
    name: str
    points: List[KMLPoint]        # Placemarks do tipo Point (nós P1-P8)
    polygons: List[KMLPolygon]    # Placemarks do tipo Polygon (campus, prédios)

class KMLPolygon(BaseModel):
    label: str
    role: KMLPolygonRole          # Enum: CAMPUS_BOUNDARY | BUILDING | OBSTACLE
    coordinates: List[Tuple[float, float]]   # [(lon, lat), ...]
    altitude_m: float = 0.0
```

**Impacto no fluxo Folium**: polígonos de edificações alimentam tanto o mapa visual quanto o motor de Ray Tracing 2D. Nenhum acoplamento com Bloco 1 — os polígonos ficam em `gis/`.

### 2.2 Altitude 3D — Gap entre rise_3 e Requisito Real

**Veredicto**: ❌ **GAP CRÍTICO não mapeado em rise_3**

O `file2.py` mostra que o projeto **já usa** a API SRTM 30m para obter altitude real de cada nó. A distância geodésica em rise_3 (`pyproj.Geod.inv`) é **2D** (ignora diferença de altitude).

Distância 3D relevante para path loss:
```
d_2D = pyproj.Geod.inv(lon1, lat1, lon2, lat2)  # distância superficial
d_3D = sqrt(d_2D² + Δz²)                         # distância real de propagação
```

Para P2 (altitude ~1060m) e P8 (altitude ~1040m), Δz ≈ 20m. Em d_2D = 926m, o erro é < 0.02% — desprezível. **MAS**: para nós próximos com grande variação de relevo (ex.: P1 a P3, 428m horizontal com possível Δz = 15m), o erro pode chegar a 0.12% na distância e ~0.02 dB no FSPL — aceitável para MVP.

**Conclusão**: Altitude 3D para FSPL tem impacto negligenciável nas distâncias do campus (< 1 km). **O impacto real da altitude é no Ray Tracing** (ângulo de elevação do sinal que pode passar acima ou abaixo de obstáculos) — este sim requer z_m.

**Recomendação**: manter cálculo 2D para FSPL, mas **adicionar altitude** ao `GeographicPosition` para uso no Ray Tracing.

### 2.3 Matriz de Compatibilidade de Canais — Lacuna Arquitetural

**Veredicto**: ❌ **NÃO PREVISTO em nenhum bloco**

ANATEL: 915–928 MHz → 8 canais LoRa de ~1.6 MHz de espaçamento (ou configuração ISM sub-band).

O problema de alocação de canais para 8 nós com interferência mútua é um **problema de coloração de grafos**:
- Grafo: nós = P1–P8; arestas = enlaces com SIR < limiar (interferência)
- Objetivo: atribuir canal/SF a cada nó minimizando cores (canais) usadas
- Restrição: nós adjacentes (interferentes) devem ter canais diferentes

**Onde essa lógica se encaixa**:

```
NÃO pertence a CP-9 (Relatórios) — lógica de negócio não fica em gerador de PDF
NÃO pertence a CP-8 (GIS/Cobertura) — é algoritmo de otimização de rede

Pertence a: NOVA PÁGINA UI + NOVO MÓDULO
  src/lora_antenna/network/channel_plan.py   ← algoritmo
  src/lora_antenna/pages/network_manager.py  ← UI Streamlit
```

O `network/channel_plan.py` deve ser adicionado como **CP-8B** ou extensão do CP-8, pois depende da matriz de SIR gerada pelo Bloco 2. **Não é relatório — é ferramenta de decisão de projeto**.

---

## 3. Mapeamento de Gaps (Lacunas Críticas)

### Gap 1: SIR não existe no Bloco 1

**Arquivo afetado**: `propagation/friis.py` (extensão, não modificação)  
**Novo arquivo**: `propagation/interference.py`

```python
# propagation/interference.py — NOVO
# Pertence ao Bloco 1. Sem imports de gis/ ou network/.

import math
from typing import List

def power_sum_dbm(powers_dbm: List[float]) -> float:
    """Soma potências em mW, converte de volta para dBm."""
    if not powers_dbm:
        return -999.0
    total_mw = sum(10 ** (p / 10) for p in powers_dbm)
    return 10 * math.log10(total_mw)

def sir_db(
    signal_power_dbm: float,
    interferers_dbm: List[float],
) -> float:
    """
    SIR = Pr_sinal(dBm) - P_interferência_total(dBm).
    interferers_dbm: lista de Pr de cada nó interferente no receptor.
    Retorna -inf se sem interferentes.
    """
    if not interferers_dbm:
        return float("inf")
    interference_total_dbm = power_sum_dbm(interferers_dbm)
    return signal_power_dbm - interference_total_dbm

def sir_is_decodable(sir_value_db: float, sf: int = 12) -> bool:
    """
    Limiar SIR por SF (LoRa). Fonte: Semtech SX1276 datasheet.
    SF12: ~6 dB; SF7: ~10 dB. Modelo linear interpolado.
    """
    # SF12=6, SF11=6.5, SF10=7, SF9=7.5, SF8=9, SF7=10
    thresholds = {7: 10.0, 8: 9.0, 9: 7.5, 10: 7.0, 11: 6.5, 12: 6.0}
    threshold = thresholds.get(sf, 6.0)
    return sir_value_db >= threshold
```

### Gap 2: `link_margin_db` não classifica risco

**Arquivo afetado**: `propagation/friis.py` — adicionar função pura (sem quebra de retrocompatibilidade)

```python
# Adicionar em propagation/friis.py (função nova, não modifica existentes)
from enum import Enum

class LinkRisk(str, Enum):
    LOW = "LOW"       # Margem > 20 dB — enlace robusto
    MEDIUM = "MEDIUM" # 0 < Margem ≤ 20 dB — viável com limitações
    HIGH = "HIGH"     # Margem ≤ 0 dB — inviável

def classify_link_risk(
    received_power_dbm: float,
    rx_sensitivity_dbm: float = -110.0,  # SX1262 SF12/BW125 @ 915 MHz
) -> LinkRisk:
    """
    Classifica risco do enlace.
    Sensibilidade padrão: -110 dBm (SX1262 — mais comum em sistemas de segurança).
    SX1276: -137 dBm (SF12). Usar -110 dBm é conservador (sem SF máximo).
    """
    margin = received_power_dbm - rx_sensitivity_dbm
    if margin > 20:
        return LinkRisk.LOW
    elif margin > 0:
        return LinkRisk.MEDIUM
    else:
        return LinkRisk.HIGH
```

### Gap 3: `GeographicPosition` sem altitude real (SRTM)

**Arquivo afetado**: `models/geo.py` (proposto em rise_3)  
**Extensão necessária**: campo `altitude_srtm_m` separado de `altitude_m` (KML pode ter altitude incorreta)

```python
class GeographicPosition(BaseModel):
    label: str = ""
    latitude: float
    longitude: float
    altitude_m: float = 0.0           # altitude do KML/usuário
    altitude_srtm_m: Optional[float] = None  # altitude da API SRTM (autoritativa)

    @property
    def effective_altitude_m(self) -> float:
        """SRTM tem prioridade sobre KML se disponível."""
        return self.altitude_srtm_m if self.altitude_srtm_m is not None else self.altitude_m
```

**Novo módulo para fetch SRTM** (Bloco 2, sem impacto em Bloco 1):

```python
# gis/elevation.py — NOVO (Bloco 2)
import requests
from typing import List
from lora_antenna.models.geo import GeographicPosition

SRTM_API = "https://api.opentopodata.org/v1/srtm30m"

def fetch_srtm_elevations(positions: List[GeographicPosition]) -> List[GeographicPosition]:
    """
    Consulta API SRTM 30m e preenche altitude_srtm_m.
    Baseado em file2.py do projeto.
    Retorna novas instâncias (imutável — Pydantic).
    """
    coords_str = "|".join(f"{p.latitude},{p.longitude}" for p in positions)
    resp = requests.get(f"{SRTM_API}?locations={coords_str}", timeout=10)
    resp.raise_for_status()
    elevations = [item["elevation"] for item in resp.json()["results"]]
    return [
        p.model_copy(update={"altitude_srtm_m": elev})
        for p, elev in zip(positions, elevations)
    ]
```

**Aviso de dependência externa**: `opentopodata.org` é API pública com rate limiting. Em produção, usar cache local ou SRTM file offline (biblioteca `elevation` do PyPI).

### Gap 4: `kml_parser.py` sem suporte a `<Polygon>`

**Arquivo afetado**: `gis/kml_parser.py` (rise_3)  
**Extensão**: adicionar `KMLPolygon` e `parse_polygons()`

```python
from enum import Enum
from typing import List, Tuple

class KMLPolygonRole(str, Enum):
    CAMPUS_BOUNDARY = "campus_boundary"
    BUILDING = "building"
    OBSTACLE = "obstacle"
    UNKNOWN = "unknown"

class KMLPolygon(BaseModel):
    label: str
    role: KMLPolygonRole = KMLPolygonRole.UNKNOWN
    exterior_ring: List[Tuple[float, float]]  # [(lon, lat), ...]

# Adicionar em KMLDocument:
class KMLDocument(BaseModel):
    name: str = "unnamed"
    points: List[KMLPoint]
    polygons: List[KMLPolygon] = []  # retrocompatível — default vazio
```

### Gap 5: Ray Tracing 2D — arquivo inexistente no plano atual

**Novo arquivo**: `gis/ray_tracing_2d.py`

```python
# gis/ray_tracing_2d.py — NOVO (Bloco 2)
# Depende de shapely (já é dep. via geopandas).
# NÃO importa de propagation/ — injeta resultado via losses_db.

from shapely.geometry import LineString, Polygon
from typing import List
from lora_antenna.gis.kml_parser import KMLPolygon

def count_buildings_crossed(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    buildings: List[KMLPolygon],
) -> int:
    """Conta quantos polígonos de edificação o segmento Pi→Pj cruza."""
    line = LineString([(lon1, lat1), (lon2, lat2)])
    count = 0
    for building in buildings:
        if building.role in ("building", "obstacle"):
            poly = Polygon(building.exterior_ring)
            if line.crosses(poly) or line.within(poly):
                count += 1
    return count

def building_attenuation_db(
    n_buildings: int,
    nominal_db_per_building: float = 15.0,  # parede concreto @915MHz
) -> float:
    """Atenuação total por travessia de edificações."""
    return n_buildings * nominal_db_per_building
```

### Gap 6: `network/channel_plan.py` — inexistente, nova página necessária

**Novo módulo**: `src/lora_antenna/network/`  
**Algoritmo**: coloração de grafos (graph coloring) com restrição de SIR

```python
# network/channel_plan.py — NOVO
# Algoritmo greedy de coloração de grafos para alocação de canais LoRa.
# Input: matriz de SIR; Output: {nó: canal_index}

from typing import Dict, List, Tuple
import math

# 8 canais disponíveis: 915.2, 916.8, 918.4, 920.0, 921.6, 923.2, 924.8, 926.4 MHz
LORA_CHANNELS_MHZ = [915.2, 916.8, 918.4, 920.0, 921.6, 923.2, 924.8, 926.4]

def build_interference_graph(
    sir_matrix: Dict[Tuple[str, str], float],
    sir_threshold_db: float = 6.0,
) -> Dict[str, List[str]]:
    """
    Grafo de interferência: aresta existe se SIR < threshold.
    sir_matrix: {("P1","P2"): sir_db_value, ...}
    """
    graph: Dict[str, List[str]] = {}
    for (a, b), sir in sir_matrix.items():
        if sir < sir_threshold_db:
            graph.setdefault(a, []).append(b)
            graph.setdefault(b, []).append(a)
    return graph

def greedy_channel_assignment(
    nodes: List[str],
    interference_graph: Dict[str, List[str]],
    n_channels: int = 8,
) -> Dict[str, int]:
    """
    Greedy graph coloring para alocação de canais.
    Retorna {nó: índice_canal} (0-indexed).
    """
    assignment: Dict[str, int] = {}
    for node in nodes:
        neighbors = interference_graph.get(node, [])
        used = {assignment[n] for n in neighbors if n in assignment}
        for ch in range(n_channels):
            if ch not in used:
                assignment[node] = ch
                break
        else:
            assignment[node] = 0  # fallback: reuso forçado
    return assignment
```

---

## 4. Proposta de Ajuste na Assinatura do Código

### Princípio de Separação

```
Bloco 2 (gis/) PRODUZ dados geográficos e calcula atenuações
    ↓ injection via parâmetros escalares
Bloco 1 (propagation/) CONSOME valores numéricos, não sabe de coordenadas
    ↓ nunca importa de gis/ ou network/
```

Nenhum módulo do Bloco 1 importa de `gis/`, `network/`, ou `models/geo.py`.

### Contrato limpo — `InterferenceBatchResult`

```python
# gis/multi_link.py — versão estendida (rise_3 + interferência)
from dataclasses import dataclass, field
from typing import List, Optional
from lora_antenna.propagation.interference import sir_db, sir_is_decodable
from lora_antenna.propagation.friis import classify_link_risk, LinkRisk

@dataclass
class LinkBatchResult:
    origin_label: str
    dest_label: str
    distance_m: float
    distance_3d_m: float
    fspl_db: float
    extra_loss_db: float          # Ray Tracing + obstáculos
    received_power_dbm: float
    link_margin_db: float
    link_risk: LinkRisk
    # Campos de interferência (None = sem interferentes calculados)
    sir_db: Optional[float] = None
    sir_decodable: Optional[bool] = None
    interferer_labels: List[str] = field(default_factory=list)
    n_buildings_crossed: int = 0


def run_link_budget_batch(
    doc: KMLDocument,
    distance_matrix: DistanceMatrix,
    antenna: Antenna,
    tx_power_dbm: float = 14.0,
    frequency_hz: float = 915e6,     # ANATEL: fixo
    rx_sensitivity_dbm: float = -110.0,  # SX1262 conservador
    buildings: Optional[List[KMLPolygon]] = None,   # Ray Tracing
    sir_threshold_db: float = 6.0,   # SF12
    sf: int = 12,
) -> List[LinkBatchResult]:
    """
    Executa LinkBudget + Ray Tracing + SIR para todos os pares.

    BLOCO 1 chamado aqui:
      fspl_db()                    ← propagation/friis.py
      friis_received_power_dbm()   ← propagation/friis.py
      link_margin_db()             ← propagation/friis.py
      classify_link_risk()         ← propagation/friis.py
      sir_db()                     ← propagation/interference.py  [NOVO]
      sir_is_decodable()           ← propagation/interference.py  [NOVO]

    BLOCO 2 chamado aqui:
      count_buildings_crossed()    ← gis/ray_tracing_2d.py        [NOVO]
      building_attenuation_db()    ← gis/ray_tracing_2d.py        [NOVO]

    Bloco 1 não sabe que Bloco 2 existe.
    Bloco 2 injeta perdas como float escalar (extra_loss_db).
    """
    results: List[LinkBatchResult] = []

    for (origin_label, dest_label), distance_m in distance_matrix.items():
        origin_pt = doc.get_point(origin_label)
        dest_pt = doc.get_point(dest_label)

        # --- BLOCO 2: Ray Tracing (gis/ — não entra em Bloco 1) ---
        n_buildings = 0
        extra_loss = 0.0
        if buildings:
            n_buildings = count_buildings_crossed(
                origin_pt.latitude, origin_pt.longitude,
                dest_pt.latitude, dest_pt.longitude,
                buildings,
            )
            extra_loss = building_attenuation_db(n_buildings)

        # Distância 3D
        dz = abs(origin_pt.effective_altitude_m - dest_pt.effective_altitude_m)
        distance_3d = math.sqrt(distance_m ** 2 + dz ** 2)

        # --- BLOCO 1: Friis (apenas valores escalares) ---
        fspl = fspl_db(distance_3d, frequency_hz)
        pr = friis_received_power_dbm(
            tx_power_dbm=tx_power_dbm,
            tx_gain_dbi=antenna.gain_dbi,
            rx_gain_dbi=antenna.gain_dbi,
            fspl_db=fspl,
            losses_db=extra_loss,   # ← Ray Tracing injetado como escalar
        )
        margin = link_margin_db(pr, rx_sensitivity_dbm)
        risk = classify_link_risk(pr, rx_sensitivity_dbm)

        results.append(LinkBatchResult(
            origin_label=origin_label,
            dest_label=dest_label,
            distance_m=distance_m,
            distance_3d_m=round(distance_3d, 1),
            fspl_db=round(fspl, 2),
            extra_loss_db=round(extra_loss, 1),
            received_power_dbm=round(pr, 2),
            link_margin_db=round(margin, 2),
            link_risk=risk,
            n_buildings_crossed=n_buildings,
        ))

    # --- Cálculo de SIR (pós-processamento — precisa de todos os Pr) ---
    pr_map = {(r.origin_label, r.dest_label): r.received_power_dbm for r in results}

    for result in results:
        dest = result.dest_label
        # Todos os outros TX que chegam ao mesmo destino = interferentes
        interferer_powers = [
            pr for (orig, dst), pr in pr_map.items()
            if dst == dest and orig != result.origin_label
        ]
        if interferer_powers:
            sir = sir_db(result.received_power_dbm, interferer_powers)
            result.sir_db = round(sir, 2)
            result.sir_decodable = sir_is_decodable(sir, sf=sf)
            result.interferer_labels = [
                orig for (orig, dst) in pr_map if dst == dest and orig != result.origin_label
            ]

    return sorted(results, key=lambda r: r.link_margin_db, reverse=True)
```

### Diagrama de Dependências Final

```
models/geo.py           (sem imports internos)
    ↑
propagation/friis.py    (sem imports de gis/)
propagation/interference.py  [NOVO] (sem imports de gis/)
    ↑
gis/kml_parser.py       (sem imports de propagation/)
gis/distance_matrix.py  (importa models/geo.py)
gis/elevation.py        [NOVO] (importa models/geo.py, requests)
gis/ray_tracing_2d.py   [NOVO] (importa gis/kml_parser.py, shapely)
gis/multi_link.py       (importa propagation/ + gis/ — única ponte)
    ↑
network/channel_plan.py [NOVO] (importa propagation/interference.py)
    ↑
pages/network_manager.py [NOVO] (importa network/, gis/)
pages/campus_coverage.py (importa gis/)
```

**Zero acoplamento circular.** `propagation/` nunca importa `gis/` ou `network/`.

---

## Resumo dos Gaps e Ações

| # | Gap | Severidade | Tipo de Mudança | Sprint Sugerido |
|---|-----|-----------|----------------|-----------------|
| 1 | SIR não calculado | 🔴 CRÍTICO | Novo arquivo `propagation/interference.py` | CP-5-6 (extensão) |
| 2 | Classificação de risco de enlace ausente | 🟡 ALTO | Nova função em `propagation/friis.py` | CP-5-6 (extensão) |
| 3 | `GeographicPosition` sem altitude SRTM | 🟡 ALTO | Extensão `models/geo.py` + novo `gis/elevation.py` | CP-8 |
| 4 | `kml_parser.py` sem `<Polygon>` | 🔴 CRÍTICO | Extensão `gis/kml_parser.py` | CP-8 |
| 5 | Ray Tracing 2D inexistente | 🔴 CRÍTICO | Novo `gis/ray_tracing_2d.py` | CP-8 |
| 6 | `channel_plan.py` inexistente | 🟡 ALTO | Novo módulo `network/` + nova página UI | CP-8B (novo sprint) |
| 7 | Distância 3D ignorada | 🟢 BAIXO | Extensão `gis/distance_matrix.py` | CP-8 |
| 8 | Relatório sem SIR e risco | 🟡 MÉDIO | Extensão `reports/markdown_report.py` | CP-9 |

**Mudanças que QUEBRAM retrocompatibilidade**: **NENHUMA**.  
Todas as extensões são funções novas ou campos opcionais com defaults. `LinkBudgetResult` existente não muda. `friis_received_power_dbm` não muda.

**Pré-requisito urgente**: extrair `GeographicPosition` para `models/geo.py` (rise_3) **antes** de qualquer código de interferência — caso contrário, o campo `altitude_srtm_m` fica em `propagation/link_directivity.py`, criando acoplamento indesejado.
