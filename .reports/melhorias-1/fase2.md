# Relatório — Fase 2: Modelos e Schemas

**Data:** 2026-06-21  
**Branch:** versao-2  
**Status:** CONCLUÍDA — 196 passed, 1 skipped, 0 falhas  
**Delta de testes:** +34 novos (162 → 196)

---

## Resumo

Três blocos implementados:

1. **Etapa 1 — NodeSpec estendido:** 6 novos campos opcionais com defaults — sem quebrar retrocompatibilidade.
2. **Etapa 2 — Catálogo LoRa:** schema `LoRaModule`, JSON estático com 3 módulos, storage read-only, rotas REST.
3. **Etapa 3 — Novos solvers:** `PcbSolver` (PCB quasi-omni, 0–2 dBi) e `ColinearSolver` (colinear 6 dBi) com `solve()`, `gain_dbi()`, `impedance_ohm()` e `pattern_g(θ,φ)`. Registrados no `_SOLVERS` do sandbox.

---

## Arquivos Criados

| Arquivo | Descrição |
|---|---|
| `backend/app/schemas/lora_module.py` | `SensitivityByMode` + `LoRaModule` com `get_sensitivity(sf, bw_khz)` |
| `backend/app/data/lora_modules.json` | Catálogo estático: RFM95W, LRO2_ASR6601, E220_900T22D |
| `backend/app/storage/lora_module_storage.py` | `list_modules()`, `get_module(id)` — leitura de JSON com `encoding="utf-8"` |
| `backend/app/solvers/pcb_solver.py` | `PcbSolver` — antena PCB integrada, 0–2 dBi, penalidade de elevação |
| `backend/app/solvers/colinear_solver.py` | `ColinearSolver` — colinear 6 dBi, padrão gaussiano em elevação, HPBW 20° |
| `tests/test_lora_modules.py` | 16 testes: storage unitário + endpoints `/api/v1/antennas/lora-modules` |
| `tests/test_new_antenna_solvers.py` | 18 testes: PcbSolver, ColinearSolver unitário + sandbox API |

## Arquivos Modificados

| Arquivo | Alteração |
|---|---|
| `backend/app/schemas/node_spec.py` | +6 campos: `extra_loss_db`, `fading_margin_db`, `polarization_loss_db`, `azimuth_deg`, `tilt_deg`, `lora_module_id` |
| `backend/app/api/library_routes.py` | Rotas `GET /lora-modules` e `GET /lora-modules/{id}` adicionadas antes de `/{id}` (evitar conflito FastAPI) |
| `backend/app/api/sandbox_routes.py` | Imports + instâncias `_pcb` / `_colinear`; funções `_solve_pcb_compact()` / `_solve_colinear()`; `_SOLVERS` atualizado |

---

## Decisões de Implementação

### URL dos módulos LoRa
O `library_routes.py` usa prefix `/api/v1/antennas`. Os módulos ficaram em `/api/v1/antennas/lora-modules` (não `/api/v1/library/lora-modules` como sugerido no roadmap). Mudança de prefix quebraria testes existentes de antenas. Os testes foram escritos contra a URL real.

### Ordem de rotas em library_routes.py
`GET /lora-modules` e `GET /lora-modules/{module_id}` foram inseridos ANTES de `GET /{id}` para evitar que FastAPI capture `"lora-modules"` como valor de `id`.

### `backend/app/data/` — diretório novo
Criado para dados estáticos do catálogo (não é dados de usuário). Distinto de `backend/data/scenarios/` que armazena cenários em runtime.

### `pattern_g()` — não abstrato em BaseSolver
`BaseSolver` abstrato define apenas `solve()`. Os novos solvers adicionam `pattern_g(theta, phi, freq_hz)` como método concreto extra — disponível para Fase 3 sem alterar o contrato base.

---

## Critérios de Conclusão

| Critério | Status |
|---|---|
| `uv run pytest tests/ -v` — zero falhas | ✅ 196 passed |
| `GET /api/v1/antennas/lora-modules` retorna 3 módulos | ✅ `test_api_list_lora_modules_count` |
| RFM95W SF12 sensitivity = -139 dBm | ✅ `test_api_rfm95w_sensitivity_sf12` |
| Sandbox aceita `pcb_compact` sem 422 | ✅ `test_sandbox_pcb_compact_preview_200` |
| Sandbox aceita `commercial_omni_6dbi` sem 422 | ✅ `test_sandbox_colinear_preview_200` |
| `NodeSpec` aceita novos campos sem erro | ✅ retrocompatibilidade confirmada (196 passed) |
| Cenários antigos carregam corretamente | ✅ todos defaults preenchidos pelo Pydantic |

---

## Pendências para Fases Futuras

| Item | Fase destino |
|---|---|
| `lora_module_id` em `NodeSpec` ainda não sobrescreve `rx_sensitivity_dbm` / `tx_power_dbm` — campo existe, lógica de resolução pendente | Fase 3 |
| `extra_loss_db`, `fading_margin_db`, `polarization_loss_db` não entram ainda no `compute_link` | Fase 3 |
| `azimuth_deg` / `tilt_deg` não usados em `pattern_g` ainda (Fase 3 vai integrar G(θ,φ)) | Fase 3 |
| Frontend: dropdown de módulo LoRa não implementado | Fase 5 |
| E220_900T22D opera a 900 MHz — cenários a 915 MHz precisam de nota de validade | Fase 3/4 |
