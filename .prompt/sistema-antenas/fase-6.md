# Prompt — Sistema de Antenas LoRa — Fase 6

## Objetivo

Implementar solvers avançados como plugins, com fallback e guardião de recursos.

## Contexto obrigatório

Leia antes de executar:

- `.plan/plan_v2.md`
- `.reports/sistema-antenas/Fase_5.md`, se existir

## Tarefas

1. Criar `backend/app/solvers/base_solver.py`.
2. Definir contrato:

```text
solve(spec) -> SolverResult
```

3. Criar `backend/app/solvers/mom_solver.py`.
4. Integrar PyNEC para:
   - dipolo;
   - monopolo;
   - helicoidal.
5. Se PyNEC não estiver disponível:
   - usar fallback analítico;
   - registrar aviso no log;
   - não falhar fatalmente.
6. Criar `backend/app/solvers/aperture_solver.py`.
7. Criar `backend/app/solvers/okumura_hata.py`.
8. Criar `backend/app/solvers/longley_rice.py`.
9. Criar `backend/app/workers/resource_guard.py`.
10. Guardião deve aplicar:
    - `MAX_RAM_GB`;
    - `MAX_RUNTIME_MIN`.
11. Integrar modos `Padrão` e `Preciso` no sandbox.
12. Criar docs:
    - `docs/calculos/03-metodo-dos-momentos-mom.md`
    - `docs/calculos/04-parabolica-aproximacao-abertura.md`
    - `docs/calculos/06-okumura-hata.md`
    - `docs/calculos/07-longley-rice-itm.md`
    - `docs/calculos/09-limites-computacionais.md`
13. Criar `backend/app/solvers/ray_tracing_solver.py` como stub arquitetural:
    - apenas comentário indicando que é gancho para implementação futura;
    - nenhuma lógica funcional;
    - não conectar a nenhuma rota.
14. Criar `tests/test_solvers.py`.

## Checkpoints obrigatórios

- [ ] `BaseSolver.solve()` é importável e documentado
- [ ] Dipolo λ/2 em modo Padrão retorna ganho entre 1.8 dBi e 2.5 dBi
- [ ] Cenário de referência está documentado em `tests/test_solvers.py`
- [ ] Parabólica usa `aperture_solver`, não MoM
- [ ] Simulação acima de 25 GB gera `FAILED_MEMORY_LIMIT`
- [ ] Simulação acima de 30 min gera `FAILED_TIME_LIMIT`
- [ ] Log parcial persiste em `backend/data/simulations/{id}/log.jsonl`
- [ ] PyNEC ausente gera fallback analítico + aviso
- [ ] Okumura-Hata retorna perda em dB com tolerância ±1 dB
- [ ] `pytest tests/test_solvers.py` passa
- [ ] `ray_tracing_solver.py` existe como stub (sem lógica, apenas comentário de implementação futura)

## Devolutiva obrigatória

Criar:

```text
.reports/sistema-antenas/Fase_6.md
```

O relatório deve conter:

- solvers criados;
- fallback implementado;
- limites de RAM/tempo;
- logs gerados;
- docs criadas;
- comandos executados;
- resultado dos testes;
- checkpoints marcados.

## Regra final

Ray Tracing continua fora desta fase. Criar apenas o stub `ray_tracing_solver.py` — sem implementação funcional.
