# Report — Melhorias 2 — Fase 5

**Data:** 2026-06-22

## Regra de Polarização Implementada

`backend/app/domain/link_budget.py` — funções novas: `_get_polarization()`, `estimate_polarization_loss()`.

### Tabela de decisão

| TX pol | RX pol | Perda |
|---|---|---|
| `circular/elliptical` | `linear*` | `3.0 dB` |
| `linear*` | `circular/elliptical` | `3.0 dB` |
| `linear horizontal` | `linear vertical` | `LINEAR_MISMATCH_LOSS_DB` (1.5 dB) |
| `linear` (bare) | `linear vertical` | `0.0 dB` (compatível — orientação vazia) |
| `feed-dependent` | qualquer | `0.0 dB` (desconhecida) |
| `None` / ausente | qualquer | `0.0 dB` |
| iguais | iguais | `0.0 dB` |

Constante configurável: `LINEAR_MISMATCH_LOSS_DB: float = 1.5` (módulo-level).

### `_get_polarization(antenna)`

Extrai `polarization` efetiva:
- Se Pydantic model → `apply_antenna_defaults().spec.polarization` (usa preset se `None`).
- Outros objetos → `getattr(antenna, "polarization", None)`.

Helicoidal sem `polarization` explícita recebe `"circular/elliptical"` via preset.

## Campos Novos em `LinkResult`

`backend/app/schemas/link_scenario.py`:

```python
polarization_loss_db: float = 0.0
```

Rastreabilidade separada: não somado em `extra_loss_db`.

## Decisão Final — `extra_loss_db` e Perda Total

### Antes (Fase anterior)

```python
extra = extra_loss_a + extra_loss_b + polarization_loss_db(node_a) + fading_margin_a
```

`extra_loss_db` no resultado = soma de extra + pol manual + fading.

### Depois (Fase 5)

```python
extra = extra_loss_a + extra_loss_b + fading_margin_a
pol_total = node_a.polarization_loss_db  +  estimate_polarization_loss(ant_a, ant_b)
rx_power = ... - extra - pol_total
```

| Campo | Contém |
|---|---|
| `extra_loss_db` | extra manual (cabos, obstrução) + fading — sem polarização |
| `polarization_loss_db` | pol manual (NodeSpec) + pol automática (tipo de antena) |

**Semântica clarificada**: `extra_loss_db` não inclui mais polarização manual. Comportamento idêntico quando `NodeSpec.polarization_loss_db == 0` (default).

## Testes Criados

### `tests/test_link_budget.py` — 11 novos testes

| Teste | O que verifica |
|---|---|
| `test_polarization_circular_vs_linear_is_3db` | helicoidal vs dipolo → 3 dB |
| `test_polarization_linear_vs_circular_is_3db` | dipolo vs helicoidal (ordem invertida) → 3 dB |
| `test_polarization_two_linear_vertical_no_penalty` | dipolo vs dipolo → 0 dB |
| `test_polarization_linear_bare_vs_linear_vertical_no_penalty` | pcb ("linear") vs dipolo ("linear vertical") → 0 dB |
| `test_polarization_feed_dependent_no_penalty` | parabolica vs dipolo → 0 dB |
| `test_polarization_none_antenna_no_penalty` | None → 0 dB (ambas direções) |
| `test_polarization_linear_h_vs_v_mismatch` | linear horizontal vs linear vertical → 1.5 dB |
| `test_polarization_link_result_field_exposed` | `LinkResult.polarization_loss_db == 3.0` |
| `test_polarization_manual_plus_auto_sum` | NodeSpec.pol=2.0 + auto=3.0 → total=5.0 |
| `test_polarization_reduces_margin` | margem com mismatch < sem mismatch |
| `test_polarization_manual_still_works_no_antenna` | pol manual sem antena → total = manual |

### `tests/test_comparison.py` — 1 novo teste

| Teste | O que verifica |
|---|---|
| `test_run_comparison_helicoidal_vs_dipolo_lower_than_dipolo_vs_dipolo` | helicoidal-helicoidal pol=0 dB; helicoidal-dipolo pol=3 dB; margem mismatch < match |

## Validações Executadas

```powershell
uv run pytest tests/test_link_budget.py tests/test_comparison.py -v
```

Resultado: **50 passed, 1 warning**.

```powershell
uv run pytest
```

Resultado: **314 passed, 1 skipped, 1 warning** (regressão zero).

## Pendências e Riscos

| Item | Detalhe |
|---|---|
| Parabolica `feed-dependent` → 0 dB | Conservador. Se o feed for linear, o usuário pode setar `polarization="linear vertical"` explicitamente na spec para ativar a lógica. |
| `LINEAR_MISMATCH_LOSS_DB = 1.5` | Configurável por constante de módulo. Sem preset para "linear horizontal" nos 6 tipos, esse branch nunca é ativado em cenários normais — apenas via spec explícita do usuário. |
| NodeSpec.polarization_loss_db vem só do node_a | Comportamento preservado da fase anterior. Para enlace bidirecional com perda manual em node_b, o usuário deve somar manualmente ou mover para node_a. |
| Mudança de semântica de `extra_loss_db` | Agora exclui pol manual. Qualquer cenário salvo que dependia de `extra_loss_db` para incluir pol terá `extra_loss_db` ligeiramente menor, mas `polarization_loss_db` expõe o valor separado. Margem total inalterada. |
