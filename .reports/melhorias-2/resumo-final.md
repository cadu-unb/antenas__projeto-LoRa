# Resumo Final — Melhorias 2

**Data:** 2026-06-22  
**Branch:** versao-3

## Fases Concluídas

| Fase | Título | Status |
|---|---|---|
| 1 | Correções Documentais | ✓ Concluída |
| 2 | Evolução Compatível do Schema | ✓ Concluída |
| 3 | Presets Canônicos dos 6 Tipos | ✓ Concluída |
| 4 | Uso dos Campos no Cálculo de Ganho | ✓ Concluída |
| 5 | Polarização Automática | ✓ Concluída |
| 6 | Ranking com Scores de Antena | ✓ Concluída |
| 7 | API, Biblioteca e Frontend | ✓ Concluída |
| 8 | Compatibilidade e Migração Leve | ✓ Concluída |
| 9 | Testes de Regressão Integrados | ✓ Concluída |

## Principais Mudanças Entregues

### Schema e Presets
- `AntennaSpec` ganhou 8 campos físicos opcionais (`gmax_dbi`, `hpbw_deg`, `polarization`, `is_directional`, `pattern_model`, `practicality_score`, `multi_direction_score`, `notes`)
- `schema_version` bumpa para `"2.0"` automaticamente quando campo físico está presente
- `ANTENNA_PRESETS` — registry canônico com valores para todos os 6 tipos, alinhados com referência MATLAB externa
- `apply_antenna_defaults(spec)` — preenche campos `None` em runtime via preset, sem escrever disco

### Cálculo de Ganho
- `_effective_gain()` prioriza campos explícitos da spec: `gmax_dbi` e `hpbw_deg`
- `pcb_compact`: preset `gmax_dbi=1` ignorado; solver usa ganho por faixa (1.5 dBi em 915 MHz); override apenas se usuário definiu `gmax_dbi` explicitamente
- `commercial_omni_6dbi`: HPBW agora usa `35°` do preset em vez de `20°` legado
- Parabólica/helical: `hpbw_deg` da spec sobrescreve cálculo geométrico interno

### Polarização Automática
- `estimate_polarization_loss(tx_ant, rx_ant)` — penalidade automática: circular vs linear = 3 dB; incompatíveis = 1 dB; iguais/desconhecidas = 0 dB
- `LinkResult.polarization_loss_db` — campo separado de `extra_loss_db` para rastreabilidade

### Ranking
- `_compute_robustness` usa `multi_direction_score` via preset/spec para penalizar GW direcional em cenário multi-sensor
- `ComparisonRow` ganhou `practicality_score`, `aggregate_score` e `scores_source`
- Parabólica como GW multi-sensor: robustness ~8× menor que omni

### Frontend
- Sandbox: `pcb_compact` e `commercial_omni_6dbi` adicionados ao dropdown com SVG visual, Pattern3D e GEO_FIELDS vazio
- Sandbox: seção colapsável "Campos Físicos" com 7 campos e auto-preenchimento por tipo
- Library: nova coluna "Física" com badges HPBW, polarização e direcional

### Backfill
- `scripts/backfill_antenna_fields.py` — dry-run por padrão, `--write` para aplicar, `--data-dir` para dir alternativo
- Preserva `geometry`, `results`, `metadata` e campos físicos já definidos pelo usuário

### Documentação
- Docs atualizados: 4 arquivos em `docs/` e `docs/for-dummies/`
- `backend/data/README.md` — seção de backfill com exemplos e tabela de casos

## Estado Final da Validação

```
uv run pytest
336 passed, 1 skipped, 1 warning
```

Progressão por fase:

| Após Fase | Total passed |
|---|---|
| 5 | 285 |
| 6 | 323 (+9 novos em test_comparison.py, +29 em outras) |
| 7 | 323 (zero novos — API/storage já cobertos) |
| 8 | 336 (+13 em test_backfill.py) |
| 9 | 336 (confirmação, zero regressão) |

Todos os 9 casos mínimos da Fase 9 cobertos por testes automatizados.

## Próximos Passos Recomendados

| Item | Prioridade | Esforço |
|---|---|---|
| Ordenar comparação por `aggregate_score` em vez de `min_margin_db` | Média | Baixo — 1 linha em `comparison.py` |
| Substituir `httpx` por `httpx2` nos testes | Baixa | Baixo — atualização de dependência |
| Testes automatizados de UI (Playwright/Selenium) | Baixa | Alto — setup significativo |
| Visualização 3D completa de diagramas de irradiação | Baixa | Alto — fora do escopo das melhorias 2 |
| Backfill explícito de specs antigas em produção | Quando necessário | Baixo — script pronto |
