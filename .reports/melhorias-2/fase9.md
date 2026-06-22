# Report — Melhorias 2 — Fase 9

**Data:** 2026-06-22

## Comandos Executados

```powershell
# Direcionado
uv run pytest tests/test_library.py tests/test_new_antenna_solvers.py tests/test_phase3_link_budget.py tests/test_link_budget.py tests/test_comparison.py -v

# Completo
uv run pytest
```

## Resultados

| Bateria | Resultado |
|---|---|
| Direcionada (5 suítes) | **151 passed, 1 warning** |
| Completa (todas suítes) | **336 passed, 1 skipped, 1 warning** |

Zero falhas. Zero regressões. O 1 skip e 1 warning preexistem às melhorias 2 (FastAPI/httpx deprecation warning, skip em teste de simulação pesada).

## Falhas Encontradas e Correções

Nenhuma falha. Todos os testes passaram na primeira execução.

## Cobertura dos Casos Mínimos

| Caso mínimo | Teste(s) cobrindo |
|---|---|
| Antena antiga sem campos novos carrega e calcula | `test_library.py::test_old_spec_without_physical_fields_loads` |
| `pcb_compact` em 915 MHz → `1.5 dBi` (preset `gmax_dbi=1` ignorado) | `test_phase3_link_budget.py::test_effective_gain_pcb_915mhz_preset_gmax_ignored` |
| `pcb_compact` com `gmax_dbi=1` explícito → override no link budget | `test_phase3_link_budget.py::test_effective_gain_pcb_explicit_gmax_used`, `test_effective_gain_pcb_explicit_gmax_custom_value` |
| `commercial_omni_6dbi` com `hpbw_deg=35` usa esse HPBW | `test_new_antenna_solvers.py::test_colinear_pattern_hpbw_default_is_35`, `test_phase3_link_budget.py::test_effective_gain_colinear_uses_preset_hpbw_35` |
| Helicoidal apontada → margem maior | `test_phase3_link_budget.py::test_directional_gain_penalizes_misalignment` |
| Helicoidal desalinhada → margem menor | `test_phase3_link_budget.py::test_directional_gain_penalizes_misalignment` |
| Parabólica penalizada em cenário multi-sensor | `test_comparison.py::test_comparison_parabolica_good_p2p_bad_multisensor`, `test_comparison_commercial_omni_vs_parabolica_multiazimuth` |
| Polarização circular vs linear → penalidade 3 dB | `test_link_budget.py::test_polarization_circular_vs_linear_is_3db`, `test_polarization_linear_vs_circular_is_3db` |
| Export/import de antena nova preserva campos | `test_library.py::test_physical_fields_preserved_on_save_and_load` |

Todos os 9 casos cobertos.

## Reports de Fases

Todos presentes em `.reports/melhorias-2/`:
`fase1.md`, `fase2.md`, `fase3.md`, `fase4.md`, `fase5.md`, `fase6.md`, `fase7.md`, `fase8.md`.

## Pendências e Riscos Restantes

| Item | Detalhe |
|---|---|
| `httpx2` deprecation warning | FastAPI recomenda trocar `httpx` por `httpx2`. Não é regressão das melhorias — preexistia. |
| 1 skip em simulação pesada | Teste marcado como skip deliberado (ambiente/lentidão). Não relacionado às melhorias 2. |
| Ordenação por `aggregate_score` | Ranking ainda ordena por `min_margin_db`. `aggregate_score` está disponível na resposta da API mas não é o critério primário. Mudança disruptiva — decisão futura. |
| Frontend não testado automaticamente | Sandbox e library testados manualmente (Fase 7). Não há testes automatizados de UI. |
