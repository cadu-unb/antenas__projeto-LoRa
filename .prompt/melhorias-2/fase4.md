# Prompt — Melhorias 2 — Fase 4

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 4 — Uso dos Campos no Cálculo de Ganho**. Consulte também `.reports/melhorias-2/quadro-antenas.md` para entender as divergências entre MATLAB externo e Python atual.

## Objetivo

Fazer o cálculo de ganho efetivo usar campos explícitos da antena (`pattern_model`, `gmax_dbi`, `hpbw_deg`) quando disponíveis, mantendo compatibilidade com o comportamento atual quando eles estiverem ausentes.

## Arquivos alvo

- `backend/app/domain/link_budget.py`
- `backend/app/solvers/mom_solver.py`
- `backend/app/solvers/aperture_solver.py`
- `backend/app/solvers/pcb_solver.py`
- `backend/app/solvers/colinear_solver.py`
- `tests/test_phase3_link_budget.py`
- `tests/test_solvers.py`
- `tests/test_new_antenna_solvers.py`

## Passos

1. Leia o plano e confira as decisões da Fase 4.
2. Atualize `_effective_gain()` para considerar, nesta ordem:
   - valores explícitos da spec do usuário;
   - defaults/presets em runtime;
   - fallback legado do solver.
3. Faça o cálculo aceitar `pattern_model` quando existir, incluindo o alias `omni_colinear`.
4. Permita que `hpbw_deg` sobrescreva constantes internas nos padrões que usam largura de feixe:
   - colinear;
   - parabólica;
   - helicoidal, se aplicável.
5. Para `commercial_omni_6dbi`, use `hpbw_deg=35` vindo da spec/preset; mantenha `20°` somente como fallback interno legado.
6. Para `pcb_compact`, mantenha o ganho por faixa do solver quando o `gmax_dbi=1` veio apenas do preset. Use override `gmax_dbi` somente quando o usuário tiver informado explicitamente esse campo.
7. Padronize ou documente o significado de `theta_deg` nos solvers:
   - off-boresight para diretivas;
   - ângulo polar/elevacional para omnis, conforme comportamento atual.
8. Adicione testes para antena apontada, desalinhada, HPBW customizado, `commercial_omni_6dbi` com `35°`, `pcb_compact` em 915 MHz e override explícito de `gmax_dbi`.

## Critérios de aceite

- Alterar `hpbw_deg` muda o ganho angular de diretivas/colinear.
- Specs sem campos novos mantêm resultado próximo ao comportamento atual.
- `pcb_compact` em 915 MHz usa `1.5 dBi` quando apenas o preset existe.
- `pcb_compact` com `gmax_dbi=1` explícito usa `1.0 dBi` no link budget.
- `commercial_omni_6dbi` usa HPBW `35°` quando vier de spec/preset.

## Validação

Execute:

```powershell
uv run pytest tests/test_phase3_link_budget.py tests/test_solvers.py tests/test_new_antenna_solvers.py
```

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase4.md` descrevendo:

- mudanças em `_effective_gain()` e solvers;
- regra final para `hpbw_deg`;
- regra final para `pcb_compact.gmax_dbi`;
- testes criados ou alterados;
- validações executadas;
- pendências ou riscos restantes.
