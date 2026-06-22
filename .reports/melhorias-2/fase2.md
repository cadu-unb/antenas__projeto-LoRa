# Report — Melhorias 2 — Fase 2

**Data:** 2026-06-22

## Campos adicionados a `AntennaSpec`

| Campo | Tipo | Validação |
|---|---|---|
| `gmax_dbi` | `float \| None` | numérico |
| `hpbw_deg` | `float \| None` | > 0 |
| `polarization` | `str \| None` | — |
| `is_directional` | `bool \| None` | — |
| `pattern_model` | `str \| None` | — |
| `practicality_score` | `float \| None` | 0–10 |
| `multi_direction_score` | `float \| None` | 0–10 |
| `notes` | `str` | — (default `""`) |

Todos opcionais. Specs antigas sem esses campos continuam carregando sem alteração.

## Regra de versionamento

- `schema_version = "1.0"` → default; mantido para specs sem campos físicos.
- `schema_version = "2.0"` → promovido automaticamente pelo `model_validator` quando ao menos um campo físico está preenchido (`gmax_dbi`, `hpbw_deg`, `polarization`, `is_directional`, `pattern_model`, `practicality_score`, `multi_direction_score`) ou `notes != ""`.
- Leitura de spec antiga não regrava arquivo em disco (comportamento do storage existente).

## Arquivos alterados

| Arquivo | Alteração |
|---|---|
| `backend/app/schemas/antenna_spec.py` | 8 campos opcionais adicionados; `field_validator` para `hpbw_deg` e scores; `model_validator` para auto-bump de `schema_version` |
| `tests/test_library.py` | 10 testes novos: campos preservados, versão bumped, versão mantida, spec antiga carrega, 4 testes de validação de range |
| `docs/antenna-spec-schema.md` | Tabela de campos dividida em v1.0 e v2.0; exemplo Commercial Omni atualizado para v2.0 com todos os campos físicos; regra de versionamento documentada |

## Validações executadas

```
uv run pytest tests/test_library.py tests/test_new_antenna_solvers.py -v
```

Resultado: **34/34 passed**.

## Pendências e riscos

| Item | Detalhe |
|---|---|
| Presets canônicos por tipo | Os campos existem no schema mas não são preenchidos automaticamente. Fase 3 cria `apply_antenna_defaults(spec)` e o registry de presets. |
| `_effective_gain()` ainda não usa `gmax_dbi` ou `hpbw_deg` | Fase 4. Comportamento de link budget sem alteração nesta fase. |
| `schema_version` não é validado explicitamente | `"1.0"` e `"2.0"` são os valores esperados mas não há enum — permite qualquer string. Não é problema prático agora. |
