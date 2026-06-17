# Fase 9 — Topologias Avançadas
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Topologias implementadas

| Valor | Nome | Descrição |
|---|---|---|
| `P2P` | Ponto a Ponto | Existia desde Fase 4 |
| `CHAIN` | Cadeia | Existia desde Fase 4 |
| `STAR` | Estrela | Existia desde Fase 4 |
| `MESH` | Malha manual | **Novo** — enlaces livres entre quaisquer nós |
| `MULTI_STAR` | Multi-estrela | **Novo** — múltiplos hubs com folhas próprias |
| `HIERARCHICAL` | Hierárquico | **Novo** — armazenado; sem lógica específica (reservado) |

---

## Schemas novos/modificados

### `NodeSpec` — campo adicionado
```python
is_hub: bool = False
```
Nós hub recebem ícone diferente no mapa (quadrado azul com borda amarela vs círculo).

### `LinkEdge` (novo)
```python
class LinkEdge(BaseModel):
    id: str  # UUID pré-atribuído pelo frontend
    node_a_id: str
    node_b_id: str
```

### `HopResult` (novo)
Resultado por enlace individual: `edge_id`, `node_a_id/name`, `node_b_id/name`, `distance_m`, `fspl_db`, `rx_power_dbm`, `link_margin_db`, `feasibility`.

### `TopologyResult` (novo)
```python
class TopologyResult(BaseModel):
    hops: list[HopResult]
    islands: list[str]        # IDs de nós sem nenhum enlace
    bottleneck_margin_db: float  # min(hop.link_margin_db)
    feasibility: str
```

### `LinkScenario` — campos adicionados
```python
links: list[LinkEdge] = []
topology_result: Optional[TopologyResult] = None
```

---

## Rotas criadas

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/scenarios/{id}/links` | Adicionar enlace individual |
| `DELETE` | `/api/v1/scenarios/{id}/links/{link_id}` | Remover enlace por ID |
| `POST` | `/api/v1/scenarios/{id}/calculate_links` | Calcular budget de toda a topologia |

### `POST /api/v1/scenarios/{id}/links`
- Body: `{id?: str, node_a_id: str, node_b_id: str}`
- Resposta: `LinkScenario` atualizado
- 404 se cenário não encontrado

### `DELETE /api/v1/scenarios/{id}/links/{link_id}`
- 204 no content em sucesso
- 404 se enlace não existe no cenário

### `POST /api/v1/scenarios/{id}/calculate_links`
- Calcula cada `LinkEdge` em `scenario.links`
- Usa `_antenna_gain()` igual ao endpoint P2P
- Persiste `topology_result` no cenário
- Resposta: `TopologyResult`

---

## Lógica de link budget multi-hop

Para LoRa, cada nó regenera o sinal — cada hop é **independente**.

```
Para cada LinkEdge:
  d = haversine(na, nb)
  loss = FSPL(d, f)
  rx_power = tx_power + gain_tx - cable_tx - loss + gain_rx - cable_rx
  margin = rx_power - rx_sensitivity

bottleneck = min(margin de todos os hops)
feasibility = feasibility(bottleneck)
```

O gargalo determina a viabilidade da rede: se um hop falha, a cadeia quebra.

---

## Validação de ilhas

`find_islands(all_node_ids, links)` em `link_budget.py`:
- Coleta todos os `node_a_id` e `node_b_id` de todos os enlaces
- Retorna IDs de nós **ausentes** desse conjunto
- Complexidade O(n_nodes + n_links)

Ilhas são:
- Listadas em `TopologyResult.islands`
- Destacadas no mapa com ícone vermelho
- Exibidas em banner de aviso na seção de enlaces

---

## Redundância

`best_path_margin(target_node_id, hops)` em `link_budget.py`:
- Filtra todos os hops que chegam ou partem de `target_node_id`
- Retorna `max(link_margin_db)` dos caminhos encontrados
- `None` se nenhum hop alcança o nó

Na UI: a tabela exibe **todos os hops** para o nó (uma linha por enlace). O usuário vê todas as margens e identifica o melhor caminho visualmente.

---

## Frontend

### Novos botões na topology-bar
- **Malha** → `MESH`
- **Multi-Estrela** → `MULTI_STAR`

### Painel de enlaces manuais (`#mesh-section`)
Visível apenas em MESH/MULTI_STAR:
- Botão **Conectar nós** entra em modo de seleção
- Click em nó A → destaque amarelo
- Click em nó B → enlace criado (linha azul no mapa)
- Click na linha → popup com botão **Remover**
- Lista de enlaces abaixo do botão com remoção individual

