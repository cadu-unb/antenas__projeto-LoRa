# Link Planner — Schemas

Schemas do domínio de planejamento de enlace. Salvos em `backend/data/scenarios/{id}.json`.

---

## NodeSpec

Representa um nó da rede (gateway, sensor, repetidor).

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `id` | string (UUID) | não | auto | Identificador único |
| `name` | string | **sim** | — | Nome legível |
| `lat` | float | **sim** | — | Latitude em graus decimais |
| `lon` | float | **sim** | — | Longitude em graus decimais |
| `height_m` | float | não | `0.0` | Altura sobre o solo em metros |
| `antenna_id` | string \| null | não | `null` | ID da `AntennaSpec` da biblioteca |
| `tx_power_dbm` | float | não | `14.0` | Potência de transmissão em dBm |
| `rx_sensitivity_dbm` | float | não | `-137.0` | Sensibilidade do receptor em dBm |
| `cable_loss_db` | float | não | `0.0` | Perda de cabo/conector em dB |
| `is_hub` | bool | não | `false` | Nó hub (ícone diferente, usado em MULTI_STAR) |

---

## LinkResult

Resultado calculado de um enlace P2P.

| Campo | Tipo | Unidade | Descrição |
|---|---|---|---|
| `distance_m` | float | m | Distância geodésica (Haversine) |
| `azimuth_deg` | float | ° | Azimute inicial de A→B (0–360°) |
| `elevation_deg` | float | ° | Ângulo de elevação de A→B |
| `fspl_db` | float | dB | FSPL = 20·log10(4π·d·f/c) |
| `rx_power_dbm` | float | dBm | Potência recebida estimada |
| `link_margin_db` | float | dB | Margem = Rx power − sensibilidade |
| `feasibility` | string | — | `"verde"` / `"amarelo"` / `"vermelho"` |

### Critério de viabilidade

| Margem | Semáforo | Significado |
|---|---|---|
| > 10 dB | Verde | Enlace robusto |
| 0 – 10 dB | Amarelo | Enlace marginal |
| < 0 dB | Vermelho | Enlace inviável |

---

## LinkEdge

Enlace explícito entre dois nós (usado em MESH/MULTI_STAR).

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `id` | string (UUID) | não | auto | ID do enlace |
| `node_a_id` | string | **sim** | — | ID do nó A |
| `node_b_id` | string | **sim** | — | ID do nó B |

---

## HopResult

Resultado de um hop individual em topologia multi-hop.

| Campo | Tipo | Descrição |
|---|---|---|
| `edge_id` | string | ID do `LinkEdge` |
| `node_a_id` / `node_b_id` | string | IDs dos nós |
| `node_a_name` / `node_b_name` | string | Nomes |
| `distance_m` | float | Distância do hop |
| `fspl_db` | float | FSPL do hop |
| `rx_power_dbm` | float | Potência Rx no destino |
| `link_margin_db` | float | Margem do hop |
| `feasibility` | string | `verde` / `amarelo` / `vermelho` |

---

## TopologyResult

Resultado de topologia multi-hop (MESH/MULTI_STAR).

| Campo | Tipo | Descrição |
|---|---|---|
| `hops` | `list[HopResult]` | Um resultado por `LinkEdge` |
| `islands` | `list[str]` | IDs de nós sem nenhum enlace |
| `bottleneck_margin_db` | float | Menor margem dentre todos os hops |
| `feasibility` | string | Baseado no gargalo |

---

## CandidateSite

Candidato a posição de torre para Site Selection.

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `id` | string (UUID) | não | auto | Identificador único |
| `name` | string | **sim** | — | Nome do candidato |
| `lat` | float | **sim** | — | Latitude |
| `lon` | float | **sim** | — | Longitude |
| `height_m` | float | não | `20.0` | Altura da antena sobre o solo (m) |
| `is_existing_tower` | bool | não | `false` | `true` se importado via KML com "torre"/"tower" no nome |
| `notes` | string | não | `""` | Observações livres |

---

## NodeCoverageResult

Resultado de cobertura de um nó de campo avaliado por um candidato.

| Campo | Tipo | Descrição |
|---|---|---|
| `node_id` | string | ID do nó de campo |
| `node_name` | string | Nome do nó |
| `distance_m` | float | Distância candidato→nó |
| `link_margin_db` | float | Margem de enlace candidato→nó |
| `feasibility` | string | `verde` / `amarelo` / `vermelho` |

---

## CandidateCoverageResult

