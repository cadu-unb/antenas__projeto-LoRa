# Report — Melhorias 2 — Fase 4

**Data:** 2026-06-22

## Mudanças em `_effective_gain()`

`backend/app/domain/link_budget.py` — função `_effective_gain()` reescrita.

### Prioridade de ganho (no azimuth/pico)

```
user-explicit gmax_dbi  →  return diretamente
preset gmax_dbi         →  ignorado (exceto PCB — veja abaixo)
nenhum                  →  solver.gain_dbi() (comportamento anterior)
```

### Prioridade de HPBW (com azimuth/padrão angular)

```
spec/preset hpbw_deg    →  sempre passado como kwarg para pattern_g()
nenhum                  →  cada solver usa sua constante interna
```

`hpbw_deg` é sempre repassado (usuário E preset), diferente de `gmax_dbi`, porque o preset HPBW é o dado canônico MATLAB que corrige divergências (colinear 35° vs 20°).

### Regra para `gmax_dbi`

- Verificação via `apply_antenna_defaults()` + `from_preset`:
  - `"gmax_dbi" not in from_preset` → usuário definiu explicitamente → `use_gmax = valor`
  - `"gmax_dbi" in from_preset` → veio do preset → `use_gmax = None` → solver calcula
- Exceção PCB: regra idêntica. `gmax_dbi=1` do preset é nominal MATLAB; solver usa 1.5 dBi a 915 MHz.

### Regra final `pcb_compact.gmax_dbi`

| Fonte do `gmax_dbi` | Ganho no link budget |
|---|---|
| Nenhum (spec v1.0) | Solver por faixa: 0 / 1.5 / 2.0 dBi |
| Preset (from_preset) | Ignorado → solver por faixa (1.5 dBi a 915 MHz) |
| Usuário explícito | Usa o valor informado (`1.0`, `2.5`, etc.) |

### Objetos não-AntennaSpec

Guard: `if hasattr(antenna, "model_dump")` protege `apply_antenna_defaults()` de objetos `SimpleNamespace` passados em testes de baixo nível.

## Mudanças nos solvers

### `ColinearSolver.pattern_g()`

- HPBW default: `20.0` → **`35.0`** (alinhado ao MATLAB externo).
- Aceita `hpbw_deg` e `gmax_dbi` via `**kwargs`.

### `ApertureSolver.pattern_g()`

- Aceita `gmax_dbi` kwarg: substitui cálculo de abertura como G_max.
- Aceita `hpbw_deg` kwarg: substitui `70λ/D` empírico.

### `PcbSolver.pattern_g()`

- Aceita `gmax_dbi` kwarg: substitui `self.gain_dbi(freq_hz)` como pico.
- Sem mudança na penalidade de elevação.

### `MoMSolver.pattern_g()`

- Aceita `gmax_dbi` kwarg: substitui `self.gain_dbi(freq_hz, **kwargs)` como pico.
- `hpbw_deg` ignorado — dipolo/monopolo usam modelo toroidal (sin²θ); helicoidal usa cos²θ.

## Testes criados

### `tests/test_phase3_link_budget.py` — 9 novos testes

| Teste | O que verifica |
|---|---|
| `test_effective_gain_pcb_915mhz_preset_gmax_ignored` | preset 1.0 ignorado → solver retorna 1.5 dBi |
| `test_effective_gain_pcb_explicit_gmax_used` | gmax_dbi=1.0 explícito → usa 1.0 |
| `test_effective_gain_pcb_explicit_gmax_custom_value` | gmax_dbi=2.5 explícito → usa 2.5 |
| `test_effective_gain_explicit_gmax_overrides_solver` | dipolo gmax_dbi=5.0 → usa 5.0 |
| `test_effective_gain_no_explicit_gmax_uses_solver` | sem gmax → solver 1.8–2.5 dBi |
| `test_effective_gain_colinear_hpbw_from_spec_changes_pattern` | hpbw estreito < hpbw largo em offset 90° |
| `test_effective_gain_colinear_uses_preset_hpbw_35` | ponto de meia potência em 17.5° ≈ −3 dB |
| `test_effective_gain_aperture_hpbw_override` | hpbw kwarg muda atenuação angular na parabólica |
| `test_effective_gain_none_antenna_returns_zero` | antenna=None → 0 dBi |

### `tests/test_new_antenna_solvers.py` — 7 novos testes

| Teste | O que verifica |
|---|---|
| `test_colinear_pattern_hpbw_default_is_35` | ponto −3 dB em 17.5° (HPBW 35°) |
| `test_colinear_pattern_hpbw_kwarg_changes_gain` | kwarg hpbw_deg muda ganho angular |
| `test_colinear_pattern_gmax_kwarg_shifts_gain` | kwarg gmax_dbi eleva curva |
| `test_aperture_pattern_hpbw_kwarg_overrides_geometric` | kwarg hpbw_deg substitui 70λ/D |
| `test_aperture_pattern_gmax_kwarg` | kwarg gmax_dbi=25 → peak=25 dBi |
| `test_pcb_pattern_gmax_kwarg` | kwarg gmax_dbi=1.0 → 1.0; default 915 MHz → 1.5 |
| `test_mom_pattern_gmax_kwarg_dipolo` | kwarg gmax_dbi=5.0 aumenta ganho no toroidal |

## Validações executadas

```powershell
uv run pytest tests/test_phase3_link_budget.py tests/test_solvers.py tests/test_new_antenna_solvers.py -v
```

Resultado: **108 passed, 1 skipped**.

## Pendências e riscos

| Item | Detalhe |
|---|---|
| MoMSolver / helicoidal sem HPBW explícito | cos²θ não usa hpbw_deg; kwarg ignorado. Aceitável — HPBW de helicoidal depende de geometria (espiras), não de constante. Fase futura pode implementar beamwidth adaptativo. |
| `apply_antenna_defaults` chamado por enlace | Reconstrução AntennaSpec completa a cada cálculo. Sem caching. Não é problema em produção LoRa (< 100 nós), mas pode ser otimizado se necessário. |
| Comportamento sem azimuth para colinear | Retorna `use_gmax=6.0` do preset (preset ≠ from_preset para não-PCB? Não: colinear gmax_dbi=6.0 VEM do preset → `from_preset` → `use_gmax=None` → `solver.gain_dbi()=6.0`). Resultado idêntico. |