### Hub toggle
Visível em MULTI_STAR:
- Checkbox por nó: "Hub (gateway central)"
- Hub → ícone quadrado azul com borda amarela
- Folha → ícone circular laranja

### Resultado de topologia (`#topo-results-section`)
- Tabela por hop: Enlace | Dist (km) | FSPL (dB) | Margem (dB) | Status
- Badge de semáforo: gargalo da rede
- Banner de ilhas se `islands.length > 0`

### IDs de nó pré-atribuídos no frontend
Frontend gera UUIDs para `node_a`, `node_b` e cada extra node. Enviados no payload ao criar cenário — backend usa o ID fornecido em vez de gerar novo. Garante que links referenciem IDs corretos antes mesmo de criar o cenário.

---

## Testes criados (`tests/test_topology.py`)

| Teste | O que verifica |
|---|---|
| `test_find_islands_all_isolated` | Sem enlaces → todos ilhas |
| `test_find_islands_none` | Todos conectados → sem ilhas |
| `test_find_islands_partial` | Nó D isolado → apenas D |
| `test_best_path_margin_redundant` | Dois caminhos → melhor margem |
| `test_best_path_margin_single` | Um caminho → margem direta |
| `test_best_path_margin_no_match` | Nó sem caminho → None |
| `test_add_link_returns_updated_scenario` | POST links → cenário atualizado |
| `test_add_link_with_explicit_id` | ID fornecido → preservado |
| `test_add_link_scenario_not_found` | 404 em cenário inexistente |
| `test_remove_link_success` | DELETE → 204, cenário sem enlace |
| `test_remove_link_not_found` | 404 em link inexistente |
| `test_remove_link_does_not_delete_scenario` | Cenário persiste após remoção |
| `test_calculate_links_no_links_all_islands` | Sem links → todos ilhas, vermelho |
| `test_calculate_links_single_hop_margin` | Enlace LoRa 20 dBm → margem positiva |
| `test_calculate_links_bottleneck_is_minimum_margin` | Gargalo = menor margem |
| `test_calculate_links_island_detection` | Nó D sem enlace → em islands |
| `test_multi_star_two_hubs_connected` | 3 enlaces, sem ilhas |
| `test_multi_star_node_with_two_upstream_hubs` | Redundância → 2 hops para node-c |
| `test_topology_type_mesh_persisted` | MESH armazenado |
| `test_topology_type_hierarchical` | HIERARCHICAL aceito |
| `test_is_hub_field_persisted` | is_hub persistido nos nós |

---

## Resultado dos testes

```
tests/test_topology.py — 21 passed
Suite completa         — 134 passed, 1 skipped, 2 warnings in 3.21s
```

---

## Checkpoints

- [x] Enlace criado por arrastar (click-click) entre dois nós no mapa
- [x] Enlace removido individualmente sem apagar o cenário
- [x] Nós sem enlace (ilhas) marcados visualmente (ícone vermelho + banner)
- [x] Multi-estrela: dois hubs com folhas próprias + enlace hub-a-hub calculado
- [x] Link budget multi-hop acumula perdas corretamente (hop independente, gargalo = min margin)
- [x] Nó com dois hubs upstream → ambas margens exibidas na tabela, melhor identificada por `best_path_margin()`
- [x] `pytest tests/test_topology.py` passa (21/21)

---

## Limitações conhecidas

- Arrastar entre nós = click no primeiro + click no segundo (Leaflet não suporta drag de marcador para outro marcador nativamente)
- Topologia `HIERARCHICAL` armazenada mas sem lógica específica de cálculo (reservado para extensão)
- Links calculados individualmente — sem roteamento automático de caminhos ótimos
- Frontend requer cenário novo a cada "Calcular" (IDs pré-atribuídos garantem consistência)