Resultado de cobertura de um candidato sobre todos os nós de campo.

| Campo | Tipo | Descrição |
|---|---|---|
| `candidate_id` | string | ID do `CandidateSite` |
| `candidate_name` | string | Nome do candidato |
| `height_m` | float | Altura efetiva usada no cálculo (pode diferir do stored por `height_overrides`) |
| `coverage_pct` | float | % de nós com `link_margin_db > 0` |
| `node_results` | `list[NodeCoverageResult]` | Um resultado por nó de campo |
| `feasibility` | string | `verde` ≥80% / `amarelo` ≥50% / `vermelho` <50% |

---

## SiteSelectionResult

Resultado completo de site selection — lista ranqueada de candidatos.

| Campo | Tipo | Descrição |
|---|---|---|
| `candidates` | `list[CandidateCoverageResult]` | Ordenado desc por `coverage_pct` |

---

## LinkScenario

Cenário completo.

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `id` | string (UUID) | não | auto | Identificador único |
| `name` | string | **sim** | — | Nome do cenário |
| `node_a` | NodeSpec | **sim** | — | Nó A |
| `node_b` | NodeSpec | **sim** | — | Nó B |
| `frequency_hz` | float | **sim** | — | Frequência de operação em Hz |
| `topology_type` | string | não | `"P2P"` | Ver valores válidos abaixo |
| `extra_nodes` | `list[NodeSpec]` | não | `[]` | Nós extras (cadeia, estrela, malha) |
| `links` | `list[LinkEdge]` | não | `[]` | Enlaces explícitos (MESH/MULTI_STAR) |
| `polygons` | `list[dict]` | não | `[]` | Polígonos KML (apenas visual) |
| `candidates` | `list[CandidateSite]` | não | `[]` | Candidatos a torre (site selection) |
| `results` | `LinkResult \| null` | não | `null` | Preenchido após `/calculate` |
| `topology_result` | `TopologyResult \| null` | não | `null` | Preenchido após `/calculate_links` |
| `site_selection_result` | `SiteSelectionResult \| null` | não | `null` | Preenchido após `/site-selection` |
| `metadata` | dict | não | `{}` | Dados livres |

### Valores válidos para `topology_type`

| Valor | Nome | Descrição |
|---|---|---|
| `P2P` | Ponto a Ponto | Enlace único A↔B |
| `CHAIN` | Cadeia | A–extra1–extra2–B em série |
| `STAR` | Estrela | A (hub) conectado a todos os outros |
| `MESH` | Malha | Enlaces livres — cada enlace em `links[]` |
| `MULTI_STAR` | Multi-Estrela | Múltiplos hubs com folhas, enlaces em `links[]` |
| `HIERARCHICAL` | Hierárquico | Reservado — armazenado, sem lógica específica |

---

## Rotas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/scenarios` | Cria cenário |
| `GET` | `/api/v1/scenarios` | Lista todos |
| `GET` | `/api/v1/scenarios/{id}` | Detalhe |
| `POST` | `/api/v1/scenarios/{id}/calculate` | Link budget P2P |
| `POST` | `/api/v1/scenarios/{id}/links` | Adicionar enlace |
| `DELETE` | `/api/v1/scenarios/{id}/links/{link_id}` | Remover enlace |
| `POST` | `/api/v1/scenarios/{id}/calculate_links` | Link budget multi-hop |
| `POST` | `/api/v1/scenarios/{id}/candidates` | Adicionar candidato |
| `GET` | `/api/v1/scenarios/{id}/candidates` | Listar candidatos |
| `POST` | `/api/v1/scenarios/{id}/site-selection` | Calcular cobertura |
| `POST` | `/api/v1/scenarios/{id}/kml` | Importar KML |

---

## Fórmulas usadas

### FSPL (Free Space Path Loss)
```
FSPL (dB) = 20·log10(4π·d·f / c)
```
- `d` = distância em metros
- `f` = frequência em Hz
- `c` = 3×10⁸ m/s

### Haversine (distância geodésica)
```
a = sin²(Δφ/2) + cos(φ₁)·cos(φ₂)·sin²(Δλ/2)
d = 2·R·atan2(√a, √(1−a))   (R = 6 371 000 m)
```

### Link Budget
```
Rx (dBm) = Tx (dBm) + G_tx (dBi) − L_tx (dB) − FSPL (dB) − L_rx (dB) + G_rx (dBi)
Margem    = Rx (dBm) − Sensibilidade (dBm)
```
