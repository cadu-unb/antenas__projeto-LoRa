# Report — Melhorias 2 — Fase 6

**Data:** 2026-06-22

## Mudanças no Cálculo de Robustez e Ranking

`backend/app/domain/comparison.py`

### `_DIRECTIONAL` → `_DIRECTIONAL_FALLBACK`

Renomeado. Mantido apenas como fallback quando `is_directional` não está disponível na spec/preset. Não é mais a fonte primária de decisão.

### `_get_ant_field(antenna, field_name, fallback=None)`

Nova função helper. Extrai campo de qualquer tipo de antena:

| Tipo de entrada | Comportamento |
|---|---|
| `AntennaSpec` | `apply_antenna_defaults().spec.<field>` |
| `str` (type name) | `ANTENNA_PRESETS[type].get(field)` |
| `SimpleNamespace` / outros | `getattr(antenna, field, fallback)` |
| `None` | retorna `fallback` |

### `_compute_robustness(margins, tx_antenna, gw_antenna=None)`

Assinatura expandida. Antes: `(margins, tx_antenna_type: str)`. Agora aceita objetos.

#### Penalidade TX (preservada)
- Usa `is_directional` via `_get_ant_field`; fallback para `_DIRECTIONAL_FALLBACK` se campo ausente.
- Se `is_directional=True` e `std_m > 10` → multiplicador `0.5`.

#### Fator GW `multi_direction_score` (novo)
- Obtido via `_get_ant_field(gw_antenna, "multi_direction_score")`.
- `mds_factor = score / 10.0` se disponível; `1.0` se ausente (retrocompatível).
- Scores de referência: `commercial_omni_6dbi=8`, `dipolo=9`, `parabolica=1`, `helicoidal=3`.
- Efeito: parabolica como GW em cenário multi-sensor → robustness ~8× menor que omni como GW.

### Fórmula completa

```
base = mean_margin / (std + 1.0)
dir_penalty = 0.5  se tx_is_dir e std > 10, senão 1.0
mds_factor = gw_multi_direction_score / 10.0  (ou 1.0)
robustness_score = base × dir_penalty × mds_factor
```

## Campos Adicionados em `ComparisonRow`

| Campo | Tipo | Conteúdo |
|---|---|---|
| `practicality_score` | `float` | Média de `practicality_score` TX e GW; 0.0 se ausente |
| `aggregate_score` | `float` | `robustness_score + practicality_score × 0.5` |
| `scores_source` | `str` | `"preset"` \| `"spec"` \| `"fallback"` |

Scores de praticidade de referência: `pcb_compact=10`, `commercial_omni_6dbi=9`, `dipolo=8`, `monopolo=7`, `helicoidal=5`, `parabolica=2`.

## API `/compare`

`backend/app/api/link_routes.py` — campos novos adicionados à resposta JSON:

```json
{
  "robustness_score": 4.123,
  "practicality_score": 8.5,
  "aggregate_score": 8.375,
  "scores_source": "preset"
}
```

## Fallbacks Mantidos

| Cenário | Comportamento |
|---|---|
| Spec sem `is_directional` | Fallback para `_DIRECTIONAL_FALLBACK` por type string |
| GW sem `multi_direction_score` | `mds_factor = 1.0` (sem penalidade) |
| `practicality_score` ausente em ambas | `practicality_score=0.0`, `scores_source="fallback"` |
| Type desconhecido (sem preset) | Todos campos None → fallback comportamento antigo |
| `_compute_robustness(margins, "helicoidal")` | Ainda funciona (type string → preset lookup) |

## Testes Criados

### `tests/test_comparison.py` — 9 novos testes (Fase 6)

| Teste | O que verifica |
|---|---|
| `test_get_ant_field_from_preset_via_spec` | `is_directional`, `multi_direction_score`, `practicality_score` via preset |
| `test_get_ant_field_from_type_string` | Lookup por string funciona (parabolica, commercial_omni_6dbi) |
| `test_get_ant_field_none_antenna_returns_fallback` | None → fallback value |
| `test_robustness_gw_parabolica_penalized_vs_omni` | parabolica GW robustness < commercial_omni GW |
| `test_robustness_backward_compat_string_args` | `_compute_robustness` com strings ainda funciona |
| `test_comparison_row_has_practicality_aggregate_fields` | Campos novos presentes e >0 para dipolo |
| `test_comparison_commercial_omni_vs_parabolica_multiazimuth` | omni > parabolica em 4 sensores multi-azimute |
| `test_comparison_parabolica_good_p2p_bad_multisensor` | parabolica penalizada vs omni em multi-sensor |
| `test_comparison_scores_source_fallback_for_unknown_type` | tipo sem preset → scores_source="fallback" |

## Validações Executadas

```powershell
uv run pytest tests/test_comparison.py -v
```

Resultado: **22 passed, 1 warning**.

```powershell
uv run pytest
```

Resultado: **323 passed, 1 skipped, 1 warning** (regressão zero, +9 testes vs Fase 5).

## Pendências e Riscos

| Item | Detalhe |
|---|---|
| Ordenação por `aggregate_score` | Ranking ainda ordena por `min_margin_db`. Aggregate é informativo. Mudar ordenação primária para aggregate_score seria mudança mais disruptiva. |
| `commercial_omni_6dbi` em `_DIRECTIONAL_FALLBACK` | Removido do fallback (estava no antigo `_DIRECTIONAL`). Preset define `is_directional=False`, o que é correto para omni colinear. Comportamento anterior classificava-o como diretivo incorretamente. |
| Praticidade parcial (só TX ou só GW) | `scores_source="spec"` e soma simples (não média). Pode inflar se um lado tem score e o outro não. Raro na prática (todos os 6 tipos têm preset). |
| robustness_score não normalizado | Valores absolutos dependem da faixa de margens. Aggregate_score = robustness + prac×0.5 mistura escala. Adequado para ranking relativo, não para valores absolutos. |
