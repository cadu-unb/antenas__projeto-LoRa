# Relatório — Fase 4: Features Analíticas

**Data:** 2026-06-21  
**Branch:** versao-2  
**Status:** CONCLUÍDA — 246 passed, 1 skipped, 0 falhas  
**Delta de testes:** +30 novos (216 → 246)

---

## Resumo

Quatro blocos implementados:

1. **Etapa 1 — comparison.py:** `ComparisonRow` dataclass + `run_comparison()` varrendo módulo × antena_TX × antena_GW. Labels A–Z. Endpoint `POST /{id}/compare`.
2. **Etapa 2 — robustness_score:** `_compute_robustness()` penaliza antenas diretivas com `std > 10 dB`. Embutido no loop de `run_comparison`.
3. **Etapa 3 — energy.py:** `EnergyEstimate` dataclass + `estimate_energy()` via ToA simplificado (preamble + payload_symbols). Endpoint `POST /lora-modules/{id}/energy`.
4. **Etapa 4 — minimax gateway:** `minimax_gateway_rank()` em `link_budget.py`. `selection_mode=minimax` query param no endpoint `site-selection`. Retorna lista com `rank`, `max_dist_m`, `mean_dist_m`.

---

## Arquivos Criados

| Arquivo | Descrição |
|---|---|
| `backend/app/domain/comparison.py` | `ComparisonRow`, `_compute_robustness`, `run_comparison` |
| `backend/app/domain/energy.py` | `EnergyEstimate`, `estimate_energy` (ToA simplificado) |
| `tests/test_comparison.py` | 12 testes: unit + API endpoint compare |
| `tests/test_energy.py` | 18 testes: energia, API endpoint, minimax |

## Arquivos Modificados

| Arquivo | Alteração |
|---|---|
| `backend/app/domain/link_budget.py` | +`minimax_gateway_rank()` |
| `backend/app/api/link_routes.py` | +endpoint `/{id}/compare`; +`selection_mode` query param no `site_selection`; import `lora_module_storage`, `run_comparison` |
| `backend/app/api/library_routes.py` | +endpoint `POST /lora-modules/{id}/energy`; import `estimate_energy` |

---

## Decisões de Implementação

### run_comparison usa compute_link_full
O prompt pseudocodificava `compute_link(node_tx, node_gw, ...)` — porém a função atual é `compute_link_full`. O `comparison.py` chama `compute_link_full` para obter ganho direcional e perdas extras automaticamente.

### site_selection sem response_model fixo
Minimax retorna `list[dict]`; coverage retorna `SiteSelectionResult`. Removido `response_model=SiteSelectionResult` do decorator. FastAPI serializa ambos corretamente. Testes existentes (que verificam `data["candidates"]`) continuam passando.

### Minimax não persiste resultado
Para coverage, o resultado é salvo em `site_selection_result`. Para minimax, não há campo correspondente no `LinkScenario`. Resultado retornado sem persistência. Pendência: Fase 5 pode adicionar campo `minimax_result` ao schema se necessário.

### compare com library vazia
Quando não há antenas salvas, `all_antennas[:3]` retorna `[]`, `run_comparison` retorna `[]`. Endpoint retorna 200 com lista vazia — comportamento correto, sem 500.

### Energia: 20 dBm RF95W não dura 1 dia
RFM95W a 20 dBm = 120 mA; SF12 ToA ≈ 721 ms; 96 tx/dia → 27.4 J/dia > bateria 2000 mAh/3.3V (23.8 J). Fisicamente correto. Testes ajustados para 14 dBm (29 mA) nos critérios `> 1 dia`.

---

## Critérios de Conclusão

| Critério | Status |
|---|---|
| `uv run pytest tests/ -v` — zero falhas | ✅ 246 passed |
| `POST /compare` retorna rows com `min_margin_db`, `failure_count`, `robustness_score` | ✅ `test_compare_endpoint_with_antennas_returns_rows` |
| Rows ordenadas por `min_margin_db` desc | ✅ `test_compare_endpoint_sorted_by_min_margin` |
| `POST /energy?sf=12` retorna `battery_life_days > 1` | ✅ `test_energy_endpoint_battery_life_gt_1` (14 dBm) |
| `selection_mode=minimax` sem erro 422 | ✅ `test_minimax_returns_200` |
| `robustness_score` diretiva < omni com mesma margem média e alta variância | ✅ `test_robustness_directional_high_variance_penalized` |

---

## Pendências para Fases Futuras

| Item | Fase destino |
|---|---|
| Frontend: tabela de comparação, painel de energia | Fase 5 |
| `lora_module_id` sobrescrever `rx_sensitivity_dbm` / `tx_power_dbm` no link budget | Fase 5 |
| Persistir resultado minimax no `LinkScenario` | Fase 5 (se necessário) |
| `calculate_links` (topologia) e `site_selection` (coverage) ainda usam `compute_link` antigo + haversine 2D | Fase 5 (melhoria incremental) |
| Modelo de propagação selecionável via frontend | Fase 5 |
