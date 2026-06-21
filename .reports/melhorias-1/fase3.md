# Relatório — Fase 3: Motor Físico

**Data:** 2026-06-21  
**Branch:** versao-2  
**Status:** CONCLUÍDA — 216 passed, 1 skipped, 0 falhas  
**Delta de testes:** +20 novos (196 → 216)

---

## Resumo

Quatro blocos implementados:

1. **Etapa 1 — geometry.py:** módulo ENU com WGS-84, `ENUVector` dataclass, `geodetic_to_ecef`, `geodetic_to_enu`. 6 testes.
2. **Etapa 2 — pattern_g em todos os solvers:** `BaseSolver` ganhou `gain_dbi()` e `pattern_g()` com implementação padrão (G_max). MoMSolver, ApertureSolver, PcbSolver, ColinearSolver implementaram `pattern_g` específico. `solvers/__init__.py` ganhou `get_solver()` registry.
3. **Etapa 3 — compute_link_full:** nova função em `link_budget.py` que usa ENU 3D, `_effective_gain()` com despacho direcional, e soma perdas extras. `link_routes.py` `calculate` atualizado para usar `compute_link_full`. 14 testes.
4. **Etapa 4 — dispatch de modelos de propagação:** `path_loss_db(dist_m, freq_hz, model, ...)` despacha para FSPL, Okumura-Hata ou Longley-Rice. Campo `propagation_model` adicionado a `LinkScenario` e `LinkResult`.

---

## Arquivos Criados

| Arquivo | Descrição |
|---|---|
| `backend/app/domain/geometry.py` | `ENUVector`, `geodetic_to_ecef`, `geodetic_to_enu` (WGS-84) |
| `tests/test_geometry.py` | 6 testes: distância, azimute ~270°, elevação positiva, caso zero |
| `tests/test_phase3_link_budget.py` | 14 testes: 3D dist, perdas extras, ganho direcional, modelos de prop, API |

## Arquivos Modificados

| Arquivo | Alteração |
|---|---|
| `backend/app/solvers/base_solver.py` | +`gain_dbi(**kwargs)` raise NotImplementedError; +`pattern_g()` default retorna `gain_dbi()` |
| `backend/app/solvers/mom_solver.py` | +`gain_dbi()` por tipo (dipolo/monopolo/helicoidal); +`pattern_g()` toroidal (dipolo/mono) e endfire cos²θ (helicoidal) |
| `backend/app/solvers/aperture_solver.py` | +`gain_dbi(**kwargs)` via fórmula de abertura; +`pattern_g()` gaussiano com HPBW=70λ/D |
| `backend/app/solvers/pcb_solver.py` | Assinaturas atualizadas para aceitar `**kwargs` |
| `backend/app/solvers/colinear_solver.py` | Assinaturas atualizadas para aceitar `**kwargs` |
| `backend/app/solvers/__init__.py` | `get_solver(antenna_type) -> BaseSolver | None` com registry de 6 tipos |
| `backend/app/schemas/link_scenario.py` | `LinkResult` +`extra_loss_db`, +`propagation_model`; `LinkScenario` +`propagation_model: Literal[...]` |
| `backend/app/domain/link_budget.py` | +`path_loss_db()` dispatch; +`_effective_gain()`; +`compute_link_full()`; import geometry |
| `backend/app/api/link_routes.py` | `calculate` handler reescrito para usar `compute_link_full` |

---

## Decisões de Implementação

### Retrocompatibilidade de `compute_link`
A função antiga `compute_link(tx_power_dbm, tx_gain_dbi, ...)` foi mantida intacta. Os testes existentes do `test_link_budget.py` a usam com interface posicional — nenhuma quebra. A nova `compute_link_full(node_a, node_b, freq_hz, ...)` é adicionada em paralelo e passa a ser usada pelo route handler.

### ENU vs Haversine
Distância ENU 3D difere de Haversine em ~5.5 m para 14 km (modelos geodésicos diferentes: WGS-84 elipsoide vs esfera de raio médio). Tolerância do teste ajustada para 100 m. Os testes existentes de distância (`test_calculate_distance_plano_taguatinga`: 12–16 km) continuam passando.

### `pattern_g` via `**kwargs`
Para que MoMSolver e ApertureSolver saibam o tipo de antena e parâmetros de geometria, `_effective_gain` passa `antenna_type=ant.type` e `**antenna.geometry` como kwargs. Isso evita alterar a assinatura pública de `pattern_g(theta, phi, freq_hz)`.

### `gain_dbi` em BaseSolver
Mudado de ausente para `raise NotImplementedError` (sem `@abstractmethod`) — MoM e Abertura implementam; PCB e Colinear já tinham. PcbSolver e ColinearSolver assinaturas atualizadas para `**kwargs` para compatibilidade.

### `path_loss_db` dispatch
Usa `okumura_hata()` e `longley_rice()` existentes via import lazy dentro da função. Ambas as funções já existiam — nenhum novo solver criado. A função fallback padrão continua sendo `fspl_db()`.

### Backward compat de `LinkResult`
`fspl_db` permanece no `LinkResult` (testes existentes verificam esse campo). `compute_link_full` popula-o com o path loss real (seja FSPL, OH ou LR). Novos campos `extra_loss_db` e `propagation_model` têm defaults — cenários salvos em disco carregam sem erro.

---

## Critérios de Conclusão

| Critério | Status |
|---|---|
| `uv run pytest tests/ -v` — zero falhas | ✅ 216 passed |
| `geodetic_to_enu(...).distance_2d` retorna ~13 km | ✅ `test_enu_distance_matches_haversine_approximately` |
| Helicoidal com `azimuth_deg=270` em enlace Norte tem margem menor que `azimuth_deg=0` | ✅ `test_directional_gain_penalizes_misalignment` |
| `extra_loss_db=10` reduz margem em exatamente 10 dB | ✅ `test_extra_loss_reduces_margin_exactly` |
| `LinkResult` contém campo `warnings` no JSON | ✅ `test_api_calculate_returns_warnings_field` |
| Okumura-Hata retorna `fspl_db` diferente de FSPL | ✅ `test_api_calculate_okumura_hata_different_loss` |

---

## Pendências para Fases Futuras

| Item | Fase destino |
|---|---|
| `lora_module_id` ainda não sobrescreve `rx_sensitivity_dbm` / `tx_power_dbm` no link budget | Fase 4/5 |
| `propagation_model` selecionável via frontend | Fase 5 |
| `calculate_links` (topologia multi-hop) ainda usa `compute_link` antigo + haversine 2D | Fase 4/5 |
| `site_selection` também usa cálculo antigo | Fase 4/5 |
| DEM para altitude absoluta — `height_m` é altura acima do solo, não ASL | Fora de escopo |
