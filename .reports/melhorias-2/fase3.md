# Report — Melhorias 2 — Fase 3

**Data:** 2026-06-22

## Arquivo criado

`backend/app/domain/antenna_presets.py`

## Valores finais dos presets

| Tipo | `gmax_dbi` | `hpbw_deg` | `polarization` | `is_directional` | `pattern_model` | `practicality_score` | `multi_direction_score` |
|---|---:|---:|---|---|---|---:|---:|
| `dipolo` | 2.15 | 78.0 | linear vertical | false | dipole | 8.0 | 9.0 |
| `monopolo` | 5.15 | 55.0 | linear vertical | false | monopole | 7.0 | 8.0 |
| `helicoidal` | 11.0 | 55.0 | circular/elliptical | true | helical | 5.0 | 3.0 |
| `parabolica` | 20.0 | 18.0 | feed-dependent | true | parabolic | 2.0 | 1.0 |
| `pcb_compact` | 1.0¹ | 120.0 | linear | false | pcb | 10.0 | 7.0 |
| `commercial_omni_6dbi` | 6.0 | 35.0 | linear vertical | false | omni_colinear | 9.0 | 8.0 |

¹ `pcb_compact.gmax_dbi=1` é valor nominal MATLAB. O solver usa ganho por faixa (1.5 dBi a 915 MHz). A Fase 4 deve checar `from_preset` e ignorar esse override para PCB.

## Como defaults são aplicados sem mutar arquivos antigos

`apply_antenna_defaults(spec)` retorna um novo `AntennaSpec` construído via `AntennaSpec(**merged_data)`. O objeto original passado como argumento não é modificado — `model_copy` foi evitado porque não dispara `model_validator`. O storage nunca é chamado dentro do helper; a spec enriquecida existe apenas em memória.

## Como valores explícitos do usuário são diferenciados dos presets

`apply_antenna_defaults` retorna `SpecWithDefaults(spec, from_preset: frozenset[str])`. Campos em `from_preset` vieram do preset; campos ausentes em `from_preset` foram definidos pelo usuário. Exemplo de uso na Fase 4:

```python
result = apply_antenna_defaults(spec)
use_gmax = (
    result.spec.gmax_dbi
    if "gmax_dbi" not in result.from_preset or spec.type != "pcb_compact"
    else None  # usa cálculo por faixa do solver
)
```

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `backend/app/domain/antenna_presets.py` | Criado: `ANTENNA_PRESETS`, `SpecWithDefaults`, `apply_antenna_defaults` |
| `backend/app/api/sandbox_routes.py` | `_solve_colinear`: HPBW substituído de `20.0` hardcoded para `ANTENNA_PRESETS["commercial_omni_6dbi"]["hpbw_deg"]` (35°) |
| `tests/test_new_antenna_solvers.py` | 28 testes novos adicionados |

## Validações executadas

```
uv run pytest tests/test_new_antenna_solvers.py -v
```

Resultado: **45/45 passed**.

## Pendências e riscos

| Item | Detalhe |
|---|---|
| `_effective_gain()` ainda não usa presets | Fase 4. `from_preset` já exposto para orientar a implementação. |
| `apply_antenna_defaults` não é chamado automaticamente | Chamada explícita necessária nos solvers/comparison. Fase 4 integra no link budget. |
| Registro de solver separado | `backend/app/solvers/__init__.py` não alterado — registry de solvers continua independente dos presets físicos. |
