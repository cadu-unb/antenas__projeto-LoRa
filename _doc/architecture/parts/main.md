<link rel="stylesheet" type="text/css" href="../../css/style_.css">

# Implementation Roadmap — LoRa Antenna Platform MVP

**Status**: Ready for Development  
**Target**: Production-ready MVP com gateways LoRa corporativos  
**Last Updated**: 2026-05-11  

---

## Visão Geral

Roadmap segmentado em 11 sprints (Checkpoint 0.5 até 10), cada um com:
- Objetivos de curto prazo (semanal)
- Dependências explícitas
- Critérios de aceite (DoD)
- Rotinas de auto-validação (gatekeeping)
- Plano de rollback

**Gatekeeping**: Nenhum sprint avança sem passar na validação anterior.

---

## Sumário

- [Implementation Roadmap — LoRa Antenna Platform MVP](#implementation-roadmap--lora-antenna-platform-mvp)
  - [Visão Geral](#visão-geral)
  - [Sumário](#sumário)
  - [Arquitetura de Blocos](#arquitetura-de-blocos)
    - [BLOCO 1: SANDBOX DE SIMULAÇÃO (Sprints 0.5-7)](#bloco-1-sandbox-de-simulação-sprints-05-7)
    - [BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO (Sprints 8-10)](#bloco-2-simulação-em-campus-darcy-ribeiro-sprints-8-10)
  - [SPRINT 0.5: DOCUMENTAÇÃO TÉCNICA](#sprint-05-documentação-técnica)
  - [SPRINT 1: NÚCLEO MATEMÁTICO](#sprint-1-núcleo-matemático)
---

## Arquitetura de Blocos

Projeto dividido em **2 blocos complementares e integrados**, desenvolvidos sequencialmente:

### BLOCO 1: SANDBOX DE SIMULAÇÃO (Sprints 0.5-7)
**Objetivo**: Construir e validar ambiente controlado para modelagem de antenas e enlaces.

- Todos os modelos matemáticos implementados
- Classes Antenna + RF chain especificadas
- Testes contra literatura (ARRL, Balanis, Pozar)
- UI para criar/visualizar antenas
- Link budget com diretividade validado
- Padrões de radiação simulados


**Gate de Saída (Bloco 1 → Bloco 2)**:
- [ ] Todos 5 tipos de antena instanciados + testados
- [ ] Link budget validado contra ≥3 casos conhecidos
- [ ] UI sandbox executa sem erros
- [ ] Visualizações (polar, gain) renderizam corretamente
- [ ] Coverage heatmap funciona em espaço abstrato

---

### BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO (Sprints 8-10)
**Objetivo**: Aplicar objetos Antenna + Link do Sandbox em mapa real (UnB Campus).

- Importação de shapefile campus
- Grade espacial (5-50m) configurável
- Heatmap LoRa com cálculo de potência por ponto
- Relatórios com parâmetros + gráficos
- Deploy em container LAN

**Saída**: Plataforma completa em produção

**Relação entre blocos**:
```
Bloco 1 (Sandbox)
    ↓ validação ✓
Objetos Antenna + Link prontos
    ↓ reuso direto (sem modificação)
Bloco 2 (Campus)
    ↓ aplicação geográfica
Heatmap + Relatórios → Produção
```

> [SUMARIO](#sumário)

---

## SPRINT 0.5: DOCUMENTAÇÃO TÉCNICA
**Status**: BLOQUEADOR para Sprints posteriores  
**Bloco**: BLOCO 1

![[SPRINT-0_5]]

> [SUMARIO](#sumário)

---

## SPRINT 1: NÚCLEO MATEMÁTICO
**Bloqueador anterior**: Sprint 0 ✓ PASSA  
**Bloco**: BLOCO 1

<!-- ![[sprint/SPRINT-1.md]] -->

> [SUMARIO](#sumário)

---
<!-- 
## SPRINT 2-3: CLASSES ANTENNA
**Bloqueador anterior**: Sprint 1 ✓ PASSA  
**Bloco**: BLOCO 1

![[sprint/SPRINT-2_3.md]]

> [SUMARIO](#sumário)

---

## SPRINT 4: UI STANDALONE
**Bloqueador anterior**: Sprint 2-3 ✓ PASSA  
**Bloco**: BLOCO 1

![[sprint/SPRINT-4.md]]

> [SUMARIO](#sumário)

---

## SPRINT 5-6: LINK BUDGET + DIRETIVIDADE
**Bloqueador anterior**: Sprint 4 ✓ PASSA  
**Bloco**: BLOCO 1

![[sprint/SPRINT-5_6.md]]

> [SUMARIO](#sumário)

---

## SPRINT 7: VISUALIZAÇÕES
**Bloqueador anterior**: Sprint 5-6 ✓ PASSA  
**Bloco**: BLOCO 1

![[sprint/SPRINT-7.md]]

> [SUMARIO](#sumário)

---


## ✅ BLOCO 1 COMPLETO — TRANSIÇÃO PARA BLOCO 2

**Marco Crítico**: Sprint 7 concluído com sucesso  
**Status**: Sandbox de simulação validado e pronto

**Checklist de Saída Bloco 1**:
- ✓ 5 tipos de antena operacionais (Monopole, Dipole, GroundPlane, Patch, Yagi + ReflectorAntenna)
- ✓ Link budget com diretividade implementado
- ✓ Friis equation validado contra 3+ casos de teste conhecidos
- ✓ UI sandbox executável sem erros
- ✓ Visualizações polares + ganho renderizam
- ✓ Heatmap funciona em espaço abstrato (sem coordenadas reais)
- ✓ Persistência (Pydantic + JSON) operacional
- ✓ Testes unitários passam (coverage > 95%)

**Próximo Passo**: Integração geográfica com Campus Darcy Ribeiro  
**Data Esperada**: Fim do dia 19-22 do cronograma total

---

## 📍 BLOCO 2: SIMULAÇÃO EM CAMPUS DARCY RIBEIRO

Blocos 1 e 2 compartilham objetos Antenna + Link do Sandbox **sem modificação**.  
Bloco 2 adiciona contexto geográfico, mapa e relatórios.

> [SUMARIO](#sumário)

---

## SPRINT 8: GIS/COBERTURA
**Bloqueador anterior**: Sprint 7 ✓ PASSA  
**Bloco**: BLOCO 2

![[sprint/SPRINT-8.md]]

> [SUMARIO](#sumário)

---

## SPRINT 9: RELATÓRIOS
**Bloqueador anterior**: Sprint 8 ✓ PASSA  
**Bloco**: BLOCO 2

![[sprint/SPRINT-9.md]]

> [SUMARIO](#sumário)

---

## SPRINT 10: DEPLOY + QA
**Bloqueador anterior**: Sprint 9 ✓ PASSA  
**Bloco**: BLOCO 2

![[sprint/SPRINT-10.md]]

> [SUMARIO](#sumário)

---

## Gatekeeping Checklist Master

```markdown
# MASTER VALIDATION GATE

## Gate 0.5 → 0 (Documentação → Infra)
- [ ] 8 docs .md criados
- [ ] Todas as fórmulas com referências
- [ ] Casos de teste enumerados (≥15)
- [ ] Accuracy matrix definida

## Gate 0 → 1 (Infra → Formulas)
- [ ] `uv run streamlit run ...` funciona
- [ ] Docker build sucesso
- [ ] Git initial commit

## Gate 1 → 2-3 (Formulas → Antenas)
- [ ] `pytest tests/test_formulas.py` 100%
- [ ] Coverage > 95%
- [ ] Casos conhecidos dentro de tolerância

## Gate 2-3 → 4 (Antenas → UI)
- [ ] 6 classes de antena implementadas
- [ ] FeedSpecification com 7 tipos
- [ ] Serialização JSON funciona
- [ ] `pytest tests/test_antenna_*.py` 100%

## Gate 4 → 5-6 (UI → Link Budget)
- [ ] Streamlit antena page funciona
- [ ] Parâmetros exibem corretamente
- [ ] JSON export/import funciona

## Gate 5-6 → 7 (Link Budget → Visualizations)
- [ ] `pytest test_friis_budget.py` 100%
- [ ] LinkBudgetComplete testado
- [ ] Casos de teste Friis validados

## Gate 7 → 8 (Visualizations → GIS)
- [ ] Gráficos polares renderizam
- [ ] Power vs distance gráfico ok
- [ ] TX/RX breakdown visual ok

## Gate 8 → 9 (GIS → Reports)
- [ ] Heatmap renderiza em 5 min ou menos
- [ ] Grade configurável 5-50m
- [ ] Aviso de modelo simplificado aparece

## Gate 9 → 10 (Reports → Deploy)
- [ ] Markdown export funciona
- [ ] Gráficos incluídos em relatório
- [ ] Limitações documentadas

## Gate 10: FINAL QA
- [ ] App acessível em http://0.0.0.0:3953
- [ ] Testes E2E passam
- [ ] Docker funciona
- [ ] README completo
```

> [SUMARIO](#sumário)

---

## Rollback Procedures

### Quick Rollback (Sem perda de código)

```bash
# Se último commit quebrou algo
git log --oneline | head -5
git revert <commit-id>

# Se quer voltar a antes do sprint
git reset --soft origin/main
git status  # Mudanças estarão em staging
```

### Full Rollback (Volta ao estado anterior)

```bash
# Backup das mudanças (para salvaguarda)
git stash
git log --oneline > sprint-backup.log

# Voltar ao HEAD anterior a este sprint
git reset --hard <commit-id>

# Limpar Docker e ambiente
docker system prune -a --volumes
rm -rf .venv uv.lock
```

### Database Rollback (Se houver)

```bash
# Se uma migração quebrar
sqlite3 gestao.db ".tables"
sqlite3 gestao.db ".schema"

# Restaurar backup anterior
cp gestao.db.backup gestao.db
```

> [SUMARIO](#sumário)

---

## Métricas de Saúde do Projeto

**A cada sprint, medir**:

1. **Code Quality**
   - Test coverage (target: > 95%)
   - Linting issues (target: 0)
   - Type check errors (target: 0)

2. **Performance**
   - Streamlit load time: < 3s
   - Heatmap render: < 5m (1km²)
   - API response: < 200ms

3. **Status de Funcionalidades**
   - Critérios de aceite: 100%
   - Bugs críticos: 0
   - Warnings em UI: minimizados

> [SUMARIO](#sumário)

---

## Conclusão

Roadmap segue abordagem **"caminho feliz primeiro"**: funcionalidades básicas antes de otimização.

**Gate keepers** impedem avanço até que fase anterior esteja sólida.

**Documentação** (Sprint 0.5) é bloqueador proposital para evitar refatorações dispendiosas.

Cronograma realista **38-45 dias** com margem para contingências. -->
