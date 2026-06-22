# Prompt — Melhorias 2 — Fase 9

Use como referência principal o arquivo `.reports/melhorias-2/plano-implementacao.md`, especialmente a seção **Fase 9 — Testes de Regressão Integrados**. Esta fase deve ser executada depois das fases anteriores.

## Objetivo

Executar regressão integrada e confirmar que as melhorias de antenas não quebraram compatibilidade, cálculo, ranking, API, import/export e documentação essencial.

## Arquivos e áreas alvo

- `tests/test_library.py`
- `tests/test_new_antenna_solvers.py`
- `tests/test_phase3_link_budget.py`
- `tests/test_link_budget.py`
- `tests/test_comparison.py`
- Demais testes do projeto
- Reports das fases anteriores em `.reports/melhorias-2/fase*.md`

## Passos

1. Leia o plano e os reports das fases anteriores.
2. Confirme que os casos mínimos foram cobertos:
   - antena antiga sem campos novos carrega e calcula;
   - `pcb_compact` em 915 MHz usa `1.5 dBi` quando apenas preset existe;
   - `pcb_compact` com `gmax_dbi=1` explícito usa override no link budget;
   - `commercial_omni_6dbi` com `hpbw_deg=35` usa esse HPBW;
   - helicoidal apontada tem margem maior;
   - helicoidal desalinhada tem margem menor;
   - parabólica é penalizada em cenário multi-sensor;
   - polarização circular vs linear aplica perda automática;
   - export/import de antena nova preserva campos.
3. Rode a bateria direcionada:

```powershell
uv run pytest tests/test_library.py tests/test_new_antenna_solvers.py tests/test_phase3_link_budget.py tests/test_link_budget.py tests/test_comparison.py
```

4. Rode a suíte completa:

```powershell
uv run pytest
```

5. Se houver falhas:
   - identifique se são regressões reais ou testes desatualizados;
   - corrija o mínimo necessário;
   - rode novamente os testes relevantes.
6. Faça uma revisão final dos reports para garantir que cada fase descreve o executado.

## Critérios de aceite

- Suíte direcionada passa.
- Suíte completa passa, ou falhas externas/ambientais ficam documentadas com evidência.
- Casos mínimos da Fase 9 estão cobertos.
- Reports de fases existem e são objetivos.

## Report final obrigatório

Ao concluir, crie um report objetivo e conciso em `.reports/melhorias-2/fase9.md` descrevendo:

- comandos executados;
- resultado dos testes;
- falhas encontradas e correções aplicadas;
- cobertura dos casos mínimos;
- pendências ou riscos restantes.

Também atualize ou crie um resumo final em `.reports/melhorias-2/resumo-final.md` com:

- fases concluídas;
- principais mudanças entregues;
- estado final da validação;
- próximos passos recomendados.
