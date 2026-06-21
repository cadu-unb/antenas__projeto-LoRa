# Roadmap — Melhorias 1

**Referência:** `.reports/externo/resume.md` (19 gaps identificados)
**Data:** 2026-06-21
**Escopo:** Implementar melhorias prioritárias ao sistema Python e corrigir a escala de distância dos fixtures/presets.

---

## Visão Geral

O sistema já possui infraestrutura web/API robusta (FastAPI, biblioteca de antenas, sandbox, KML, topologias, site selection, jobs). O trabalho aqui foca em **corrigir gaps físicos e de usabilidade** identificados pela comparação com o material MATLAB de referência (Campus Darcy Ribeiro UnB, 915 MHz).

As melhorias estão divididas em **5 fases** que seguem ordem de dependência lógica: primeiro corrigir a base, depois enriquecer os modelos, depois a física, depois as análises avançadas, e por último integrar tudo no frontend.

---

## Mapa de Dependências

```
Fase 1 (Fundações)
  ├── Fase 2 (Modelos/Schemas)
  │     └── Fase 3 (Motor Físico)
  │           └── Fase 4 (Features Analíticas)
  └── Fase 5 (Frontend) ← consome resultado de todas as fases
```

- **Fase 5** pode ser desenvolvida em paralelo com Fase 2–4 para os campos que não dependem de lógica nova (ex: presets de coordenadas, botão de exportação).
- **Fase 3** exige Fase 2 concluída (NodeSpec com novos campos e modelos de antena completos).
- **Fase 4** exige Fase 2 e Fase 3 concluídas.

---

## Resumo das Fases

| Fase | Título | Gaps cobertos | Complexidade |
|------|--------|--------------|-------------|
| 1 | Correções Fundamentais | 18, 19 | Baixa |
| 2 | Modelos e Schemas | 2, 4, 6, 11 | Média |
| 3 | Motor Físico | 1, 3, 7, 13, 17 | Alta |
| 4 | Features Analíticas | 5, 8, 9, 10, 12, 15 | Alta |
| 5 | Frontend e Integração | todos | Média |

---

## Critérios de Conclusão por Fase

Cada fase é considerada concluída quando:

1. Todos os testes de unidade passam (`uv run pytest` sem falhas).
2. A API retorna os novos campos nos endpoints afetados (verificado via `curl` ou docs em `/docs`).
3. As etapas marcadas como "verificar no frontend" funcionam visualmente no browser.
4. Nenhuma rota existente regride (rodar a suíte completa após cada etapa).

---

## Arquivos-Chave de Referência

| Arquivo | Papel |
|---------|-------|
| `backend/app/schemas/node_spec.py` | Model de nó — campos a expandir nas Fases 2 e 3 |
| `backend/app/schemas/link_scenario.py` | Model de cenário — separação setup/resultados na Fase 1 |
| `backend/app/domain/link_budget.py` | Cálculo de enlace — integrar perdas e G(θ,φ) na Fase 3 |
| `backend/app/api/link_routes.py` | Rotas de cenário — novo endpoint de export na Fase 1 |
| `backend/app/solvers/` | Solvers de antena — novos tipos e G(θ,φ) na Fase 3 |
| `tests/test_site_selection.py` | Fixtures de coordenadas — corrigir escala na Fase 1 |
| `frontend/public/link-planner.html` | UI principal — campos novos na Fase 5 |
| `frontend/public/js/api-client.js` | Cliente JS — novas chamadas de API na Fase 5 |

---

## Arquivo de Fases

- [fase1.md](fase1.md) — Correções Fundamentais (escala + persistência)
- [fase2.md](fase2.md) — Modelos e Schemas (NodeSpec, LoRaModule, antenas novas)
- [fase3.md](fase3.md) — Motor Físico (G(θ,φ), ENU, orientação, perdas, propagação)
- [fase4.md](fase4.md) — Features Analíticas (comparação A-E, ranking, energia)
- [fase5.md](fase5.md) — Frontend e Integração (UI, presets, seletor de módulo, exportação)
