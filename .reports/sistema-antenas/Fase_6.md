# Fase 6 — Solvers Avançados
**Data:** 2026-06-17
**Status:** ✅ Concluída

---

## Solvers criados

| Arquivo | Tipo | Antenas/Uso |
|---|---|---|
| `backend/app/solvers/base_solver.py` | ABC | Contrato base: `solve(spec) → SolverResult` |
| `backend/app/solvers/mom_solver.py` | MoM/PyNEC | Dipolo, monopolo, helicoidal |
| `backend/app/solvers/aperture_solver.py` | Abertura | Parabólica |
| `backend/app/solvers/okumura_hata.py` | Propagação empírica | Link budget 150–1500 MHz |
| `backend/app/solvers/longley_rice.py` | Propagação terreno | Enlace em terreno irregular |
| `backend/app/solvers/ray_tracing_solver.py` | Stub arquitetural | Gancho para implementação futura |

---

## BaseSolver

`BaseSolver.solve(spec: Any) -> SolverResult` — ABC com docstring completa.

`SolverResult` — Pydantic model com campos:
- `gain_dbi`, `impedance_ohm`, `swr`, `efficiency_pct`
- `radiation_pattern`, `solver_used`
- `warning: Optional[str]`, `extra: dict`

---

## Fallback PyNEC

PyNEC não disponível no ambiente (instalação requer compilador C — risco alto no Windows, documentado em `.plan/plan_v2.md`).

Comportamento implementado:
- `import PyNEC` falhando → `_PYNEC_AVAILABLE = False`
- `logger.warning(...)` com mensagem de instalação registrado na inicialização
- `MoMSolver.solve()` chama `_analytic_fallback()` automaticamente
- `SolverResult.solver_used = "mom_analitico"` e `warning` indica fallback ativo
- Nenhum `ImportError` propagado — comportamento degradado mas não fatal

---

## Solvers de propagação

### Okumura-Hata

Implementação completa de Hata (1980):
- 4 ambientes: `urban_large`, `urban_small`, `suburban`, `open`
- Fator `a(h_m)` correto para cidade grande (f ≥ 300 MHz) e pequena
- Aviso automático fora do intervalo 150–1500 MHz, 1–20 km, 30–200 m, 1–10 m

**Valor de referência validado:**
```
f=900 MHz, h_b=30m, h_m=1.5m, d=1km, urban_large → 126.43 dB
Teste: abs(resultado - 126.43) ≤ 1.0 dB ✓
```

### Longley-Rice (simplificado)

Implementação analítica dos conceitos ITM:
- Determinação de LOS por raio efetivo da Terra (k=4/3)
- Região LOS: FSPL + correção de irregularidade `A_terrain`
- Região difração: FSPL + J(ν) knife-edge + `A_difração` + `A_terrain`
- Campo `los: bool` no resultado indica regime de propagação

Nota: implementação simplificada — não usa tabelas do ITM original (Fortran). Recomendado splat! ou NTIA/ITS C++ para produção com DEM real.

---

## Limites de RAM e Tempo

`backend/app/workers/resource_guard.py` — `ResourceGuard`:

| Limite | Valor | Código de erro |
|---|---|---|
| RAM | 25 GB (`MAX_RAM_GB`) | `FAILED_MEMORY_LIMIT` |
| Tempo | 30 min (`MAX_RUNTIME_MIN`) | `FAILED_TIME_LIMIT` |

- `check_ram()` — verificação pré-flight com `psutil.virtual_memory()`
- `run_guarded(coro)` — `asyncio.wait_for` com timeout configurável
- `_ram_override_gb` e `_timeout_override_s` — parâmetros de teste injetáveis
- `ResourceLimitError(code, message)` — exceção estruturada com mensagem acionável

---

## Logs de simulação

Log gravado em `backend/data/simulations/{id}/log.jsonl`:

```jsonl
{"ts": 1750123456.0, "event": "START", "max_ram_gb": 25, "max_runtime_min": 30, "timeout_s": 1800}
{"ts": 1750123456.1, "event": "DONE", "elapsed_min": 0.002}
```

Evento `FAILED_*` gravado mesmo em jobs abortados — log parcial persiste.

Eventos: `START`, `DONE`, `FAILED_MEMORY_LIMIT`, `FAILED_TIME_LIMIT`, `ERROR`.

---

## Integração no Sandbox

`backend/app/api/sandbox_routes.py` atualizado:

- `solver = "padrao"` ou `"preciso"` → `_preview_advanced(req)` → MoM ou Abertura
- `solver = "rapido"` → caminho analítico existente (inalterado)
- Padrão de radiação calculado analiticamente mesmo no modo avançado (UI não muda)
- Parabólica em modo Padrão/Preciso → `ApertureSolver` (não MoM)

---

## Dependência adicionada

```
psutil==7.2.2   (via uv add psutil)
```

---

## Docs criadas

| Arquivo | Conteúdo |
|---|---|
| `docs/calculos/03-metodo-dos-momentos-mom.md` | MoM: parâmetros, referências, limitações |
| `docs/calculos/04-parabolica-aproximacao-abertura.md` | Abertura: G = η·(πD/λ)², por que não MoM |
| `docs/calculos/06-okumura-hata.md` | Fórmulas, ambientes, referências bibliográficas |
| `docs/calculos/07-longley-rice-itm.md` | LOS/difração, parâmetros, limitações desta versão |
| `docs/calculos/09-limites-computacionais.md` | Limites RAM/tempo, log JSONL, modos e custos |

---

## Resultado dos testes

```
tests/test_solvers.py — 33 passed
Suite completa     — 98 passed, 1 warning in 2.05s
```

---

## Checkpoints

- [x] `BaseSolver.solve()` importável e documentado
- [x] Dipolo λ/2 em modo Padrão retorna ganho entre 1.8 dBi e 2.5 dBi (2.15 dBi)
- [x] Cenário de referência documentado em `tests/test_solvers.py` (docstring + assert)
- [x] Parabólica usa `aperture_solver`, não MoM (`solver_used == "abertura"` verificado)
- [x] Simulação acima de 25 GB gera `FAILED_MEMORY_LIMIT` (via `_ram_override_gb=30`)
- [x] Simulação acima de 30 min gera `FAILED_TIME_LIMIT` (via `_timeout_override_s=0.1`)
- [x] Log parcial persiste em `backend/data/simulations/{id}/log.jsonl` mesmo em jobs abortados
- [x] PyNEC ausente gera fallback analítico + aviso (`_PYNEC_AVAILABLE = False` verificado)
- [x] Okumura-Hata retorna perda em dB com tolerância ±1 dB (126.43 dB ±1 dB)
- [x] `pytest tests/test_solvers.py` passa (33/33)
- [x] `ray_tracing_solver.py` existe como stub (sem lógica, apenas comentário de implementação futura)

---

## Erros conhecidos / limitações

- PyNEC requer compilador C no Windows (MSVC ou MinGW). Em Linux/WSL2: `pip install PyNEC` direto. Instruções completas em `README.md`. Fallback analítico ativo automaticamente quando PyNEC ausente.
- Longley-Rice simplificado: sem tabelas do ITM original. Para terrenos reais, splat! é recomendado.
- `asyncio.run()` nos testes de ResourceGuard: cria novo event loop por teste — correto em Python 3.10+ mas pode conflitar com pytest-asyncio se instalado com `mode=auto`.
- `test_mom_solver_fallback_sem_pynec` é skipado quando PyNEC está instalado; `test_mom_solver_pynec_quando_disponivel` roda no lugar. Ambos condicionais via `pytest.mark.skipif`.
